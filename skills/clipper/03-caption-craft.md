# Captions

Burned-in word-by-word captions are not decoration. Most people watch with sound
off for the first second, and the caption is what makes them turn sound on. Every
clip gets them.

## Generate them

```bash
python3 scripts/build_ass.py CLIP.json OUT.ass opus
```

Three styles ship in the script:

| Style | Look | Use for |
|---|---|---|
| `opus` | Big bold white, active word gold | Default. Works everywhere. |
| `punch` | ALL CAPS, gold, slight pop on the active word | Gaming, rage, hype |
| `clean` | White, no highlight, smaller | Talking head, storytelling, documentary |

Burn them:

```bash
ffmpeg -y -i CLIP.mp4 -vf "subtitles=OUT.ass" \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -c:a copy FINAL.mp4
```

Subtitles must be burned in a **separate pass** after the vertical reformat, and the
transcript must come from the **trimmed** clip — Whisper timestamps are relative to
whatever file you fed it, so transcribing the source and using those numbers on a
clip puts every word in the wrong place.

## Fix the transcript before you burn

Whisper `tiny.en` gets ordinary speech right and proper nouns wrong. Streamer names,
game titles, item names, and slang come out mangled. Open the JSON, correct the
`word` fields, re-run `build_ass.py`. This takes thirty seconds and is the difference
between a clip that looks produced and one that looks automated.

Also worth fixing:
- Numbers written as words when digits read faster ("two hundred" → "200")
- Filler that adds nothing ("uh", "um") — delete the word entry entirely
- Profanity, if the account needs to stay advertiser-safe: swap to `f***` in the
  caption while the audio stays as-is

## Tuning

Edit the constants at the top of `build_ass.py`:

- `MAX_WORDS = 4` — words on screen at once. 3 for fast delivery, 5 for slow.
- `MAX_CHARS = 22` — line width. Lower it if long words run off-screen.
- `PAUSE_BREAK = 0.55` — a gap this long starts a new line. Lower for punchier cuts.
- `margin_v` in the `STYLES` table — 420 keeps captions above every platform's UI.
  Raise it to push captions higher; do not lower it below ~400.

## Font notes

The styles ask for **Arial Black** (macOS) and fall back automatically elsewhere. On
Linux/WSL, install a proper heavy font or captions look thin:

```bash
sudo apt install -y fonts-dejavu fonts-liberation
```

Then change the font name in `STYLES` to `DejaVu Sans` and set bold to `-1`.

## Check one frame before you burn twenty

```bash
ffmpeg -y -ss 2 -i FINAL.mp4 -frames:v 1 check.png
```

Look at it. You are checking for: text running off either edge, captions overlapping
the subject's face, captions sitting low enough that a platform's UI will cover them,
and misspelled names. All four are invisible until you look, and all four are fatal.
