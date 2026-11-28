# predigestation benchmarks

## Voice timing, 2026-11-28

How close `scripts/voice.pl est` comes to the real length of a spoken line.

**Method.** Lines were rendered silently with `say -v Daniel -r 185 -o <file>` and measured with `afinfo`. Ten training lines updated the model with `voice.pl cal`; six other lines were scored before and after. One run, one Mac. Error is expected minus actual, so a positive number means the voice finished early.

**Result.** Training did not improve the score.

| | Per-letter time `k` | Mean absolute error | Mean error |
|---|---|---|---|
| Before | 0.04251 | 0.25 s | +0.24 s |
| After | 0.04262 | 0.25 s | +0.25 s |

### Test lines

| Line | Actual (s) | Expected before (s) | Expected after (s) |
|---|---|---|---|
| All done. | 0.58 | 0.69 | 0.69 |
| Here is the next chart. | 1.42 | 1.41 | 1.41 |
| Costs fell for the third quarter in a row. | 2.22 | 2.39 | 2.39 |
| Great question! Let me bring up the numbers for you. | 3.00 | 3.26 | 3.27 |
| The team fixed the problem in under an hour, and no data was lost. | 3.49 | 3.83 | 3.84 |
| That is the end of the report. Thank you for listening, and please ask me anything you like. | 4.91 | 5.51 | 5.52 |

### Training lines

Each error was measured before the model learned from that line.

| Line | Error (ms) |
|---|---|
| Got it. | +42 |
| We sure can! | -71 |
| Sales rose twelve percent this month. | -181 |
| Yes, the stage is on and ready. | +102 |
| Most outages started right after a deploy. | -231 |
| Say the word, and I will walk you through a report, one chart at a time. | +438 |
| Good news! Everything is saved, clean, and matches the copy online. | -297 |
| Two things need your attention before Friday: the budget, and the schedule. | +250 |
| Hello everyone. Today we will look at what happened, why it happened, and what we are doing about it. | +350 |
| Response times improved across every region, although the west still trails the others by a small margin. | -142 |

Longer lines miss by more, in either direction. All the longer test lines finished early, but the training lines did not all lean that way.

### Also tried

Refitting all four timing numbers to the training lines by least squares (fixed 0.32 s, per letter 0.0432 s, sentence pause 0.64 s, comma pause 0.08 s) scored worse on the test lines: mean absolute error 0.39 s, worst 0.81 s. Not kept.

### Not measured

- Chart framing.
- Timing of individual words within a line.
- The delay if `speak` measured each line before showing it.
