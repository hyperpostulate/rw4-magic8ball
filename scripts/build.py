#!/usr/bin/env python3
"""Build one .rpk per locale.

The app ships both languages as pre-rendered PNG sets and picks one at build
time: `index.ux` reads `LOCALE` from the generated asset block, so the runtime
never branches on language and only the assets of the built locale are opened.

For each locale in LOCALE_ORDER this script

  1. rewrites `const LOCALE = '<loc>'` in src/pages/index/index.ux,
  2. runs `aiot build` (same package name for every locale: installing the other
     .rpk updates the app in place instead of adding a second launcher entry),
  3. renames the produced .rpk to `<base>.<loc>.rpk` in dist/,
  4. restores LOCALE to the default ('en') so the tree is left as committed.

Run it instead of `npm run build`:

    npm run build              # -> dist/<pkg>.debug.<version>.en.rpk + .tr.rpk
    npm run build:en           # only the English package
    npm run build:tr           # only the Turkish package

The generated PNGs must already exist: run `python3 scripts/gen_assets.py`
first (both locales are generated in one pass).
"""

import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UX_PATH = os.path.join(ROOT, "src", "pages", "index", "index.ux")
MANIFEST_PATH = os.path.join(ROOT, "src", "manifest.json")
DIST = os.path.join(ROOT, "dist")
DEFAULT_LOCALE = "en"
LOCALE_ORDER = ("en", "tr")

LOCALE_LINE = re.compile(r"^const LOCALE = '[a-z]{2}'$", re.M)
# Generated per-locale asset trees inside src/common. The build packs everything
# under src/, so a locale that is not the active one is moved aside while its
# package is compiled; otherwise every .rpk carries the other language's faces
# and doubles in size (PNGs do not compress).
LOCALE_ASSET_KINDS = ("face", "txt")


def _set_locale(loc):
    with open(UX_PATH, encoding="utf-8") as f:
        text = f.read()
    new, count = LOCALE_LINE.subn("const LOCALE = '%s'" % loc, text)
    assert count == 1, ("expected exactly one LOCALE line in index.ux", count)
    if new != text:
        with open(UX_PATH, "w", encoding="utf-8") as f:
            f.write(new)


def _manifest():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def _assets_present():
    """Both locales' generated hints must exist; otherwise the build is stale."""
    with open(UX_PATH, encoding="utf-8") as f:
        text = f.read()
    srcs = re.findall(r"'(/common/[^']+\.png)'", text)
    assert srcs, "no generated asset block in index.ux - run gen_assets.py"
    missing = [s for s in srcs if not os.path.isfile(os.path.join(ROOT, "src", s.lstrip("/")))]
    if missing:
        raise SystemExit("missing generated PNGs (run scripts/gen_assets.py): %s"
                         % ", ".join(missing[:5]))


def _stash_inactive_locales(active, stash_root):
    """Move every other locale's asset dirs out of src/ so they are not packed."""
    moved = []
    for loc in LOCALE_ORDER:
        if loc == active:
            continue
        for kind in LOCALE_ASSET_KINDS:
            src = os.path.join(ROOT, "src", "common", kind, loc)
            if not os.path.isdir(src):
                continue
            dst = os.path.join(stash_root, kind, loc)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            os.replace(src, dst)
            moved.append((src, dst))
    return moved


def _unstash(moved):
    for src, dst in moved:
        os.makedirs(os.path.dirname(src), exist_ok=True)
        os.replace(dst, src)


def _unstash_from(stash_root):
    """Recover trees left behind by an interrupted run (crash / SIGKILL)."""
    if not os.path.isdir(stash_root):
        return
    for kind in LOCALE_ASSET_KINDS:
        for loc in LOCALE_ORDER:
            src = os.path.join(stash_root, kind, loc)
            if not os.path.isdir(src):
                continue
            dst = os.path.join(ROOT, "src", "common", kind, loc)
            print("restoring interrupted build: %s" % os.path.relpath(dst, ROOT))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            os.replace(src, dst)


def _aiot_build():
    exe = shutil.which("aiot")
    cmd = [exe, "build"] if exe else ["npx", "--no-install", "aiot", "build"]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stdout.write(proc.stdout[-4000:])
        sys.stderr.write(proc.stderr[-4000:])
        raise SystemExit("aiot build failed (%d)" % proc.returncode)


def _rename_newest(dest_base, loc, staging):
    """Move the single freshly produced .rpk into the staging dir as <base>.<loc>.rpk."""
    rpks = [f for f in os.listdir(DIST) if f.endswith(".rpk")]
    assert rpks, "build produced no .rpk in dist/"
    # The build writes exactly one file per run; pick the newest to be safe.
    newest = max(rpks, key=lambda f: os.path.getmtime(os.path.join(DIST, f)))
    target = "%s.%s.rpk" % (dest_base, loc)
    os.replace(os.path.join(DIST, newest), os.path.join(staging, target))
    return target


def main(argv):
    wanted = [a for a in argv[1:] if a in LOCALE_ORDER] or list(LOCALE_ORDER)
    unknown = [a for a in argv[1:] if a not in LOCALE_ORDER]
    if unknown:
        raise SystemExit("unknown locale(s): %s (expected: %s)"
                         % (", ".join(unknown), ", ".join(LOCALE_ORDER)))

    # A hard kill during a build can leave the stashed locale trees behind; put
    # them back before validating anything, otherwise they would be deleted.
    _unstash_from(os.path.join(ROOT, ".rpk-staging", "src"))

    _assets_present()
    manifest = _manifest()
    base = "%s.%s.%s" % (manifest["package"],
                         "debug" if os.environ.get("AIOT_RELEASE") != "1" else "release",
                         manifest["versionName"])

    # aiot build wipes dist/ on every run, so variants are staged outside it
    # and only published once every locale has been built.
    staging = os.path.join(ROOT, ".rpk-staging")
    if os.path.isdir(staging):
        shutil.rmtree(staging)
    os.makedirs(staging)

    made = []
    try:
        for loc in wanted:
            _set_locale(loc)
            moved = _stash_inactive_locales(loc, os.path.join(staging, "src"))
            try:
                _aiot_build()
            finally:
                _unstash(moved)
            made.append(_rename_newest(base, loc, staging))
    finally:
        _set_locale(DEFAULT_LOCALE)
        os.makedirs(DIST, exist_ok=True)
        for name in made:
            os.replace(os.path.join(staging, name), os.path.join(DIST, name))
        shutil.rmtree(staging, ignore_errors=True)

    for name in made:
        print("built dist/%s" % name)


if __name__ == "__main__":
    main(sys.argv)
