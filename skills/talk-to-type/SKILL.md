---
name: talk-to-type
description: Build a macOS push-to-talk dictation app that inserts cleaned-up text at the cursor in any app. Use when the user asks for dictation, voice typing, speech-to-text at the cursor, or a Wispr Flow style tool.
---

> Replaces **Wispr Flow ($15/mo)**. Runs locally — no API key, no credits.

# Talk To Type — push-to-talk dictation anywhere

Build a macOS menu bar app: hold a key, talk, release, and cleaned-up text appears at
the cursor **in whatever app is frontmost**.

Swift + SwiftPM, no Xcode project needed — a `build.sh` that runs
`swift build -c release`, assembles a `.app` bundle and ad-hoc codesigns it.

## Behaviour

- **Hold Fn** to record via a global event tap. Release to insert. **Esc** cancels.
- Ignore an accidental tap under 0.4s with nothing said.
- **Fn + Space** for hands-free mode: keep talking without holding. Tap Fn to stop.
- **Hold Fn + Ctrl** for command mode: speak an instruction ("make this more concise",
  "turn this into bullet points"). If text is selected, replace it; otherwise insert.

## Speech

Use Apple's on-device **SFSpeechRecognizer**. Free, no API key, works offline, and
fast enough for push-to-talk. Feed the user's personal dictionary (names, brands,
jargon) in as contextual strings — it fixes most proper-noun errors.

## Cleanup

Polish the raw transcript with `claude -p` — the user's Claude subscription, **not**
an API key. Strip filler words, resolve self-corrections ("tuesday, wait no, friday"
→ "friday"), fix grammar, and match the tone of the target app (formal in Mail, casual
in Slack, code-aware in a terminal).

Ship a rule-based fallback for when `claude` isn't installed, so it degrades instead
of breaking.

## Inserting the text — do it exactly this way

```
1. save the user's current clipboard
2. put the transcript on the pasteboard
3. send a synthetic Cmd+V
4. RESTORE the saved clipboard
```

This is the only approach that works in every app. **Skipping step 4 silently eats
whatever the user had copied** — it's the single most common way this feature makes
people hate the app.

## UI

A floating pill at the bottom of the screen while recording, colour-coded by mode, so
it's obvious the mic is live. Keep a searchable history of the last ~200 dictations.

## Permissions

Microphone, Speech Recognition, and **Accessibility** (for the global hotkey event tap
and the paste). Prompt on first launch.

> **The trap:** every rebuild changes the ad-hoc signature and invalidates the old TCC
> grants. The Accessibility toggle shows ON but is dead. After each rebuild:
> ```bash
> tccutil reset Accessibility <bundle-id>
> tccutil reset Microphone <bundle-id>
> tccutil reset SpeechRecognition <bundle-id>
> ```

## Why this one isn't a localhost app

Typing into other applications requires a native global event tap and Accessibility
permission. A web page can't do it. This one is a real menu bar app.

## What you need to build it

**Not full Xcode.** This builds with SwiftPM (`swift build -c release`), which only
needs the **Command Line Tools**:

```bash
xcode-select --install     # ~1GB, and it opens a dialog you have to click Install on
```

Claude can run that command for you, but macOS shows a GUI prompt that a human has to
accept — it can't be fully automated. Once the tools are in, everything else is
scripted.
