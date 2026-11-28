# Privacy

predigestation collects nothing for its author. It has no server, account, analytics or telemetry, and its scripts make no network requests.

## What stays on your Mac

- `scripts/runs.jsonl`: a log of actions and timings, including report file names and some spoken lines
- `scripts/voice.json`: speech timing
- State files and built slides in `scripts/`, which can contain the text and charts of your last report
- Temporary audio in `/tmp`, used to measure speech length

Delete these at any time. They are not shared.

## What it reads

The report you ask for. `behold` also reads the names and titles of HTML files in `~/Downloads` to find it.

## Other software involved

- Claude Code: your messages, command output and any report Claude reads are handled under Anthropic's privacy policy.
- Safari: a report that links to online images, fonts or scripts will load them when shown.
- macOS speech: lines are spoken by the system `say` command, and anyone nearby can hear them.

## Contact

[Open an issue](https://github.com/markpoon/predigestation/issues).
