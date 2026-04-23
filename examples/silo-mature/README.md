# `silo-mature/` — What a populated silo looks like

A fresh install gives each agent an empty silo:

```
hive/agents/<name>/
├── log.md      # "Silo initialized by memory-hive installer."
├── context.md  # "(What is this agent's responsibility?)"
└── memory.md   # (empty bullet lists)
```

After a few weeks of real use, the same silo looks very different. This
example shows what "mature" looks like so you can calibrate your own —
how dense is too dense, what belongs in `log.md` vs `memory.md`, what
a real `learnings/raw/` entry looks like.

## What's in here

```
silo-mature/
└── coder/
    ├── log.md          ← ~20 dated entries covering a few weeks of work
    ├── context.md      ← role, current focus, open questions, collaborators
    ├── memory.md       ← durable facts, preferences, and lessons
    └── learnings/
        ├── 2026-03-11-test-isolation-patterns.md
        └── 2026-03-18-mock-boundary-rule.md
```

The `coder` is a generic engineer agent. Content is synthetic — there's
no real person or project behind it. Borrow the shape, not the specifics.

## How to use this

**Don't copy this into your hive.** Creating an agent named `coder` with
`memory-hive add coder --role coder` scaffolds empty files that your
agent will populate from real use. Seeding with this example's content
would pollute your memory with events that didn't happen.

Read it as a reference. When you open your own agent's `log.md` and
it's empty, remember this is what it'll look like in a month.

## What "mature" means for each file

| File | Grows with | Looks like |
|---|---|---|
| `log.md` | Each task the agent completes | Append-only dated entries, 1–3 lines each |
| `context.md` | Changes in what the agent is working on | Short, current, overwritten as focus shifts |
| `memory.md` | Lessons learned that the agent wants to remember forever | Bullet lists under stable headings |
| `learnings/*.md` | Generalizable insights the agent wants to contribute to the hive | One file per insight, with frontmatter for curator review |

A mature silo is not a mature archive. `log.md` can get long (50KB is
the cap); `context.md` should stay short (current state only);
`memory.md` accretes slowly.
