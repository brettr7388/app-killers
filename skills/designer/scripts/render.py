#!/usr/bin/env python3
"""Render an HTML file to a PNG with headless Chrome, and check it at feed size.

    python3 render.py page.html out.png --size 1600x900
    python3 render.py page.html out.png --size 1280x720 --no-thumb

Also writes out_thumb.png at 400px wide — always look at that one. Text that reads
fine at full size and turns to mush in a feed is the single most common failure.

No design tool, no subscription, no export limit.
"""
import os
import shutil
import subprocess
import sys

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome", "chromium", "chromium-browser",
]

PRESETS = {
    "youtube": (1280, 720), "x": (1600, 900), "square": (1080, 1080),
    "story": (1080, 1920), "reel": (1080, 1920), "pin": (1000, 1500),
    "og": (1200, 630),
}


def find_chrome():
    for c in CHROME_CANDIDATES:
        if os.path.exists(c) or shutil.which(c):
            return c if os.path.exists(c) else shutil.which(c)
    sys.exit("Chrome or Chromium not found — install Google Chrome.")


def parse_size(spec):
    if spec in PRESETS:
        return PRESETS[spec]
    try:
        w, h = spec.lower().split("x")
        return int(w), int(h)
    except ValueError:
        sys.exit(f"bad --size '{spec}'. Use WxH (1600x900) or a preset: "
                 f"{', '.join(PRESETS)}")


def main():
    argv = sys.argv[1:]
    files = [a for a in argv if not a.startswith("--")]
    if len(files) < 2:
        sys.exit(__doc__)
    src, dst = os.path.abspath(files[0]), os.path.abspath(files[1])
    if not os.path.exists(src):
        sys.exit(f"no such file: {src}")

    size = "1600x900"
    if "--size" in argv:
        size = argv[argv.index("--size") + 1]
    w, h = parse_size(size)

    chrome = find_chrome()
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={w},{h}", f"--screenshot={dst}",
                    "--virtual-time-budget=2500", f"file://{src}"],
                   capture_output=True)

    if not os.path.exists(dst):
        sys.exit("Chrome produced no image — check the HTML opens in a browser first.")

    print(f"rendered {w}x{h} -> {dst} ({os.path.getsize(dst)/1000:.0f}KB)")

    if "--no-thumb" not in argv and shutil.which("ffmpeg"):
        thumb = dst.replace(".png", "_thumb.png")
        subprocess.run(["ffmpeg", "-y", "-i", dst, "-vf", "scale=400:-1", thumb],
                       capture_output=True)
        if os.path.exists(thumb):
            print(f"feed-size check   -> {thumb}")
            print("  LOOK AT THE THUMB. If the headline isn't readable there, the type "
                  "is too small — nothing else matters.")


if __name__ == "__main__":
    main()
