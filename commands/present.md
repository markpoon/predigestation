---
description: Build a timed, spoken slide run from a report and play it on the stage. Use when asked to present a report. Turns the stage on if needed
argument-hint: <path to report> [minutes]
---
Run `"${CLAUDE_PLUGIN_ROOT}/scripts/present" $ARGUMENTS` with Bash. It turns the stage on if needed (do not run presto first), turns the report into slides, plays them on the stage and speaks each one, fitted to the minutes given (default 4). Report in one line how many slides ran. macOS only.
