#!/usr/bin/env python3
"""Build a narrated 9:16 documentary short from an episode JSON. Zero cost.

    python3 make_short.py episode.json out.mp4

episode.json:
{
  "title": "The City That Vanished In A Day",
  "contact": "you@youremail.com",     <-- REQUIRED. Wikimedia blocks anonymous bots.
  "voice": "en-US-GuyNeural",
  "rate": "-8%",
  "beats": [
    {"text": "In 79 AD, a Roman city went to sleep and never woke up.",
     "query": "Pompeii ruins Vesuvius"},
    {"text": "...", "query": "...", "image": "optional/local/path.jpg"}
  ]
}

Each beat is one sentence of narration and one image. The narration is voiced in a
single pass (so the prosody is continuous), then split on silence to get real
per-sentence timings — the images cut exactly when the sentence changes.

Requires: ffmpeg, python3, `pip install edge-tts`. Nothing paid, no API keys.
"""
import asyncio
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

W, H, FPS = 1080, 1920, 24

# Wikimedia requires a User-Agent with a real contact address and returns 403 to
# anything that looks anonymous or like a placeholder. Set it once, per episode
# ("contact" in the JSON) or globally (export WIKI_CONTACT=you@youremail.com).
UA = {"User-Agent": "DocShortBuilder/1.0 (unset)"}


def set_contact(email):
    if not email or "example.com" in email or "@" not in email:
        sys.exit(
            "Set a real contact email before sourcing images.\n"
            "  Add \"contact\": \"you@youremail.com\" to your episode JSON,\n"
            "  or run: export WIKI_CONTACT=you@youremail.com\n"
            "Wikimedia blocks image requests that don't identify who's asking. "
            "It is never shown in the video and is only sent to Wikimedia."
        )
    UA["User-Agent"] = f"DocShortBuilder/1.0 ({email})"
FONT = "/System/Library/Fonts/Helvetica.ttc"
if not os.path.exists(FONT):
    FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def sh(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def duration(path):
    r = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "csv=p=0", path])
    return float(r.stdout.strip())


# ---------------------------------------------------------------- narration

def narrate(text, voice, rate, out):
    import edge_tts

    async def go():
        await edge_tts.Communicate(text, voice, rate=rate).save(out)

    asyncio.run(go())


def speech_spans(audio, n_expected):
    """Split narration into per-sentence spans using silence detection."""
    r = subprocess.run(
        ["ffmpeg", "-i", audio, "-af", "silencedetect=n=-35dB:d=0.28", "-f", "null", "-"],
        capture_output=True, text=True)
    starts, ends = [], []
    for line in r.stderr.splitlines():
        m = re.search(r"silence_start: ([\d.]+)", line)
        if m:
            starts.append(float(m.group(1)))
        m = re.search(r"silence_end: ([\d.]+)", line)
        if m:
            ends.append(float(m.group(1)))

    total = duration(audio)
    spans, cursor = [], 0.0
    for st, en in zip(starts, ends + [total]):
        if st - cursor > 0.15:
            spans.append([cursor, st])
        cursor = en
    if total - cursor > 0.25:
        spans.append([cursor, total])

    # Reconcile against the number of sentences we actually wrote.
    while len(spans) > n_expected:                       # merge the two closest
        gaps = [(spans[i + 1][0] - spans[i][1], i) for i in range(len(spans) - 1)]
        _, i = min(gaps)
        spans[i][1] = spans[i + 1][1]
        del spans[i + 1]
    while len(spans) < n_expected and spans:             # split the longest
        i = max(range(len(spans)), key=lambda k: spans[k][1] - spans[k][0])
        a, b = spans[i]
        mid = (a + b) / 2
        spans[i] = [a, mid]
        spans.insert(i + 1, [mid, b])

    # Stretch each span to the start of the next so there is never a black gap.
    for i in range(len(spans) - 1):
        spans[i][1] = spans[i + 1][0]
    if spans:
        spans[-1][1] = total
    return spans, total


# ---------------------------------------------------------------- images

