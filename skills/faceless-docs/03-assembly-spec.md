# How the build works (and how to change it)

`scripts/make_short.py` does five things. You only need this file when you want to
modify one of them.

## 1. Narration in a single pass

The whole script is voiced as one continuous piece of audio, then split. This matters:
voicing sentence-by-sentence and concatenating produces flat, disconnected delivery
because the TTS engine resets its prosody at every call. One pass keeps the sentences
connected the way a real narrator connects them.

Change the voice and pace in the episode JSON:

```json
"voice": "en-GB-RyanNeural",
"rate": "-8%"
```

`-8%` is documentary pace. `0%` sounds like a phone assistant. `-15%` starts to drag.
List all voices: `edge-tts --list-voices | grep en-`.

## 2. Timings from silence, not from guessing

The script runs `silencedetect` over the narration and treats each speech region as
one sentence. That's how images cut exactly when the sentence changes — no manual
timeline, no drift over a 90-second video.

If the beat count and the detected spans disagree, the script merges the closest
spans or splits the longest until they match. That auto-correction is why a sentence
containing a dramatic pause doesn't break the whole episode.

Tuning, in `speech_spans()`:
- `n=-35dB` — silence threshold. Raise to `-30dB` if the narrator's breaths are being
  counted as speech.
- `d=0.28` — minimum silence length. Raise to `0.4` if sentences are splitting mid-clause.

## 3. Ken Burns motion

Every still gets slow motion — pushing in, pulling out, or tilting down — cycling by
shot so consecutive images never move the same way. A static image on screen for six
seconds reads as a slideshow; the same image drifting reads as film.

Two details in `ken_burns()` that are doing real work:

- **The 2x pre-upscale.** `zoompan` jitters visibly when the source is close to the
  output size. Scaling to 2160×3840 first makes the motion smooth. Remove it and the
  video looks cheap in a way that's hard to diagnose.
- **The 2% inset.** Shaves scan borders, watermarks, and museum frame edges that sit
  at the extreme edge of archival scans.

Slow the motion down by reducing `0.0016` in the zoom expressions. It should be
barely perceptible — if you notice the movement, it's too fast.

## 4. Title card

Wrapped to a max line length, auto-sized so long titles don't run off frame, held
2.8 seconds, then faded. Written through a `textfile` rather than inline `text=` so
apostrophes, colons, and commas in titles don't break the filter graph.

To move it, change `y=(h-text_h)/2-h*0.10` in `title_card()`. To drop it entirely,
skip the call — the video is fine without one, and on TikTok the on-screen title
competes with the platform's own caption.

## 5. Audio

Narration is loudness-normalized to −15 LUFS and mixed over two synthesized sine
tones at 55 Hz and 82.4 Hz — a low drone bed at about a third of the narration's
volume.

This is deliberate: **it is not music, so it can never be copyright-claimed.** Every
faceless channel that uses "royalty free" library music eventually eats a claim from
a rights aggregator that scraped the same library. A synthesized drone is yours by
definition.

If you want real music anyway, mix it in yourself afterwards and accept the risk:

```bash
ffmpeg -i episode.mp4 -i music.mp3 -filter_complex \
  "[1:a]volume=0.18[m];[0:a][m]amix=inputs=2:duration=first[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac out.mp4
```

## Optional: burned captions

Shorts perform better with captions. Transcribe the finished video and burn them
using the caption builder from The Clipper kit, or:

```bash
pip3 install --user --break-system-packages openai-whisper
whisper episode_01.mp4 --model tiny.en --word_timestamps True --output_format srt
ffmpeg -y -i episode_01.mp4 -vf "subtitles=episode_01.srt:force_style=\
'FontName=Helvetica,FontSize=22,PrimaryColour=&H00FFFFFF&,Outline=2,MarginV=180'" \
  -c:a copy episode_01_cap.mp4
```

Keep documentary captions smaller and lower-key than clip captions — big bouncing
yellow words undercut the tone.

## Output spec

1080×1920, 24fps, h264 crf 20, AAC 192k. 24fps is intentional: stills-based video
gains nothing from 30 or 60, and 24 keeps the file small and the motion filmic.
