---
description: Choose whether Claude speaks its replies while a presentation is playing (on by default). Use when asked to stay quiet, or to speak again, during presentations
argument-hint: on | off (nothing flips it)
allowed-tools: Bash("${CLAUDE_PLUGIN_ROOT}/scripts/interject":*)
---
Run `"${CLAUDE_PLUGIN_ROOT}/scripts/interject" $ARGUMENTS` with Bash. Report in one line whether replies are spoken during presentations. macOS only.
