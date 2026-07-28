# The Designer

*HTML + headless Chrome = a PNG*

**Replaces:** Canva Pro ($18/mo)
**Runs at:** `localhost:7303`

Paste this into [Claude Code](https://claude.com/claude-code). It installs what it needs.

```
Make me a [thumbnail / carousel / banner] about [TOPIC], [W]x[H] px.

Build it as HTML and CSS, then render it to PNG with headless Chrome:

  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --headless=new --disable-gpu --hide-scrollbars \
    --window-size=W,H --screenshot=out.png \
    --virtual-time-budget=2500 file://page.html

Rules: no external fonts, no CDNs, no web requests - everything inline so it
renders offline. One accent colour. Type big enough to read at thumbnail size:
if the headline isn't legible when the image is scaled to 400px wide, it's too
small. Dark background unless I say otherwise.

Render it, LOOK at the PNG yourself, and fix what's wrong BEFORE showing me.
Then give me a 400px-wide copy so I can check it at feed size.

Then wrap it in a local web app on localhost:7303 where I type the text and see
the render update.
```

---

[← all seven prompts](../README.md)
