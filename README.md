# App Killers

**Claude Code skills that replace software I got tired of paying for.**

Each one is a real [Claude Code skill](https://docs.anthropic.com/en/docs/claude-code)
— a `SKILL.md` plus the reference files and scripts it needs. Drop a folder into
`~/.claude/skills/` and Claude picks it up automatically. No API key, no credits,
nothing uploaded anywhere.

| Skill | Replaces | Their price | What it does |
|---|---|---|---|
| **[clipper](skills/clipper/SKILL.md)** | CapCut Pro | $19.99/mo | long video in, vertical captioned clips out |
| **[faceless-docs](skills/faceless-docs/SKILL.md)** | AI video tools | $30-70/mo | a narrated documentary short for $0 an episode |
| **[listing-videos](skills/listing-videos/SKILL.md)** | listing video services | $150-400/video | photos in, branded property tour out |
| **[mentorly](skills/mentorly/SKILL.md)** | Cluely | $20/mo | ask about anything on your screen, get arrows pointing at the real UI |
| **[talk-to-type](skills/talk-to-type/SKILL.md)** | Wispr Flow | $15/mo | hold a key, talk, polished text appears at your cursor |
| **[transcriber](skills/transcriber/SKILL.md)** | Otter.ai | $16.99/mo | unlimited local transcription, no 1,200-minute cap |
| **[designer](skills/designer/SKILL.md)** | Canva Pro | $18/mo | HTML + headless Chrome renders any graphic to PNG |
| **[image-jobs](skills/image-jobs/SKILL.md)** | Photoshop | $22.99/mo | the four things you actually opened Photoshop for |

That's **$186.47/month** of software — $2,237.64/year — at $0.

Those are each tool's *cheapest* advertised rate; several cost considerably more
month-to-month (Photoshop is $34.49, Zapier is $73.50). Prices verified July 2026.

---

## Install

Copy any skill folder into your Claude Code skills directory:

```bash
git clone https://github.com/brettr7388/app-killers.git
mkdir -p ~/.claude/skills
cp -r app-killers/skills/clipper ~/.claude/skills/
```

Then just say what you want in any Claude Code session — *"cut clips from this
video"* — and the skill loads itself.

Don't have Claude Code yet:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

A $20/mo Pro plan is enough. The skills install their own dependencies (ffmpeg,
whisper, edge-tts) the first time they need them — you don't have to know what those
are.

---

## The idea

CapCut Pro doubled to $19.99/month this year. What it does to make a clip is cut a
file, crop it to vertical, and burn captions on it — that's ffmpeg and a speech model,
both free, both already on your laptop.

The transcoding was never the product. The judgment was: which thirty seconds are
worth posting, which room to show first, which frame to cut on. That's the part you
were renting, and that's the part that became something you can just ask for.

Apps aren't dying. **Thin apps are** — the ones whose entire product was a friendly UI
around a capability that's now directly invocable. If a company's moat was "we know
the ffmpeg flags and you don't," that moat is gone. If it's a decade of template
curation or a genuinely hard technical problem, they're fine.

**Being fair:** Photoshop is a masterpiece and I'm not replacing it — I'm replacing
four things I used it for. You give up mobile, polish, onboarding, and someone to
email at 2am. If your income depends on a tool working perfectly at 3am the night
before a launch, buy the tool. I mean that.

---

## Notes

- Every skill here is one I've actually run. Where a skill is a native app rather than
  a script, it links to the working source.
- MIT licensed — take them, change them, sell what you build.
- If one breaks, open an issue and I'll fix it.

— [@Brosenberg0](https://x.com/Brosenberg0)
