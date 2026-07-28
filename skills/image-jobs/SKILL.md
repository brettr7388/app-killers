---
name: image-jobs
description: Batch image editing — remove backgrounds, resize, watermark, convert formats. Use when the user asks to resize/convert/watermark images, remove a background, or process a folder of photos.
---

> Replaces **Photoshop ($22.99/mo)**. Runs locally — no API key, no credits.

# Image Jobs — batch editing without Photoshop

Not a Photoshop replacement. This covers the four things most people actually open
Photoshop for, each one command.

## Setup

```bash
brew install ffmpeg imagemagick          # macOS
pip3 install --user --break-system-packages rembg   # only for background removal
```

## The four jobs

```bash
python3 scripts/imgtool.py info      photos/
python3 scripts/imgtool.py resize    photos/ --width 1080
python3 scripts/imgtool.py convert   photos/ --to webp
python3 scripts/imgtool.py watermark photos/ --text "© Your Name" --pos br
python3 scripts/imgtool.py bgremove  photos/
```

Everything lands in `photos/out/`. Non-image files are skipped, not fatal. The
originals are never touched.

The raw commands, if you'd rather drive them yourself:

**Batch resize** (keeps aspect ratio):
```bash
for f in src/*.jpg; do
  ffmpeg -y -i "$f" -vf "scale=1080:-1" "out/$(basename "${f%.*}")_1080.jpg"
done
```

**Watermark** (bottom-right, with a shadow so it reads on any background):
```bash
ffmpeg -y -i in.jpg -vf "drawtext=fontfile=/System/Library/Fonts/Helvetica.ttc:\
text='© YOUR NAME':fontcolor=white@0.75:fontsize=46:x=w-tw-40:y=h-th-40:\
shadowcolor=black@0.5:shadowx=2:shadowy=2" out.jpg
```

**Convert format** (webp is typically 60-75% smaller than jpg at the same quality):
```bash
ffmpeg -y -i in.jpg -quality 82 out.webp
```

**Remove background:**
```bash
rembg i in.jpg out.png
```

## Rules

- **Non-destructive, always.** Write to a new folder. Never overwrite the originals,
  even when asked to "just replace them" — write new files and let the user delete.
- **Keep the original filenames**, add a suffix.
- **Skip non-images instead of crashing** on them. A `.DS_Store` in the folder should
  not end the job.
- **Report counts**: how many processed, how many skipped, and why.
- **Show one before/after pair and wait for approval** before running a batch of 200.

## Local panel

```bash
python3 scripts/ui.py        # localhost:7304
```

Pick a folder and an operation. Note that output lands in `<your folder>/out/`, next
to the originals — not in the panel's own output folder.
