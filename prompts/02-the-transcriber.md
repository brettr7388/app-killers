# The Transcriber

*unlimited, offline, no 1,200-minute cap*

**Replaces:** Otter.ai ($16.99/mo)
**Runs at:** `localhost:7302`

Paste this into [Claude Code](https://claude.com/claude-code). It installs what it needs.

```
Transcribe this and give me something I can actually use: [file or URL]

Install openai-whisper if missing. If the `whisper` command isn't on PATH, use
`python3 -m whisper`. Run it with word timestamps. Then give me a markdown file:

- a clean transcript with paragraph breaks at TOPIC changes, not every sentence
- speaker labels if there's more than one voice (split on long pauses, label them
  A/B, and TELL me you guessed rather than pretending you know)
- timestamps every ~30 seconds in [mm:ss] form
- a 5-bullet summary at the top
- any decisions, numbers or action items pulled into their own list

Fix obvious mis-hears of proper nouns. Flag anything you genuinely couldn't make
out as [?] instead of inventing a word. Save it next to the source file.

Then wrap it in a local web app on localhost:7302 - one Python file, standard
library only, where I drop a file and read the transcript in the page.
```

---

[← all seven prompts](../README.md)
