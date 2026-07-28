# The format

One default, used for everything unless the user overrides it: **full-frame video,
centered, over a blurred fill of itself, 1080×1920.**

Not split-screen. Not a face-tracking crop. Split-screen was a 2023 trend that now
reads as low-effort, and aggressive face crops throw away the part of the frame
where the action is — in gaming and IRL clips the funny thing is almost never the
face. The blur fill keeps the entire original frame visible while still filling a
vertical phone screen.

## The command

```bash
ffmpeg -y -hwaccel auto -i IN.mp4 -filter_complex "\
[0:v]split=2[bg][fg];\
[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=42:3,eq=brightness=-0.06[bgb];\
[fg]scale=1080:-2:flags=lanczos[fgs];\
[bgb][fgs]overlay=(W-w)/2:(H-h)/2[v]" \
  -map "[v]" -map 0:a -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 192k OUT.mp4
```

`boxblur=42:3` is the look — heavy enough to be clearly background, not so heavy it
turns to mud. `eq=brightness=-0.06` darkens the fill so the real frame pops forward.
Both are worth keeping.

## Vertical placement

Centered is the default and it's correct for most clips. Two exceptions:

- **Gameplay with a HUD at the bottom** (health bars, kill feed): shift the main
  frame up so the HUD clears the platform's caption area. Change the overlay to
  `overlay=(W-w)/2:(H-h)/2-140`.
- **A face cam in one corner:** if the face cam is the moment, crop tighter instead.
  See "when to crop instead" below.

## Safe zones — the thing that quietly kills clips

TikTok, Reels, and Shorts all paint their own UI over your video:

- **Bottom ~380px** — caption, username, sound. Nothing important goes here.
- **Right ~180px** — like/comment/share rail.
- **Top ~180px** — Shorts title and Reels header.

Your burned captions must sit above the bottom 380px. The spec in
`03-caption-craft.md` already does this (`MarginV=420`). If you move captions, keep
them out of the dead zones or half your viewers read half your words.

## When to crop instead of blur-fill

If — and only if — the entire moment is one person's face and reaction, a center
crop is better because it's bigger:

```bash
ffmpeg -y -i IN.mp4 -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920:flags=lanczos" \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -c:a copy OUT.mp4
```

Change the `x` term from `(iw-ih*9/16)/2` to a fixed pixel value to follow a face
cam that isn't centered. **Export a still and look at it before rendering the whole
clip** — face cam positions differ per creator, per layout, and per stream, so a
value that worked yesterday can be wrong today.

## 4K sources

Downscale to 1080p first (`-vf scale=1920:-2`) before doing anything else. It's
faster, the output is 1080×1920 regardless, and every crop coordinate you eyeball
from a probe frame stays in the numbers you actually looked at.

## Audio

Normalize so clips don't ping-pong in volume across a posting session:

```bash
-af "loudnorm=I=-14:TP=-1.5:LRA=11"
```

`-14 LUFS` is the platform target. Add this to the final render, not to intermediate
files.

## Final encode settings

`libx264`, `crf 20`, `preset fast`, `yuv420p`, AAC 192k, 1080×1920. Keep the source
frame rate — don't convert 60fps to 30fps, the platforms handle 60 and it looks
better. Files land around 8–20MB for a 20-second clip, which is well inside every
upload limit.
