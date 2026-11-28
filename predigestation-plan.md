# predigestation: plan (v0.2, Nov 26 2026, reviewed by Skeptic)

Turn data into a show for people who aren't technical, live in a meeting, by voice.
Built and rehearsed on a Mac on Nov 25 to 26, 2026. Status: working prototype; items under "Next" are not built yet.
Updated Nov 26: code now lives only in `~/Code/predigestation`; the wrong-tab, wrong-document and tab-closing risks are fixed and tested.

Updated Nov 27: packaged as a Claude Code plugin; `behold` and `present` start the stage themselves; `abra`, `reply` and `interject` added; stage words are in capitals and lead the voice by 0.15 s. See the [README](README.md).

## 1. Principles

- **Speed first.** Latency is the worst thing. Sacrifice picture quality before speed.
- **Main thread is the presentation.** Building, calibrating, tidying and fetching run in the background so Claude can keep talking.
- **Speak first, then show data.** Spoken words also appear on screen, word by word.
- **Send data, not pictures.** Drawing code lives on the Mac; each move sends a few hundred characters at most.
- **Measure everything.** Every action is logged to `runs.jsonl`; check by numbers every time, by screenshot only when numbers look off or in rehearsal.
- **Never strobe or flash.** Slow, gentle motion only.

## 2. Controls (spoken)

| Say | What happens | Measured (Mac side only) |
|---|---|---|
| **Presto** | Toggle. On: one stage to the front, full screen, Mac kept awake, silent. Off: a sign-off from context ("That was the coffee report. Good night."), every stage closed, Mac allowed to sleep, focus back to Claude | On 0.45 to 0.9 s |
| **Behold** + document | Finds it (in Downloads; must match more than half the words asked for), opens the document itself in Safari, frames the first chart, speaks its headline | 0.3 to 0.45 s |
| (with the stage off or closed) | `behold` and `present` open a stage; `go`, `speak` and `pd` are voice only | |
| **Abra** | Presto that says "cadabra"; in Claude Code, replies are then spoken | |
| next, back, first, last, a number, "2 slides ago", or a description ("the one about how people paid") | Moves to that chart; remembers the place across stage detours | about 0.2 s |
| **notice / highlight / flag** + a thing, in a normal sentence (not in the code yet) | Outlines that bar or slice in gold, dims the rest, speaks a line | about 0.7 to 1.1 s |
| Spotlight (trigger word still to choose) | Zooms into one part of a chart | |
| A question about the document's numbers | Answers from the data stored inside the report, shown big on the stage | about 1 s plus speech |
| Anything outside the document | Ad hoc fetch (section 5), then back to the saved place | 5 to 60 s |

Timings are Mac side only: from the command starting to the screen changing. They leave out speech recognition and Claude's own turn, which is currently several seconds per reply and the biggest delay (see Next 1 and 2).

## 3. How it looks

