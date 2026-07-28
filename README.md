# App Killers

**Seven apps I rebuilt as prompts. They run on my own laptop for $0.**

I priced out the software a normal creator gets told to buy:

> CapCut Pro $19.99 · Photoshop $22.99 · Canva Pro $18 · Otter.ai $16.99 ·
> Zapier $49 · Loom $12.50 · Grammarly $12 · Cluely $20
>
> **= $171.47/month. $2,057.64/year.**

Those are each tool's *cheapest* advertised rate — several cost considerably more
month-to-month (Photoshop is $34.49, Zapier is $73.50, Grammarly is $30), so that
total is deliberately conservative.

Here's what I've built so far, and what each one replaces:

| What I built | Replaces | Their price | Runs at |
|---|---|---|---|
| **The Clipper** | CapCut Pro | $19.99/mo | `localhost:7301` |
| **The Transcriber** | Otter.ai | $16.99/mo | `localhost:7302` |
| **The Designer** | Canva Pro | $18/mo | `localhost:7303` |
| **Image Jobs** | Photoshop | $22.99/mo | `localhost:7304` |
| **Faceless Docs** | AI video tools | $30-70/mo | `localhost:7305` |
| **Listing Videos** | listing video services | $150-400/video | `localhost:7306` |
| **The Audiogram** | podcast clip tools | $15-25/mo | `localhost:7307` |

