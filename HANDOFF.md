# Handoff — Memory Hive + Hive Swarm dual project

Active across **two GitHub repos** + **two Next.js sites** that ship as a sister-product
family on `neural-forge.io`. Working dirs all live under `/tmp/` (volatile — macOS prunes
inactive files; reattach config from sister dir if files vanish).

| Project | Path | Repo / URL |
|---|---|---|
| memory-hive (canon) | `/tmp/memory-hive` | github.com/TJCurnutte/memory-hive · memoryhive.neural-forge.io |
| hive-swarm (sister) | `/tmp/hive-swarm` | github.com/TJCurnutte/hive-swarm · hiveswarm.neural-forge.io |
| memoryhive site | `/tmp/memory-hive-site` | Vercel project `memory-hive-site`, no git |
| hiveswarm site | `/tmp/hive-swarm-site` | Vercel project `hive-swarm-site`, no git |

## Branch & Tree

**memory-hive** — branch `main`, clean except for spurious local `D` rows (macOS `/tmp`
pruning artifacts; remote repo is fine; do **not** stage with `git add -A`).

```
git status --short:
 D LICENSE
 D hive/curator/CONFLICTS.md
 D hive/curator/DRAFT.md
 D hive/knowledge/SOUL.md
 D hive/learnings/distilled/{cross-agent-insights,mistakes,patterns,wins}.md
 D hive/tasks/queue.md
 D templates/claude-boot-block.md
 D update.sh
?? assets/og-card-v0.3.png
```

```
git log --oneline -10:
42a1c1c fix: GitHub logo now matches site navbar mark exactly
655eb4d fix: GitHub logo overlap — switch to relative tspan dx spacing
fdb3be5 chore: cut v0.3.1 — audit pass + Hive Swarm interop
2750d67 docs: rename Hermes Swarm Extension → Hive Swarm in interop note
e371820 docs: add Hermes Swarm Extension interop note
33e8efc docs: reconcile curation loop with the shipped CLI verbs
f1856f7 Merge PR #22 (shell audit — 8 fixes)
9770e7f Merge PR #21 (docs audit — 6 fixes)
8061649 fix: assorted shell-portability nits
4f8ad99 fix: seed substitutes __DAYS_AGO_N__; mh_watch POSIX; help
```

`git stash list`: empty.

**hive-swarm** — branch `main`. Three untracked OG cards in `assets/`. Latest commits:
`7f0413a` (logo rename Hermes→Hive), `bbaa5fd` (full hermes→hive rename), `685e282`
(initial v0.1.0).

## What this session accomplished

- **memory-hive v0.3.1 shipped** — audit-pass release ([CHANGELOG.md:9](CHANGELOG.md))
  capturing PRs #21+#22 (14 fixes), arch-doc reconciliation, Hive Swarm interop note.
  GitHub release published. Tag `v0.3.1` is `Latest`.
- **hive-swarm v0.1.0 created from scratch** at `/tmp/hive-swarm` — full Python package
  (9 modules, 4 schemas, 42 tests, runtime-agnostic integration example, FastAPI
  heartbeat daemon). Repo created at github.com/TJCurnutte/hive-swarm. v0.1.0 release
  published.
- **Renamed `hermes-swarm` → `hive-swarm`** mid-session. User push-back: name was too
  Hermes-specific; same orchestration applies to OpenClaw, NanoClaw, Claude Code, custom
  runtimes. Bulk perl rename across `.py/.md/.toml/.yml/.yaml/.json`, plus HTTP headers
  (`X-Hermes-*` → `X-Hive-*`) and env var (`HERMES_SWARM_SECRET` → `HIVE_SWARM_SECRET`).
  GitHub repo renamed via `gh repo rename`. Two follow-ups landed for SVG assets which
  the bulk rename missed.
- **GitHub logos fixed** on both repos — wordmark overlap from hardcoded `x="545"` →
  `<tspan dx="0.18em">` for font-metric robustness on GitHub's serif fallback. Then a
  second fix to make memory-hive's GitHub logo match the site navbar's monochrome
  3-cell honeycomb exactly (commits `655eb4d`, `42a1c1c`).
- **Sister site `hiveswarm.neural-forge.io` built + deployed** — cloned APIARY design
  system from memoryhive site, swapped palette to indigo `#6366F1` + cyan `#22D3EE`
  (memoryhive stayed amber + teal). Both share the cyan/teal bridge accent.
- **`/changelog` pages on both sites** — release-card layout showing latest 3 releases
  with version, date, tagline, sections, bullet lists. Top-of-page link to GitHub
  Releases. Implemented with a custom inline-markdown parser (`page.tsx:38-127`) and
  card CSS appended to each `globals.css`.
- **Two-agent audit pass** on memory-hive — PR #21 (docs/site, 6 fixes + site SEO + 5
  missing verbs surfaced) and PR #22 (shell/CI/templates, 8 fixes — top: `mh_seed`
  shipped lint-failing templates; renamed 16 templates to use `__DAYS_AGO_N__` marker).
  Both merged.
- **Commands.tsx compaction** on both sites — was a wall of 34 verb paragraphs (~3
  screens of vertical scroll on mobile). Now a chip-grid with hover tooltips +
  "Expand details" toggle for power readers + "Full reference on GitHub" link.
  See `Commands.tsx:chipLabel()` for the verb-name extraction heuristic.

## In-progress work

