---
name: transcriber
description: Transcribe audio or video locally into a usable document with timestamps, speaker labels and a summary. Use when the user says "transcribe this", "get me a transcript", "what was said in this recording", or shares a meeting/interview/podcast file.
---

> Replaces **Otter.ai ($16.99/mo)**. Runs locally — no API key, no credits.

# Transcriber — local, unlimited, offline

Turn any audio or video into a document someone can actually use. Runs entirely on the
user's machine: no upload, no minute cap, no subscription.

## Setup

```bash
pip3 install --user --break-system-packages openai-whisper
```

**If the `whisper` command isn't on PATH after install — and it often isn't — use
`python3 -m whisper` instead.** Check before you run anything:

```bash
command -v whisper || echo "use python3 -m whisper"
```

## Transcribe

```bash
python3 scripts/transcribe.py recording.m4a              # -> recording.md
python3 scripts/transcribe.py interview.mp4 --speakers   # guess speaker turns
python3 scripts/transcribe.py hard-audio.wav --model small.en
```

It writes a markdown file next to the source: a summary (via `claude -p` if the CLI
is installed), the transcript broken into paragraphs at topic changes, and a
timestamp on every paragraph.

Under the hood that's:

```bash
whisper INPUT --model tiny.en --output_format json --output_dir ./out
```

`tiny.en` is ~10× faster than `small.en` and accurate enough for English speech. For
other languages use `--model base` and drop `--language`. For a hard recording (heavy
accents, crosstalk, poor mic) step up to `small.en` — it's slower but noticeably better.

## Then produce the document

Don't hand back raw JSON. Write a markdown file next to the source containing:

- A **5-bullet summary** at the top — what was decided, what matters.
- The **transcript with paragraph breaks at topic changes**, not one line per sentence.
- **Timestamps every ~30 seconds** as `[mm:ss]`.
- **Speaker labels** if there's more than one voice. Split on long pauses, label them
  A/B/C, and *say that you inferred them* rather than implying certainty.
- **Decisions, numbers and action items** pulled into their own list.

## Accuracy rules

- Fix obvious mis-hears of proper nouns, product names and jargon before delivering.
  Whisper mangles names constantly — it turned "Vesuvius" into "the Suvius" in testing.
- Flag anything genuinely inaudible as `[?]`. **Never invent a plausible word.**
- If the audio is bad enough that you're guessing often, say so at the top rather than
  handing over a confident-looking transcript that's wrong.

## Local panel

```bash
python3 scripts/ui.py        # localhost:7302
```

A single-file panel: pick a file, pick a model, hit Run, watch the log, click the
output. Standard library only. Its own app on its own port — nothing shared.
