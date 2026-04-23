#!/usr/bin/env python3
"""
Memory Hive — Discord ingester.

Polls one or more Discord channels via the bot API and appends new
messages to the hive's Tier 1 raw capture folder. Append-only; never
edits or deletes existing entries.

Reads config from environment variables so the same script works across
different hives and users.

Usage:
    export DISCORD_BOT_TOKEN=...                              # required
    export DISCORD_CHANNEL_IDS=1234567890,2345678901          # required, comma-separated
    export MEMORY_HIVE_DIR=~/.memory-hive                     # optional, default $HOME/.memory-hive
    export POLL_INTERVAL=15                                   # optional, default 15 (seconds)
    export MESSAGE_MAX_LEN=600                                # optional, default 600 chars per message
    export DISCORD_CHANNEL_NAMES=eng-team,standup             # optional, labels per channel (matched by index)

    python3 discord_ingester.py

Output:
    <MEMORY_HIVE_DIR>/hive/raw/discord/<channel-label>.md
    <MEMORY_HIVE_DIR>/hive/raw/discord/.state.json

No third-party dependencies. Uses stdlib only.
"""

import json
import os
import sys
import time
import traceback
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


# --- config ---------------------------------------------------------------

TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
CHANNEL_IDS = [c.strip() for c in os.environ.get("DISCORD_CHANNEL_IDS", "").split(",") if c.strip()]
CHANNEL_NAMES = [c.strip() for c in os.environ.get("DISCORD_CHANNEL_NAMES", "").split(",") if c.strip()]
HIVE_DIR = Path(os.path.expanduser(os.environ.get("MEMORY_HIVE_DIR", "~/.memory-hive")))
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "15"))
MESSAGE_MAX_LEN = int(os.environ.get("MESSAGE_MAX_LEN", "600"))
MESSAGE_MIN_LEN = int(os.environ.get("MESSAGE_MIN_LEN", "2"))

RAW_DIR = HIVE_DIR / "hive" / "raw" / "discord"
STATE_FILE = RAW_DIR / ".state.json"


def die(msg: str) -> None:
    sys.stderr.write(f"ERROR: {msg}\n")
    sys.exit(1)


def log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


# --- state ----------------------------------------------------------------

def load_state() -> dict:
    if STATE_FILE.exists():
        with STATE_FILE.open() as f:
            return json.load(f)
    return {"last_message_ids": {}}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".json.tmp")
    with tmp.open("w") as f:
        json.dump(state, f, indent=2)
    tmp.replace(STATE_FILE)


# --- channel label resolution --------------------------------------------

def label_for(index: int, channel_id: str) -> str:
    if index < len(CHANNEL_NAMES):
        return CHANNEL_NAMES[index]
    return channel_id  # fall back to raw ID if no name provided


# --- Discord API ---------------------------------------------------------

def fetch_messages(channel_id: str, limit: int = 20) -> list:
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit={limit}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bot {TOKEN}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data if isinstance(data, list) else []
    except urllib.error.HTTPError as e:
        log(f"HTTP {e.code} for channel {channel_id}: {e.reason}")
        return []
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as e:
        log(f"Error fetching channel {channel_id}: {e}")
        return []


# --- entry formatting ----------------------------------------------------

def format_entry(msg: dict, channel_label: str) -> str | None:
    content = (msg.get("content") or "").strip()
    if len(content) < MESSAGE_MIN_LEN:
        return None

    if len(content) > MESSAGE_MAX_LEN:
        content = content[:MESSAGE_MAX_LEN].rstrip() + "…"

    author = (msg.get("author") or {}).get("username", "unknown")
    ts = msg.get("timestamp", "")

    attachments = msg.get("attachments") or []
    if attachments:
        names = [a.get("filename") or a.get("url") or "attachment" for a in attachments]
        attach_line = ", ".join(names)
    else:
        attach_line = "(none)"

    return (
        f"## [{ts}] #{channel_label} — @{author}\n"
        f"**Message:** {content}\n"
        f"**Attachments:** {attach_line}\n"
    )


# --- write out -----------------------------------------------------------

def append_entries(channel_label: str, entries: list) -> None:
    if not entries:
        return
    target = RAW_DIR / f"{channel_label}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a") as f:
        if target.stat().st_size == 0:
            f.write(f"# Discord raw capture — #{channel_label}\n\n")
        f.write("\n".join(entries))
        f.write("\n")


# --- poll loop -----------------------------------------------------------

def poll_once(state: dict) -> int:
    written = 0
    for i, channel_id in enumerate(CHANNEL_IDS):
        label = label_for(i, channel_id)
        msgs = fetch_messages(channel_id)
        if not msgs:
            continue

        last_known = state["last_message_ids"].get(channel_id)
        new_entries = []
        for msg in msgs:  # Discord returns newest first
            if last_known and msg["id"] <= last_known:
                break
            entry = format_entry(msg, label)
            if entry:
                new_entries.append(entry)

        if new_entries:
            new_entries.reverse()  # append in chronological order
            append_entries(label, new_entries)
            written += len(new_entries)
            log(f"#{label}: appended {len(new_entries)} message(s)")

        state["last_message_ids"][channel_id] = msgs[0]["id"]

    if written:
        save_state(state)
    return written


def main() -> None:
    if not TOKEN:
        die("DISCORD_BOT_TOKEN is not set. export it and re-run.")
    if not CHANNEL_IDS:
        die("DISCORD_CHANNEL_IDS is not set. export a comma-separated list of channel IDs.")

    log(f"Starting — writing to {RAW_DIR}, polling every {POLL_INTERVAL}s, watching {len(CHANNEL_IDS)} channel(s)")
    state = load_state()

    once = os.environ.get("POLL_ONCE", "0") == "1"
    while True:
        try:
            poll_once(state)
        except Exception:
            log(f"FATAL: {traceback.format_exc()}")
        if once:
            break
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