- **Two X launch posts staged but not posted**:
  1. **Post 1 — memory-hive v0.3 launch.** Text was typed into the X composer via
     Chrome MCP successfully but `file_upload` returns `{"code":-32000,"message":"Not
     allowed"}`. Image at `/tmp/mh-card-v3/card.png` (1200×630, "Agents that remember"
     headline, two-layer architecture verbs). User must drag image in + click Post
     manually. **Composer was never closed** — may still be open in their browser.
  2. **Post 2 — hive-swarm v0.1.0.** Copy is ready; image iteration in progress. User
     rejected the first OG-style image and the dense 5-step infographic. Last action:
     I gave them a Claude-Design prompt at the end of the previous turn so they can
     generate a better image themselves. They have not come back with the result.
- **memory-hive-site `/tmp` pruning recovery** — restored config files (`package.json`,
  `tsconfig.json`, etc.) from `/tmp/hive-swarm-site` and rewrote `Principles.tsx` from
  scratch (sister site's version was hive-swarm-flavored). Built + deployed cleanly.
  See `src/components/Principles.tsx`.

## Decisions & rationale

- **Hive-swarm runtime-agnostic**, not Hermes-only. Same controller logic applies to any
  runtime that can call a Python `preplan_hook(task) -> SchedulerPlan` before spawning
  agents. Hermes Agent stays as a *named* supported runtime, alongside OpenClaw,
  NanoClaw, Claude Code. The integration example is `examples/runtime_integration.py`.
- **Brains-vs-muscle separation in hive-swarm** — controller produces plans, caller
  supplies the `runner` callable. Controller has no opinion about *what* a "local agent"
  is, only *where* work goes. Documented in `docs/RFC.md`.
- **Sister-site palette bridge: teal/cyan.** Memory Hive (amber `#F59E0B` primary) and
  Hive Swarm (indigo `#6366F1` primary) both use teal/cyan as accent. Reads as a
  product family without making the sites identical.
- **Chip-grid Commands**: rejected hover-only descriptions. Kept the full paragraph
  view available behind the "Expand details" toggle. This balances scannability with
  full-reference accessibility.
- **`<tspan dx>` for SVG wordmarks**: chose relative spacing over `textLength` because
  `dx` is universally supported and stable across font fallbacks; `textLength` distorts
  characters. See `assets/logo-light.svg:35`.
- **Brittle / temporary**: `/tmp/` is volatile — macOS will prune it. Sites should
  eventually move to git repos so they survive. The tiny markdown renderer in
  `src/app/changelog/page.tsx` is hand-rolled; if changelog format gets fancier
  (tables, nested lists), swap for `marked` or `remark`.

## Next steps (numbered, concrete)

1. **Decide Post 2 image path.** User is iterating in Claude Design with the prompt I
   provided. Either: (a) wait for their result, or (b) accept the existing 4K
   `/tmp/hs-info-card/card-4k.png` and proceed. **Verify**: ask user.
2. **Fire Post 1 + Post 2 to X.** Drive Chrome to `x.com/compose/post` via Chrome MCP
   (`mcp__Claude_in_Chrome__navigate` → `find` textbox → `computer.left_click` +
   `computer.type` with the staged copy). User drags image in + clicks Post. Verify:
   tweet visible at x.com/traviscurnutte.
3. **Sites need git repos.** Both `/tmp/memory-hive-site` and `/tmp/hive-swarm-site` are
   not under version control — they survived this session by accident. Init each with
   `git init && gh repo create TJCurnutte/<name>-site --source . --push`. Verify: `gh
   repo view`.
4. **Restore memory-hive `/tmp/` pruned files.** `cd /tmp/memory-hive && git checkout
   HEAD -- LICENSE update.sh hive/ templates/claude-boot-block.md` to drop the spurious
   `D` rows from `git status`. Verify: `git status` clean.
5. **Commit hive-swarm OG cards.** `cd /tmp/hive-swarm && git add assets/og-card-*.png
   && git commit -m "assets: launch + 4K OG cards" && git push`. Verify: cards visible
   on the GitHub releases page.

## Environment & gotchas

- **Vercel CLI**: `npx vercel` (current 50.39.0; v52.0.0 available). Both sites linked
  via `.vercel/project.json` to scope `thricealwaysnice-7369s-projects`.
- **Python 3.11** is the canonical interpreter for `/tmp/hive-swarm/.venv` (3.10+
  required). Run `pip install -e '.[dev]'` after recreating the venv.
- **DNS subdomain**: `hiveswarm.neural-forge.io` is wired via `vercel domains add`.
- **GH CLI (`gh`)** authenticated as TJCurnutte; releases auto-publish via
  `.github/workflows/release.yml` on tag push.
- **Chrome MCP `file_upload` is blocked** in the user's environment — workaround: the
  user drags images from Preview into the X composer themselves.
- **Do NOT commit** these scratch dirs: `/tmp/mh-card-v3/`, `/tmp/hs-card/`,
  `/tmp/hs-launch-card/`, `/tmp/hs-info-card/`. They contain throwaway HTML+PNG.

## Open questions

- **Post 2 image**: which version does user want to ship — the 4K info-poster at
  `/tmp/hs-info-card/card-4k.png`, or whatever they generate in Claude Design?
- **Are the Vercel-only sites OK to keep out of git long-term?** They're surviving on
  Vercel's deployed bundle alone. Recommend git-init for resilience but user hasn't
  said.
- **Memory Hive curate's auto-promote behavior in CI** — PR #16 was merged but should
  be smoke-tested manually against a real hive (synthetic CI test exists; live verify
  has not been done).
