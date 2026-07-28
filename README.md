# App Killers

**Claude Code skills that do what the paid apps do, on your own machine, for $0.**

Every skill here is a real [Claude Code skill](https://docs.anthropic.com/en/docs/claude-code):
a `SKILL.md` plus the reference files and working scripts it needs. Drop a folder into
`~/.claude/skills/` and Claude uses it automatically. No API key, no credits, no
uploads, no account.

**New here? → [START-HERE.md](START-HERE.md)** — one paste and you're set up.

| Skill | Replaces | Their price | What it does | Verified |
|---|---|---|---|---|
| **[clipper](skills/clipper/SKILL.md)** | CapCut Pro | $19.99/mo | long video in, vertical captioned clips out | run |
| **[faceless-docs](skills/faceless-docs/SKILL.md)** | AI video tools | $30-70/mo | a narrated documentary short for $0 an episode | run |
| **[listing-videos](skills/listing-videos/SKILL.md)** | listing video services | $150-400/video | photos in, branded property tour out | run |
| **[mentorly](skills/mentorly/SKILL.md)** | Cluely | $20/mo | ask about anything on your screen, get arrows pointing at the real UI | build |
| **[talk-to-type](skills/talk-to-type/SKILL.md)** | Wispr Flow | $15/mo | hold a key, talk, polished text appears at your cursor | build |
| **[transcriber](skills/transcriber/SKILL.md)** | Otter.ai | $16.99/mo | unlimited local transcription, no 1,200-minute cap | run |
| **[designer](skills/designer/SKILL.md)** | Canva Pro | $18/mo | HTML + headless Chrome renders any graphic to PNG | run |
| **[image-jobs](skills/image-jobs/SKILL.md)** | Photoshop | $22.99/mo | the four things you actually opened Photoshop for | run |
| **[n8n-local](skills/n8n-local/SKILL.md)** | n8n Cloud / Zapier | $20-49/mo | self-host the automation platform and have Claude build the workflows | run |
| **[recorder](skills/recorder/SKILL.md)** | Loom | $12.50/seat/mo | screen recording with a local transcript and a shareable page | run |
| **[pdf](skills/pdf/SKILL.md)** | Adobe Acrobat | $22.99/mo | merge, split, rotate, compress, extract text, images to PDF | run |

That's **$198.46/month** — $2,381.52/year — at $0.

Each is that tool's *cheapest* advertised rate; several cost more month-to-month
(Photoshop $34.49, Zapier $73.50, Grammarly $30). Where a tool lists a range I used
the low end, and `listing-videos` is excluded from the total because it's billed per
video, not monthly. Prices checked July 2026.

**Verified** means I ran it. 104 automated checks pass against a fresh clone of this
repo: every SKILL.md validates, every referenced file exists, every script parses, and
every skill that ships a script was executed on real input and its output inspected.
The two marked *build* produce native macOS apps, so they need Xcode rather than a
script run.

---

## Install

```bash
git clone https://github.com/brettr7388/app-killers.git
mkdir -p ~/.claude/skills
cp -r app-killers/skills/* ~/.claude/skills/
python3 app-killers/check-setup.py     # tells you what's ready and what's missing
```

Then just say what you want in any Claude Code session:

| Say this | Skill that wakes up |
|---|---|
| "cut clips from this video" + a link | `clipper` |
| "transcribe this recording" | `transcriber` |
| "make me a YouTube thumbnail about X" | `designer` |
| "merge these PDFs" / "split this PDF" | `pdf` |
| "resize all the images in this folder" | `image-jobs` |
| "record my screen for 30 seconds" | `recorder` |
| "make a documentary short about X" | `faceless-docs` |
| "make a listing video from these photos" | `listing-videos` |
| "set up n8n locally" | `n8n-local` |

You don't need to remember skill names. Say what you want; Claude picks the skill and
installs whatever that skill needs.

No Claude Code yet:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

A $20/mo Pro plan is enough.

---

## The idea

CapCut Pro doubled to $19.99/month this year. What it does to make a clip is cut a
file, crop it to vertical, and burn captions on it — that's ffmpeg and a speech model,
both free, both already sitting on your laptop.

The transcoding was never the product. The judgment was: which thirty seconds are
worth posting, which room to show first, which frame to cut on. That's what you were
renting, and that's what became something you can simply ask for.

Apps aren't dying. **Thin apps are** — the ones whose entire product was a friendly UI
around a capability that's now directly invocable. If the moat was "we know the ffmpeg
flags and you don't," that moat is gone. If it's a decade of template curation or a
genuinely hard technical problem, they're fine.

**Being fair:** Photoshop is a masterpiece and I'm not replacing it — I'm replacing
four things I used it for. You give up mobile, polish, onboarding and someone to email
at 2am. If your income depends on a tool working perfectly at 3am the night before a
launch, buy the tool. I mean that.

---

## Notes

- Everything runs locally. Your files aren't uploaded anywhere. The two exceptions are
  obvious in context: `faceless-docs` fetches images from Wikimedia Commons, and
  `clipper` downloads a video if you hand it a URL.
- MIT licensed. Take them, change them, sell what you build.
- Something broken? [Open an issue](https://github.com/brettr7388/app-killers/issues).

— [@Brosenberg0](https://x.com/Brosenberg0)