- Voice: macOS Daniel, 185 words per minute, short pauses. Planned (not in the code yet): Music ducks to 15% while speaking and is restored, even if speech fails.
- Type: Helvetica Neue bold. Flashed words are in capitals without punctuation (`speak`), and appear 0.15 s ahead of the voice.
- Background, night (19:00 to 07:00, by the laptop's own clock): a dark gradient glowing from the top left, more black than grey.
- Background, day: a light gradient glowing from the top right, with dark text.
- When a reply offers a list, the spoken line ends by asking about the first item. Speech only, never on screen or in reports.
- One stage window at a time. The word flash (`stage.html`), live charts (`stage2.html`) and the presented document all load in that same single tab; anything extra is closed after every action.

## 4. Presenting a document: what was learned

- Use the document itself, untouched on disk. Present it with a camera: pan and magnify the view to fill about 94% of the screen with the chart, capped at 4x, short glides (0.25 to 0.5 s), first move instant.
- Page zoom (Safari's own zoom, or the equivalent) reflows responsive pages, so small charts do not grow. Screenshots proved this; magnifying the view works.
- Plain scrolling is fastest (about 20 ms) but leaves small charts small.
- Reports built for this (pd-report format): every chart is `<figure data-say="headline">`, coloured by class names, raw data in a JSON block, so headlines can be spoken and questions answered instantly.

## 5. Ad hoc fetch (agent plan)

1. Acknowledge on the stage within 2 s ("Fetching that now").
2. Simple asks (one or two numbers): Claude fetches directly, several lookups at once (about 5 to 15 s).
3. Bigger asks (several sources): several Scout helpers in parallel, one per source, each returning only a tiny table (labels, numbers, source, as-of date) within a time limit.
4. Show partial results first; add the rest as it lands.
5. Quick sanity check (dates match, numbers plausible); a full Skeptic review runs afterwards, never live.
6. Return to the saved place in the document.

Cost notes: a helper takes about 7 s and 61,000 tokens just to start, so helpers only for big jobs, never for quick replies.

## 6. Calibration (automatic, background, no added wait)

- Voice and words: after every spoken line, the real speech length is measured silently and the timing model updated. Errors fell from up to 0.63 s to about 0.12 s on average.
- Framing: after every move, chart fill and centring are measured (target 94%, centred). Below 85% or off-centre triggers a screenshot check.

## 7. Skills and agents

Skills: **pd-voice** (speak and flash), **pd-behold** (open and frame), **pd-navigate** (moves and descriptions), **pd-point** (notice / highlight / flag), **pd-spotlight**, **pd-ask** (answer from the report's data), **pd-adhoc** (fetch and return), **pd-calibrate** (background checks), **pd-report** (build portable reports).

Dropped: side by side, show-ready check, recap, behold-anything, graceful recovery (anything that would need recovery goes ad hoc).

Agents, background only: Scout helpers for ad hoc fetches; Skeptic after the fact for anything fetched live.

## 8. Files (`~/Code/predigestation/`)

In `scripts/`: `presto`, `abra`, `behold`, `go`, `speak`, `reply`, `interject`, `tidy`, `present`, `stage.sh` (stage-window guard), `voice.pl` (timing model), `nav.js` (camera and navigation), `stage.html` (word flash), `stage2.html` (live charts and big numbers), `pd` (live chart command), `runs.jsonl` (log), `gen_report.py` (report builder). Sample: `scripts/incident-report.html`. Slash commands are in `commands/`, tests in `tests/`.

## 9. Known traps (from rehearsal)

- AppleScript reserved words break scripts: st, before, after, line, it, left, voices.
- osascript calls over about 20 s fail silently: keep every action short.
- Phrases starting with a number ("8 am rush") were read as slide numbers: fixed.
- Talking to a page before the new one has loaded: always wait for the right page.
- Measuring under page zoom double-counted the zoom: trust screenshots over that math.
- Not yet fixed: `presto` stretches a window rather than using true full screen, and toggles off even if its window was already closed.
- Not yet fixed: word timing is estimated per line, so words can trail the voice on long lines.
- Keystrokes and menu clicks are blocked (no Accessibility permission for osascript).
- Fixed: commands used to act on Safari's front tab and could land on your own tabs. They now act only on the stage window (`stage.sh`).
- Asking Finder for the screen size stalls while the display is asleep: only Presto asks, once, with a 5 s limit.
- Closed Safari windows linger as invisible windows with no tabs: check `visible`, not just existence.

## 10. Next

1. **Mac voice commands:** Voice Control plus Shortcuts run `go`, `behold` and `presto` directly; simple commands in under 0.5 s with no model involved. Biggest speed win.
2. **Meeting session kit:** a short fresh session with only the plugin loaded, and a fixed phrase table, so Claude acts rather than reasons. Optionally a faster model chosen by Mark in the model picker.
3. **Safety fix: done (Nov 26).** Presto saves the stage window's ID; every command acts only on that window. With the stage off or missing, voice only (changed Nov 27 for `behold` and `present`, which open a stage).
4. **Spotlight trigger word.**
5. **Plugin:** slash commands done (Nov 27). The skills in section 7 are not written yet.
6. Later: Windows (David or Mark voices, PowerShell).
