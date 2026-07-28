#!/usr/bin/env python3
"""Transcribe audio/video locally into a document you can actually use.

    python3 transcribe.py FILE [--model tiny.en] [--speakers] [--no-summary]

Writes FILE.md next to the source: summary, timestamped transcript with paragraph
breaks at topic changes, and speaker labels if asked. Nothing is uploaded.

Needs: pip install openai-whisper   (ffmpeg must be on PATH)
"""
import json
import os
import shutil
import subprocess
import sys

GAP_PARAGRAPH = 1.4      # a pause this long starts a new paragraph
GAP_SPEAKER = 2.0        # a pause this long is *probably* a speaker change


def whisper_cmd():
    return ["whisper"] if shutil.which("whisper") else [sys.executable, "-m", "whisper"]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        tail = "\n".join(r.stderr.strip().splitlines()[-5:])
        sys.exit(f"failed: {' '.join(cmd[:3])}\n{tail}")
    return r


def ts(seconds):
    return f"{int(seconds)//60:02d}:{int(seconds)%60:02d}"


def transcribe(src, model, workdir):
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found. Install it: brew install ffmpeg")
    print(f"[1/3] transcribing with {model} (first run downloads the model)", flush=True)
    run(whisper_cmd() + [src, "--model", model, "--output_format", "json",
                         "--output_dir", workdir])
    js = os.path.join(workdir, os.path.splitext(os.path.basename(src))[0] + ".json")
    if not os.path.exists(js):
        sys.exit("whisper produced no output")
    return json.load(open(js)).get("segments", [])


def paragraphs(segments, label_speakers):
    """Group segments into paragraphs, optionally guessing speaker turns."""
    blocks, cur, speaker, prev_end = [], [], "A", 0.0
    for seg in segments:
        text = seg["text"].strip()
        if not text:
            continue
        gap = seg["start"] - prev_end
        if cur and gap > GAP_PARAGRAPH:
            if label_speakers and gap > GAP_SPEAKER:
                blocks.append((cur[0][0], speaker, " ".join(t for _, t in cur)))
                speaker = "B" if speaker == "A" else "A"
            else:
                blocks.append((cur[0][0], None, " ".join(t for _, t in cur)))
            cur = []
        cur.append((seg["start"], text))
        prev_end = seg["end"]
    if cur:
        blocks.append((cur[0][0], speaker if label_speakers else None,
                       " ".join(t for _, t in cur)))
    return blocks


def summarize(text):
    """Use the user's Claude subscription if the CLI is there. Never required."""
    if not shutil.which("claude"):
        return None
    print("[2/3] summarizing with claude", flush=True)
    prompt = ("Summarize this transcript in exactly 5 short bullets, then list any "
              "decisions, numbers or action items under a '## Action items' heading. "
              "Output markdown only, no preamble.\n\n" + text[:12000])
    r = subprocess.run(["claude", "-p", prompt], capture_output=True, text=True, timeout=180)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def main():
    argv = sys.argv[1:]
    files = [a for a in argv if not a.startswith("--") and os.path.exists(a)]
    if not files:
        sys.exit(__doc__)
    src = files[0]

    model = "tiny.en"
    if "--model" in argv:
        model = argv[argv.index("--model") + 1]

    workdir = os.path.join(os.path.dirname(os.path.abspath(src)) or ".", "_transcribe")
    os.makedirs(workdir, exist_ok=True)

    segments = transcribe(src, model, workdir)
    if not segments:
        sys.exit("no speech found in that file")

    blocks = paragraphs(segments, "--speakers" in argv)
    plain = "\n\n".join(b[2] for b in blocks)

    summary = None if "--no-summary" in argv else summarize(plain)

    print("[3/3] writing document", flush=True)
    out = os.path.splitext(src)[0] + ".md"
    with open(out, "w") as f:
        f.write(f"# Transcript — {os.path.basename(src)}\n\n")
        if summary:
            f.write(summary + "\n\n---\n\n")
        else:
            f.write("_Install the Claude Code CLI to get an automatic summary here._\n\n---\n\n")
        for start, speaker, text in blocks:
            who = f"**{speaker}:** " if speaker else ""
            f.write(f"`[{ts(start)}]` {who}{text}\n\n")

    words = sum(len(b[2].split()) for b in blocks)
    print(f"\ndone -> {out}")
    print(f"  {len(blocks)} paragraphs, {words} words, "
          f"{ts(segments[-1]['end'])} long")
    if "--speakers" in argv:
        print("  speaker labels are INFERRED from pauses — check them before you rely on them")


if __name__ == "__main__":
    main()
