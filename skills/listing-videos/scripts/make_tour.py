#!/usr/bin/env python3
"""Build a listing tour video from photos. Zero cost, no AI credits.

    python3 make_tour.py listing.json tour.mp4

listing.json:
{
  "address": "11926 Verrazano Dr",
  "city": "Orlando, FL",
  "price": "$660,000",
  "specs": "4 bed  ·  3 bath  ·  2,940 sqft",
  "agent": {"name": "Debbi Jones", "phone": "(407) 555-0142", "brokerage": "Keller Williams"},
  "orientation": "vertical",           // or "horizontal"
  "seconds_per_shot": 3.2,
  "music": "optional/path/to/music.mp3",
  "narration": "optional spoken script; omit for a silent video",
  "voice": "en-US-AriaNeural",
  "shots": [
    {"file": "photos/01_front.jpg",   "motion": "in",   "label": "Welcome home"},
    {"file": "photos/02_foyer.jpg",   "motion": "left"},
    {"file": "photos/03_kitchen.jpg", "motion": "in",   "label": "Chef's kitchen"}
  ]
}

motion: in | out | left | right | up | still
Requires: ffmpeg. Narration additionally needs `pip install edge-tts`.
"""
import asyncio
import json
import os
import subprocess
import sys

FPS = 30
XFADE = 0.6          # crossfade length between shots
FONT = "/System/Library/Fonts/Helvetica.ttc"
if not os.path.exists(FONT):
    FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("\n".join(r.stderr.strip().splitlines()[-6:]))
        raise SystemExit(f"ffmpeg failed: {' '.join(cmd[:6])} ...")
    return r


def duration(path):
    r = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "csv=p=0", path])
    return float(r.stdout.strip())


def probe_image(path):
    r = sh(["ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", path])
    w, h = r.stdout.strip().split("x")[:2]
    return int(w), int(h)


def esc(text):
    """Escape drawtext metacharacters."""
    return (text.replace("\\", "").replace(":", "\\:")
                .replace("'", "").replace("%", "").replace(",", "\\,"))


# ---------------------------------------------------------------- shots

