<!-- Language: English | [Türkçe](README-TR.md) -->

<p align="center">
  <img src="src/common/logo.png" alt="Magic 8 Ball" width="96" height="96">
</p>

<h1 align="center">rw4-magic8ball — Magic 8 Ball for the Redmi Watch 4</h1>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Xiaomi%20Vela-blue" alt="Platform: Xiaomi Vela">
  <img src="https://img.shields.io/badge/device-Redmi%20Watch%204-orange" alt="Device: Redmi Watch 4">
  <img src="https://img.shields.io/badge/version-1.0.0-green" alt="Version 1.0.0">
  <img src="https://img.shields.io/badge/license-GPLv3-blue" alt="License: GPLv3">
</p>

<p align="center">Ask a question out loud, tap the screen, get an answer. A Xiaomi Vela quick app for the Redmi Watch 4.</p>

<p align="center">Türkçe sürüm: <a href="README-TR.md">README-TR.md</a></p>

A Magic 8 Ball — the classic toy [from 1950](https://en.wikipedia.org/wiki/Magic_8_Ball) — rebuilt as a single-screen `.rpk` for the Redmi Watch 4. All 20 canonical answers are on board, chosen uniformly at random. Built on the [rw4-poc](https://github.com/hyperpostulate/rw4-poc) boilerplate, so it stays inside everything the device actually allows: no text rendering, no canvas, no network.

* * *

## Table of Contents

- [What it does](#what-it-does)
- [Install on the Watch](#install-on-the-watch)
- [Build & Run](#build--run)
- [Project Structure](#project-structure)
- [Design](#design)
- [On-device findings](#on-device-findings)
- [Limitations](#limitations)
- [License](#license)
- [Developer](#developer)
- [Contributing](#contributing)

* * *

## What it does

One screen, three states, one input: **tap anywhere**.

| State | Screen | Haptics |
| :-- | :-- | :-- |
| **Idle** | Navy card with a steel ring and "8", hint `Tap to seek answer…` | — |
| **Rolling** (600 ms) | The ring becomes a spinning arc, 6 frames at 100 ms | short pulse on tap |
| **Answer** | One of the 20 answers on the card, hint `Tap to ask again` | long pulse on settle |

Answers are the canonical set, 10 affirmative / 5 non-committal / 5 negative, each with a 1/20 probability — the classic ball has no memory and no bias. The answer's tint carries the category: near-white for yes, silver-blue for unclear, pale rose for no.

```
┌───────────────────────────────┐    ┌───────────────────────────────┐
│          MAGIC 8 BALL         │    │          MAGIC 8 BALL         │
│    ╭───────────────────╮      │    │    ╭───────────────────╮      │
│    │                   │      │    │    │                   │      │
│    │       ( 8 )       │      │    │    │  Concentrate      │      │
│    │                   │      │    │    │  and ask again.   │      │
│    ╰───────────────────╯      │    │    ╰───────────────────╯      │
│      Tap to seek answer…      │    │        Tap to ask again       │
└───────────────────────────────┘    └───────────────────────────────┘
```

* * *

## Install on the Watch

The `.rpk` is installed over Bluetooth from an Android phone using the **[Notify for Xiaomi](https://play.google.com/store/apps/details?id=com.mc.xiaomi1)** app (package `com.mc.xiaomi1`, by OneZeroBit). The Redmi Watch 4 is on the app's official compatibility list, and the app's official site documents installing custom VelaJS (`.rpk`) apps this way.

> **Verification status:** fully verified on a real Redmi Watch 4 — the app installs, tap input drives the idle→rolling→answer flow exactly as designed, and both vibration pulses fire.

> **Bump the version on every build.** Notify for Xiaomi and the watch cache quick-app packages by `versionName` and `versionCode`. If both are unchanged, the cached build can be installed instead of the fresh `.rpk`. Before every build, increment both fields in `src/manifest.json`; `versionName` is also part of the output filename, so a bump gives a distinct file as well (`dist/com.hyperpostulate.rw4magic8ball.debug.<versionName>.rpk`).

### Prerequisites

- An **Android phone** (iOS cannot install `.rpk` files).
- **Notify for Xiaomi** installed from Google Play.
- The watch paired with Notify: the in-app setup wizard fetches the pairing (auth) key through your Xiaomi account, so Mi Fitness does not need to stay installed.
- Only one app can hold the watch's Bluetooth connection at a time. If Mi Fitness is installed, force-stop it, deny its "Nearby devices" permission, or uninstall it — but **do not un-pair the watch from Mi Fitness before uninstalling**.

### Steps

1. Build the package: `npm run build` → `dist/com.hyperpostulate.rw4magic8ball.debug.1.0.0.rpk`.
2. Open **Notify for Xiaomi**.
3. Go to **Device**.
4. Select **Third party app**.
5. Select the `.rpk` file.
6. Keep the watch near the phone and follow the guided steps.
7. When the installation finishes, **Magic 8 Ball** appears in the watch's app list.

### Notes

- The debug-signed `.rpk` produced by `npm run build` is fine for this app: Vela only checks the certificate for watch↔phone Interconnect communication, which this app does not use.
- Redmi Watch 4 limits: at most ~20 quick apps installed, and ~87 MB of free space is required for quick-app installs.
- To update, build a new `.rpk` and install it over the same package name (`com.hyperpostulate.rw4magic8ball`). Changing the `package` value installs a **separate** app instead of updating.
- Unverified details: the app version that introduced `.rpk` installs, and whether the feature requires the (about €3, one-time) PRO purchase, are not officially documented. The menu labels above are the English ones; the app itself is localized, but the Turkish labels were not verified.

Sources: [Notify for Xiaomi VelaJS install guide](https://mibandnotify.com/xiaomi-mi-band/notify-xms-app-instructions.php) · [Google Play listing](https://play.google.com/store/apps/details?id=com.mc.xiaomi1)

* * *

## Build & Run

| Requirement | Version / Notes |
| :-- | :-- |
| Node.js | 18+ (tested on v24.12.0) |
| npm | 9+ (tested on 11.6.2) |
| Python 3 + Pillow | Only needed to regenerate the PNG assets (`scripts/gen_assets.py`) |
| Android phone | Only needed to install the `.rpk` onto the watch via **Notify for Xiaomi** (see [Install on the Watch](#install-on-the-watch)) |
| `aiot-toolkit` | Pulled in automatically as a dev dependency (`npm install`) |

```
git clone https://github.com/hyperpostulate/rw4-magic8ball.git
cd rw4-magic8ball
npm install                          # Install the aiot-toolkit toolchain
npm run build                        # Build a debug .rpk into dist/
npm run release                      # Build a release .rpk (requires signing keys)
npm run start                        # aiot start --watch (live development)
python3 scripts/gen_assets.py        # Regenerate the PNG assets from code
```

The build produces `dist/com.hyperpostulate.rw4magic8ball.debug.1.0.0.rpk`. The debug `.rpk` needs no signing; a release package needs `sign/private.pem` and `sign/certificate.pem` (generate with OpenSSL).

### On-device checklist

All seven checks below **pass on a real Redmi Watch 4** (verified 2026-11-20). Keep the list for regression runs after a change.

1. Does the app open on the idle card (title, "8" ring, `Tap to seek answer…`)? ✅
2. **Does a tap start the spin?** ✅ Both `@click` and `@touchstart` are bound; which one the runtime emits was never isolated, so the pair stays bound behind the 350 ms guard.
3. Do 6 arc frames animate, then an answer appear within ~0.7 s? ✅
4. Does the answer text wrap into at most 3 lines, never clipped by the card? ✅
5. Does the vibration pulse on tap and on settle? ✅ Both pulses confirmed.
6. Does a second tap roll again, and does the hint stay `ask` during the roll? ✅
7. Are the rounded screen corners cropping nothing (title, hint, card edge)? ✅

* * *

## Project Structure

```
rw4-magic8ball/
├── src/
│   ├── manifest.json          # package com.hyperpostulate.rw4magic8ball, designWidth 390
│   ├── app.ux                 # app entry (onCreate/onDestroy)
│   ├── common/
│   │   ├── logo.png           # launcher icon: navy tile + ring + "8", 96x96
│   │   ├── txt/               # title + two hints (generated)
│   │   └── face/              # idle + 6 spinner + 20 answer faces (generated)
│   └── pages/
│       └── index/
│           └── index.ux       # the whole app: 3 images, state machine, styles
├── scripts/
│   ├── gen_assets.py          # reproducible Pillow generator for all 31 PNGs
│   └── assets/
│       ├── ui-subset.ttf          # DejaVu Sans Book (generation time only)
│       └── DejaVuSans-Bold.ttf    # generation time only
├── docs/
│   ├── design.md              # UI spec: palette, geometry, typography, motion, copy (English)
│   ├── findings.md            # bilingual on-device findings (from the boilerplate)
│   ├── development.md         # bilingual guide: developing new apps from this template
│   └── native-development.md  # research: what is possible beyond quick apps
├── dist/                      # build output (.rpk) - gitignored
├── build/                     # intermediate build output - gitignored
├── package.json
├── LICENSE                    # GPLv3 full text
├── README.md                  # English
└── README-TR.md               # Turkish
```

### Core Files

| File | Purpose |
| :-- | :-- |
| `src/manifest.json` | Vela app manifest: `package` = `com.hyperpostulate.rw4magic8ball`, `name` = `Magic 8 Ball`, `deviceTypeList: ["watch"]`, `designWidth: 390`, `features: ["system.router", "system.vibrator"]` |
| `src/pages/index/index.ux` | The whole app: template (title, face, hint), the idle→rolling→answer state machine, tap guard, timers, styles, generated asset names |
| `scripts/gen_assets.py` | Generates the card faces, title, hints and launcher icon deterministically; stamps filenames with a content hash and rewrites the asset block in `index.ux` |
| `docs/design.md` | The authoritative UI spec (palette, geometry, typography, motion, copy list) |

* * *

## Design

"Midnight blue minimal": true-black background, one deep-navy rounded card (`#0A192F`) with a 2 px steel edge (`#4A6B8A`), near-white text. No skeuomorphic sphere, no triangle — the card itself is the ball.

Every number is in **[docs/design.md](docs/design.md)**. The short version:

- Canvas 390×450; content stops at y = 398 because the curved glass crops the corners.
- Title 320×34 at (35,34); card 310×280 at (40,86); hint 320×24 at (35,374).
- Answer box 242×184 inside the card, 30 px DejaVu Sans Book, 38 px line height, greedy wrap, max 3 lines — the generator downshifts to 28/26 px if any answer would overflow, and asserts the block fits.
- 31 PNGs, 3 `<image>` nodes on screen.

### Why everything is a PNG

The Redmi Watch 4's Vela runtime draws **no readable text**: `<text>`, `<span>` and `<input>` paint nothing or tofu boxes, and a bundled `@font-face` has no effect. `<image>` renders perfectly. So every visible string is pre-rendered by `scripts/gen_assets.py` and the card face (fill + edge + answer text) is baked into a single image, which also keeps the on-screen node count at three.

Because the watch caches images **by path** across installs, asset filenames embed a content-hash stamp (`ans00_81d7cf41.png`). Editing copy changes the stamp, so the new build cannot render the old pixels.

* * *

## On-device findings

Verified on a **real Redmi Watch 4**. Full detail — including the complete system-API table — is in **[docs/findings.md](docs/findings.md)**.

- **Text does not render.** Every visible string must be a pre-rendered PNG.
- **Which system APIs work.** `@system.device`, `@system.storage`, `@system.brightness`, `@system.app`, `@system.vibrator` and the JS clock work; geolocation (GPS, error `203`), sensor, battery, network, bluetooth, record, fetch and crypto do not.
- **Canvas crashes the watch** — black screen, then a runtime reboot. The `<image>` renderer is the only option.
- **Launcher icon size moves the app name**: the **96×96** `logo.png` is deliberate (`192×192` pushed the label into the middle of the row).
- **Tap input and vibration are verified.** `@click` and `@touchstart` are both bound to one handler behind a 350 ms guard — the runtime delivers taps reliably, but *which* of the two event names it emits was never isolated, so the pair stays. `vibrator.vibrate()` fires both the short (tap) and long (settle) pulse.

* * *

## Limitations

- **No network, no GPS, no sensors.** The answers are a fixed local list; nothing is fetched or computed from the environment.
- **Text must be images.** Adding or editing an answer means editing `ANSWERS` in `scripts/gen_assets.py`, re-running the generator and rebuilding — the copy is compiled into PNGs, not stored as strings.
- **One input mechanism.** Only tap; there is no settings screen, no history, no sound.
- **No background execution.** Nothing runs while the app is closed.
- **`npm audit` reports vulnerabilities in transitive dev dependencies** of `aiot-toolkit`. They are build-time only and do not ship inside the `.rpk`.

* * *

## License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)** — see the [LICENSE](LICENSE) file for the full license text. It is a derivative of [hyperpostulate/rw4-poc](https://github.com/hyperpostulate/rw4-poc), so it stays GPLv3.

* * *

## Developer

**Mesut ORMANLI**

- Email: [mesutormanli@gmail.com](mailto:mesutormanli@gmail.com)
- GitHub: [@hyperpostulate](https://github.com/hyperpostulate)

* * *

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request
