# Design Specification — Magic 8 Ball (Redmi Watch 4, "Midnight Blue Minimal")

Binding UI spec for `com.hyperpostulate.rw4magic8ball`. Every number here is consumed
directly by `scripts/gen_assets.py` and `src/pages/index/index.ux`; if one changes, all
three change together.

## 1. Concept

A single-screen divination card. No skeuomorphic 8-ball sphere and no triangle: the app
is a "digital oracle" — one deep-navy rounded card floating on true black, a thin steel
edge, near-white text. The card face is the only thing that changes between states, so
the screen reads as a single object that answers you.

The visual language is calm and restrained: one accent hue (steel blue), one card, three
text tints (near-white / silver-blue / pale rose) that only the answer text ever uses.

## 2. Palette

| Role | Hex | RGBA | Where |
| :--- | :--- | :--- | :--- |
| Backdrop | `#000000` | 0,0,0,255 | Page background (true black, AMOLED) |
| Card fill | `#0A192F` | 10,25,47,255 | Card interior, logo tile |
| Card edge | `#4A6B8A` | 74,107,138,255 | 2 px card stroke, ring, spinner arc, logo |
| Title | `#8FA9C0` | 143,169,192,255 | `MAGIC 8 BALL` (recessive, hierarchy) |
| Text primary | `#EFF7FF` | 239,247,255,255 | Affirmative answers |
| Text muted | `#CBD5E0` | 203,213,224,255 | Non-committal answers, hints |
| Text warn | `#E5B7B7` | 229,183,183,255 | Negative answers |
| Emblem | `#4A6B8A` | 74,107,138,255 | Idle ring + "8", spinner arc |

Contrast against the card fill (`#0A192F`): primary ≈ 15.9:1, muted ≈ 11.6:1, warn ≈ 9.4:1
— all far above 7:1. Title sits on black at ≈ 8.1:1.

Category tinting is the only semantic colour use: affirmative → primary, non-committal →
muted, negative → warn. Hints are always muted; the title is always the title tint.

## 3. Geometry (390 × 450 canvas)

| Element | X | Y | W | H | Notes |
| :--- | ---: | ---: | ---: | ---: | :--- |
| Canvas | 0 | 0 | 390 | 450 | `designWidth: 390` |
| Title | 35 | 34 | 320 | 34 | Centred text in a transparent PNG |
| Card | 40 | 86 | 310 | 280 | Single PNG incl. 2 px stroke |
| Answer box | 74 | 138 | 242 | 184 | Inside the card, centred |
| Hint | 35 | 374 | 320 | 24 | Centred text, transparent PNG |

The display crops its corners, and the bottom-right quadrant is the least reliable.
Content therefore stops at **y = 398** (hint bottom); nothing is placed below that, and
nothing extends past x = 366 except the invisible box padding of the centred text assets.

Card centre is (195, 226). Answer box centre is (195, 230) — deliberately 4 px above the
card centre so the 3-line block optically centres against the rounded corners.

## 4. Assets

All PNGs are RGBA, generated at exactly their displayed size (4× supersample, Lanczos
downsample), and must be non-blank. They live under `src/common/`.

| Filename | Size | Content | Used by |
| :--- | ---: | :--- | :--- |
| `logo.png` | 96×96 | Navy rounded tile, steel ring, bold "8" | Launcher icon (unversioned) |
| `txt/title_<stamp>.png` | 320×34 | `MAGIC 8 BALL`, bold 22 px, ls 3 px, title tint | All states |
| `txt/hint_ask_<stamp>.png` | 320×24 | `Tap to seek answer…`, 18 px, muted | Idle / rolling |
| `txt/hint_again_<stamp>.png` | 320×24 | `Tap to ask again`, 18 px, muted | Answer |
| `face/idle_<stamp>.png` | 310×280 | Card + ring (Ø 104) + bold "8" (56 px) | Idle |
| `face/roll0..5_<stamp>.png` | 310×280 | Card + ring + 90° arc stepping 60°/frame | Rolling (6 frames) |
| `face/ans00..19_<stamp>.png` | 310×280 | Card + wrapped answer text | Answer (20) |

31 PNGs total. **3 `<image>` nodes are on screen at any moment** (title, face, hint); the
face swaps `src` and the hint swaps `src`. No other nodes are needed.

`<stamp>` is an 8-hex content stamp computed from the copy + geometry constants. The watch
caches image resources by path across installs, so changing copy or geometry changes the
stamp and therefore every filename; `gen_assets.py` rewrites the generated constants block
inside `index.ux` to match.

`logo.png` is deliberately **96×96**: the launcher derives the app-name offset from the
icon's pixel size, and 192×192 pushes the name into the middle of the row (verified on
device upstream). It is unversioned because the launcher re-reads it on install.

## 5. Typography (DejaVu Sans)

| Level | Weight | Size | Line height | Letter spacing | Colour | Wrap |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| Title | Bold | 22 px | — | 3 px | title tint | none |
| Emblem "8" | Bold | 56 px | — | 0 px | card edge | none |
| Answer | Book | 30 px | 38 px | 0 px | per category | greedy, ≤ 3 lines, box 242 px |
| Hint | Book | 18 px | — | 0.5 px | muted | none |

