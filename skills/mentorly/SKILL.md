---
name: mentorly
description: Build a macOS menu bar assistant that answers questions about whatever is on screen and draws arrows at the real UI elements. Use when the user asks for a screen-aware assistant, an on-screen helper, a Cluely-style tool, or "something that explains what I'm looking at".
---

> Replaces **Cluely ($20/mo)**. Runs locally — no API key, no credits.

# Mentorly — a screen-aware assistant

Build a macOS menu bar app: double-tap **Command** anywhere, type what you're confused
about, and get a plain-language answer streamed into a small panel — while labeled
arrows are drawn **on the live screen**, pinned to the actual buttons and fields the
answer talks about.

A working implementation is open source at
**https://github.com/brettr7388/Mentorly** (MIT). Read it before rebuilding — the
hard parts are already solved there. Use this skill to build your own, or to help
someone set that one up.

## The architecture that matters

**1. Answers run on the user's Claude subscription, not an API key.**
Drive the local `claude` CLI with `claude -p`. No Anthropic API key, no per-token
billing, nothing to pay for beyond the plan they already have. Verify it first:

```bash
claude -p "hello"      # must answer without asking for a key
```

Keep an API-key path as an *optional* fallback, never the default.

**2. Point at the real UI, not at a screenshot.**
This is the whole trick and it's what separates this from "send a screenshot to an
LLM". On trigger, read the frontmost app's **macOS Accessibility tree** to get the
on-screen frame of every control. Send Claude the screenshot *and* the list of named
controls. Have Claude name which controls to point at; draw arrows at those exact
frames in a transparent overlay window.

If you skip the Accessibility tree and let the model guess pixel coordinates from the
image, the arrows land in the wrong place and the illusion dies immediately.

**3. Double-tap Command as the trigger.**
It collides with nothing: a lone Command tap means nothing on its own, any Cmd+key
chord is ignored, and the listener must be **listen-only** — it must never swallow a
keystroke. Either Command key works. One-handed, one thumb.

**4. A transparent, click-through overlay window** for the arrows, so several can stay
pinned at once (numbered how-to steps) while the user reads and keeps working.

## Permissions

Needs **Screen Recording** (ScreenCaptureKit, macOS 14.2+) and **Accessibility** (to
read the element tree). Prompt on first launch and explain *why* in plain language —
these two prompts are where users bail.

> **The trap:** every rebuild changes the code signature, which silently invalidates
> the old TCC grants. The toggle in System Settings will show ON but be dead. After
> each rebuild:
> ```bash
> tccutil reset ScreenCapture <bundle-id>
> tccutil reset Accessibility <bundle-id>
> ```
> Then re-grant. This will waste an hour of your life if nobody tells you.

## Answer style

Tune the system prompt for a beginner: short, human, no jargon, no em dashes, and
never assume background knowledge. The answer appears in a small panel while the
arrows point — so write for someone reading and looking at the same time.

## Privacy

Each ask sends one screenshot plus the question to Claude over the user's own
subscription — the same data path as pasting a screenshot into the Claude app. No
telemetry, no analytics, no logging, no servers. Say so out loud in the README;
a screen-reading tool that isn't explicit about this doesn't get installed.

## Requirements

macOS 14.2+, Xcode 15+, a Claude subscription with the Claude Code CLI signed in.
