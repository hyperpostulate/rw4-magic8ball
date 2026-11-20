#!/usr/bin/env python3
"""Reproducible PNG generator for the rw4-magic8ball quick app.

Why images? The Redmi Watch 4 Vela runtime does not draw text: <text>/<span>/<input>
paint nothing (or notdef boxes) and a bundled @font-face has no effect, while <image>
renders perfectly. Everything visible in this app is therefore a pre-rendered PNG
generated here, at exactly its on-screen display size.

Three states, three <image> nodes (title, face, hint):

    idle    -> face/idle_<stamp>.png     + txt/hint_ask_<stamp>.png
    rolling -> face/roll0..5_<stamp>.png + txt/hint_ask_<stamp>.png
    answer  -> face/ans00..19_<stamp>.png + txt/hint_again_<stamp>.png

<stamp> is a hash of the palette/geometry/copy constants below. The watch caches image
resources BY PATH across installs, so a stable filename keeps rendering stale pixels
after an update; hashing the content into the name makes every content change a new
path. This script also rewrites the generated constants block in
src/pages/index/index.ux so the app always points at the current names.

Run from anywhere:

    python3 scripts/gen_assets.py

Wipes and regenerates src/common/txt/ and src/common/face/, then re-opens and verifies
every file it wrote. Deterministic: same spec in, byte-identical PNGs out.

Spec: docs/design.md (authoritative for every number below).
"""

import hashlib
import json
import os
import re

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
COMMON = os.path.join(SRC, "common")
TXT_DIR = os.path.join(COMMON, "txt")
FACE_DIR = os.path.join(COMMON, "face")
FONT_BOOK = os.path.join(ROOT, "scripts", "assets", "ui-subset.ttf")
FONT_BOLD = os.path.join(ROOT, "scripts", "assets", "DejaVuSans-Bold.ttf")
MANIFEST_PATH = os.path.join(SRC, "manifest.json")
UX_PATH = os.path.join(SRC, "pages", "index", "index.ux")

SS = 4  # supersampling factor; everything is drawn at 4x then Lanczos-downsampled

# ---- palette (docs/design.md 2) ----
BLACK = (0, 0, 0, 255)
CARD = (10, 25, 47, 255)        # #0A192F
EDGE = (74, 107, 138, 255)      # #4A6B8A
TITLE = (143, 169, 192, 255)    # #8FA9C0
PRIMARY = (239, 247, 255, 255)  # #EFF7FF
MUTED = (203, 213, 224, 255)    # #CBD5E0
WARN = (229, 183, 183, 255)     # #E5B7B7

# ---- geometry (docs/design.md 3) ----
SCREEN_W, SCREEN_H = 390, 450
TITLE_BOX = (320, 34)
HINT_BOX = (320, 24)
CARD_BOX = (310, 280)
CARD_RADIUS = 44
CARD_STROKE = 2
# Answer box, in card-local coordinates (absolute 74,138 -> 316,322).
ANS_BOX = (34, 52, 242, 184)
ANS_LINE_H = 38
ANS_SIZES = (30, 28, 26)  # largest that wraps every answer into <= 3 lines

# ---- typography (docs/design.md 5) ----
TITLE_SIZE, TITLE_TRACK = 22, 3
HINT_SIZE, HINT_TRACK = 18, 0.5
EMBLEM_SIZE = 56
RING_D = 104
RING_W = 4
ARC_W = 6
RING_DIM = 0.28  # alpha multiplier of the spinner's track ring
LOGO_SIZE = 96

# ---- copy (docs/design.md 7) ----
APP_TITLE = "MAGIC 8 BALL"
HINT_ASK = "Tap to seek answer\u2026"
HINT_AGAIN = "Tap to ask again"

