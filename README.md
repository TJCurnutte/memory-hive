# 🧠 Memory Hive

**🌐 Live:** [https://memoryhive.neural-forge.io](https://memoryhive.neural-forge.io)
**📦 Source:** [github.com/TJCurnutte/memory-hive](https://github.com/TJCurnutte/memory-hive)

```
                    ┌─────────────────────────────────────────┐
                    │          THE SHARED HIVE 🧠             │
                    │                                         │
                    │  ┌─────────────────────────────────┐    │
                    │  │  registry/     knowledge/       │    │
                    │  │  ├── AGENTS.md  ├── SOUL.md     │    │
                    │  │  └── SKILLS    ├── DOMAINS.md   │    │
                    │  │                             │    │
                    │  │  learnings/    tasks/         │    │
                    │  │  ├── raw/      ├── queue.md  │    │
                    │  │  ├── distilled/  └── active/ │    │
                    │  │  └── META.json               │    │
                    │  └─────────────────────────────────┘    │
                    │           ▲              ▲              │
                    │           │   curator    │              │
                    │   writes  │   reviews    │  reads       │
                    │           │              │              │
                    └───────────┼──────────────┼──────────────┘
                                │              │
              ┌─────────────────┼──────────────┼─────────────────┐
              │                 │              │                 │
    ┌─────────▼─────────┐ ┌────▼────┐ ┌───────▼────┐ ┌──────────▼────────┐
    │  🤖 Coder         │ │  🎧     │ │  🔒        │ │  📱 Social Media  │
    │  Private Silo │   │ │Vibe Coder│ │Sec-Auditor│ │  Manager          │
    │  └── log.md       │ │Silo │   │ │Silo │     │ │  Silo             │
    │  └── notes.md     │ └───┘   │ └───┘     │ └───┘                  │
    └───────────────────┘         │         │                         │
              │                    │         │                         │
    ┌─────────▼─────────┐ ┌────▼────┐ ┌───────▼────┐ ┌──────────▼────────┐
    │  🎯 SDR Alpha     │ │  ⚡ SDR │ │  🌐 Web    │ │  🔬 Research      │
    │  Silo             │ │  Beta   │ │  Dev      │ │  Analyst          │
    │                   │ │Silo     │ │Silo       │ │  Silo             │
    └───────────────────┘ └─────────┘ └───────────┘ └───────────────────┘
              │
    ┌─────────▼─────────┐ ┌────────▼────┐ ┌──────────▼─────┐
    │  📊 Data Analyst  │ │  ✍️ Content │ │  ☁️ CXaaS       │
    │  Silo             │ │  Strategist │ │  Specialist    │
    │                   │ │  Silo       │ │  Silo          │
    └───────────────────┘ └────────────┘ └─────────────────┘
```

**A shared, continuously learning memory system for multi-agent AI architectures.**

Memory Hive gives every agent two memory layers:
- **Private silo** — personal continuity for each agent
- **Shared hive** — collective intelligence that compounds

Every agent reads from the hive on boot. Every agent writes learnings after tasks. A curator synthesizes contributions. The system gets smarter with every task.

---

## The Two-Layer Architecture

### Layer 1 — Private Silos

Each agent has its own personal memory space that nobody else touches:

```
agents/[agent-id]/
├── log.md        ← Personal notes, observations, working context
├── context.md    ← Agent-specific state and preferences
└── memory.md     ← Private learnings only this agent needs
```

Silos give agents continuity. When a Coder wakes up, they remember what they were working on last week. When SDR Beta runs a campaign, they know what SDR Alpha tried before.

### Layer 2 — Shared Hive

All agents read from and contribute to the collective brain:

```
hive/
├── index.md           ← Entry point — always read first
├── registry/          ← Who's who and what they do
├── knowledge/         ← Curated truth (curator only writes)
├── learnings/         ← Raw → distilled → patterns
├── tasks/             ← Shared work queue
└── curator/           ← Curation workspace
```

The hive is the cross-pollination layer. What the Coder learns benefits the Web Developer. What SDR Alpha discovers informs SDR Beta's approach.

---

## How It Works

```
Agent spawns
    │
    ▼
┌────────────────────────────────────────────────┐
│ 1. Read hive/index.md        (current state)   │
│ 2. Read hive/registry/AGENTS.md              │
│ 3. Read hive/registry/SKILLS_CATALOG.md       │
│ 4. Read hive/knowledge/HUMAN_CONTEXT.md       │
│ 5. Read hive/learnings/distilled/patterns.md  │
│ 6. Read hive/tasks/queue.md                  │
│ 7. Read own private silo (agents/[id]/)      │
│ 8. Load active task context                   │
│ 9. Begin work                                 │
└────────────────────────────────────────────────┘
    │
    ▼
Task completes
    │
    ▼
┌────────────────────────────────────────────────┐
│ 1. Write learnings to hive/learnings/raw/      │
│ 2. Update private silo (agents/[id]/log.md)   │
│ 3. Submit summary to curator/DRAFT.md         │
│ 4. Curator reviews → promotes to distilled/   │
│ 5. Next agent boots → reads updated hive      │
└────────────────────────────────────────────────┘
    │
    ▼
Hive is smarter than before
```

---

## Core Architecture

```
~/.openclaw/hive/                    ~/.openclaw/hive/agents/[id]/
├── index.md                         ├── log.md        ← private
├── registry/                        ├── context.md    ← private
│   ├── AGENTS.md                   └── memory.md     ← private
├── knowledge/                      
│   ├── HUMAN_CONTEXT.md                    
│   ├── SOUL.md                              
│   └── DOMAINS.md                            
├── learnings/                      
│   ├── raw/[agent-id]/                        
│   ├── distilled/                              
│   │   ├── patterns.md                        
│   │   ├── mistakes.md                        
│   │   ├── wins.md                            
│   │   └── cross-agent-insights.md            
│   └── META.json                              
├── tasks/                          
│   ├── queue.md                                 
│   └── active/                                 
└── curator/                        
    ├── DRAFT.md                                 
    ├── CONFLICTS.md                            
    └── DECISIONS.md                            
```

---

## Key Principles

### 1. Double Layer — Both, Not Either
Private silos for personal continuity. Shared hive for collective intelligence. Each serves a different purpose. Agents have both.

### 2. Curator System
One agent (typically the orchestrator/Chief of Staff) acts as curator. Agents contribute freely to `learnings/raw/`. The curator reviews and promotes valuable insights to `learnings/distilled/`. This keeps the system organized without creating contribution friction.

### 3. Two-Tier Learning
- **Raw learnings** — Agents dump post-task observations without friction
- **Distilled learnings** — Curator reviews and writes canonical patterns, mistakes, wins

### 4. Silo Privacy Respected
Each agent's private directory is theirs alone. The curator doesn't read private silos unless explicitly asked. What happens in an agent's silo stays in that agent's silo.

### 5. Conflict Resolution
When two agents contradict each other, both go to `curator/CONFLICTS.md`. Curator investigates and resolves — logged in `DECISIONS.md`. No unilateral overwrites.

### 6. Memory Hygiene
- Raw learnings >7 days unreviewed → auto-escalate
- Active tasks >14 days old → auto-escalate
- Private silos never auto-cleaned (agent owns its own space)
- Confidence gates prevent low-confidence info from polluting core knowledge

---

## For Developers

### Quick Start

```bash
# Clone the repo
git clone https://github.com/TJCurnutte/memory-hive.git
cd memory-hive

# Set up your hive directory
mkdir -p ~/.openclaw/hive
cp -r hive/ ~/.openclaw/hive/

# Each agent gets its own silo
mkdir -p ~/.openclaw/hive/agents/[your-agent-id]

# Integrate with your agent system
# See INTEGRATION.md for framework-specific guides
```

### For OpenClaw Users

All agents in your OpenClaw system automatically use the hive boot sequence. Each agent already has its own workspace — point it to `~/.openclaw/hive/` for the shared layer and `~/.openclaw/hive/agents/[agent-id]/` for private silo.

### Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Key areas:
- Framework adapters (LangChain, AutoGen, CrewAI, etc.)
- Curation automation tools
- Memory hygiene improvements
- Visualization tools

---

## The Curator Role

The **Chief of Staff** (main agent) acts as curator. This is the most important role in the system — it maintains the shared hive so all other agents can focus on their specialties.

**Curator responsibilities:**
- Maintain `knowledge/` as curated truth
- Review `learnings/raw/` daily
- Promote valuable learnings to `learnings/distilled/`
- Resolve conflicts in `curator/CONFLICTS.md`
- Log every decision in `curator/DECISIONS.md`
- Keep the hive organized and useful
- Synthesize cross-agent insights

---

## Who Built This

[Travis Curnutte](https://github.com/TJCurnutte) — built this as the central memory system for his own multi-agent architecture. It started as internal infrastructure and got open-sourced because nothing else like it exists.

## License

MIT — use it, build on it, make it better.

---

**The hive learns. Every task. Every agent. Every time.**
**Parallelize everything — ship faster.**