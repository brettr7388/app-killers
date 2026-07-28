#!/usr/bin/env python3
"""Record the screen, transcribe it locally, and build a shareable page.

    python3 record.py [seconds] [--out NAME] [--no-transcript]

Produces NAME.mp4 plus NAME.html — a self-contained page with the video, the
transcript beside it, and clickable timestamps that seek the video. Nothing is
uploaded; both files stay on your disk.

macOS only for capture (uses screencapture). Needs Screen Recording permission for
whichever terminal you run it from.
"""
import html
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def sh(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        tail = "\n".join(r.stderr.strip().splitlines()[-4:])
        raise SystemExit(f"failed: {' '.join(cmd[:3])}\n{tail}")
    return r


def whisper_cmd():
    return ["whisper"] if shutil.which("whisper") else [sys.executable, "-m", "whisper"]


def record(seconds, out_mov):
    """screencapture -v records the main display. -x silences the shutter sound."""
    print(f"[1/3] recording {seconds}s — switch to what you want to capture now", flush=True)
    sh(["screencapture", "-v", "-V", str(seconds), "-x", out_mov])
    return out_mov


def to_mp4(src, dst):
    sh(["ffmpeg", "-y", "-i", src, "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "128k", dst])
    return dst


def transcribe(mp4, workdir):
    """Local whisper. Returns [(start, text)] or [] when there's no speech."""
    print("[2/3] transcribing locally (first run downloads the model)", flush=True)
    try:
        sh(whisper_cmd() + [mp4, "--model", "tiny.en", "--output_format", "json",
                            "--output_dir", workdir, "--language", "en"])
    except SystemExit as e:
        print(f"      no transcript: {e}", flush=True)
        return []
    js = os.path.join(workdir, os.path.splitext(os.path.basename(mp4))[0] + ".json")
    if not os.path.exists(js):
        return []
    data = json.load(open(js))
    return [(s["start"], s["text"].strip()) for s in data.get("segments", [])
            if s.get("text", "").strip()]


def duration(path):
    r = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "csv=p=0", path])
    return float(r.stdout.strip())


PAGE = """<!doctype html><html><head><meta charset="utf-8">
<title>__TITLE__</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--bg:#0d1015;--card:#161b22;--line:#242c38;--fg:#e6edf3;--dim:#8b97a6;--acc:#ffd24a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,sans-serif}
header{padding:22px 28px;border-bottom:1px solid var(--line)}
h1{margin:0;font-size:18px}
header span{color:var(--dim);font-size:13px}
main{display:grid;grid-template-columns:1.5fr 1fr;gap:22px;padding:22px 28px;
max-width:1400px;margin:0 auto;align-items:start}
@media(max-width:900px){main{grid-template-columns:1fr}}
video{width:100%;border-radius:12px;background:#000;border:1px solid var(--line)}
.panel{background:var(--card);border:1px solid var(--line);border-radius:12px;
padding:16px 18px;max-height:70vh;overflow:auto}
.panel h2{margin:0 0 12px;font-size:13px;color:var(--dim);text-transform:uppercase;
letter-spacing:.6px}
.seg{display:flex;gap:12px;padding:7px 8px;border-radius:7px;cursor:pointer}
.seg:hover{background:#1d2531}
.seg.on{background:#20293a}
.t{color:var(--acc);font:12px/1.7 ui-monospace,Menlo,monospace;flex-shrink:0}
.empty{color:var(--dim);font-size:14px}
footer{color:var(--dim);font-size:12px;text-align:center;padding:8px 20px 34px}
</style></head><body>
<header><h1>__TITLE__</h1>
<span>__DUR__ · recorded locally · nothing was uploaded</span></header>
<main>
  <video id="v" controls playsinline src="__SRC__"></video>
  <div class="panel"><h2>Transcript</h2><div id="segs">__SEGS__</div></div>
</main>
<footer>Keep this file next to __SRC__ — the page plays it from disk.</footer>
<script>
const v = document.getElementById('v');
const segs = [...document.querySelectorAll('.seg')];
segs.forEach(s => s.onclick = () => { v.currentTime = parseFloat(s.dataset.t); v.play(); });
v.ontimeupdate = () => {
  let cur = null;
  for (const s of segs) if (parseFloat(s.dataset.t) <= v.currentTime) cur = s;
  segs.forEach(s => s.classList.toggle('on', s === cur));
  if (cur) cur.scrollIntoView({block:'nearest'});
};
</script></body></html>"""


def build_page(mp4, segments, out_html, title):
    if segments:
        rows = "\n".join(
            f'<div class="seg" data-t="{t:.2f}">'
            f'<span class="t">{int(t)//60:02d}:{int(t)%60:02d}</span>'
            f'<span>{html.escape(text)}</span></div>'
            for t, text in segments)
    else:
        rows = ('<div class="empty">No speech detected — this recording is silent, '
                'or whisper isn\'t installed.</div>')

    secs = duration(mp4)
    doc = (PAGE.replace("__TITLE__", html.escape(title))
               .replace("__SRC__", html.escape(os.path.basename(mp4)))
               .replace("__DUR__", f"{int(secs)//60:d}m {int(secs)%60:02d}s")
               .replace("__SEGS__", rows))
    open(out_html, "w").write(doc)
    return out_html


def main():
    argv = sys.argv[1:]
    name = "recording"
    if "--out" in argv:
        i = argv.index("--out")
        name = argv[i + 1] if i + 1 < len(argv) else name
        del argv[i:i + 2]                       # drop the flag AND its value
    positional = [a for a in argv if not a.startswith("--")]
    seconds = int(positional[0]) if positional else 10

    workdir = os.path.abspath("_rec")
    os.makedirs(workdir, exist_ok=True)
    mov = os.path.join(workdir, f"{name}.mov")
    mp4 = os.path.abspath(f"{name}.mp4")

    if os.path.exists(os.environ.get("RECORD_FROM", "")):
        # lets you rebuild the page from an existing capture instead of re-recording
        print(f"[1/3] using existing capture: {os.environ['RECORD_FROM']}", flush=True)
        shutil.copy(os.environ["RECORD_FROM"], mov)
    else:
        record(seconds, mov)

    to_mp4(mov, mp4)
    segments = [] if "--no-transcript" in sys.argv else transcribe(mp4, workdir)

    print("[3/3] building page", flush=True)
    page = build_page(mp4, segments, os.path.abspath(f"{name}.html"),
                      f"Screen recording — {time.strftime('%b %d, %Y')}")

    print(f"\ndone\n  video: {mp4}\n  page:  {page}"
          f"\n  {len(segments)} transcript segment(s)")
    return page


if __name__ == "__main__":
    main()