def commons_image(query, dest, min_px=900):
    """Download one usable Wikimedia Commons image for a query. Returns (path,w,h)."""
    search = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "list": "search",
        "srsearch": query + " filetype:bitmap", "srnamespace": "6", "srlimit": "6"})
    data = json.load(urllib.request.urlopen(
        urllib.request.Request(search, headers=UA), timeout=30))

    for hit in data.get("query", {}).get("search", []):
        info_url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
            "action": "query", "format": "json", "titles": hit["title"],
            "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": "2200"})
        try:
            page = list(json.load(urllib.request.urlopen(
                urllib.request.Request(info_url, headers=UA), timeout=30)
            )["query"]["pages"].values())[0]
            ii = page.get("imageinfo", [{}])[0]
            if ii.get("width", 0) < min_px:
                continue
            url = ii.get("thumburl") or ii.get("url")
            blob = urllib.request.urlopen(
                urllib.request.Request(url, headers=UA), timeout=60).read()
            open(dest, "wb").write(blob)
            w, h = probe_image(dest)
            if w and min(w, h) > 400:
                credit = ii.get("extmetadata", {}).get("Artist", {}).get("value", "")
                return dest, w, h, re.sub(r"<[^>]+>", "", credit).strip()
        except Exception as e:
            print(f"  ! {hit['title']}: {e}")
    return None


def probe_image(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", path],
        capture_output=True, text=True)
    try:
        w, h = r.stdout.strip().split("x")[:2]
        return int(w), int(h)
    except ValueError:
        return None, None


# ---------------------------------------------------------------- video

def ken_burns(img, w, h, secs, out, mode):
    """One 9:16 clip with slow drift. mode 0 = push in, 1 = pull out, 2 = tilt down."""
    frames = max(int(round(secs * FPS)), 12)

    # cover-crop to 9:16, with a 2% inset that shaves watermarks and scan borders
    if w / h > W / H:
        cw, ch = int(h * W / H), h
        cx, cy = (w - cw) // 2, 0
    else:
        cw, ch = w, int(w * H / W)
        cx, cy = 0, min(int(h * 0.08), max(h - ch, 0))
    cx, cy = cx + int(cw * 0.02), cy + int(ch * 0.02)
    cw, ch = int(cw * 0.96), int(ch * 0.96)

    if mode == 0:
        z, y = "1.02+0.0016*on", "ih/2-(ih/zoom/2)"
    elif mode == 1:
        z, y = "if(eq(on,0),1.30,max(zoom-0.0016,1.02))", "ih/2-(ih/zoom/2)"
    else:
        z, y = "1.16", f"(ih-ih/zoom)*on/{frames}"

    # pre-upscale 2x: zoompan jitters badly on a source close to its output size
    vf = (f"crop={cw}:{ch}:{cx}:{cy},scale={W*2}:{H*2}:flags=lanczos,"
          f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='{y}':d={frames}:s={W}x{H}:fps={FPS},"
          f"format=yuv420p")
    sh(["ffmpeg", "-y", "-loop", "1", "-i", img, "-t", f"{secs:.3f}",
        "-vf", vf, "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-r", str(FPS), "-an", out])
    return out


def wrap_title(text, max_chars=17, max_lines=3):
    """Break a title into balanced lines. drawtext does not wrap on its own."""
    words, lines, cur = text.split(), [], ""
    for word in words:
        if cur and len(cur) + 1 + len(word) > max_chars:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:                      # too long: widen and retry once
        return wrap_title(text, max_chars + 6, max_lines + 1)
    return lines


