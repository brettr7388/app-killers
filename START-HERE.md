# Start here

You need two things: a Claude subscription ($20/mo Pro is enough) and about five
minutes. You do **not** need to know what ffmpeg, whisper or Python are — the skills
install what they need, when they need it.

---

## Step 1 — Install Claude Code

Open **Terminal** (Mac: press `Cmd+Space`, type "Terminal", hit Enter) and paste this:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Then run `claude` and log in with your Claude account when it asks.

> On Windows, install [WSL](https://learn.microsoft.com/windows/wsl/install) first,
> then run the same command inside it.

## Step 2 — Start Claude and paste this

In Terminal, type `claude`, press Enter, then paste the whole block below:

```
Set me up with the App Killers skills.

1. Clone https://github.com/brettr7388/app-killers into my home folder.
2. Create ~/.claude/skills if it doesn't exist, and copy every folder from the
   repo's skills/ directory into it.
3. Check what's already installed on this machine: ffmpeg, ffprobe, yt-dlp, whisper,
   edge-tts, python3, node, npm. Don't install anything yet — just tell me what's
   there and what's missing, and roughly what each missing one is for. Note that
   whisper often isn't on PATH after install and has to be run as
   `python3 -m whisper`; check for that specifically.
4. Read the SKILL.md in each skill folder and give me a short list: the skill's name,
   what it does in one line, what it replaces, and what I'd literally type to use it.
5. Run `python3 check-setup.py` from the repo and show me the output — it lists every
   skill and whether it's ready on this machine.

Don't install anything or change any settings without asking me first. When you're
done, ask me which one I want to try, and set that one up.
```

That's the whole setup. Claude clones the repo, installs the skills, checks your
machine, and tells you what you can do.

## Step 3 — Use one

After that, just say what you want in plain English in any Claude Code session:

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

Two of the eleven (`mentorly`, `talk-to-type`) build native macOS apps instead of
running a script — those need Xcode. The other nine run immediately.

You don't have to remember skill names. Say what you want; Claude picks the skill.

---

## The three things that trip people up

**1. Claude asks permission before running commands.** It has to run commands to do
anything. Approve them. If the prompting gets tedious, start it with
`claude --permission-mode acceptEdits`.

**2. The first run of anything with speech is slow.** Whisper downloads its model the
first time — a minute or two, once. After that it's fast and works offline.

**3. Talk to it when something's wrong.** These aren't apps with settings menus. If a
clip starts too early, say "start it three seconds later." If captions are too big,
say so. It edits and re-runs. That's the entire point.

---

## What if something breaks

Tell Claude what happened, in plain English — it wrote the tool, it can fix the tool.
If it's a real bug in a skill,
[open an issue](https://github.com/brettr7388/app-killers/issues) and I'll fix it.

## Privacy

Everything runs on your machine. Your videos, recordings and documents are not
uploaded anywhere. The only thing that leaves your computer is your conversation with
Claude — the same as any Claude Code session.

Two exceptions, both obvious in context: `faceless-docs` downloads images from
Wikimedia Commons, and `clipper` downloads a video if you give it a URL.
