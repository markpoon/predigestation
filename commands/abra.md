---
description: Same as presto, with a spoken reply. Turns the stage on and says "cadabra", or turns it off. While on, Claude speaks its replies
allowed-tools: Bash("${CLAUDE_PLUGIN_ROOT}/scripts/abra"), Bash("${CLAUDE_PLUGIN_ROOT}/scripts/reply":*)
---
Run `"${CLAUDE_PLUGIN_ROOT}/scripts/abra"` with Bash. It toggles the stage like presto does; when it turns the stage on it also says "cadabra" aloud. Report in one line whether the stage is now on or off. macOS only.

If it printed `on`: from your next reply until the stage is turned off, speak every reply aloud as well as writing it. Before you finish each reply, run `"${CLAUDE_PLUGIN_ROOT}/scripts/reply" '<reply>'` once with Bash. It keeps charts and slides on screen, and speaks even while a presentation plays unless the user has turned that off with /interject; if it prints `quiet`, just write your answer. Use a warm, social tone, the way you would talk to someone in the room. The spoken version may be shorter than the written one: give the gist and leave the detail on screen. Use plain spoken words: no Markdown, code, links or file paths (describe them instead), and no apostrophes inside the quotes. Ask any question aloud too.

If it printed `off`: stop speaking your replies.
