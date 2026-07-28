#!/usr/bin/env python3
"""Batch image jobs. Non-destructive — originals are never touched.

    python3 imgtool.py resize    FOLDER --width 1080
    python3 imgtool.py convert   FOLDER --to webp [--quality 82]
    python3 imgtool.py watermark FOLDER --text "© Your Name" [--pos br]
    python3 imgtool.py bgremove  FOLDER
    python3 imgtool.py info      FOLDER

Everything writes into FOLDER/out/. Non-image files are skipped, not fatal.

Needs ffmpeg (resize/convert/watermark) and, for bgremove only:
    pip install rembg
"""
import os
import shutil
import subprocess
import sys

EXTS = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".tif", ".tiff", ".bmp")
FONT = "/System/Library/Fonts/Helvetica.ttc"
if not os.path.exists(FONT):
    FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

POSITIONS = {                    # x:y expressions for ffmpeg drawtext
    "br": ("w-tw-40", "h-th-40"), "bl": ("40", "h-th-40"),
    "tr": ("w-tw-40", "40"), "tl": ("40", "40"),
    "c": ("(w-tw)/2", "(h-th)/2"),
}


def images_in(folder):
    if not os.path.isdir(folder):
        sys.exit(f"not a folder: {folder}")
    files, skipped = [], 0
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if not os.path.isfile(path):
            continue
        if name.lower().endswith(EXTS):
            files.append(path)
        else:
            skipped += 1                 # a stray .DS_Store must not end the job
    return files, skipped


def arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", path],
                       capture_output=True, text=True)
    try:
        w, h = r.stdout.strip().split("x")[:2]
        return int(w), int(h)
    except ValueError:
        return None, None


def run_ffmpeg(args):
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + args,
                       capture_output=True, text=True)
    return r.returncode == 0, r.stderr.strip()


def main():
    argv = sys.argv[1:]
    if not argv:
        sys.exit(__doc__)
    cmd = argv[0]
    folders = [a for a in argv[1:] if os.path.isdir(a)]
    if not folders:
        sys.exit("give me a folder of images")
    folder = folders[0]

    files, skipped = images_in(folder)
    if not files:
        sys.exit(f"no images in {folder}")

    if cmd == "info":
        print(f"{len(files)} image(s) in {folder}" +
              (f" ({skipped} non-image file(s) ignored)" if skipped else ""))
        for f in files[:20]:
            w, h = probe(f)
            print(f"  {os.path.basename(f):<34} {w}x{h}  "
                  f"{os.path.getsize(f)/1000:.0f}KB")
        if len(files) > 20:
            print(f"  ... and {len(files)-20} more")
        return

    out = os.path.join(folder, "out")
    os.makedirs(out, exist_ok=True)

    done, failed = 0, []
    for src in files:
        stem, ext = os.path.splitext(os.path.basename(src))

        if cmd == "resize":
            width = int(arg(argv, "--width", "1080"))
            dst = os.path.join(out, f"{stem}_{width}{ext}")
            ok, err = run_ffmpeg(["-i", src, "-vf", f"scale={width}:-1", dst])

        elif cmd == "convert":
            to = arg(argv, "--to", "webp").lstrip(".")
            q = arg(argv, "--quality", "82")
            dst = os.path.join(out, f"{stem}.{to}")
            ok, err = run_ffmpeg(["-i", src, "-quality", q, dst])

        elif cmd == "watermark":
            text = arg(argv, "--text", "© Your Name").replace(":", r"\:").replace("'", "")
            x, y = POSITIONS.get(arg(argv, "--pos", "br"), POSITIONS["br"])
            dst = os.path.join(out, f"{stem}_wm{ext}")
            vf = (f"drawtext=fontfile={FONT}:text='{text}':fontcolor=white@0.78:"
                  f"fontsize=h/26:x={x}:y={y}:"
                  f"shadowcolor=black@0.5:shadowx=2:shadowy=2")
            ok, err = run_ffmpeg(["-i", src, "-vf", vf, dst])

        elif cmd == "bgremove":
            if not shutil.which("rembg"):
                sys.exit("rembg not installed. Run: "
                         "pip3 install --user --break-system-packages rembg")
            dst = os.path.join(out, f"{stem}_nobg.png")
            r = subprocess.run(["rembg", "i", src, dst], capture_output=True, text=True)
            ok, err = r.returncode == 0, r.stderr.strip()

        else:
            sys.exit(f"unknown command '{cmd}'\n{__doc__}")

        if ok and os.path.exists(dst):
            done += 1
        else:
            failed.append((os.path.basename(src), err.splitlines()[-1] if err else "?"))

    print(f"{cmd}: {done}/{len(files)} written to {out}")
    if skipped:
        print(f"  skipped {skipped} non-image file(s)")
    for name, why in failed:
        print(f"  ! {name}: {why}")
    print(f"  originals in {folder} were not modified")


if __name__ == "__main__":
    main()
