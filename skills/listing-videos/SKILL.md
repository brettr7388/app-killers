---
name: listing-videos
description: Build a real estate listing tour video from property photos, vertical and horizontal. Use when the user says "listing video", "property tour", "real estate video", or gives a folder of home photos plus an address.
---

> Replaces **listing video services ($150-400/video)**. Runs locally — no API key, no credits, nothing uploaded.

# LISTING VIDEOS — build brief for Claude

You turn a set of listing photos into a property tour video: vertical for social,
horizontal for the MLS and the agent's website. No filming, no drone, no editor, no
subscription.

A tour takes about ten minutes. That's the whole business model — agents pay
$150–$400 for this, and the marginal cost here is zero.

Read `01-shot-order.md` before Phase 2 and `02-assembly-spec.md` before Phase 4.
`03-getting-clients.md` is for the user, not for you — point them at it when the
first video is done.

---

## PHASE 0 — Environment (silently, once)

```bash
command -v ffmpeg python3
```

macOS: `brew install ffmpeg` (install Homebrew first if `brew` is missing).
Linux/WSL: `sudo apt install -y ffmpeg python3-pip`.
Only if they want narration: `pip3 install --user --break-system-packages edge-tts`.

## PHASE 1 — Gather the inputs

**ASK** for these together, in one message, not one at a time:

1. The listing photos — a folder, or the Zillow/MLS URL to pull them from
2. Address, city, price, and beds/baths/sqft
3. The agent's name, phone, and brokerage (for the end card)
4. Vertical (Instagram/TikTok) or horizontal (MLS/website), or both

**Before you use any photos, confirm the user has the right to use them.** Listing
photos are usually owned by the photographer or the brokerage, not the agent, and
not the user. If the user is making this for a client, the client needs to confirm
they can use their own listing photos — most agent agreements allow it, some don't.
Ask once, take the answer, move on. Never scrape photos from a listing the user has
no relationship with.

If given a folder, list the photos and identify what room each one shows before doing
anything else — you cannot order a walkthrough you haven't looked at.

## PHASE 2 — Order the shots

Read `01-shot-order.md`. The MLS order is not the tour order. Build a route a person
could actually walk, assign a motion direction to each shot, and decide which 8–12
photos make the cut.

Show the user your running order as a numbered list with the motion for each, and
say which photos you're leaving out and why. **ASK** for approval. Reordering here
costs seconds; reordering after rendering costs a rebuild.

## PHASE 3 — Write the JSON

```json
{
  "address": "11926 Verrazano Dr",
  "city": "Orlando, FL 32836",
  "price": "$660,000",
  "specs": "4 bed  ·  3 bath  ·  2,940 sqft",
  "agent": {"name": "...", "phone": "...", "brokerage": "..."},
  "orientation": "vertical",
  "seconds_per_shot": 3.2,
  "shots": [
    {"file": "photos/01_front.jpg", "motion": "in", "label": "Welcome home"},
    {"file": "photos/02_foyer.jpg", "motion": "left"}
  ]
}
```

Labels are optional and should be rare — three or four across the whole video, on the
rooms that sell it. Labeling every room turns a tour into a slideshow with captions.

Narration is optional and off by default. If the user wants it, add `"narration"` and
read the fair-housing rules in `01-shot-order.md` first — this is the one place where
a listing video can create real legal exposure for the agent.

## PHASE 4 — Build

```bash
python3 scripts/make_tour.py listing.json tour_vertical.mp4
```

For both orientations, write two JSONs (change `orientation`) and build twice. The
horizontal cut should run a little longer per shot — 3.6s vs 3.2s — because it's
watched on a bigger screen with less urgency.

## PHASE 5 — Look at it

Pull stills across the video and read them:

```bash
for t in 1.5 6 12 20; do ffmpeg -y -ss $t -i tour_vertical.mp4 -frames:v 1 chk_$t.png; done
```

Checking for: text readable and clear of the bottom UI zone, no photo cropped into
nonsense by the vertical crop, the address spelled right, the phone number right.
**Get the phone number wrong and the entire video is worthless** — read it back to
the user digit by digit before you ship it.

Then `open tour_vertical.mp4`.

## PHASE 6 — Deliver

Hand over the video plus:

- A social caption (address, price, one honest hook, agent's handle)
- The MLS/website version if they wanted both
- A thumbnail: `ffmpeg -ss 5 -i tour_vertical.mp4 -frames:v 1 thumb.jpg`

Then point them at `03-getting-clients.md` if they're selling these.

---

## Standing rules

- **Never invent a property detail.** Not square footage, not the school district,
  not "recently renovated." Everything on screen must come from what the user gave
  you. A false statement in a listing video is the agent's liability, not yours.
- **No fair-housing language.** Never describe who the home is for or what the
  neighborhood is like — no "perfect for families", "safe area", "great schools",
  "quiet neighbors". Describe the property only. This is a legal line, not a style
  preference.
- **The photos are the ceiling.** Bad photos make a bad video and no amount of motion
  fixes it. If the source photos are dark, blurry, or full of clutter, say so plainly
  and suggest which ones to drop — a 7-shot tour of good photos beats a 14-shot tour
  that includes four bad ones.
