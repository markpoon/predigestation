# stage.sh: sourced by every command (set D first). The stage is one Safari window,
# remembered by ID when Presto creates it. Nothing else in Safari is ever touched.
STAGE_FILE="$D/.stage_window"

# Prints the stage window's ID only if that window still exists, is on screen, and its
# front tab is a page this toolkit put there. Prints nothing otherwise: voice only.
stage_id(){
  [ -f "$STAGE_FILE" ] || return 0
  osascript - "$(cat "$STAGE_FILE")" "file://$D/" <<'EOS' 2>/dev/null
on run argv
  if application "Safari" is not running then return ""
  tell application "Safari"
    set wid to (item 1 of argv) as integer
    if not (exists window id wid) then return ""
    if not (visible of window id wid) then return ""
    set u to URL of current tab of window id wid
    if u starts with (item 2 of argv) then return wid
    if u starts with "file://" and u contains "?pdk=" then return wid
  end tell
  return ""
end run
EOS
}

# Closes toolkit pages in the stage window only. Second argument "keep" spares its front tab.
# Tabs you opened yourself are never closed. Prints how many were closed.
stage_close(){
  [ -f "$STAGE_FILE" ] || { echo 0; return 0; }
  osascript - "$(cat "$STAGE_FILE")" "file://$D/" "$1" <<'EOS' 2>/dev/null
on run argv
  if application "Safari" is not running then return 0
  set closed to 0
  tell application "Safari"
    set wid to (item 1 of argv) as integer
    if not (exists window id wid) then return 0
    set kept to 0
    if (item 3 of argv) is "keep" then set kept to index of current tab of window id wid
    repeat with i from (count of tabs of window id wid) to 1 by -1
      try
        set u to URL of tab i of window id wid
        if i is not kept and (u starts with (item 2 of argv) or (u starts with "file://" and u contains "?pdk=")) then
          close tab i of window id wid
          set closed to closed + 1
        end if
      end try
    end repeat
  end tell
  return closed
end run
EOS
}

# Turns the stage on if there is no usable one, and prints its window ID (nothing if it could not open).
# Never toggles an open stage off.
stage_ensure(){
  local w; w=$(stage_id)
  if [ -z "$w" ]; then
    # The stage was marked on but its window is gone: clear that, so presto opens rather than closes.
    [ -f "$D/.caffeinate.pid" ] && kill "$(cat "$D/.caffeinate.pid")" 2>/dev/null
    rm -f "$D/.presto_on" "$D/.caffeinate.pid"
    "$D/presto" >/dev/null || return 0
    # A new window can take a moment to report its page.
    for _ in 1 2 3 4 5 6 7 8 9 10; do w=$(stage_id); [ -n "$w" ] && break; sleep 0.2; done
  fi
  echo "$w"
}

# The spoken headlines of a report, one per line.
headlines(){
  perl -0ne 'while(/<figure[^>]*?\sdata-say="([^"]*)"/g){my $s=$1;
    $s=~s/&#x27;|&#39;/\x27/g;$s=~s/&quot;/"/g;$s=~s/&lt;/</g;$s=~s/&gt;/>/g;$s=~s/&amp;/&/g;print "$s\n"}' "$1"
}
