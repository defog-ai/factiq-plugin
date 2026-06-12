---
description: Answer a data question with FactIQ and publish a shareable chart
argument-hint: "<question, e.g. How has US unemployment changed since 2019?>"
disable-model-invocation: true
allowed-tools: Bash(python3:*), Bash(python:*), Read, Write
---

Answer this question with real data from FactIQ:

> $ARGUMENTS

Read `${CLAUDE_PLUGIN_ROOT}/SKILL.md` and follow its orchestration workflow
exactly (context → discover → fetch → compute → chart → share). Finish by
returning the share URL and a short narrative of what the data shows. If no
question was provided above, ask the user what they want to know.