ANSWERS = [
    # affirmative -> PRIMARY
    ("affirmative", "It is certain."),
    ("affirmative", "It is decidedly so."),
    ("affirmative", "Without a doubt."),
    ("affirmative", "Yes definitely."),
    ("affirmative", "You may rely on it."),
    ("affirmative", "As I see it, yes."),
    ("affirmative", "Most likely."),
    ("affirmative", "Outlook good."),
    ("affirmative", "Yes."),
    ("affirmative", "Signs point to yes."),
    # non-committal -> MUTED
    ("unclear", "Reply hazy, try again."),
    ("unclear", "Ask again later."),
    ("unclear", "Better not tell you now."),
    ("unclear", "Cannot predict now."),
    ("unclear", "Concentrate and ask again."),
    # negative -> WARN
    ("negative", "Don't count on it."),
    ("negative", "My reply is no."),
    ("negative", "My sources say no."),
    ("negative", "Outlook not so good."),
    ("negative", "Very doubtful."),
]

CAT_COLOR = {"affirmative": PRIMARY, "unclear": MUTED, "negative": WARN}

ROLL_FRAMES = 6


# --------------------------------------------------------------------------- utils

def _font(path, size):
    return ImageFont.truetype(path, size)


def _spec_stamp():
    """8 hex chars over everything that affects pixels or the on-screen strings."""
    spec = json.dumps({
        "palette": [BLACK, CARD, EDGE, TITLE, PRIMARY, MUTED, WARN],
        "geometry": [SCREEN_W, SCREEN_H, TITLE_BOX, HINT_BOX, CARD_BOX, CARD_RADIUS,
                     CARD_STROKE, ANS_BOX, ANS_LINE_H, ANS_SIZES, RING_D, RING_W,
                     ARC_W, RING_DIM],
        "type": [TITLE_SIZE, TITLE_TRACK, HINT_SIZE, HINT_TRACK, EMBLEM_SIZE, LOGO_SIZE],
        "copy": [APP_TITLE, HINT_ASK, HINT_AGAIN, ANSWERS],
        "render": [SS, ROLL_FRAMES],
    }, sort_keys=True).encode("utf-8")
    return hashlib.sha256(spec).hexdigest()[:8]


def _new(size):
    """Transparent canvas at SS times the target size, plus its draw handle."""
    return Image.new("RGBA", (size[0] * SS, size[1] * SS), (0, 0, 0, 0))


def _down(img, size):
    return img.resize(size, Image.LANCZOS)


def _verify(path, size, min_colors=1):
    chk = Image.open(path)
    chk.load()
    assert chk.size == size, ("wrong size", path, chk.size, size)
    alpha = chk.getchannel("A")
    bbox = alpha.getbbox()
    assert bbox is not None, "blank image: " + path
    if min_colors > 1:
        colors = chk.getcolors(maxcolors=1 << 16)
        assert colors is not None, "too many colours to verify: " + path
        assert len(colors) >= min_colors, ("flat image", path, len(colors))
    # a text asset must have some ink strictly inside the canvas edges
    assert bbox[0] >= 0 and bbox[2] <= size[0] and bbox[1] >= 0 and bbox[3] <= size[1]


def _save(img, size, path, min_colors=1):
    out = _down(img, size)
    out.save(path, optimize=True)
    _verify(path, size, min_colors)


def _tracked_width(text, font, tracking):
    return sum(font.getlength(c) for c in text) + tracking * max(0, len(text) - 1)


def _draw_tracked(img, text, font, tracking, cx, cy, fill):
    """Draw text with letter spacing, centred on (cx, cy) in SS pixels."""
    d = ImageDraw.Draw(img)
    x = cx - _tracked_width(text, font, tracking) / 2.0
    for ch in text:
        d.text((x, cy), ch, font=font, fill=fill, anchor="lm")
        x += font.getlength(ch) + tracking


def _wrap(text, font, max_w):
    """Greedy word wrap; never splits a word. max_w in un-scaled px."""
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        cand = w if not cur else cur + " " + w
        if font.getlength(cand) <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _pick_answer_font():
    """Largest size from ANS_SIZES that fits every answer in ANS_BOX: <=3 lines, height ok."""
    box_w, box_h = ANS_BOX[2], ANS_BOX[3]
    for size in ANS_SIZES:
        font = _font(FONT_BOOK, size)
        ok = True
        for _, text in ANSWERS:
            lines = _wrap(text, font, box_w)
            if len(lines) > 3 or len(lines) * ANS_LINE_H > box_h:
                ok = False
                break
            if any(font.getlength(line) > box_w for line in lines):
                ok = False
                break
        if ok:
            return size
    raise SystemExit("no font size fits the answer box: shrink the copy")


