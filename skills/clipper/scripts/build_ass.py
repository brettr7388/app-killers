#!/usr/bin/env python3
"""Word-by-word ASS captions from a Whisper JSON transcript.

Usage:
    python3 build_ass.py transcript.json out.ass [style]

Styles:
    opus   (default) big bold white, active word in gold      - the TikTok look
    punch            ALL CAPS, active word gold + slight pop   - gaming / hype
    clean            white, no highlight, smaller              - talking head / docs

Designed for 1080x1920. Captions sit above every platform's UI dead zone.
No dependencies beyond the standard library.
"""
import json
import sys

W, H = 1080, 1920

STYLES = {
    #            font          size  primary        highlight      outline shadow  bold  margin_v  upper
    "opus":  ("Arial Black",   92,  "&H00FFFFFF&", "&H0000D7FF&", 6,      3,      -1,   420,      False),
    "punch": ("Arial Black",  104,  "&H00FFFFFF&", "&H0000D7FF&", 7,      4,      -1,   440,      True),
    "clean": ("Helvetica",     74,  "&H00FFFFFF&", "&H00FFFFFF&", 4,      2,      -1,   400,      False),
}

MAX_WORDS = 4          # words visible at once
MAX_CHARS = 22         # break a chunk early if it gets wide
PAUSE_BREAK = 0.55     # a gap this long starts a new chunk
MIN_DUR = 0.08         # never emit a sub-frame dialogue line


def ts(t):
    """seconds -> 0:00:00.00"""
    t = max(0.0, float(t))
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def esc(text):
    """Escape ASS control characters."""
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")")


def load_words(path):
    data = json.load(open(path))
    words = []
    for seg in data.get("segments", []):
        for w in seg.get("words", []) or []:
            raw = w.get("word", w.get("text", ""))
            token = raw.strip()
            if not token:
                continue
            start, end = w.get("start"), w.get("end")
            if start is None or end is None:
                continue
            words.append({"t": token, "s": float(start), "e": float(end)})
    if not words:
        sys.exit("No word timestamps found. Re-run whisper with --word_timestamps True")
    return words


def chunk(words):
    """Group words into on-screen lines."""
    out, cur, chars = [], [], 0
    for i, w in enumerate(words):
        gap = w["s"] - words[i - 1]["e"] if i else 0.0
        breaks = (
            len(cur) >= MAX_WORDS
            or (cur and chars + len(w["t"]) + 1 > MAX_CHARS)
            or (cur and gap > PAUSE_BREAK)
            or (cur and cur[-1]["t"][-1] in ".!?")
        )
        if breaks:
            out.append(cur)
            cur, chars = [], 0
        cur.append(w)
        chars += len(w["t"]) + 1
    if cur:
        out.append(cur)
    return out


def build(words, style_name):
    font, size, primary, highlight, outline, shadow, bold, margin_v, upper = STYLES[style_name]

    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},{size},{primary},{primary},&H00000000&,&H80000000&,{bold},0,0,0,100,100,0,0,1,{outline},{shadow},2,60,60,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    lines = []
    for group in chunk(words):
        for i, active in enumerate(group):
            start = active["s"]
            # hold the line until the next word starts so there is never a blank frame
            end = group[i + 1]["s"] if i + 1 < len(group) else active["e"] + 0.10
            if end - start < MIN_DUR:
                end = start + MIN_DUR

            parts = []
            for w in group:
                token = esc(w["t"].upper() if upper else w["t"])
                if w is active and highlight != primary:
                    pop = r"\fscx108\fscy108" if style_name == "punch" else ""
                    parts.append(f"{{\\c{highlight}{pop}}}{token}{{\\c{primary}\\fscx100\\fscy100}}")
                else:
                    parts.append(token)
            text = " ".join(parts)
            lines.append(f"Dialogue: 0,{ts(start)},{ts(end)},Cap,,0,0,0,,{{\\fad(60,0)}}{text}")

    return head + "\n".join(lines) + "\n"


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, dst = sys.argv[1], sys.argv[2]
    style = sys.argv[3] if len(sys.argv) > 3 else "opus"
    if style not in STYLES:
        sys.exit(f"Unknown style '{style}'. Choose: {', '.join(STYLES)}")
    open(dst, "w").write(build(load_words(src), style))
    print(f"wrote {dst} ({style})")


if __name__ == "__main__":
    main()
