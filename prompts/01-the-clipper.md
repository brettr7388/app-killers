# The Clipper

*long video in, vertical captioned clips out*

**Replaces:** CapCut Pro ($19.99/mo)
**Runs at:** `localhost:7301`

Paste this into [Claude Code](https://claude.com/claude-code). It installs what it needs.

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

---

[← all seven prompts](../README.md)
