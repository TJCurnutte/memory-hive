#!/usr/bin/env python3
"""Memory Hive MCP server — stdio JSON-RPC, stdlib only.

Exposes the hive to any MCP client (Claude Desktop/Code, Cursor, Goose,
Copilot, ...) the way `memory-hive guide` exposes it to any shell: the
client gets native memory tools with no boot block at all.

Tools mirror the ask/create split popularized by ambient-memory products:
  ask_hive     ranked, cited retrieval (HyperRecall; falls back to query)
  hive_log     task-end ritual step 1 — dated line in the agent's silo log
  hive_learn   lint-valid raw learning in the agent's shared-pool subdir
  hive_capture ambient workstream event into hive/raw/<source>/
  hive_guide   the platform-neutral operating guide (optionally one topic)

Protocol: MCP over stdio, newline-delimited JSON-RPC 2.0. No third-party
imports — the same dependency envelope as HyperRecall (python3 only).
"""

import json
import os
import subprocess
import sys

SERVER_VERSION = "1.0"
FALLBACK_PROTOCOL = "2024-11-05"


def install_dir():
    env = os.environ.get("MEMORY_HIVE_DIR")
    if env and os.path.isfile(os.path.join(env, "memory-hive")):
        return env
    here = os.path.dirname(os.path.abspath(__file__))
    if os.path.isfile(os.path.join(here, "memory-hive")):
        return here
    return os.path.expanduser("~/.memory-hive")


INSTALL_DIR = install_dir()
CLI = os.path.join(INSTALL_DIR, "memory-hive")


def run_cli(args, stdin_text=None):
    """Run a memory-hive verb; return (ok, combined_output)."""
    try:
        proc = subprocess.run(
            ["sh", CLI] + args,
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ, "MEMORY_HIVE_DIR": INSTALL_DIR},
        )
    except Exception as exc:  # missing CLI, timeout, ...
        return False, "memory-hive CLI failed to run: %s" % exc
    out = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
    return proc.returncode == 0, out.strip() or "(no output)"


TOOLS = [
    {
        "name": "ask_hive",
        "description": (
            "Ask Memory Hive a question and get ranked, cited context from "
            "the shared hive and agent silos (decisions, learnings, logs, "
            "preferences from past sessions). Use when the user references "
            "prior work, 'last time', lessons, or preferences."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Natural-language question or search terms.",
                },
            },
            "required": ["question"],
        },
    },
    {
        "name": "hive_log",
        "description": (
            "Memory Hive task-end ritual step 1: append a dated one-line "
            "summary of what was just done to the agent's silo log. Call at "
            "the end of any non-trivial task."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "what": {
                    "type": "string",
                    "description": "What was done, one line.",
                },
                "agent": {
                    "type": "string",
                    "description": "Agent id (default: main).",
                },
            },
            "required": ["what"],
        },
    },
    {
        "name": "hive_learn",
        "description": (
            "Write a reusable lesson to Memory Hive's shared pool as a "
            "lint-valid raw learning. Use when a lesson generalizes beyond "
            "the current agent — like a smart checkpoint other agents can "
            "build on."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "rule": {
                    "type": "string",
                    "description": "The generalizable rule, stated imperatively.",
                },
                "context": {
                    "type": "string",
                    "description": "One line: where this came up.",
                },
                "kind": {
                    "type": "string",
                    "enum": ["pattern", "win", "mistake", "insight"],
                    "description": "Kind of lesson (default: pattern).",
                },
                "confidence": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Confidence (default: low for new observations).",
                },
                "body": {
                    "type": "string",
                    "description": "Optional markdown body (what happened / rule).",
                },
                "agent": {
                    "type": "string",
                    "description": "Agent id (default: main).",
                },
            },
            "required": ["rule", "context"],
        },
    },
    {
        "name": "hive_capture",
        "description": (
            "Capture an ambient workstream event (timestamped) into Memory "
            "Hive's raw stream — meetings, decisions in chat, things worth "
            "remembering that aren't a finished lesson yet."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "event": {
                    "type": "string",
                    "description": "The event text, one line.",
                },
                "source": {
                    "type": "string",
                    "description": "Stream name under hive/raw/ (default: sessions).",
                },
                "agent": {
                    "type": "string",
                    "description": "Agent id tag (default: main).",
                },
            },
            "required": ["event"],
        },
    },
    {
        "name": "hive_guide",
        "description": (
            "Print Memory Hive's operating guide (paths, hydrate/retrieve/"
            "write-back workflows, lane rules, curation). Optional topic: "
            "paths|id|hydrate|retrieve|write|lanes|curate|health."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Optional single section to print.",
                },
            },
        },
    },
]


