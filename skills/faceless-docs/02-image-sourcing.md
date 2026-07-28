# Images

Every picture comes from Wikimedia Commons — millions of files, all freely licensed,
no subscription, no stock-footage bill, no AI generation credits. The catch is that
Commons search is a keyword match, not a librarian, so it will confidently hand you
the wrong thing.

## Writing queries that work

The `query` field is a Commons search. It must name **a thing that was photographed,
painted, or drawn.**

| ✅ Returns something | ❌ Returns noise |
|---|---|
| `Pompeii plaster cast body` | `the tragedy of Pompeii` |
| `RMS Titanic launch 1911` | `Titanic disaster aftermath` |
| `Chernobyl reactor 4 roof` | `nuclear danger` |
| `Apollo 1 capsule interior` | `space program setbacks` |

Rules of thumb:

- **Two to four words.** More words narrows Commons to zero, not to precision.
- **Include a proper noun** — a place, ship, person, or building.
- **Add a year** when the subject changed over time (`Berlin Wall 1961`).
- **Add the medium** when photography didn't exist yet: `painting`, `engraving`,
  `lithograph`, `woodcut`. `Vesuvius eruption painting` works; `Vesuvius 79 AD`
  returns modern tourist photos.
- **For portraits**, use `portrait` plus the full name.

## The verification step people skip

The builder prints what it found for each beat:

```
01 'Mount Vesuvius eruption painting' -> img01.jpg  [Pietro Antoniani]
```

That tells you a file arrived. It does **not** tell you the file shows the right
thing. Before you ship, pull a still from each shot and look:

```bash
for t in 2 12 24 36; do ffmpeg -y -ss $t -i episode_01.mp4 -frames:v 1 c_$t.png; done
```

Commons has four different Vesuvius eruptions, several ships called Titanic, and a
lot of statues that are captioned as one emperor and depict another. Looking takes
thirty seconds.

Also watch for `NO IMAGE for '...'` in the build output. That beat is silently
reusing the previous image — the video still renders, and it looks lazy. Rewrite the
query and rebuild.

## When Commons has nothing

Some subjects have no visual record at all. Three fallbacks, in order:

1. **Photograph the place today.** The ruins, the building, the coastline. A modern
   photo of a historical site is honest and almost always available.
2. **Use a period artwork of the same subject matter** — a painting of a similar ship,
   a contemporaneous map, a diagram from a period book. Commons has enormous
   collections of scanned public-domain books (`filetype:bitmap` plus the book title).
3. **Rewrite the beat.** If nothing exists, the sentence is describing something
   unpicturable, which `01-script-formula.md` says not to write anyway.

Whatever you do: **never let the narration claim an image is something it isn't.**
"Here we see the moment the wall fell" over a stock photo of a different wall is how
channels get community-noted.

## Licensing and credit

Commons files are freely licensed but most licenses (CC-BY, CC-BY-SA) require
attribution. The builder prints each file's author as it downloads. Collect those
and put them in your video description:

```
Images: Wikimedia Commons — Jebulon, Pietro Antoniani, Giorgio Sommer (CC BY-SA).
```

This takes one line, satisfies the license, and costs you nothing. Public-domain
files need no credit, but crediting them anyway is free goodwill.

Two things to actually avoid:
- **Files tagged "non-free" or "fair use"** on Commons — rare, but they exist. If the
  file page says non-free, don't use it.
- **Modern press photography** that ended up on Commons by mistake. If an image looks
  like a wire-service news photo from the last 30 years, be suspicious.

## The contact email

Wikimedia returns `403 Forbidden` to requests that don't identify who is asking. Set
it once:

```bash
export WIKI_CONTACT=you@youremail.com
```

or add `"contact": "you@youremail.com"` to every episode JSON. It is sent only in the
request header to Wikimedia — it never appears in the video, and it isn't shared
anywhere else. Skipping it doesn't make you anonymous, it just makes the download
fail.
