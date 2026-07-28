#!/usr/bin/env python3
"""Cut one finished vertical clip: trim -> 9:16 -> captions -> normalized audio.

    python3 make_clip.py SOURCE START END OUT.mp4 [options]

START/END accept seconds (74.5) or timestamps (1:14.5 / 00:01:14.5).

Options:
    --style opus|punch|clean   caption style (default opus)
    --fill blur|crop           blur-fill the whole frame (default) or center-crop
    --no-captions              skip transcription and burning
    --horizontal               keep 16:9 instead of going vertical

Claude picks the moments; this renders them. Also driven by the Studio UI.
"""
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920


def sh(cmd, quiet=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        tail = "\n".join(r.stderr.strip().splitlines()[-5:])
        raise SystemExit(f"failed: {cmd[0]} {cmd[1] if len(cmd) > 1 else ''}\n{tail}")
    return r


def parse_time(value):
    """'1:14.5' or '00:01:14.5' or '74.5' -> seconds."""
    value = str(value).strip()
    if re.fullmatch(r"[\d.]+", value):
        return float(value)
    parts = [float(p) for p in value.split(":")]
    secs = 0.0
    for p in parts:
        secs = secs * 60 + p
    return secs


def have(tool):
    return shutil.which(tool) is not None


def whisper_cmd():
    if have("whisper"):
        return ["whisper"]
    return [sys.executable, "-m", "whisper"]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if len(args) < 4:
        sys.exit(__doc__)

    source, start_raw, end_raw, out = args[0], args[1], args[2], os.path.abspath(args[3])
    start, end = parse_time(start_raw), parse_time(end_raw)
    if end <= start:
        sys.exit(f"end ({end}) must be after start ({start})")
    dur = end - start

    style = "opus"
    for f in flags:
        if f.startswith("--style"):
            style = f.split("=", 1)[1] if "=" in f else style
    if "--style" in sys.argv:                       # also accept "--style punch"
        i = sys.argv.index("--style")
        if i + 1 < len(sys.argv):
            style = sys.argv[i + 1]

    vertical = "--horizontal" not in flags
    fill = "crop" if "--fill=crop" in flags or "crop" in flags else "blur"
    captions = "--no-captions" not in flags

    work = os.path.join(os.path.dirname(out) or ".", "_work")
    os.makedirs(work, exist_ok=True)
    stem = os.path.splitext(os.path.basename(out))[0]

    # 1 — trim. Re-encoded rather than -c copy so the cut is frame-accurate;
    # a stream-copy cut can start on a black frame or clip the first word.
    print(f"[1/4] trimming {dur:.1f}s from {start:.1f}s", flush=True)
    trimmed = os.path.join(work, f"{stem}_trim.mp4")
    sh(["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i", source, "-t", f"{dur:.3f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", "-avoid_negative_ts", "make_zero", trimmed])

    # 2 — reframe
    staged = trimmed
    if vertical:
        print(f"[2/4] reframing to 9:16 ({fill})", flush=True)
        staged = os.path.join(work, f"{stem}_vert.mp4")
        if fill == "blur":
            fc = (f"[0:v]split=2[bg][fg];"
                  f"[bg]scale={W}:{H}:force_original_aspect_ratio=increase,"
                  f"crop={W}:{H},boxblur=42:3,eq=brightness=-0.06[bgb];"
                  f"[fg]scale={W}:-2:flags=lanczos[fgs];"
                  f"[bgb][fgs]overlay=(W-w)/2:(H-h)/2[v]")
        else:
            fc = (f"[0:v]crop=ih*9/16:ih:(iw-ih*9/16)/2:0,"
                  f"scale={W}:{H}:flags=lanczos[v]")
        sh(["ffmpeg", "-y", "-hwaccel", "auto", "-i", trimmed, "-filter_complex", fc,
            "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "fast",
            "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "copy", staged])
    else:
        print("[2/4] keeping 16:9", flush=True)

    # 3 — captions
    ass = None
    if captions:
        print("[3/4] transcribing (first run downloads the model)", flush=True)
        try:
            sh(whisper_cmd() + [staged, "--model", "tiny.en", "--word_timestamps", "True",
                                "--output_format", "json", "--output_dir", work,
                                "--language", "en"])
            js = os.path.join(work, os.path.splitext(os.path.basename(staged))[0] + ".json")
            if os.path.exists(js):
                ass = os.path.join(work, f"{stem}.ass")
                sh([sys.executable, os.path.join(HERE, "build_ass.py"), js, ass, style])
        except SystemExit as e:
            print(f"      captions skipped: {e}", flush=True)
            ass = None
    else:
        print("[3/4] captions off", flush=True)

    # 4 — burn + normalize to the platform loudness target
    print("[4/4] rendering", flush=True)
    vf = f"subtitles={ass}" if ass else "null"
    sh(["ffmpeg", "-y", "-i", staged, "-vf", vf,
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", out])

    size = os.path.getsize(out) / 1e6
    print(f"done -> {out}  ({dur:.1f}s, {size:.1f}MB)", flush=True)


if __name__ == "__main__":
    main()