def call_tool(name, args):
    if name == "ask_hive":
        q = args.get("question")
        if not q:
            return False, "missing required parameter: question"
        ok, out = run_cli(["recall", q])
        if not ok:
            ok, out = run_cli(["query", q])
            if ok:
                out = "[fallback: query]\n" + out
        return ok, out
    if name == "hive_log":
        what = args.get("what")
        if not what:
            return False, "missing required parameter: what"
        cmd = ["log", what]
        if args.get("agent"):
            cmd += ["--agent", args["agent"]]
        return run_cli(cmd)
    if name == "hive_learn":
        rule = args.get("rule")
        context = args.get("context")
        if not rule:
            return False, "missing required parameter: rule"
        if not context:
            return False, "missing required parameter: context"
        cmd = ["learn", rule, "--context", context]
        if args.get("kind"):
            cmd += ["--kind", args["kind"]]
        if args.get("confidence"):
            cmd += ["--confidence", args["confidence"]]
        if args.get("agent"):
            cmd += ["--agent", args["agent"]]
        if args.get("body"):
            cmd += ["--body", "-"]
            return run_cli(cmd, stdin_text=args["body"])
        return run_cli(cmd)
    if name == "hive_capture":
        event = args.get("event")
        if not event:
            return False, "missing required parameter: event"
        cmd = ["capture", event]
        if args.get("source"):
            cmd += ["--source", args["source"]]
        if args.get("agent"):
            cmd += ["--agent", args["agent"]]
        return run_cli(cmd)
    if name == "hive_guide":
        cmd = ["guide"]
        if args.get("topic"):
            cmd.append(args["topic"])
        return run_cli(cmd)
    return False, "unknown tool: %s" % name


HIVE_DIR = os.path.join(INSTALL_DIR, "hive")


def list_resources():
    """Hive canon as MCP resources: index, rendered guide, knowledge and
    distilled learnings. Scanned fresh per call so curator promotions show
    up without restarting the server."""
    res = [
        {
            "uri": "hive://index",
            "name": "Hive index",
            "description": "Boot entrypoint and global hive state.",
            "mimeType": "text/markdown",
        },
        {
            "uri": "hive://guide",
            "name": "Operating guide",
            "description": "How agents hydrate, retrieve, write back, and curate.",
            "mimeType": "text/markdown",
        },
    ]
    for sub, prefix in (("knowledge", "hive://knowledge/"),
                        ("learnings/distilled", "hive://distilled/")):
        d = os.path.join(HIVE_DIR, sub)
        try:
            names = sorted(os.listdir(d))
        except Exception:
            continue
        for n in names:
            if not n.endswith(".md"):
                continue
            res.append({
                "uri": prefix + n,
                "name": "%s/%s" % (sub, n),
                "description": "Curated shared hive content.",
                "mimeType": "text/markdown",
            })
    return res


def read_resource(uri):
    """Resolve a registered uri to text. Only uris produced by
    list_resources are readable — no path traversal surface."""
    if uri == "hive://index":
        path = os.path.join(HIVE_DIR, "index.md")
    elif uri == "hive://guide":
        ok, out = run_cli(["guide"])
        if not ok:
            raise ValueError("guide unavailable: %s" % out)
        return out
    elif uri.startswith("hive://knowledge/"):
        name = os.path.basename(uri[len("hive://knowledge/"):])
        path = os.path.join(HIVE_DIR, "knowledge", name)
        if not os.path.abspath(path).startswith(os.path.abspath(HIVE_DIR)):
            raise ValueError("invalid resource path")
    elif uri.startswith("hive://distilled/"):
        name = os.path.basename(uri[len("hive://distilled/"):])
        path = os.path.join(HIVE_DIR, "learnings", "distilled", name)
        if not os.path.abspath(path).startswith(os.path.abspath(HIVE_DIR)):
            raise ValueError("invalid resource path")
    else:
        raise ValueError("unknown resource: %s" % uri)
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def reply(msg_id, result=None, error=None):
    out = {"jsonrpc": "2.0", "id": msg_id}
    if error is not None:
        out["error"] = error
    else:
        out["result"] = result
    sys.stdout.write(json.dumps(out) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            sys.stdout.write(json.dumps({
                "jsonrpc": "2.0", "id": None,
                "error": {"code": -32700, "message": "Parse error"},
            }) + "\n")
            sys.stdout.flush()
            continue
        msg_id = msg.get("id")
        method = msg.get("method", "")
        params = msg.get("params") or {}

        if msg_id is None:
            continue  # notification — nothing to answer

        try:
            if method == "initialize":
                proto = params.get("protocolVersion") or FALLBACK_PROTOCOL
                reply(msg_id, {
                    "protocolVersion": proto,
                    "capabilities": {"tools": {}, "resources": {}},
                    "serverInfo": {
                        "name": "memory-hive",
                        "version": SERVER_VERSION,
                    },
                })
            elif method == "ping":
                reply(msg_id, {})
            elif method == "tools/list":
                reply(msg_id, {"tools": TOOLS})
            elif method == "resources/list":
                reply(msg_id, {"resources": list_resources()})
            elif method == "resources/read":
                uri = str(params.get("uri") or "")
                try:
                    text = read_resource(uri)
                    reply(msg_id, {"contents": [{
                        "uri": uri,
                        "mimeType": "text/markdown",
                        "text": text,
                    }]})
                except Exception as exc:
                    reply(msg_id, error={
                        "code": -32602,
                        "message": str(exc),
                    })
            elif method == "tools/call":
                name = params.get("name", "")
                args = params.get("arguments") or {}
                ok, out = call_tool(name, args)
                reply(msg_id, {
                    "content": [{"type": "text", "text": out}],
                    "isError": not ok,
                })
            else:
                reply(msg_id, error={
                    "code": -32601,
                    "message": "method not found: %s" % method,
                })
        except Exception as exc:
            reply(msg_id, error={"code": -32603, "message": str(exc)})


if __name__ == "__main__":
    main()
