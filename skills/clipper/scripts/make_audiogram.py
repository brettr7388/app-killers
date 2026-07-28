#!/usr/bin/env python3
"""Audio-only clip -> vertical audiogram: logo, live waveform, word-by-word captions.

    python3 make_audiogram.py SOURCE START END LOGO.png OUT.mp4 [--style opus]

For podcasts and shows with no video. The captions carry the clip, so fix any
misspelled names in the transcript before you ship it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_clip import parse_time, sh, whisper_cmd          # noqa: E402

W, H = 1080, 1920
ACCENT = "0x4ad2ff"          # waveform colour — override with --color=0xRRGGBB


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    if len(args) < 5:
        sys.exit(__doc__)

    source, start_raw, end_raw, logo, out = args[:5]
    out = os.path.abspath(out)
    start, end = parse_time(start_raw), parse_time(end_raw)
    dur = end - start
    if dur <= 0:
        sys.exit("end must be after start")
    if not os.path.exists(logo):
        sys.exit(f"logo not found: {logo}")

    style = "opus"
    if "--style" in sys.argv:
        i = sys.argv.index("--style")
        if i + 1 < len(sys.argv):
            style = sys.argv[i + 1]
    color = next((f.split("=", 1)[1] for f in flags if f.startswith("--color=")), ACCENT)

    work = os.path.join(os.path.dirname(out) or ".", "_work")
    os.makedirs(work, exist_ok=True)
    stem = os.path.splitext(os.path.basename(out))[0]

    # 1 — pull the segment's audio
    print(f"[1/3] cutting {dur:.1f}s of audio", flush=True)
    audio = os.path.join(work, f"{stem}.m4a")
    sh(["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i", source, "-t", f"{dur:.3f}",
        "-vn", "-c:a", "aac", "-b:a", "192k", audio])

    # 2 — build the frame: blurred logo bed, crisp logo, live waveform
    print("[2/3] rendering audiogram", flush=True)
    silent = os.path.join(work, f"{stem}_silent.mp4")
    fc = (
        # background: the logo itself, blown up and blurred so the clip is on-brand
        f"[1:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"boxblur=48:3,eq=brightness=-0.16:saturation=0.75[bg];"
        # the logo, crisp, upper third
        f"[1:v]scale=640:640:force_original_aspect_ratio=decrease[logo];"
        f"[bg][logo]overlay=(W-w)/2:380[base];"
        # spectrum bars reacting to the real audio. showfreqs draws on opaque black,
        # so key the black out rather than overlaying a black slab on the artwork.
        # (Don't screen-blend instead: blending in YUV wrecks the chroma.)
        f"[0:a]showfreqs=s={W}x300:mode=bar:ascale=sqrt:fscale=log:"
        f"win_size=1024:colors={color}[bars];"
        f"[bars]format=rgba,colorkey=0x000000:0.30:0.04[barsk];"
        f"[base][barsk]overlay=0:1050:shortest=1[v]"   # above the caption line at ~1450
    )
    sh(["ffmpeg", "-y", "-i", audio, "-loop", "1", "-i", logo,
        "-filter_complex", fc, "-map", "[v]", "-map", "0:a",
        "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "copy", "-r", "25", silent])

    # 3 — captions do all the work in an audiogram, so they are not optional
    print("[3/3] transcribing and burning captions", flush=True)
    vf = "null"
    try:
        sh(whisper_cmd() + [silent, "--model", "tiny.en", "--word_timestamps", "True",
                            "--output_format", "json", "--output_dir", work,
                            "--language", "en"])
        js = os.path.join(work, f"{stem}_silent.json")
        if os.path.exists(js):
            ass = os.path.join(work, f"{stem}.ass")
            sh([sys.executable, os.path.join(HERE, "build_ass.py"), js, ass, style])
            vf = f"subtitles={ass}"
            print(f"      check {js} for misspelled names before posting", flush=True)
    except SystemExit as e:
        print(f"      captions skipped: {e}", flush=True)

    sh(["ffmpeg", "-y", "-i", silent, "-vf", vf,
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", out])

    print(f"done -> {out}  ({dur:.1f}s)", flush=True)


if __name__ == "__main__":
    main()
