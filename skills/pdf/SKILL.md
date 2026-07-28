---
name: pdf
description: Merge, split, rotate, compress PDFs, extract their text, or turn images into a PDF. Use when the user mentions combining PDFs, splitting pages, compressing a PDF, extracting text from a PDF, or scanning documents.
---

> Replaces **Adobe Acrobat ($22.99/mo)**. Runs locally — no API key, no credits.

# PDF — the toolkit Acrobat charges $22.99/mo for

Every one of these runs locally. No upload, no watermark, no page limit, and the
originals are never modified.

```bash
pip3 install --user --break-system-packages pypdf pillow
```

## The operations

```bash
python3 scripts/pdftool.py info     in.pdf                   # pages, size, text layer?
python3 scripts/pdftool.py merge    a.pdf b.pdf -o out.pdf
python3 scripts/pdftool.py split    in.pdf --pages 1-3,7 -o out.pdf
python3 scripts/pdftool.py split    in.pdf --each            # one file per page
python3 scripts/pdftool.py rotate   in.pdf --deg 90 -o out.pdf
python3 scripts/pdftool.py text     in.pdf                   # -> in.txt
python3 scripts/pdftool.py compress in.pdf -o out.pdf
python3 scripts/pdftool.py images   a.jpg b.png -o out.pdf
```

Page ranges are 1-indexed and inclusive: `--pages 1-3,7` keeps pages 1, 2, 3 and 7.

## Rules

- **Never overwrite the original.** Always write a new file, even when the user says
  "just replace it" — write the new one and let them delete the old.
- **Run `info` first** on anything unfamiliar. It tells you page count, size, whether
  it's encrypted, and how many pages actually have a text layer.
- **Check the output** before reporting success. A merge that silently dropped a file
  still exits zero.

## Two things that surprise people

**A scanned PDF has no text.** `text` will return `[no text layer]` for those pages —
the file is images of words, not words. That needs OCR, which is a different tool:

```bash
brew install ocrmypdf && ocrmypdf in.pdf out.pdf
```

Say this plainly rather than handing back an empty file.

**`compress` is lossless and modest.** It dedupes objects and compresses content
streams, so a text-heavy PDF shrinks maybe 10%. If a PDF is huge, the weight is
*images*, and shrinking those means re-encoding them:

```bash
brew install ghostscript
gs -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook -dNOPAUSE -dBATCH    -sOutputFile=small.pdf in.pdf
```

That's lossy. Tell the user before you do it, and keep the original.
