# Image Jobs

*the 4 things you actually opened it for*

**Replaces:** Photoshop ($22.99/mo)
**Runs at:** `localhost:7304`

Paste this into [Claude Code](https://claude.com/claude-code). It installs what it needs.

```
I need [remove background / batch resize / watermark / convert format] on the
images in [FOLDER].

Install what's needed: ffmpeg and imagemagick handle resize, watermark and
convert; use rembg for background removal.

Rules:
- NON-DESTRUCTIVE. Write to a new folder. Never overwrite my originals. Ever.
- Keep the original filenames, add a suffix.
- Skip anything that isn't an image instead of crashing on it.
- Tell me exactly how many files you processed and how many you skipped.

Show me ONE before/after pair and wait for my OK before running the whole batch.

Then wrap it in a local web app on localhost:7304 where I pick a folder, pick the
operation, and see the before/after side by side.
```

---

[← all seven prompts](../README.md)
