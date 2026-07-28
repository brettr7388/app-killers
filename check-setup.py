#!/usr/bin/env python3
"""Check this machine and tell you which App Killers skills are ready to run.

    python3 check-setup.py

Reads nothing, installs nothing, changes nothing. Just looks and reports.
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.join(HERE, "skills")

GREEN, RED, DIM, BOLD, OFF = "\033[32m", "\033[31m", "\033[90m", "\033[1m", "\033[0m"


def have(tool):
    return shutil.which(tool) is not None


def have_whisper():
    """The command often isn't on PATH after install, but the module is."""
    if have("whisper"):
        return True, "whisper"
    r = subprocess.run([sys.executable, "-c", "import whisper"], capture_output=True)
    return (r.returncode == 0), ("python3 -m whisper" if r.returncode == 0 else None)


def have_module(name):
    return subprocess.run([sys.executable, "-c", f"import {name}"],
                          capture_output=True).returncode == 0


def have_chrome():
    for c in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Chromium.app/Contents/MacOS/Chromium"):
        if os.path.exists(c):
            return True
    return have("google-chrome") or have("chromium")


whisper_ok, whisper_how = have_whisper()

TOOLS = {
    "ffmpeg": (have("ffmpeg"), "video and image work", "brew install ffmpeg"),
    "ffprobe": (have("ffprobe"), "reads media files", "brew install ffmpeg"),
    "whisper": (whisper_ok, "speech to text", "pip3 install --user --break-system-packages openai-whisper"),
    "Chrome": (have_chrome(), "renders graphics to PNG", "download Google Chrome"),
    "edge-tts": (have_module("edge_tts"), "narration voice", "pip3 install --user --break-system-packages edge-tts"),
    "pypdf": (have_module("pypdf"), "PDF operations", "pip3 install --user --break-system-packages pypdf"),
    "pillow": (have_module("PIL"), "images to PDF", "pip3 install --user --break-system-packages pillow"),
    "yt-dlp": (have("yt-dlp"), "downloads videos by URL", "brew install yt-dlp"),
    "claude": (have("claude"), "the whole point", "curl -fsSL https://claude.ai/install.sh | bash"),
    "node": (have("node"), "only for n8n", "brew install node"),
}

# skill -> what it needs to run at all
NEEDS = {
    "clipper": ["ffmpeg", "whisper"],
    "transcriber": ["whisper"],
    "designer": ["Chrome"],
    "image-jobs": ["ffmpeg"],
    "faceless-docs": ["ffmpeg", "edge-tts"],
    "listing-videos": ["ffmpeg"],
    "recorder": ["ffmpeg", "whisper"],
    "pdf": ["pypdf"],
    "n8n-local": ["node"],
    "mentorly": [],
    "talk-to-type": [],
}

NATIVE = {"mentorly", "talk-to-type"}


def main():
    print(f"\n{BOLD}Tools on this machine{OFF}\n")
    for name, (ok, why, fix) in TOOLS.items():
        mark = f"{GREEN}✓{OFF}" if ok else f"{RED}✗{OFF}"
        note = f"  {DIM}{fix}{OFF}" if not ok else ""
        print(f"  {mark} {name:<10} {DIM}{why}{OFF}{note}")

    if whisper_ok and whisper_how != "whisper":
        print(f"\n  {DIM}note: the `whisper` command isn't on your PATH, but the module "
              f"is.\n        Skills already fall back to `python3 -m whisper`.{OFF}")

    print(f"\n{BOLD}Skills{OFF}\n")
    ready = blocked = 0
    for skill in sorted(os.listdir(SKILLS)) if os.path.isdir(SKILLS) else []:
        missing = [t for t in NEEDS.get(skill, []) if not TOOLS.get(t, (False,))[0]]
        if skill in NATIVE:
            print(f"  {DIM}○{OFF} {skill:<15} {DIM}builds a native app — needs Xcode{OFF}")
        elif missing:
            blocked += 1
            print(f"  {RED}✗{OFF} {skill:<15} needs: {', '.join(missing)}")
        else:
            ready += 1
            print(f"  {GREEN}✓{OFF} {skill:<15} {DIM}ready{OFF}")

    print(f"\n{ready} ready, {blocked} blocked, {len(NATIVE)} build a native app\n")

    if blocked:
        print(f"{BOLD}To unblock everything, paste this into Claude Code:{OFF}\n")
        print("  Install the missing tools from check-setup.py, then re-run it.\n")
    else:
        print(f"{BOLD}Everything's ready.{OFF} Try: "
              f'"transcribe this file" or "merge these PDFs"\n')


if __name__ == "__main__":
    main()
