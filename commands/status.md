---
description: Check FactIQ auth, plan, and connection status
disable-model-invocation: true
allowed-tools: Bash(python3:*), Bash(python:*)
---

## Current FactIQ status

!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/factiq.py" whoami 2>&1`

## Your task

Summarize the status above for the user in one or two sentences:

- If it shows a user object: report the email, plan, and monthly usage
  (`monthly_usage.request_count` of `request_limit`), and confirm the skill
  is ready to use.
- If it shows an auth error (no key / invalid key): tell the user to get
  their API key at https://factiq.com/settings/security and run
  `/factiq:set-key`, then stop.
- If it shows a connection error: report which API base URL failed and
  suggest checking `FACTIQ_API_URL` / `~/.factiq/config.json`.
