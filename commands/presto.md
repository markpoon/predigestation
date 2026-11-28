---
description: Turn the predigestation stage on or off (one word toggles it)
allowed-tools: Bash("${CLAUDE_PLUGIN_ROOT}/scripts/presto")
---
Run `"${CLAUDE_PLUGIN_ROOT}/scripts/presto"` with Bash. It toggles the stage: the first run brings the stage window to the front, fills the screen and keeps the Mac awake; the next run speaks a short sign-off, closes the stage and lets the Mac sleep. Report in one line whether the stage is now on or off. macOS only.
