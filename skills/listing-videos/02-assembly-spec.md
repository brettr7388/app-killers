# How the build works (and how to change it)

`scripts/make_tour.py` builds: opening card → moving shots → end card, crossfaded
throughout, with optional music and narration.

## Motion

Each photo becomes a moving clip via `zoompan`. Two details are load-bearing:

- **The 2x pre-upscale.** `zoompan` jitters visibly when the source is near the output
  size. Scaling to 2×frame first makes the drift smooth. This is the difference
  between "camera move" and "cheap slideshow" and it is not optional.
- **Slow rates.** `0.0011` per frame. Interiors punish fast motion — it makes rooms
  feel small and viewers feel rushed. If you can consciously notice the movement,
  it's too fast.

## Crossfades

Shots are chained with `xfade=transition=fade:duration=0.6`. The offsets accumulate:
each transition starts `0.6s` before the running total, so the final runtime is
`sum(durations) - 0.6 × (number of transitions)`.

`fade` is the right transition for property video. ffmpeg offers `wipeleft`,
`circleopen`, `dissolve` and thirty others — they all read as 2009 PowerPoint. Change
`XFADE` at the top of the script if you want a faster or slower dissolve; 0.4–0.8 is
the usable range.

## Cards

The opening card carries the address, city, price, and specs. The end card carries
the agent's name, phone, and brokerage on the same dark background.

Both are drawn through a `textfile` rather than inline text, so apostrophes, colons,
and commas in addresses and brokerage names can't break the filter graph. Font sizes
are fractions of frame height, so vertical and horizontal cuts stay visually
consistent.

To brand it for a specific agent, change `color=c=0x111418` in `card()` to the
brokerage's color. Keep it dark — light cards blow out against interior photos in the
crossfade.

## Vertical vs horizontal

`"orientation": "vertical"` gives 1080×1920; `"horizontal"` gives 1920×1080. Same
photos, different crops, and photos that work in one often fail in the other — check
both if you build both.

In vertical, room labels are pushed up to clear the bottom ~380px where TikTok and
Reels paint their caption and button UI. In horizontal there's no dead zone, so
labels sit lower. That's automatic, based on frame shape.

## Audio

Silent by default, which is the correct default: Instagram and TikTok often supply
their own audio, and a silent file lets the agent add a trending sound.

```json
"music": "music.mp3"                            // bed at 42%, fades out over the last 2.5s
"narration": "Welcome to 1420 Maple Ridge Lane."  // TTS voiceover; ducks music to 16%
"voice": "en-US-AriaNeural"
```

**Music licensing is the buyer's problem to get right, and it's the most common way
these videos get muted.** A video that gets copyright-claimed on the agent's own
Instagram is worse than a silent one. Use a licensed library the user actually pays
for, or ship it silent and let the platform's sound do the work. Do not tell a client
a track is "royalty free" unless you can point at the license.

## Output spec

30fps, h264 crf 19, AAC 192k. crf 19 (rather than the 20 used for clips) because
listing photos are high-detail stills and compression artifacts in a kitchen backsplash
are visible and look cheap.

## Rebuilding

The build is idempotent — edit `listing.json` and re-run. Nothing is cached, so a
rebuild after reordering shots takes the same ~1–2 minutes as the first one. Iterate
on the JSON, not on the video.
