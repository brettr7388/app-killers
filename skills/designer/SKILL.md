---
name: designer
description: Design and render graphics — thumbnails, banners, quote cards, carousels, social images — as HTML rendered to PNG. Use when the user asks for a thumbnail, a banner, a cover image, a carousel, an infographic, or any designed image with text in it.
---

> Replaces **Canva Pro ($18/mo)**. Runs locally — no API key, no credits.

# Designer — graphics without a design tool

Write the graphic as HTML and CSS, then screenshot it with headless Chrome. No design
app, no subscription, no export limits, and it's fully scriptable.

## Render

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --hide-scrollbars \
  --window-size=WIDTH,HEIGHT --screenshot=out.png \
  --virtual-time-budget=2500 file:///absolute/path/page.html
```

On Linux use `google-chrome` or `chromium`. `--virtual-time-budget` matters: without
it, fonts and layout may not settle before the shot is taken.

## Rules that decide whether it looks designed or generated

- **No external fonts, no CDNs, no web requests.** Inline everything — it renders
  offline and identically every time. Use the system font stack
  (`-apple-system, BlinkMacSystemFont, "Helvetica Neue"`); it's excellent and free.
- **One accent colour.** Two accents is where amateur design starts.
- **Type big enough for the surface.** For a thumbnail: if the headline isn't legible
  when the image is scaled to 400px wide, it's too small. Test it, don't estimate.
- **Dark backgrounds** unless asked otherwise — they photograph better in feeds and
  hide compression artifacts.
- **Let the content size the canvas.** A card padded with 400px of dead space at the
  bottom reads as broken. Compute the height from the content.

## Non-negotiable: look at the output

Render it, **open the PNG and actually look at it**, and fix what's wrong before
showing the user. Then produce a 400px-wide copy and look at *that* — text that
overflows, wraps mid-word, or vanishes at thumbnail size is invisible in the code and
obvious in the image.

## Sizes worth knowing

| Use | Size |
|---|---|
| YouTube thumbnail | 1280×720 |
| X post / link card | 1600×900 |
| Instagram square / carousel | 1080×1080 |
| Story / Reel / TikTok | 1080×1920 |
| Pinterest pin | 1000×1500 |

## Optional local UI

Wrap it in a single-file Python web app on `localhost:7303` — standard library only —
where the user types the text and sees the render update.
