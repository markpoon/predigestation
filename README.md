# predigestation

Turn data into a show for people who aren't technical, live in a meeting. macOS shell scripts drive one Safari window (the "stage"), speak with the system voice, and move a camera around the charts of an HTML report.

**Status: working prototype.** Voice control is not wired up yet: the commands are run from a terminal or by an assistant such as Claude. See [the plan](predigestation-plan.md) for what is built and what is next.

## Requirements

- macOS with Safari, and the "Daniel" system voice
- In Safari's Develop menu, turn on **Allow JavaScript from Apple Events**
- Allow your terminal to control Safari and Finder when macOS asks
- For the tests: Python 3 and Node

## Quick start

```bash
git clone https://github.com/markpoon/predigestation.git
```

```bash
cd predigestation
```

```bash
scripts/presto
```

```bash
scripts/behold incident report
```

```bash
scripts/go next
```

```bash
scripts/presto
```

The first `presto` opens the stage and the last one closes it. `incident-report.html` is a sample with invented data.

## Commands

| Command | What it does |
|---|---|
| `presto` | Toggle the stage. On: opens a new Safari window and keeps the Mac awake (up to 3 hours). Off: speaks a sign-off and closes the stage's pages. |
| `abra` | Same as `presto`, and says "cadabra" when it loads the stage. |
| `behold <words or path>` | Finds a report in `~/Downloads` (or `*report*.html` in the scripts folder), turns the stage on if needed, opens the report there, frames the first chart and speaks its headline. |
| `go next\|back\|first\|last\|3\|-2\|<words>` | Moves to another chart. |
| `speak "<line>"` | Says a line, flashing each word on the stage. |
| `pd "<headline>" "c=bar&s=Cups~5,3&x=Latte,Mocha"` | Draws a live `bar`, `line` or `big` chart from data and says the headline. |
| `present <report.html> [seconds]` | Turns the stage on if needed and steps through every chart on its own. |
| `tidy` | Closes extra toolkit pages in the stage window and clears scratch files. |
| `python3 gen_report.py` | Rebuilds the sample report. |

## Safety rules

- Commands act **only on a stage window** the toolkit created, remembered by its ID.
- If the stage is off, closed, or showing a page the toolkit did not open, `behold` and `present` open a new stage (once they have found something to show) and the other commands are **voice only**.
- Closing only touches toolkit pages inside the stage window. Your own tabs are left alone.
- `behold` opens a document only if it matches **more than half** of the meaningful words you asked for. Otherwise it says `no document found`.

## Report format

Each chart is `<figure data-say="Headline to speak">` containing an inline SVG, coloured by class names so it can be re-themed. Raw data goes in `<script type="application/json" id="report-data">`. `gen_report.py` is a working example.

## Day and night theme

The stage is light from 07:00 to 19:00 by the computer's clock and dark otherwise. No location is used. To change the hours, edit `isDay` in `stage.html`, `stage2.html` and `present`.

## Files written while running

`runs.jsonl` (a log of actions, including spoken lines and report names), `voice.json` (speech timing) and a few dot-files. All are in `.gitignore`.

## Tests

Offline tests use a fake Safari and make no sound:

```bash
python3 -m unittest discover -s tests -p 'test_offline.py'
```

The full suite also drives real Safari, using throwaway windows. It takes over the screen for about two minutes, and the display must be awake:

```bash
PD_LIVE=1 python3 -m unittest discover -s tests
```

## Not built yet

Spoken commands, highlighting ("notice / highlight / flag"), spotlight zoom, and lowering music volume while speaking. Windows is not supported.

## License

[MIT](LICENSE)