def shot_clip(img, secs, motion, out, W, H, label=None):
    """One moving clip from one photo, cover-cropped to frame."""
    w, h = probe_image(img)
    frames = max(int(round(secs * FPS)), 12)

    if w / h > W / H:                       # too wide -> crop sides
        cw, ch = int(h * W / H), h
        cx, cy = (w - cw) // 2, 0
    else:                                   # too tall -> crop, biased to the top
        cw, ch = w, int(w * H / W)
        cx, cy = 0, min(int(h * 0.10), max(h - ch, 0))

    # Interiors: a slow drift reads as a walkthrough, a fast one reads as a slideshow.
    if motion == "in":
        z, x, y = "1.02+0.0011*on", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif motion == "out":
        z, x, y = ("if(eq(on,0),1.22,max(zoom-0.0011,1.02))",
                   "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)")
    elif motion == "left":
        z, x, y = "1.14", f"(iw-iw/zoom)*(1-on/{frames})", "ih/2-(ih/zoom/2)"
    elif motion == "right":
        z, x, y = "1.14", f"(iw-iw/zoom)*on/{frames}", "ih/2-(ih/zoom/2)"
    elif motion == "up":
        z, x, y = "1.14", "iw/2-(iw/zoom/2)", f"(ih-ih/zoom)*(1-on/{frames})"
    else:                                   # still
        z, x, y = "1.06", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"

    vf = (f"crop={cw}:{ch}:{cx}:{cy},scale={W*2}:{H*2}:flags=lanczos,"
          f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS}")

    if label:
        # Vertical posts: keep labels above the bottom ~380px, where TikTok and Reels
        # paint their own caption and button UI. Horizontal has no such dead zone.
        drop = 0.26 if H > W else 0.12
        vf += (f",drawtext=fontfile={FONT}:text='{esc(label)}':fontcolor=white:"
               f"fontsize={int(H*0.030)}:shadowcolor=black@0.7:shadowx=2:shadowy=2:"
               f"x={int(W*0.06)}:y=h-{int(H*drop)}:"
               f"alpha='if(lt(t,0.4),t/0.4,if(lt(t,{secs-0.5}),1,({secs}-t)/0.5))'")

    vf += ",format=yuv420p"
    sh(["ffmpeg", "-y", "-loop", "1", "-i", img, "-t", f"{secs:.3f}",
        "-vf", vf, "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        "-r", str(FPS), "-an", out])
    return out


def card(text_lines, secs, out, W, H, work, name, sub=None):
    """A solid title/end card."""
    tpath = os.path.join(work, f"{name}.txt")
    open(tpath, "w").write("\n".join(text_lines))
    vf = (f"drawtext=fontfile={FONT}:textfile={tpath}:fontcolor=white:"
          f"fontsize={int(H*0.042)}:line_spacing={int(H*0.014)}:"
          f"x=(w-text_w)/2:y=(h-text_h)/2-{int(H*0.09)}:"
          f"alpha='if(lt(t,0.5),t/0.5,if(lt(t,{secs-0.6}),1,({secs}-t)/0.6))'")
    if sub:
        spath = os.path.join(work, f"{name}_sub.txt")
        open(spath, "w").write("\n".join(sub))
        vf += (f",drawtext=fontfile={FONT}:textfile={spath}:fontcolor=white@0.75:"
               f"fontsize={int(H*0.026)}:line_spacing={int(H*0.010)}:"
               f"x=(w-text_w)/2:y=(h/2)+{int(H*0.02)}:"
               f"alpha='if(lt(t,0.7),t/0.7,if(lt(t,{secs-0.6}),1,({secs}-t)/0.6))'")
    sh(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x111418:s={W}x{H}:r={FPS}",
        "-t", f"{secs:.2f}", "-vf", vf + ",format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-an", out])
    return out


def xfade_chain(clips, durations, out, W, H):
    """Crossfade every clip into the next. Beats a hard concat on interiors."""
    if len(clips) == 1:
        sh(["ffmpeg", "-y", "-i", clips[0], "-c", "copy", out])
        return out

    cmd = ["ffmpeg", "-y"]
    for c in clips:
        cmd += ["-i", c]

    parts, label, running = [], "0:v", durations[0]
    for i in range(1, len(clips)):
        offset = running - XFADE
        nxt = f"vx{i}"
        parts.append(f"[{label}][{i}:v]xfade=transition=fade:"
                     f"duration={XFADE}:offset={offset:.3f}[{nxt}]")
        label = nxt
        running += durations[i] - XFADE

    cmd += ["-filter_complex", ";".join(parts), "-map", f"[{label}]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "19",
            "-pix_fmt", "yuv420p", "-r", str(FPS), out]
    sh(cmd)
    return out


# ---------------------------------------------------------------- audio

def narrate(text, voice, out):
    import edge_tts

    async def go():
        await edge_tts.Communicate(text, voice, rate="-6%").save(out)

    asyncio.run(go())


def add_audio(video, out, music=None, voice_track=None):
    if not music and not voice_track:
        return video
    total = duration(video)
    cmd = ["ffmpeg", "-y", "-i", video]
    chains, mixes = [], []
    idx = 1
    if voice_track:
        cmd += ["-i", voice_track]
        chains.append(f"[{idx}:a]loudnorm=I=-16:TP=-1.5:LRA=11[nar]")
        mixes.append("[nar]")
        idx += 1
    if music:
        cmd += ["-stream_loop", "-1", "-i", music]
        # duck the bed when there is narration over it
        vol = 0.16 if voice_track else 0.42
        chains.append(f"[{idx}:a]volume={vol},afade=t=out:st={max(total-2.5,0):.2f}:d=2.5[bed]")
        mixes.append("[bed]")

    chains.append(f"{''.join(mixes)}amix=inputs={len(mixes)}:duration=first[a]")
    cmd += ["-filter_complex", ";".join(chains), "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out]
    sh(cmd)
    return out


# ---------------------------------------------------------------- main

def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    spec = json.load(open(sys.argv[1]))
    base = os.path.dirname(os.path.abspath(sys.argv[1]))
    out_path = os.path.abspath(sys.argv[2])
    work = os.path.join(os.path.dirname(out_path) or ".", "_build")
    os.makedirs(work, exist_ok=True)

    W, H = (1080, 1920) if spec.get("orientation", "vertical") == "vertical" else (1920, 1080)
    per = float(spec.get("seconds_per_shot", 3.2))
    agent = spec.get("agent", {})

    missing = [s["file"] for s in spec["shots"]
               if not os.path.exists(os.path.join(base, s["file"]))]
    if missing:
        sys.exit("Missing photos:\n  " + "\n  ".join(missing))

    clips, durs = [], []

    print("1/4 opening card...")
    open_secs = 2.8
    clips.append(card([spec["address"], spec.get("city", "")], open_secs,
                      os.path.join(work, "open.mp4"), W, H, work, "open",
                      sub=[spec.get("price", ""), spec.get("specs", "")]))
    durs.append(open_secs)

    print(f"2/4 building {len(spec['shots'])} shots...")
    for i, s in enumerate(spec["shots"]):
        secs = float(s.get("seconds", per))
        path = shot_clip(os.path.join(base, s["file"]), secs,
                         s.get("motion", "in"), os.path.join(work, f"shot{i:02d}.mp4"),
                         W, H, s.get("label"))
        clips.append(path)
        durs.append(secs)
        print(f"    {i:02d} {s['file']}  ({s.get('motion','in')}, {secs:.1f}s)")

    print("3/4 end card...")
    end_secs = 3.6
    clips.append(card([agent.get("name", ""), agent.get("phone", "")], end_secs,
                      os.path.join(work, "end.mp4"), W, H, work, "end",
                      sub=[agent.get("brokerage", "")]))
    durs.append(end_secs)

    joined = xfade_chain(clips, durs, os.path.join(work, "joined.mp4"), W, H)

    print("4/4 audio...")
    voice_track = None
    if spec.get("narration"):
        voice_track = os.path.join(work, "narration.mp3")
        narrate(spec["narration"], spec.get("voice", "en-US-AriaNeural"), voice_track)
    music = spec.get("music")
    if music and not os.path.isabs(music):
        music = os.path.join(base, music)
    if music and not os.path.exists(music):
        print(f"    ! music not found: {music} — building silent")
        music = None

    final = add_audio(joined, out_path, music, voice_track)
    if final != out_path:
        sh(["ffmpeg", "-y", "-i", joined, "-c", "copy", out_path])

    print(f"\ndone -> {out_path}  ({duration(out_path):.1f}s)")
    if not music and not voice_track:
        print("     (silent — add \"music\" or \"narration\" to the JSON, or let the "
              "platform's audio carry it)")


if __name__ == "__main__":
    main()
