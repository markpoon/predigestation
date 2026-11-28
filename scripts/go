#!/bin/bash
[ -n "$PD_QUIET" ] && say(){ :; }
# go: move the open report to a chart and speak its headline.
#   go next | back | first | last | -2 | +1 | 3 (chart number) | <words, e.g. pie, lattes, revenue>
D="$(cd "$(dirname "$0")" && pwd)"; A="$*"
. "$D/stage.sh"
case "$A" in
  next|forward) E="pdrel(1)";;
  back|previous|prev) E="pdrel(-1)";;
  first|start) E="pdto(0)";;
  last|end) E="pdto(F.length-1)";;
  [+-][0-9]|[+-][0-9][0-9]) E="pdrel($A)";;
  [0-9]|[0-9][0-9]) E="pdto($A-1)";;
  *) Q=$(printf '%s' "$A" | tr -cd 'A-Za-z0-9 .$%-'); E="pdfind('$Q')";;
esac
killall say >/dev/null 2>&1
WID=$(stage_id)
if [ -z "$WID" ]; then   # stage off or gone: voice only, by chart number or step
  [ -f "$D/.last" ] || { echo "nothing open: behold a document first"; exit 1; }
  LDOC=$(cut -d'|' -f1 "$D/.last"); I=$(cut -d'|' -f2 "$D/.last"); C=$(headlines "$LDOC" | wc -l | tr -d ' ')
  [ "$C" -gt 0 ] || { echo "no charts in $(basename "$LDOC")"; exit 1; }
  case "$A" in
    next|forward) I=$((I+1));;
    back|previous|prev) I=$((I-1));;
    first|start) I=0;;
    last|end) I=$((C-1));;
    [+-][0-9]|[+-][0-9][0-9]) I=$((I$A));;
    [0-9]|[0-9][0-9]) I=$((10#$A-1));;
    *) echo "stage is off: ask by number or step, or say Presto"; exit 1;;
  esac
  [ $I -lt 0 ] && I=0; [ $I -ge $C ] && I=$((C-1))
  S=$(headlines "$LDOC" | sed -n "$((I+1))p")
  echo "$LDOC|$I" > "$D/.last"
  [ -n "$S" ] && ( say -v Daniel -r 185 "$S" >/dev/null 2>&1 & )
  echo "slide $((I+1)), voice only: $S"
  exit 0
fi
# Resume: if the stage (or anything else) is in front, reopen the last document at the last chart first.
LAST="$D/.last"
if [ -f "$LAST" ]; then
  LDOC=$(cut -d'|' -f1 "$LAST"); LIDX=$(cut -d'|' -f2 "$LAST")
  FRONT=$(osascript -e "tell application \"Safari\" to return URL of current tab of window id $WID" 2>/dev/null | sed -E 's/[?#].*$//' | perl -pe 's/%([0-9A-Fa-f]{2})/chr(hex($1))/ge')
  case "$FRONT" in */"$(basename "$LDOC")") ;; *)
    PD_QUIET=1 "$D/behold" "$LDOC" >/dev/null
    osascript -e "tell application \"Safari\" to do JavaScript \"cur=-1;pdto($LIDX)\" in current tab of window id $WID" >/dev/null 2>&1;;
  esac
fi
R=$(osascript - "$(cat "$D/nav.js")" "$E" "$WID" <<'EOS'
on run argv
  tell application "Safari"
    set t to current tab of window id ((item 3 of argv) as integer)
    if (do JavaScript "typeof pdto" in t) is not "function" then do JavaScript (item 1 of argv) in t
    return do JavaScript "(function(){var i=" & (item 2 of argv) & ";return i<0?'0|':(i+1)+'|'+(F[i].getAttribute('data-say')||'');})()" in t
  end tell
end run
EOS
)
N="${R%%|*}"; S="${R#*|}"
if [ "${N:-0}" -gt 0 ] 2>/dev/null; then
  DOCP=$(osascript -e "tell application \"Safari\" to return URL of current tab of window id $WID" 2>/dev/null | sed -E 's#^file://##; s#[?#].*$##' | perl -pe 's/%([0-9A-Fa-f]{2})/chr(hex($1))/ge')
  [ -f "$DOCP" ] && echo "$DOCP|$((N-1))" > "$D/.last"
fi
[ -n "$S" ] && ( say -v Daniel -r 185 "$S" >/dev/null 2>&1 & )
echo "$(date '+%F %T') {\"mode\":\"go\",\"cmd\":\"$A\",\"slide\":${N:-0}}" >> "$D/runs.jsonl"
# Automatic calibration after every move (background, adds no wait): framing numbers, then the voice model.
( sleep 0.65
  M=$(osascript -e 'tell application "Safari" to do JavaScript "pdmeasure()" in current tab of window id '"$WID"  2>/dev/null)
  echo "$(date '+%F %T') {\"mode\":\"frame-cal\",\"m\":${M:-null}}" >> "$D/runs.jsonl"
  if [ -n "$S" ]; then say -v Daniel -r 185 -o /tmp/pd-cal2.aiff "$S" && A=$(afinfo /tmp/pd-cal2.aiff | awk '/estimated duration/{print $3}') \
    && echo "$(date '+%F %T') $(perl "$D/voice.pl" cal "$S" "$A")" >> "$D/runs.jsonl"; fi ) >/dev/null 2>&1 &
echo "slide $N: $S"
"$D/tidy" >/dev/null 2>&1 &
