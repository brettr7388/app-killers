#!/usr/bin/env python3
"""Local PDF toolkit — merge, split, rotate, extract text, compress, images to PDF.

    python3 pdftool.py merge   a.pdf b.pdf -o out.pdf
    python3 pdftool.py split   in.pdf --pages 1-3,7 -o out.pdf
    python3 pdftool.py split   in.pdf --each            # one file per page
    python3 pdftool.py rotate  in.pdf --deg 90 -o out.pdf
    python3 pdftool.py text    in.pdf                   # -> in.txt
    python3 pdftool.py compress in.pdf -o out.pdf
    python3 pdftool.py images  a.jpg b.png -o out.pdf
    python3 pdftool.py info    in.pdf
    python3 pdftool.py ui                               # localhost:7311

Nothing is uploaded. Originals are never modified.
Needs: pip install pypdf pillow
"""
import os
import sys

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    sys.exit("pypdf missing. Run: pip3 install --user --break-system-packages pypdf")


def out_path(default, argv):
    if "-o" in argv:
        return argv[argv.index("-o") + 1]
    return default


def parse_pages(spec, total):
    """'1-3,7' -> [0,1,2,6]. 1-indexed in, 0-indexed out."""
    pages = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            pages.extend(range(int(a) - 1, int(b)))
        elif part:
            pages.append(int(part) - 1)
    bad = [p + 1 for p in pages if p < 0 or p >= total]
    if bad:
        sys.exit(f"page(s) out of range (file has {total}): {bad}")
    return pages


def cmd_merge(files, argv):
    w = PdfWriter()
    for f in files:
        r = PdfReader(f)
        for page in r.pages:
            w.add_page(page)
        print(f"  + {os.path.basename(f)} ({len(r.pages)}p)")
    dst = out_path("merged.pdf", argv)
    with open(dst, "wb") as fh:
        w.write(fh)
    print(f"merged {len(files)} files -> {dst} ({len(PdfReader(dst).pages)} pages)")
    return dst


def cmd_split(src, argv):
    r = PdfReader(src)
    stem = os.path.splitext(os.path.basename(src))[0]

    if "--each" in argv:
        made = []
        for i, page in enumerate(r.pages, 1):
            w = PdfWriter()
            w.add_page(page)
            dst = f"{stem}_p{i:03d}.pdf"
            with open(dst, "wb") as fh:
                w.write(fh)
            made.append(dst)
        print(f"split into {len(made)} files: {made[0]} ... {made[-1]}")
        return made

    spec = argv[argv.index("--pages") + 1] if "--pages" in argv else f"1-{len(r.pages)}"
    idx = parse_pages(spec, len(r.pages))
    w = PdfWriter()
    for i in idx:
        w.add_page(r.pages[i])
    dst = out_path(f"{stem}_pages.pdf", argv)
    with open(dst, "wb") as fh:
        w.write(fh)
    print(f"kept pages {spec} -> {dst} ({len(idx)} pages)")
    return dst


def cmd_rotate(src, argv):
    deg = int(argv[argv.index("--deg") + 1]) if "--deg" in argv else 90
    r = PdfReader(src)
    w = PdfWriter()
    for page in r.pages:
        page.rotate(deg)
        w.add_page(page)
    dst = out_path(f"{os.path.splitext(os.path.basename(src))[0]}_rot.pdf", argv)
    with open(dst, "wb") as fh:
        w.write(fh)
    print(f"rotated {len(r.pages)} pages by {deg}° -> {dst}")
    return dst


def cmd_text(src, argv):
    r = PdfReader(src)
    chunks = []
    for i, page in enumerate(r.pages, 1):
        t = (page.extract_text() or "").strip()
        chunks.append(f"--- page {i} ---\n{t}" if t else f"--- page {i} ---\n[no text layer]")
    dst = out_path(os.path.splitext(src)[0] + ".txt", argv)
    open(dst, "w").write("\n\n".join(chunks))
    empty = sum(1 for c in chunks if "[no text layer]" in c)
    print(f"extracted {len(r.pages)} pages -> {dst}")
    if empty:
        print(f"  ! {empty} page(s) had no text layer — that's a scan. "
              f"OCR it: brew install ocrmypdf && ocrmypdf {src} out.pdf")
    return dst


def cmd_compress(src, argv):
    """pypdf's lossless pass: dedupe objects and compress content streams."""
    w = PdfWriter()
    for page in PdfReader(src).pages:
        w.add_page(page)
    # compress_content_streams only works once the page belongs to a writer —
    # calling it on a reader's page raises "Page must be part of a PdfWriter"
    for page in w.pages:
        page.compress_content_streams()
    dst = out_path(f"{os.path.splitext(os.path.basename(src))[0]}_small.pdf", argv)
    with open(dst, "wb") as fh:
        w.write(fh)
    before, after = os.path.getsize(src), os.path.getsize(dst)
    pct = (1 - after / before) * 100
    print(f"{before/1000:.0f}KB -> {after/1000:.0f}KB ({pct:+.0f}%) -> {dst}")
    if pct < 5:
        print("  note: little gained — the weight is images, not streams. "
              "For image-heavy PDFs use ghostscript (brew install ghostscript).")
    return dst


def cmd_images(files, argv):
    try:
        from PIL import Image
    except ImportError:
        sys.exit("pillow missing. Run: pip3 install --user --break-system-packages pillow")
    imgs = []
    for f in files:
        im = Image.open(f)
        imgs.append(im.convert("RGB") if im.mode != "RGB" else im)
    dst = out_path("images.pdf", argv)
    imgs[0].save(dst, save_all=True, append_images=imgs[1:])
    print(f"{len(imgs)} image(s) -> {dst}")
    return dst


def cmd_info(src, argv):
    r = PdfReader(src)
    meta = r.metadata or {}
    size = os.path.getsize(src) / 1000
    box = r.pages[0].mediabox
    text_pages = sum(1 for p in r.pages if (p.extract_text() or "").strip())
    print(f"{os.path.basename(src)}")
    print(f"  pages     {len(r.pages)}")
    print(f"  size      {size:.0f}KB")
    print(f"  page      {float(box.width):.0f} x {float(box.height):.0f} pt")
    print(f"  encrypted {r.is_encrypted}")
    print(f"  text      {text_pages}/{len(r.pages)} pages have a text layer")
    if meta.get("/Title"):
        print(f"  title     {meta['/Title']}")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd, argv = sys.argv[1], sys.argv[2:]
    files = [a for a in argv if not a.startswith("-") and os.path.exists(a)]

    if cmd == "ui":
        import ui  # noqa: F401  (ui.py sits next to this file)
        return ui.main()

    if cmd in ("merge", "images") and len(files) < 2:
        sys.exit(f"{cmd} needs at least 2 input files")
    if cmd not in ("merge", "images") and not files:
        sys.exit("no input file found")

    handlers = {
        "merge": lambda: cmd_merge(files, argv),
        "split": lambda: cmd_split(files[0], argv),
        "rotate": lambda: cmd_rotate(files[0], argv),
        "text": lambda: cmd_text(files[0], argv),
        "compress": lambda: cmd_compress(files[0], argv),
        "images": lambda: cmd_images(files, argv),
        "info": lambda: cmd_info(files[0], argv),
    }
    if cmd not in handlers:
        sys.exit(f"unknown command '{cmd}'\n{__doc__}")
    handlers[cmd]()


if __name__ == "__main__":
    main()
