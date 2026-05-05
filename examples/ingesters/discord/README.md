# Discord ingester

Polls Discord channels via the bot API and appends new messages to
`hive/raw/discord/<channel>.md` in the Memory Hive Tier 1 format.
Append-only; never touches existing content.

## What you need

1. A Discord bot with `Read Messages` + `Read Message History` permissions
2. The bot invited to the server(s) whose channels you want to capture
3. The channel IDs you want to ingest (right-click channel → *Copy ID*
   in Discord developer mode)

## Set up

```bash
# required
export DISCORD_BOT_TOKEN=FAKE_DO_NOT_USE_DISCORD_BOT_TOKEN
export DISCORD_CHANNEL_IDS=1234567890,2345678901

# optional
export DISCORD_CHANNEL_NAMES=eng-team,standup   # labels the output files
export MEMORY_HIVE_DIR=~/.memory-hive            # default: $HOME/.memory-hive
export POLL_INTERVAL=15                          # seconds between polls
export MESSAGE_MAX_LEN=600                       # chars per captured message

python3 discord_ingester.py
```

## What it writes

```
$MEMORY_HIVE_DIR/hive/raw/discord/
├── eng-team.md       ← one file per channel (labeled from DISCORD_CHANNEL_NAMES)
├── standup.md
└── .state.json       ← last-seen message id per channel (resumable)
```

Each entry follows the raw-capture shape from
[`../../../templates/memory-entry.md`](../../../templates/memory-entry.md):

```markdown
## [2026-04-23T14:32:11+00:00] #eng-team — @alice
**Message:** Reviewed the auth PR. LGTM modulo the rate-limit case.
**Attachments:** (none)
```

## Running in the background

### macOS / Linux — launch as a background process

```bash
nohup python3 ~/.memory-hive/examples/ingesters/discord/discord_ingester.py \
  > ~/.memory-hive/logs/discord-ingester.log 2>&1 &
```

### cron — poll once per minute instead

```bash
# Set POLL_ONCE=1 and wire through cron instead of the daemon loop
* * * * * POLL_ONCE=1 DISCORD_BOT_TOKEN=... DISCORD_CHANNEL_IDS=... \
  python3 ~/.memory-hive/examples/ingesters/discord/discord_ingester.py
```

### launchd / systemd

Wrap the command in a plist or unit file the way you'd run any other
long-lived Python daemon. There's nothing Memory-Hive-specific about
the process-management story.

## Design notes

- **Append-only.** Never edits or deletes existing entries — if a
  message is deleted on Discord, it stays captured here. Agents can
  read the raw history untouched.
- **Resumable.** The `.state.json` tracks the last message ID per
  channel. Killing and restarting the script skips everything already
  captured.
- **No third-party deps.** Uses only Python stdlib (`urllib.request`,
  `json`, `pathlib`). Works on any Python 3.9+.
- **One file per channel.** Keeps file sizes manageable and lets agents
  read only the channels they care about.

## Adapting for other platforms

Copy this script, swap the fetch function, keep the rest. The pattern
is: poll / receive events → format into the Tier 1 shape → append to
`hive/raw/<source>/<topic>.md`. See
[`../generic-webhook/`](../generic-webhook/) for the simplest possible
variant (accepts HTTP POSTs instead of polling).