Every prompt below is one I ran myself before publishing it. Paste any of them into
[Claude Code](https://claude.com/claude-code) and it installs what it needs and runs.
Each one ends up as **its own app on its own port** — nothing combined, nothing to
sign up for, no API key.

---

## How to run these

**1. Install Claude Code** (once) — open Terminal and paste:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Run `claude` and log in. A $20/mo Pro plan is enough. On Windows, install
[WSL](https://learn.microsoft.com/windows/wsl/install) first.

**2. Paste a prompt.** That's it. Claude installs ffmpeg, whisper, edge-tts or
whatever else that prompt needs. You don't need to know what any of them are.

**3. Talk to it in plain English when something's off.** "Start it three seconds
later." "Captions smaller." "Find a funnier moment." That's the part a SaaS product
can't do.

---

## The honest part

Photoshop is a masterpiece and I'm not replacing it — I'm replacing the four things I
actually opened it for. Canva's template library took a decade to build. Otter's
transcription UI is genuinely nicer than reading a JSON file.

What you give up: no mobile app, no polish, no onboarding, no one to email at 2am, and
the first run takes five minutes instead of zero. **If your income depends on a tool
working perfectly at 3am the night before a launch, buy the tool.** I mean that.

What you get: no cap, no meter, no upload, and the tool is editable. When a clip comes
out wrong I don't file a feature request and wait two quarters — I say "start it three
seconds later" and it does. A SaaS product is a set of decisions someone else froze
into a UI. A prompt is the same decisions, unfrozen.

Apps aren't dying. **Thin apps are** — the ones whose entire product was a friendly UI
wrapped around something you can now just ask for.

---

## Two bugs I only found by running these

Worth knowing, because they'd hit you on the first try:

1. **`whisper` isn't on your PATH** after a normal install — only `python3 -m whisper`
   works. Every prompt here that uses whisper says so.
2. **An audiogram's waveform can't be screen-blended.** Blending in YUV colour space
   destroys the chroma — it turned a navy logo bright purple. Colour-key it instead.

---

## The prompts

1. **[The Clipper](prompts/01-the-clipper.md)** — long video in, vertical captioned clips out *(replaces CapCut Pro, $19.99/mo)*
2. **[The Transcriber](prompts/02-the-transcriber.md)** — unlimited, offline, no 1,200-minute cap *(replaces Otter.ai, $16.99/mo)*
3. **[The Designer](prompts/03-the-designer.md)** — HTML + headless Chrome = a PNG *(replaces Canva Pro, $18/mo)*
4. **[Image Jobs](prompts/04-image-jobs.md)** — the 4 things you actually opened it for *(replaces Photoshop, $22.99/mo)*
5. **[Faceless Docs](prompts/05-faceless-docs.md)** — a narrated documentary short for $0 *(replaces AI video tools, $30-70/mo)*
6. **[Listing Videos](prompts/06-listing-videos.md)** — photos in, branded property tour out *(replaces listing video services, $150-400/video)*
7. **[The Audiogram](prompts/07-the-audiogram.md)** — for shows with no video at all *(replaces podcast clip tools, $15-25/mo)*

---

### 1. The Clipper

*long video in, vertical captioned clips out* — replaces **CapCut Pro ($19.99/mo)** · runs at `localhost:7301`

```
Turn this video into vertical clips for TikTok/Shorts: [URL or file]

Install what you need first (ffmpeg, yt-dlp, openai-whisper). If the `whisper`
command isn't on PATH after install, use `python3 -m whisper` instead. Then:

1. Transcribe with whisper tiny.en and word timestamps.
2. READ the transcript and pick 5 moments. Judge by what is SAID, not by volume.
   Look for reversals - a confident claim followed by a reaction within 10s.
   Start each clip on the SETUP line, not the payoff. End 1-2s after the reaction
   lands. 12-35 seconds each.
3. Show me the candidates with timestamps and one line each on why. Wait for me.
4. For the ones I pick: trim, then reframe to 1080x1920 by scaling the whole frame
   to fit and putting a heavy blurred copy of itself behind it
   (boxblur=42:3, darkened slightly). Do NOT crop faces. Do NOT split-screen.
5. Re-transcribe the TRIMMED clip and burn word-by-word captions, active word in
   gold, at least 400px above the bottom edge so the TikTok UI can't cover them.
   Fix misspelled names in the transcript BEFORE burning.
6. Export a still from each finished clip and LOOK at it before saying it's done.

Then wrap it in a local web app on localhost:7301 - one Python file, standard
library only, that opens in Chrome with a form and the finished clip playing
in the page.
```


### 2. The Transcriber

*unlimited, offline, no 1,200-minute cap* — replaces **Otter.ai ($16.99/mo)** · runs at `localhost:7302`

```
Transcribe this and give me something I can actually use: [file or URL]

Install openai-whisper if missing. If the `whisper` command isn't on PATH, use
`python3 -m whisper`. Run it with word timestamps. Then give me a markdown file:

- a clean transcript with paragraph breaks at TOPIC changes, not every sentence
- speaker labels if there's more than one voice (split on long pauses, label them
  A/B, and TELL me you guessed rather than pretending you know)
- timestamps every ~30 seconds in [mm:ss] form
- a 5-bullet summary at the top
- any decisions, numbers or action items pulled into their own list

Fix obvious mis-hears of proper nouns. Flag anything you genuinely couldn't make
out as [?] instead of inventing a word. Save it next to the source file.

Then wrap it in a local web app on localhost:7302 - one Python file, standard
library only, where I drop a file and read the transcript in the page.
```


### 3. The Designer

*HTML + headless Chrome = a PNG* — replaces **Canva Pro ($18/mo)** · runs at `localhost:7303`

```
Make me a [thumbnail / carousel / banner] about [TOPIC], [W]x[H] px.

Build it as HTML and CSS, then render it to PNG with headless Chrome:

  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --headless=new --disable-gpu --hide-scrollbars \
    --window-size=W,H --screenshot=out.png \
    --virtual-time-budget=2500 file://page.html

Rules: no external fonts, no CDNs, no web requests - everything inline so it
renders offline. One accent colour. Type big enough to read at thumbnail size:
if the headline isn't legible when the image is scaled to 400px wide, it's too
small. Dark background unless I say otherwise.

Render it, LOOK at the PNG yourself, and fix what's wrong BEFORE showing me.
Then give me a 400px-wide copy so I can check it at feed size.

Then wrap it in a local web app on localhost:7303 where I type the text and see
the render update.
```


### 4. Image Jobs

*the 4 things you actually opened it for* — replaces **Photoshop ($22.99/mo)** · runs at `localhost:7304`

```
I need [remove background / batch resize / watermark / convert format] on the
images in [FOLDER].

Install what's needed: ffmpeg and imagemagick handle resize, watermark and
convert; use rembg for background removal.

Rules:
- NON-DESTRUCTIVE. Write to a new folder. Never overwrite my originals. Ever.
- Keep the original filenames, add a suffix.
- Skip anything that isn't an image instead of crashing on it.
- Tell me exactly how many files you processed and how many you skipped.

Show me ONE before/after pair and wait for my OK before running the whole batch.

Then wrap it in a local web app on localhost:7304 where I pick a folder, pick the
operation, and see the before/after side by side.
```


### 5. Faceless Docs

*a narrated documentary short for $0* — replaces **AI video tools ($30-70/mo)** · runs at `localhost:7305`

```
Build me a 60-second documentary short about [SUBJECT], 1080x1920.

Install ffmpeg and edge-tts if missing.

1. Write 10-12 sentences. Sentence one is the strangest TRUE fact, stated flat -
   no preamble, no rhetorical question. Then complicate it. Then go chronological
   with real numbers. Shorten the sentences as it goes. Verify every date and
   figure; if you can't confirm it, cut it. Show me the script first.
2. Voice the WHOLE script in ONE edge-tts pass (en-US-GuyNeural, rate -8%) - not
   sentence by sentence, the prosody has to stay connected.
3. Split the audio with ffmpeg silencedetect to get real per-sentence timings.
4. One Wikimedia Commons image per sentence. Search for a thing that was
   photographed or painted ("Pompeii plaster cast body"), never a concept ("the
   tragedy of Pompeii"). Set a User-Agent with a real contact email or Commons
   will 403 you.
5. Ken Burns each image for its sentence's exact duration, alternating direction.
   Upscale 2x before zoompan or the motion jitters visibly.
6. Concat, add a wrapped title card, and mix the narration over two quiet
   synthesized sine tones (55Hz + 82.4Hz) instead of music - a synth drone can
   never be copyright-claimed.
7. Pull three stills and CHECK the image matches what the narrator is saying.

Then wrap it in a local web app on localhost:7305.
```


### 6. Listing Videos

*photos in, branded property tour out* — replaces **listing video services ($150-400/video)** · runs at `localhost:7306`

```
Make a listing tour video from the photos in [FOLDER]. Address [X], price [Y],
agent [NAME / PHONE / BROKERAGE]. Vertical 1080x1920.

1. LOOK at the photos and identify what room each one shows first.
2. Order them as a WALK, not as the MLS exported them: exterior, entry, main
   living, kitchen (two shots if you have two good angles), dining, primary bed,
   primary bath, secondary rooms, backyard. Never cut back to an exterior
   mid-tour. Never put a bathroom right after a kitchen. Cut anything past 12
   shots, starting with laundry, garage, hallways, closets. Show me the order.
3. Slow move on each - push in on hero rooms, pull out on reveals. Never the same
   motion three times running. 3.2s per shot, 0.6s crossfade.
4. Open on a card with address + price, end on the agent's details.
5. HARD RULE: describe the property ONLY. Never "perfect for families", "safe
   neighborhood", "great schools" - that's Fair Housing language and it is the
   agent's legal liability. Never state a fact I didn't give you: no square
   footage, no year built, no "recently renovated".
6. Read the phone number back to me digit by digit before exporting.

Then wrap it in a local web app on localhost:7306.
```


### 7. The Audiogram

*for shows with no video at all* — replaces **podcast clip tools ($15-25/mo)** · runs at `localhost:7307`

```
Make a vertical clip from this audio-only episode: [file], [START] to [END].
Use [LOGO.png] as the artwork.

1. Cut the audio segment with ffmpeg.
2. Build a 1080x1920 frame: the logo blown up, heavily blurred and darkened as the
   background, then the crisp logo centered in the upper third.
3. Add a spectrum reacting to the real audio:
   showfreqs=s=1080x300:mode=bar:ascale=sqrt:fscale=log
   IMPORTANT: showfreqs draws on opaque black, so key the black out
   (format=rgba,colorkey=0x000000:0.30:0.04) and overlay it - do NOT screen-blend,
   blending in YUV wrecks the colours. Place it clear of the caption line.
4. Transcribe the clip and burn word-by-word captions underneath.
5. Normalize audio to -14 LUFS.

The captions ARE the video here, so print the transcript path and tell me to
check every name before posting. Whisper WILL mangle proper nouns.

Then wrap it in a local web app on localhost:7307.
```


---

## Notes

- **Prices verified July 2026.** I used each tool's cheapest advertised rate, so the
  totals are conservative. Check them yourself before quoting me.
- **Nothing here uploads your files anywhere.** It all runs locally.
- If you build one of these, I'd like to see it. If one breaks, open an issue and I'll
  fix the prompt.

MIT licensed. Take them, change them, sell what you make with them.

— @Brosenberg0
