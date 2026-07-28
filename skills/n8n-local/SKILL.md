---
name: n8n-local
description: Run n8n locally instead of paying for n8n Cloud or Zapier, and build workflows in it. Use when the user says "n8n", "self-host n8n", "automate this", "replace zapier", or wants scheduled/triggered automations without a subscription.
---

> Replaces **n8n Cloud / Zapier ($20-49/mo)**. Runs locally — no API key, no credits.

# n8n Local — the automation platform, self-hosted

This one is different from the rest of the repo: n8n is already free and open source.
You are not rebuilding it. You are **self-hosting it** so the user stops paying for
n8n Cloud or Zapier, and then **building their workflows for them** — which is the
part that actually costs people time.

## Install and run

```bash
npm install -g n8n
./scripts/start-n8n.sh          # http://localhost:5678
```

Two environment flags matter, and the first one is the single most common reason a
first-time local install appears broken:

- **`N8N_SECURE_COOKIE=false`** — without it, n8n refuses to set its auth cookie over
  plain `http://localhost`, so you log in and get bounced straight back to the login
  screen forever. It looks like a wrong password. It isn't.
- **`N8N_DIAGNOSTICS_ENABLED=false`** — opt out of telemetry.

First launch asks you to create an owner account. That account is local, stored in
`~/.n8n/database.sqlite`. There's no cloud tier and nothing to activate.

To try it without touching an existing setup, sandbox it:

```bash
N8N_USER_FOLDER=/tmp/n8n-test N8N_PORT=5679 ./scripts/start-n8n.sh
```

## What to actually do with it

The user's bottleneck is never installing n8n — it's building the workflow. So do that
for them:

1. **Ask what should trigger it** (a schedule, a webhook, a new file, an email) and
   **what should happen**. Get the whole chain in one question, not five.
2. **Build the workflow JSON directly** and import it, rather than describing clicks.
   A workflow is `{"nodes": [...], "connections": {...}}`. Write the file, then have
   them use *Import from File* in the editor. This is much faster than talking someone
   through a canvas.
3. **Use the n8n API** for anything programmatic:
   `POST http://localhost:5678/api/v1/workflows` with an API key from Settings → API.
4. **Test with the schedule disabled first.** Run it manually, look at the actual
   output of each node, and only then turn the trigger on.

## Credentials

Credentials are stored encrypted in the local database, keyed by
`~/.n8n/config`. **Back that file up** — lose it and every stored credential becomes
unreadable, even with the database intact. They also do not travel between machines,
so a migration means re-entering every credential by hand. Warn the user before they
build fifty workflows on a laptop with no backup.

## When to use this instead of a script

n8n earns its place when there are **real integrations** — Gmail, Sheets, Slack,
Notion, a CRM — where the OAuth dance and pagination are the work. For "when a file
lands here, do that", a 40-line Python script and a cron entry is simpler, faster and
has no server to keep running. Recommend honestly; don't reach for n8n because it
looks impressive.

## Keeping it running

For an always-on machine, run it under `launchd` (macOS) or `systemd` (Linux) so it
survives a reboot. **Show the user the plist or unit file and let them install it
themselves** — never load a background job on someone's machine silently.