def title_card(video, text, out, work, hold=2.8):
    """Burn the episode title over the opening seconds, wrapped and auto-sized."""
    lines = wrap_title(text)
    longest = max(len(line) for line in lines)
    # Helvetica averages ~0.52 em per character; keep the block inside 88% of frame
    size = max(46, min(92, int((W * 0.88) / (0.52 * longest))))

    # A textfile sidesteps every escaping problem with quotes, colons and commas.
    tpath = os.path.join(work, "title.txt")
    open(tpath, "w").write("\n".join(lines))

    vf = (f"drawtext=fontfile={FONT}:textfile={tpath}:fontcolor=white:fontsize={size}:"
          f"box=1:boxcolor=black@0.55:boxborderw=26:line_spacing=14:"
          f"x=(w-text_w)/2:y=(h-text_h)/2-h*0.10:enable='lt(t,{hold})':"
          f"alpha='if(lt(t,{hold-0.6}),1,({hold}-t)/0.6)'")
    sh(["ffmpeg", "-y", "-i", video, "-vf", vf, "-c:v", "libx264",
        "-preset", "fast", "-crf", "20", "-c:a", "copy", out])
    return out


def mix_audio(video, narration, out, total):
    """Narration over a synthesized low drone bed. No music licensing, ever."""
    drone = ("sine=frequency=55:duration=%.2f,volume=0.055[d1];"
             "sine=frequency=82.4:duration=%.2f,volume=0.035[d2];"
             "[d1][d2]amix=inputs=2[bed]" % (total, total))
    sh(["ffmpeg", "-y", "-i", video, "-i", narration,
        "-filter_complex",
        f"{drone};[1:a]loudnorm=I=-15:TP=-1.5:LRA=11[nar];"
        f"[nar][bed]amix=inputs=2:duration=first:weights=1 0.5[a]",
        "-map", "0:v", "-map", "[a]", "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-shortest", out])
    return out


# ---------------------------------------------------------------- main

def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    spec = json.load(open(sys.argv[1]))
    out_path = os.path.abspath(sys.argv[2])
    work = os.path.join(os.path.dirname(out_path) or ".", "_build")
    os.makedirs(work, exist_ok=True)

    beats = spec["beats"]
    script = " ".join(b["text"].strip() for b in beats)

    # Fail on a missing contact now, before spending time on narration.
    if any(not b.get("image") for b in beats):
        set_contact(spec.get("contact") or os.environ.get("WIKI_CONTACT"))

    print(f"1/5 narrating {len(beats)} beats...")
    narration = os.path.join(work, "narration.mp3")
    narrate(script, spec.get("voice", "en-US-GuyNeural"), spec.get("rate", "-8%"), narration)
    spans, total = speech_spans(narration, len(beats))
    print(f"    {total:.1f}s of narration")

    print("2/5 sourcing images...")
    images = []
    for i, beat in enumerate(beats):
        if beat.get("image") and os.path.exists(beat["image"]):
            w, h = probe_image(beat["image"])
            images.append((beat["image"], w, h))
            print(f"    {i:02d} local: {beat['image']}")
            continue
        got = commons_image(beat["query"], os.path.join(work, f"img{i:02d}.jpg"))
        if got:
            path, w, h, credit = got
            images.append((path, w, h))
            print(f"    {i:02d} {beat['query']!r} -> {os.path.basename(path)}  [{credit[:40]}]")
        else:
            print(f"    {i:02d} NO IMAGE for {beat['query']!r} — reusing previous")
            images.append(images[-1] if images else None)

    if not images or images[0] is None:
        sys.exit("Could not source a single image. Rewrite the queries and retry.")

    print("3/5 building shots...")
    shots = []
    for i, ((img, w, h), (a, b)) in enumerate(zip(images, spans)):
        shot = os.path.join(work, f"shot{i:02d}.mp4")
        ken_burns(img, w, h, b - a, shot, i % 3)
        shots.append(shot)

    print("4/5 assembling...")
    listing = os.path.join(work, "concat.txt")
    open(listing, "w").write("".join(f"file '{os.path.abspath(s)}'\n" for s in shots))
    joined = os.path.join(work, "joined.mp4")
    sh(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listing,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", joined])

    titled = os.path.join(work, "titled.mp4")
    title_card(joined, spec["title"], titled, work)

    print("5/5 mixing audio...")
    mix_audio(titled, narration, out_path, total)
    print(f"\ndone -> {out_path}  ({duration(out_path):.1f}s)")


if __name__ == "__main__":
    main()
