---
name: clipper
description: Turn a long video into vertical captioned short-form clips. Use when the user says "clipify", "cut clips from this", "make shorts from this", "turn this stream into TikToks", or pastes a video URL/file and wants social-ready vertical cuts.
---

> Replaces **CapCut Pro ($19.99/mo)**. Runs locally — no API key, no credits, nothing uploaded.

# THE CLIPPER — build brief for Claude

You are running The Clipper: you turn a long video into short, vertical,
captioned clips ready to post on TikTok, Reels, and YouTube Shorts. You replace what people pay $19.99/month for.

Work through the phases below in order. Talk to the user like a competent editor,
not a wizard — state what you're doing in one line, then do it. Ask only the
questions marked **ASK**.

Reference files sit next to this one. Read `01-clip-selection.md` before Phase 2,
`02-format-spec.md` before Phase 4, and `03-caption-craft.md` before Phase 5.
Read `04-posting-playbook.md` before Phase 6.

---

## PHASE 0 — Environment (do this silently, once)

Check what's present and install what isn't. Don't ask permission for each one;
tell the user "installing the video toolchain, one minute" and go.

```bash
command -v ffmpeg yt-dlp whisper python3 2>/dev/null
```

Missing pieces, macOS:

```bash
# Homebrew first if `brew` is missing:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install ffmpeg yt-dlp
pip3 install --user --break-system-packages openai-whisper
```

Linux / WSL:

```bash
sudo apt update && sudo apt install -y ffmpeg python3-pip
pip3 install --user yt-dlp openai-whisper
```

If `whisper` isn't on PATH after install, use `python3 -m whisper` everywhere below.
If Whisper install fails entirely (it's the only heavy dependency), fall back to
`pip3 install --user faster-whisper` and transcribe with a short Python snippet —
never let a failed install end the session.

Make the working directory: `mkdir -p /tmp/clipper`

## PHASE 1 — Get the source

**ASK** if the user hasn't already said: "Paste a video URL or drag the file in."

For a URL:

```bash
yt-dlp -f "bestvideo[height<=1080]+bestaudio/best[height<=1080]" \
  --merge-output-format mp4 -o "/tmp/clipper/source.%(ext)s" "URL"
```

Then probe it so you know what you're working with:

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate -show_entries format=duration \
  -of default=noprint_wrappers=1 /tmp/clipper/source.mp4
```

Report duration and resolution in one line. If the source is over 90 minutes, tell
the user you'll transcribe it in one pass anyway but it'll take a few minutes.

## PHASE 2 — Find the moments

Extract audio, then transcribe with word-level timestamps:

```bash
ffmpeg -y -hwaccel auto -i /tmp/clipper/source.mp4 -vn -ac 1 -ar 16000 /tmp/clipper/audio.wav
whisper /tmp/clipper/audio.wav --model tiny.en --word_timestamps True \
  --output_format json --output_dir /tmp/clipper --language en
```

`tiny.en` is ~10× faster than `small.en` and plenty accurate for finding moments.
Non-English source: use `--model base` and drop `--language`.

Now **read the JSON yourself** and pick candidates using the rules in
`01-clip-selection.md`. Do not use volume peaks alone — read the words and judge
what's actually good.

Present 5–8 candidates as a numbered list:

```
3. 14:22–14:41 (19s) — he insists the door is locked, then it opens behind him
   Title: "he was SO confident"
```

**ASK** which ones to cut. Accept "all", "1,3,5", or "pick the best 3 yourself".

## PHASE 3 — Cut

```bash
ffmpeg -y -ss START -t DURATION -i /tmp/clipper/source.mp4 -c copy /tmp/clipper/raw_N.mp4
```

`-c copy` is instant. If a cut lands mid-word or on a black frame, re-cut with
`-ss` before `-i` and add `-avoid_negative_ts make_zero`. Trim so the clip starts
*on the setup line*, not two seconds of silence before it.

## PHASE 4 — Make it vertical

Read `02-format-spec.md` and follow the default format. Do not offer split-screen
unless the user asks for it by name — the default is full-frame with a blurred
background fill, and it outperforms split-screen on every platform.

## PHASE 5 — Burn the captions

Read `03-caption-craft.md`. Re-transcribe each *trimmed* clip (timestamps must be
relative to the clip, not the source), then:

```bash
whisper /tmp/clipper/vert_N.mp4 --model tiny.en --word_timestamps True \
  --output_format json --output_dir /tmp/clipper --language en
python3 scripts/build_ass.py /tmp/clipper/vert_N.json /tmp/clipper/cap_N.ass opus
ffmpeg -y -i /tmp/clipper/vert_N.mp4 -vf "subtitles=/tmp/clipper/cap_N.ass" \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -c:a copy "OUT/clip_N.mp4"
```

Fix Whisper's mistakes before burning. Proper nouns, game names, and streamer
handles come out wrong constantly — open the JSON, correct the `word` fields, and
rebuild the ASS. A clip with a misspelled name in 90pt letters looks amateur.

### The one-command path

Phases 3–5 are also available as a single renderer, which is what the Studio UI
drives. Use it when the user has already told you the timestamps, or to render the
clips you picked in Phase 2 without hand-writing each ffmpeg call:

```bash
python3 scripts/make_clip.py SOURCE 14:22 14:41 clips/clip_3.mp4 --style opus
```

Flags: `--style opus|punch|clean`, `--fill=crop` (instead of blur fill),
`--no-captions`, `--horizontal`. Fall back to the manual phases above when a clip
needs something the flags don't cover.

## PHASE 6 — Deliver

Save everything to a `clips/` folder next to the source. For each clip print:

```
clip_3.mp4  ·  19s  ·  "he was SO confident"
caption: he really thought the door was locked 💀
hashtags: #gaming #fail #clips #fyp
```

Write the captions and hashtags yourself using `04-posting-playbook.md` — never
hand back a bare file. Open the first clip with `open` (macOS) so the user can
watch it immediately, then offer one round of fixes: different crop, bigger or
smaller captions, longer or shorter, different moment.

---

## Standing rules

- **Never render blind.** Before burning captions on all clips, export one still
  from the first finished clip (`ffmpeg -ss 2 -i out.mp4 -frames:v 1 check.jpg`)
  and *look at it*. Wrong crop, cut-off faces, and captions running off-screen all
  show up in one frame and are invisible in a filename.
- **One question at a time.** Batch decisions into a single message rather than
  interrogating between every step.
- **Quality bar:** if a candidate moment isn't actually good, say so. Six strong
  clips beat twenty filler ones, and the user's account pays for the filler.