# --------------------------------------------------------------------------- pieces

def _card(img):
    """Rounded card with the 2px steel edge, drawn inset so the stroke stays visible."""
    d = ImageDraw.Draw(img)
    w = CARD_BOX[0] * SS
    h = CARD_BOX[1] * SS
    inset = CARD_STROKE * SS / 2.0
    d.rounded_rectangle(
        [inset, inset, w - 1 - inset, h - 1 - inset],
        radius=CARD_RADIUS * SS,
        fill=CARD,
        outline=EDGE,
        width=CARD_STROKE * SS,
    )


def _ring(img, center, radius, arc=None):
    """Steel ring at card-local (x, y); optional bright catalog arc over a dim track."""
    d = ImageDraw.Draw(img)
    cx, cy = center[0] * SS, center[1] * SS
    r = radius * SS
    box = [cx - r, cy - r, cx + r, cy + r]
    if arc is None:
        d.ellipse(box, outline=EDGE, width=RING_W * SS)
        return
    dim = (EDGE[0], EDGE[1], EDGE[2], int(round(255 * RING_DIM)))
    d.ellipse(box, outline=dim, width=RING_W * SS)
    start, end = arc
    d.arc(box, start=start, end=end, fill=EDGE, width=ARC_W * SS)
    # round caps (PIL arcs are butt-ended)
    import math
    for deg in (start, end):
        a = math.radians(deg)
        px, py = cx + r * math.cos(a), cy + r * math.sin(a)
        cap = ARC_W * SS / 2.0
        d.ellipse([px - cap, py - cap, px + cap, py + cap], fill=EDGE)


def make_logo(path):
    size = (LOGO_SIZE, LOGO_SIZE)
    img = _new(size)
    d = ImageDraw.Draw(img)
    w = LOGO_SIZE * SS
    d.rounded_rectangle([0, 0, w - 1, w - 1], radius=20 * SS, fill=CARD)
    c = w / 2.0
    r = 31 * SS
    d.ellipse([c - r, c - r, c + r, c + r], outline=EDGE, width=5 * SS)
    d.text((c, c), "8", font=_font(FONT_BOLD, 38 * SS), fill=TITLE, anchor="mm")
    _save(img, size, path, min_colors=3)


def make_title(path):
    size = TITLE_BOX
    img = _new(size)
    _draw_tracked(img, APP_TITLE, _font(FONT_BOLD, TITLE_SIZE * SS),
                  TITLE_TRACK * SS, size[0] * SS / 2.0, size[1] * SS / 2.0, TITLE)
    _save(img, size, path, min_colors=2)


def make_hint(path, text):
    size = HINT_BOX
    img = _new(size)
    _draw_tracked(img, text, _font(FONT_BOOK, HINT_SIZE * SS),
                  HINT_TRACK * SS, size[0] * SS / 2.0, size[1] * SS / 2.0, MUTED)
    _save(img, size, path, min_colors=2)


def make_idle(path):
    size = CARD_BOX
    img = _new(size)
    _card(img)
    c = (size[0] / 2.0, size[1] / 2.0)
    _ring(img, c, RING_D / 2.0)
    d = ImageDraw.Draw(img)
    d.text((c[0] * SS, c[1] * SS), "8", font=_font(FONT_BOLD, EMBLEM_SIZE * SS),
           fill=EDGE, anchor="mm")
    _save(img, size, path, min_colors=3)


def make_roll(path, frame):
    size = CARD_BOX
    img = _new(size)
    _card(img)
    c = (size[0] / 2.0, size[1] / 2.0)
    start = frame * (360.0 / ROLL_FRAMES) - 90.0
    _ring(img, c, RING_D / 2.0, arc=(start, start + 90.0))
    d = ImageDraw.Draw(img)
    d.text((c[0] * SS, c[1] * SS), "8", font=_font(FONT_BOLD, EMBLEM_SIZE * SS),
           fill=TITLE, anchor="mm")
    _save(img, size, path, min_colors=4)


