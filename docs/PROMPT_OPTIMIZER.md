# Prompt Optimizer Addon

Status: design/spec addon for the Memory Hive command surface.

Prompt Optimizer is not a separate product. It is a Memory Hive addon pattern that turns rough operator prompts into compact, grounded work orders before an agent starts work.

Memory Hive already owns the durable context: shared hive files, private agent silos, distilled learnings, session notes, and HyperRecall bundles. The optimizer uses that context to make the next prompt safer, smaller, and easier to execute.

## What it does

For each inbound prompt, the addon should:

1. Accept the raw prompt exactly as received.
2. Classify the task shape: exact-output, trivial acknowledgement, operational task, creative task, code task, research task, continuation, or ambiguous.
3. Pull the smallest useful Memory Hive slice:
   - `hive/index.md`
   - the active agent silo (`agents/<agent>/memory.md` and recent `log.md`)
   - `knowledge/HUMAN_CONTEXT.md` when human preferences matter
   - `tasks/queue.md`, `tasks/active/`, or a HyperRecall bundle when the prompt references prior work
4. Produce an internal work order:
   - goal
   - context/sources to inspect
   - relevant tools or skills
   - constraints and safety boundaries
   - deliverables
   - verification steps
5. Execute against that work order.
6. Log the result back into the agent silo and raw learnings when the lesson generalizes.

The goal is not prettier prompts. The goal is fewer stale answers, fewer missed prerequisites, and more auditable work.

## Command contract

Planned command family:

```bash
memory-hive prompt classify "<raw prompt>" --json
memory-hive prompt optimize "<raw prompt>" --json
memory-hive prompt questions "<raw prompt>" --count 3 --json
memory-hive prompt bundle "<raw prompt>" --for-agent <agent>
```

`prompt classify` returns the prompt type and the confidence behind the route.

`prompt optimize` returns a compact JSON work order. It does not rewrite the user-facing response; it prepares the agent's private execution brief.

`prompt questions` returns exactly three clarification questions, only when the prompt remains genuinely ambiguous after local context/Hive inspection and the ambiguity changes the next action.

`prompt bundle` combines the optimized work order with a cited Memory Hive recall bundle so a downstream agent can start with enough context without replaying the entire hive.

## JSON shape

```json
{
  "raw_prompt": "add to the github for memoryhive",
  "classification": "operational",
  "confidence": "medium",
  "work_order": {
    "goal": "Add the Prompt Optimizer addon documentation to the canonical Memory Hive GitHub repo and publish a release update.",
    "context_to_pull": [
      "hive/index.md",
      "agents/hermes/memory.md",
      "README.md",
      "CHANGELOG.md"
    ],
    "skills_or_tools": ["memory-hive", "github-repo-management", "github-pr-workflow"],
    "constraints": [
      "Keep Memory Hive as the canonical public product surface.",
      "Do not present planned commands as already implemented unless they are wired into the CLI."
    ],
    "deliverables": [
      "README addon section",
      "docs/PROMPT_OPTIMIZER.md",
      "CHANGELOG release entry",
      "GitHub commit/release"
    ],
    "verification": [
      "git diff --check",
      "README/readback grep",
      "release/list verification"
    ]
  },
  "clarifying_questions": []
}
```

## Clarification rule

When the optimized route is still genuinely unclear, return exactly three questions.

Bad:

```text
Can you clarify?
```

Good:

```text
1. Should this be documentation-only or should the CLI command be implemented now?
2. Should the release be a patch semver release or only an Unreleased changelog entry?
3. Should the addon be framed as experimental, planned, or stable?
```

Do not ask questions when the default interpretation is obvious and safe. Use Memory Hive, session state, repo state, and skills first.

## Exact-output exception

If the raw prompt asks for a literal answer (`reply exactly`, `one line only`, `JSON only`, etc.), do not run visible optimizer ceremony. Return the requested literal output unless verification was explicitly requested.

## Public framing

Keep public copy clear:

- Prompt Optimizer is a Memory Hive addon, not a separate SaaS product.
- Markdown remains the source of truth.
- HyperRecall is the speed layer.
- Prompt Optimizer is the preflight brain that decides what context to pull and how to turn it into an executable work order.

Short version:

> Prompt Optimizer compiles rough operator prompts into cited, executable work orders using the hive you already maintain.

## Verification checklist for future implementation

When this moves from addon spec to CLI implementation, verify:

```bash
memory-hive prompt classify "continue" --json
memory-hive prompt optimize "ship it" --json
memory-hive prompt questions "fix the thing" --count 3 --json
memory-hive prompt bundle "resume the release" --for-agent hermes
```

Expected properties:

- JSON parses cleanly.
- Exact-output prompts bypass optimizer output.
- Ambiguous prompts return exactly three questions.
- Work orders cite files or recall bundles when cross-session context is used.
- No command mutates the hive unless explicitly asked to write logs/learnings.
