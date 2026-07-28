# Faceless Docs

*a narrated documentary short for $0*

**Replaces:** AI video tools ($30-70/mo)
**Runs at:** `localhost:7305`

Paste this into [Claude Code](https://claude.com/claude-code). It installs what it needs.

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

---

[← all seven prompts](../README.md)
