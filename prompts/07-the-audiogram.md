# The Audiogram

*for shows with no video at all*

**Replaces:** podcast clip tools ($15-25/mo)
**Runs at:** `localhost:7307`

Paste this into [Claude Code](https://claude.com/claude-code). It installs what it needs.

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

[← all seven prompts](../README.md)
