---
name: faceless-docs
description: Build narrated documentary shorts from public-domain archival images for a faceless YouTube/TikTok channel. Use when the user says "make a history short", "faceless channel video", "documentary short", or asks for a narrated video built from archive images.
---

> Replaces **AI video tools ($30-70/mo)**. Runs locally — no API key, no credits, nothing uploaded.

# FACELESS DOCS — build brief for Claude

You build narrated documentary shorts for a faceless YouTube/TikTok channel. No
camera, no voice, no stock footage subscription, no AI credits. Real archival
images, a synthetic narrator, and ffmpeg.

One episode takes about 15 minutes of wall-clock time and costs nothing.

Work the phases in order. Read `01-script-formula.md` before Phase 2,
`02-image-sourcing.md` before Phase 3, and `04-channel-strategy.md` at Phase 6.

---

## PHASE 0 — Environment (silently, once)

```bash
command -v ffmpeg python3
python3 -c "import edge_tts" 2>/dev/null || pip3 install --user --break-system-packages edge-tts
```

macOS, if ffmpeg is missing: `brew install ffmpeg` (install Homebrew first if needed).
Linux/WSL: `sudo apt install -y ffmpeg python3-pip`.

**ASK once, then never again:** "What email should I use to identify us to Wikimedia?
They block anonymous image requests. It's only sent in a request header — it never
appears in the video." Store it in the episode JSON as `contact`.

## PHASE 1 — Pick the subject

**ASK** if the user hasn't said: "What's the episode about?"

If they want you to choose, propose 5 subjects from their channel's niche and say
why each one works. Good subjects share three traits:

- **A visual record exists.** Wikimedia Commons must actually have images. Ancient
  Rome, shipwrecks, WWII, space programs, natural disasters, famous buildings: yes.
  Anything from the last 30 years involving living people: usually no (copyright).
- **A single clean arc.** One thing happened, it had a cause, it had an aftermath.
  "The history of banking" is not an episode. "The bank that failed in 12 hours" is.
- **An outcome worth waiting for.** If the ending is common knowledge, find the angle
  that isn't.

## PHASE 2 — Write the script

Read `01-script-formula.md` and follow it. Write 8–14 sentences for a 60–90 second
short. Each sentence is one beat and gets one image, so write sentences that are
*visually specific* — "the ash fell for eighteen hours" can be pictured; "the
situation deteriorated rapidly" cannot.

Show the script to the user as plain prose before building anything. **ASK** for
approval or edits. This is the only creative gate and it's cheap to iterate here and
expensive to iterate after rendering.

## PHASE 3 — Write the episode JSON

Read `02-image-sourcing.md` first, then write `episode.json`:

```json
{
  "title": "The City That Vanished In A Day",
  "contact": "user@theiremail.com",
  "voice": "en-US-GuyNeural",
  "rate": "-8%",
  "beats": [
    {"text": "In 79 AD, a Roman city went to sleep and never woke up.",
     "query": "Pompeii ruins"},
    {"text": "Vesuvius had been quiet for generations.",
     "query": "Mount Vesuvius eruption painting"}
  ]
}
```

The `query` is a Wikimedia Commons search. Write queries that name a **thing that was
photographed or painted**, not a concept. `"Pompeii plaster cast body"` returns
something; `"the tragedy of Pompeii"` returns noise.

Voices worth knowing: `en-US-GuyNeural` (default, documentary baritone),
`en-US-AriaNeural` (female, warmer), `en-GB-RyanNeural` (British, works well for
history), `en-US-ChristopherNeural` (deeper, slower). List more with
`edge-tts --list-voices | grep en-`.

## PHASE 4 — Build

```bash
python3 scripts/make_short.py episode.json episode_01.mp4
```

The script narrates in one pass, splits the audio on silence to get real per-sentence
timings, downloads and verifies each image, builds a Ken Burns shot per beat, adds
the wrapped title card, and mixes narration over a synthesized drone bed.

Watch the output for `NO IMAGE for '...'` lines. Every one of those means a beat is
reusing the previous picture — rewrite that query and rebuild rather than shipping it.

## PHASE 5 — Look at it

Non-negotiable. Pull three stills and actually read them:

```bash
for t in 2 20 45; do ffmpeg -y -ss $t -i episode_01.mp4 -frames:v 1 check_$t.png; done
```

You are checking: does the image match what the narrator is saying at that moment,
is the title readable, is anything cropped into nonsense, did a wrong-subject image
sneak in (Commons search is keyword-matched and will happily hand you the wrong
Vesuvius). Then `open episode_01.mp4` so the user can watch it.

Fix by editing `episode.json` and rebuilding — it's fast and it's idempotent.

## PHASE 6 — Package it

Read `04-channel-strategy.md`. Deliver the video plus:

- **A YouTube title** — Shorts titles are ranked text, not captions. Write it as one.
- **A description** with the image credits (see `02-image-sourcing.md`)
- **Three tags** and a one-line TikTok caption
- **A thumbnail** if they're posting long-form: `ffmpeg -ss 8 -i episode_01.mp4 -frames:v 1 thumb.jpg`

Then offer the next episode. The whole point of this kit is that episode two costs
15 minutes, so the channel actually gets fed.

---

## Standing rules

- **Never invent facts.** You are writing history that a comment section will
  fact-check within an hour. If you aren't certain of a date, a number, or a name,
  either verify it or write around it. One wrong claim in the first ten seconds
  costs the channel its credibility permanently.
- **Never claim an image shows something it doesn't.** If Commons has no photo of
  the actual event, use a contemporaneous image of the place or a period painting —
  and don't have the narration say "here we see."
- **Sentences are beats.** One idea per sentence. Two ideas in one sentence means
  one image has to carry both and it won't.
