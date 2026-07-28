---
name: recorder
description: Record the screen and produce a shareable page with a synced transcript. Use when the user says "record my screen", "screen recording", "make a loom", "walkthrough video", or wants to demo something on screen for someone else.
---

> Replaces **Loom ($12.50/seat/mo)**. Runs locally — no API key, no credits.

# Recorder — screen capture with a transcript, all local

Record the screen, transcribe it on the machine, and produce one HTML page with the
video, the transcript beside it, and clickable timestamps that seek the video.

Nothing uploads. For anything with a customer's data, a dashboard or an inbox on
screen, that is the entire argument by itself.

```bash
python3 scripts/record.py 30 --out walkthrough
```

Produces `walkthrough.mp4` and `walkthrough.html`. Keep them together — the page plays
the video from disk beside it.

## How it works

1. **Capture** — `screencapture -v -V <seconds> -x` records the main display.
   macOS asks for **Screen Recording** permission the first time; it's granted to the
   *terminal app* you run it from, not to the script.
2. **Normalize** — re-encode to h264 with `+faststart` so it plays while loading.
3. **Transcribe** — whisper locally. If `whisper` isn't on PATH after install, use
   `python3 -m whisper`; the script already falls back.
4. **Page** — a self-contained HTML file. Clicking a timestamp seeks the video, and
   the current line highlights and scrolls itself into view as it plays.

A silent recording still works — the transcript panel just says so instead of failing.

## Rebuilding without re-recording

```bash
RECORD_FROM=existing.mov python3 scripts/record.py --out demo
```

Useful when you want to change the page and not sit through another take.

## Getting a good take

- **Say what you're doing as you do it.** The transcript is what makes the page
  useful, and a silent recording is just a video file.
- **Close what you don't want in the frame.** This records the whole display,
  including notifications. Turn on Do Not Disturb first.
- **Under two minutes.** Past that, people scrub instead of watching — which is
  exactly what the clickable transcript is for.

## Audio — read this before you promise anyone a transcript

`screencapture -g` records the **default audio input**, i.e. a microphone. It does
**not** record the sound coming out of the speakers. Two consequences:

- **No mic, no transcript.** A Mac mini or a Mac with no input device returns
  *"No capture audio device available"*. The script detects this and tells you it's
  recording silent instead of handing back an empty transcript panel.
- **Screen audio isn't captured.** If you're recording a video playing on screen, its
  sound will not be in the file. Capturing system audio needs a loopback device
  (BlackHole, Loopback) set as the input.

To narrate over an existing capture, record the audio separately and mux it:

```bash
ffmpeg -i screen.mov -i mic.m4a -map 0:v -map 1:a -c:v copy -c:a aac out.mp4
```

Just don't mux unrelated audio onto a video and call it a transcript — the page will
happily show you a perfectly formatted transcript of something that isn't in the
recording.