def make_answer(path, text, color, answer_size):
    size = CARD_BOX
    img = _new(size)
    _card(img)
    font = _font(FONT_BOOK, answer_size * SS)
    lines = _wrap(text, _font(FONT_BOOK, answer_size), ANS_BOX[2])
    assert 1 <= len(lines) <= 3, ("bad wrap", text, lines)
    lh = ANS_LINE_H * SS
    total = lh * len(lines)
    cx = (ANS_BOX[0] + ANS_BOX[2] / 2.0) * SS
    y0 = ANS_BOX[1] * SS + (ANS_BOX[3] * SS - total) / 2.0 + lh / 2.0
    d = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        d.text((cx, y0 + i * lh), line, font=font, fill=color, anchor="mm")
    _save(img, size, path, min_colors=4)


# --------------------------------------------------------------------------- wiring

def _sync_ux(block):
    """Replace the generated constants block in index.ux (single occurrence)."""
    with open(UX_PATH, encoding="utf-8") as f:
        text = f.read()
    pattern = re.compile(r"// __ASSETS_BEGIN__.*?// __ASSETS_END__", re.S)
    new, count = pattern.subn(block.strip(), text, count=1)
    assert count == 1, ("expected exactly one generated asset block in index.ux", count)
    if new != text:
        with open(UX_PATH, "w", encoding="utf-8") as f:
            f.write(new)


def _version():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)["versionName"]


def main():
    for d in (TXT_DIR, FACE_DIR):
        if os.path.isdir(d):
            for name in os.listdir(d):
                if name.endswith(".png"):
                    os.remove(os.path.join(d, name))
        os.makedirs(d, exist_ok=True)

    stamp = _spec_stamp()
    answer_size = _pick_answer_font()
    suffix = "_" + stamp + ".png"

    def txt(stem):
        return os.path.join(TXT_DIR, stem + suffix)

    def face(stem):
        return os.path.join(FACE_DIR, stem + suffix)

    make_logo(os.path.join(COMMON, "logo.png"))
    make_title(txt("title"))
    make_hint(txt("hint_ask"), HINT_ASK)
    make_hint(txt("hint_again"), HINT_AGAIN)
    make_idle(face("idle"))
    for i in range(ROLL_FRAMES):
        make_roll(face("roll%d" % i), i)
    for i, (cat, text) in enumerate(ANSWERS):
        make_answer(face("ans%02d" % i), text, CAT_COLOR[cat], answer_size)

    ans_srcs = ",\n  ".join("'/common/face/ans%02d%s'" % (i, suffix) for i in range(len(ANSWERS)))
    roll_srcs = ",\n  ".join("'/common/face/roll%d%s'" % (i, suffix) for i in range(ROLL_FRAMES))

    block = "\n".join([
        "// __ASSETS_BEGIN__ generated by scripts/gen_assets.py - do not edit by hand",
        "// stamp: " + stamp + " (content hash; changes whenever copy/geometry changes)",
        "// version: " + _version(),
        "const TITLE_SRC = '/common/txt/title" + suffix + "'",
        "const HINT_ASK_SRC = '/common/txt/hint_ask" + suffix + "'",
        "const HINT_AGAIN_SRC = '/common/txt/hint_again" + suffix + "'",
        "const FACE_IDLE = '/common/face/idle" + suffix + "'",
        "const FACE_ROLL = [\n  " + roll_srcs + "\n]",
        "const FACE_ANS = [\n  " + ans_srcs + "\n]",
        "// __ASSETS_END__",
    ])
    _sync_ux(block)

    print("stamp %s | answers %d @ %dpx | roll frames %d | logo %dpx"
          % (stamp, len(ANSWERS), answer_size, ROLL_FRAMES, LOGO_SIZE))
    print("wrote %d PNGs into %s and %s"
          % (1 + 3 + 1 + ROLL_FRAMES + len(ANSWERS),
             os.path.relpath(TXT_DIR, ROOT), os.path.relpath(FACE_DIR, ROOT)))


if __name__ == "__main__":
    main()
