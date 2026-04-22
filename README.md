# 🧠 Memory Hive

**A shared, continuously learning memory system for multi-agent AI architectures.**

Memory Hive is the end-all-be-all of multi-agent memory infrastructure. It gives any multi-agent system a central, shared brain that every agent reads from and writes to — creating a collective intelligence that compounds over time.

---

## The Problem

Most multi-agent systems keep agent memory siloed. Each agent finishes a task and forgets. The next agent starts from scratch. Nothing compounds. Nothing learns.

## The Solution

**One shared hive.** Every agent reads from it on boot. Every agent contributes to it after completing work. A curator (typically the Chief of Staff / orchestrator agent) synthesizes contributions and maintains the knowledge base.

The result: a system that learns from every task it completes, gets smarter over time, and can reference past work when tackling new challenges.

---

## Core Architecture

```
~/.openclaw/hive/
├── HIVE_ARCHITECTURE.md    ← Full design document
├── index.md                ← Entry point — all agents read this first
├── registry/
│   ├── AGENTS.md           ← Agent roster (who exists, what they do)
│   └── SKILLS_CATALOG.md   ← Skills matrix
├── knowledge/
│   ├── TRAVIS.md          ← Primary human context
│   ├── SOUL.md            ← System behavior guide
│   └── DOMAINS.md         ← Area expertise definitions
├── learnings/
│   ├── raw/               ← Agent dumps (no gatekeeping)
│   ├── distilled/        ← Curated learnings by curator
│   │   ├── patterns.md
│   │   ├── mistakes.md
│   │   ├── wins.md
│   │   └── cross-agent-insights.md
│   └── META.json          ← Learning stats and health
├── tasks/
│   ├── queue.md            ← Shared task queue
│   └── active/            ← Current working context
├── agents/
│   └── [agent-id]/         ← Each agent's personal log
└── curator/
    ├── DRAFT.md           ← Pending contributions
    ├── CONFLICTS.md       ← Contradictions to resolve
    └── DECISIONS.md       ← Curation audit trail
```

---

## Key Principles

### 1. Shared, Not Silos
All agents share one memory. When the Coder learns something, the Web Developer can find it. No per-agent black holes.

### 2. Curator System
One agent (typically the orchestrator/Chief of Staff) acts as curator. Agents contribute freely to `learnings/raw/`. The curator reviews and promotes valuable insights to `learnings/distilled/`. This keeps the system organized without creating contribution friction.

### 3. Two-Tier Learning
- **Raw learnings** — Agents dump post-task observations without friction
- **Distilled learnings** — Curator reviews and writes canonical patterns, mistakes, wins

### 4. Boot Sequence
Every agent, on every spawn:
1. Read `index.md`
2. Read `registry/AGENTS.md`
3. Read `registry/SKILLS_CATALOG.md`
4. Read `knowledge/TRAVIS.md`
5. Read `learnings/distilled/patterns.md`
6. Read `tasks/queue.md`
7. Read own log in `agents/[id]/`
8. Load active task context

### 5. Conflict Resolution
When two agents contradict each other, both go to `curator/CONFLICTS.md`. Curator investigates and resolves — logged in `DECISIONS.md`. No unilateral overwrites.

### 6. Memory Hygiene
- Raw learnings >7 days unreviewed → auto-escalate
- Active tasks >14 days old → auto-escalate
- Confidence gates prevent low-confidence info from polluting core knowledge
- 3 aligned low-confidence observations → upgrade to medium
- 3 aligned medium → upgrade to high

---

## For Developers

### Quick Start

```bash
# Clone the repo
git clone https://github.com/TJCurnutte/memory-hive.git
cd memory-hive

# Set up your hive directory
mkdir -p ~/.openclaw/hive
cp -r . ~/.openclaw/hive/

# Integrate with your agent system
# See INTEGRATION.md for framework-specific guides
```

### For OpenClaw Users

If you're using OpenClaw, the hive is already designed to drop into `~/.openclaw/hive/`. All agents in your system will automatically use the boot sequence on spawn.

### Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Key areas:
- New framework adapters
- Curation automation tools
- Memory hygiene improvements
- Documentation improvements

---

## Who Built This

[Travis Curnutte](https://github.com/TJCurnutte) — built this as the central memory system for his own multi-agent architecture. It started as internal infrastructure and got open-sourced because nothing else like it exists.

## License

MIT — use it, build on it, make it better.

---

**The hive learns. Every task. Every agent. Every time.**