The answer size is chosen by the generator as the largest of `[30, 28, 26]` for which
**every** answer string wraps into ≤ 3 lines inside 242 px; it then verifies the rendered
block height ≤ 184 px and prints the chosen size. Answers are vertically centred as a
block; a 1-line answer sits on the card's centre line.

Wrapping is greedy on spaces (never splits a word). No hyphenation, no ellipsis: the copy
list is fixed and asserted to fit at build time.

## 6. Motion & interaction

The whole screen is the hit area. Pointer events: `@click` **and** `@touchstart` are both
bound to the same handler with a 350 ms re-entry guard. Tap input is **verified working on
device** (2026-11-20); the exact event name the runtime emits was not isolated, so both
stay bound and the guard swallows any duplicate delivery.

```
IDLE ──tap──> ROLLING (600 ms) ──> ANSWER ──tap──> ROLLING ──> ANSWER ...
```

1. Tap accepted → `vibrator.vibrate({mode:'short'})`. The hint stays `hint_ask` (it only
   becomes `hint_again` once an answer is on screen, so it never invites a tap mid-roll).
2. Rolling: 6 spinner frames, one every **100 ms** (last frame at 500 ms, settled at 600 ms),
   `setInterval(…, 100)` cleared by a 600 ms timeout / frame counter. Face src cycles
   `roll0 → roll5` and restarts at `roll0`.
3. Settle: pick answer `i = floor(random() * 20)`, face src = `ans<i>`, `vibrator.vibrate({mode:'long'})`.
4. Next tap repeats from 1. No timer runs while idle; everything stops in `onHide`/`onDestroy`.

Vibration is **verified working** on device for both pulses (`mode:'short'` on tap,
`mode:'long'` on settle). It stays inside `try/catch` so a firmware regression can never
break the visual flow.

## 7. Copy

| Slot | String |
| :--- | :--- |
| Title | `MAGIC 8 BALL` |
| Hint, idle/rolling | `Tap to seek answer…` |
| Hint, answer | `Tap to ask again` |

Answers (index → category → string):

| # | Cat | String |
| ---: | :--- | :--- |
| 00 | affirmative | `It is certain.` |
| 01 | affirmative | `It is decidedly so.` |
| 02 | affirmative | `Without a doubt.` |
| 03 | affirmative | `Yes definitely.` |
| 04 | affirmative | `You may rely on it.` |
| 05 | affirmative | `As I see it, yes.` |
| 06 | affirmative | `Most likely.` |
| 07 | affirmative | `Outlook good.` |
| 08 | affirmative | `Yes.` |
| 09 | affirmative | `Signs point to yes.` |
| 10 | non-committal | `Reply hazy, try again.` |
| 11 | non-committal | `Ask again later.` |
| 12 | non-committal | `Better not tell you now.` |
| 13 | non-committal | `Cannot predict now.` |
| 14 | non-committal | `Concentrate and ask again.` |
| 15 | negative | `Don't count on it.` |
| 16 | negative | `My reply is no.` |
| 17 | negative | `My sources say no.` |
| 18 | negative | `Outlook not so good.` |
| 19 | negative | `Very doubtful.` |

Uniform 1/20 probability, no weighting: the classic ball has no memory and no bias.

## 8. Generator rules

- `SS = 4`: everything is drawn at 4× and downsampled with `Image.LANCZOS`; never draw at
  1× and never hand-edit output PNGs.
- Card: rounded rect, radius 44 px, fill `#0A192F`, stroke `#4A6B8A` width 2 px inset so the
  stroke is fully inside the canvas.
- Ring: circle outline Ø 104 px, stroke 4 px, at the card centre. Spinner: same ring plus a
  90° arc (width 4 px, round caps) starting at frame angle `frame * 60° - 90°`.
- Every asset is re-opened after writing and asserted: exact size, non-blank alpha, and
  (for text assets) more than one distinct colour value.
- The generated block in `index.ux` between `// __ASSETS_BEGIN__` and `// __ASSETS_END__` is
  rewritten in place; the script asserts it found exactly one block.
- The script is deterministic: same copy + geometry ⇒ byte-identical PNGs. Run it any time;
  it wipes `src/common/txt/` and `src/common/face/` first.

## 9. Wireframes

```
IDLE                              ROLLING                          ANSWER
┌───────────────────────────────┐ ┌───────────────────────────────┐ ┌───────────────────────────────┐
│          MAGIC 8 BALL         │ │          MAGIC 8 BALL         │ │          MAGIC 8 BALL         │
│                               │ │                               │ │                               │
│    ╭───────────────────╮      │ │    ╭───────────────────╮      │ │    ╭───────────────────╮      │
│    │                   │      │ │    │        ╭──╮       │      │ │    │                   │      │
│    │      ( 8 )        │      │ │    │      ╭─╯  │       │      │ │    │    It is certain. │      │
│    │                   │      │ │    │      ╰────╯       │      │ │    │                   │      │
│    ╰───────────────────╯      │ │    ╰───────────────────╯      │ │    ╰───────────────────╯      │
│                               │ │                               │ │                               │
│      Tap to seek answer…      │ │      Tap to seek answer…      │ │        Tap to ask again       │
└───────────────────────────────┘ └───────────────────────────────┘ └───────────────────────────────┘
```

Face card = 310×280 at (40,86); ring/arc and answer text are baked into that same PNG.
