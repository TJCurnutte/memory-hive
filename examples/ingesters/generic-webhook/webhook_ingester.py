#!/usr/bin/env python3
"""
Memory Hive — generic webhook ingester.

Minimal HTTP endpoint that accepts POST requests and appends each request
body to `hive/raw/<source>/<topic>.md`. Use this to capture context from
any system that can send an HTTP request (Zapier, Linear, GitHub
webhooks, internal tools, cron jobs, etc.).

No auth by default. If you expose this to the internet, put it behind
a reverse proxy with auth, or run it on localhost and forward from a
trusted gateway.

Usage:
    export MEMORY_HIVE_DIR=~/.memory-hive        # optional
    export WEBHOOK_PORT=8787                      # optional, default 8787
    export WEBHOOK_TOKEN=<optional-shared-secret> # optional; if set, required as ?token=... on requests

    python3 webhook_ingester.py

POST format (JSON):
    {
        "source": "linear",               # required — becomes hive/raw/<source>/
        "topic": "team-alpha",            # required — file name
        "author": "alice",                # optional, default "webhook"
        "timestamp": "2026-04-23T14:32Z", # optional, default now()
        "message": "PR #42 merged",       # required
        "attachments": ["url-or-filename"] # optional
    }

No third-party dependencies. Uses stdlib only.
"""

import json
import os
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


HIVE_DIR = Path(os.path.expanduser(os.environ.get("MEMORY_HIVE_DIR", "~/.memory-hive")))
PORT = int(os.environ.get("WEBHOOK_PORT", "8787"))
TOKEN = os.environ.get("WEBHOOK_TOKEN", "").strip()
RAW_ROOT = HIVE_DIR / "hive" / "raw"


# --- sanitization --------------------------------------------------------

def _safe(name: str) -> str:
    """Allow only a-z, 0-9, dash. Strip the rest."""
    out = "".join(c if (c.isalnum() or c == "-") else "-" for c in name.lower())
    out = "-".join(p for p in out.split("-") if p)  # collapse dashes
    return out[:32] or "unknown"


# --- append --------------------------------------------------------------

def append_entry(source: str, topic: str, author: str, ts: str, msg: str, attachments: list) -> Path:
    source = _safe(source)
    topic = _safe(topic)
    target = RAW_ROOT / source / f"{topic}.md"
    target.parent.mkdir(parents=True, exist_ok=True)

    attach_line = ", ".join(str(a) for a in attachments) if attachments else "(none)"

    entry = (
        f"## [{ts}] #{topic} — @{author}\n"
        f"**Message:** {msg}\n"
        f"**Attachments:** {attach_line}\n\n"
    )

    first_write = not target.exists() or target.stat().st_size == 0
    with target.open("a") as f:
        if first_write:
            f.write(f"# Webhook raw capture — {source}/{topic}\n\n")
        f.write(entry)
    return target


# --- handler -------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    def _respond(self, code: int, body: dict) -> None:
        payload = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _check_token(self) -> bool:
        if not TOKEN:
            return True
        q = parse_qs(urlparse(self.path).query)
        return q.get("token", [""])[0] == TOKEN

    def do_POST(self) -> None:  # noqa: N802
        if not self._check_token():
            self._respond(401, {"error": "missing or invalid token"})
            return

        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length else b""

        try:
            payload = json.loads(raw or b"{}")
        except json.JSONDecodeError as e:
            self._respond(400, {"error": f"invalid json: {e}"})
            return

        source = payload.get("source")
        topic = payload.get("topic")
        message = payload.get("message")
        if not source or not topic or not message:
            self._respond(400, {"error": "source, topic, and message are required"})
            return

        author = payload.get("author", "webhook")
        ts = payload.get("timestamp") or datetime.now(timezone.utc).isoformat(timespec="seconds")
        attachments = payload.get("attachments") or []

        try:
            target = append_entry(source, topic, author, ts, message, attachments)
        except OSError as e:
            self._respond(500, {"error": f"write failed: {e}"})
            return

        self._respond(200, {"ok": True, "wrote": str(target.relative_to(HIVE_DIR))})

    def do_GET(self) -> None:  # noqa: N802
        self._respond(200, {"ok": True, "hint": "POST JSON to this endpoint"})

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("[webhook] " + (fmt % args) + "\n")


def main() -> None:
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    sys.stderr.write(f"[webhook] listening on http://127.0.0.1:{PORT}  writing to {RAW_ROOT}\n")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        sys.stderr.write("[webhook] shutting down\n")


if __name__ == "__main__":
    main()
