# Handoff — Memory Hive + Hive Swarm dual project

Two GitHub product repos + two private Next.js site repos that ship as a
sister-product family on `neural-forge.io`. Working dirs all live in `/tmp/`
(volatile — macOS prunes inactive files; previous handoff already saw
this happen and recovered config from sister dir).

| Project | Path | Repo | Live URL |
|---|---|---|---|
| memory-hive (canon) | `/tmp/memory-hive` | github.com/TJCurnutte/memory-hive (public) | memoryhive.neural-forge.io |
| hive-swarm (sister) | `/tmp/hive-swarm` | github.com/TJCurnutte/hive-swarm (public) | hiveswarm.neural-forge.io |
| memoryhive site | `/tmp/memory-hive-site` | github.com/TJCurnutte/memory-hive-site (**private**) | (Vercel proj `memory-hive-site`) |
| hiveswarm site | `/tmp/hive-swarm-site` | github.com/TJCurnutte/hive-swarm-site (**private**) | (Vercel proj `hive-swarm-site`) |

## Branch & Tree

**memory-hive** — branch `main`, working tree clean except one untracked
asset.

```
$ git status --short
?? assets/og-card-v0.3.png

$ git log --oneline -10
a52d5d4 codex handoff
42a1c1c fix: GitHub logo now matches site navbar mark exactly
655eb4d fix: GitHub logo overlap — switch to relative tspan dx spacing
fdb3be5 chore: cut v0.3.1 — audit pass + Hive Swarm interop
2750d67 docs: rename Hermes Swarm Extension → Hive Swarm in interop note
e371820 docs: add Hermes Swarm Extension interop note
33e8efc docs: reconcile curation loop with the shipped CLI verbs
f1856f7 Merge PR #22 (shell audit — 8 fixes)
9770e7f Merge PR #21 (docs audit — 6 fixes)
8061649 fix: assorted shell-portability nits

$ git stash list      # empty
```

**Sister repos:**

- `/tmp/hive-swarm` (`main`): tip `07da429` "docs(README): use python3 -m pip
  for install command". Three untracked OG cards in `assets/`.
- `/tmp/memory-hive-site` (`main`): tip `a4c975e` "docs: add README". Clean.
- `/tmp/hive-swarm-site` (`main`): tip `d064c6c` "fix(install): use python3
  -m pip for the install command". Clean.

## What this session accomplished

- **Renamed `hermes-swarm` → `hive-swarm`** mid-session — agent-runtime
  agnostic. Bulk perl rewrite across `.py/.md/.toml/.yml/.yaml/.json`, plus
  HTTP headers (`X-Hermes-*` → `X-Hive-*`), env vars, and (in a follow-up)
  the SVG assets. Pushed to renamed GitHub repo.
- **`hive-swarm` v0.1.0 published** — full Python package (9 modules, 4
  schemas, 42 tests, runtime-agnostic integration example, FastAPI
  heartbeat daemon). [`hive_swarm/`](../hive-swarm/hive_swarm),
  [`docs/RFC.md`](../hive-swarm/docs/RFC.md).
- **`memory-hive` v0.3.1 cut** — captures audit-pass PRs #21 + #22 (14 fixes),
  arch-doc reconciliation, Hive Swarm interop note. See `CHANGELOG.md:9-90`.
- **Two private site repos created** — `memory-hive-site` and `hive-swarm-site`
  on GitHub, both private. Initial commits pushed for each.
- **Both sites deployed to production** — memoryhive.neural-forge.io,
  hiveswarm.neural-forge.io. Live + green.
- **`/changelog` page** on each site — release-card layout showing latest 3
  releases with version, date, tagline, sections, GitHub-Releases link at
  top. `app/changelog/page.tsx` parses CHANGELOG.md inline.
- **Commands.tsx compaction** on both sites — was a wall of 34 verb
  paragraphs; now a chip-grid with hover tooltips + "Expand details" toggle
  for power readers. `Commands.tsx:chipLabel()` extracts verb names.
- **GitHub README logos fixed** — wordmark overlap from hardcoded
  `x="545"` switched to `<tspan dx="0.18em">` (commits `655eb4d`,
  `42a1c1c`). Memory Hive's logo now mirrors the site navbar's monochrome
  3-cell honeycomb exactly.
- **Install command fixed**: `pip install hive-swarm` → `python3 -m pip
  install hive-swarm` everywhere (Hero, QuickStart, HowItWorks, Footer,
  Commands, README). Was breaking on macOS where `pip` isn't on PATH by
  default.

## In-progress work

- **`/tmp/memory-hive/assets/og-card-v0.3.png`** — untracked launch image
  (1.7 MB, 1200×630). Was created for the v0.3 X launch but never
  committed. **Decision pending**: commit or rm.
- **Three untracked OG cards in `/tmp/hive-swarm/assets/`** —
  `og-card-launch.png`, `og-card-launch-4k.png`, `og-card-v0.1.0.png`. Same
  question.
- **X launch posts** — copy + images ready in Preview, never fired. User
  said "don't worry about X posts" near end of session — explicitly
  deferred.
- **Vercel→GitHub auto-deploy linkage** — investigated, blocked by Vercel
  GitHub App not having access to the new private site repos. User opted
  to defer ("don't worry about the github stuff this is all saved here
  locally anyway"). Manual `vercel --prod` from each site dir is the
  current deploy path.
- **Last manual deploy used `--prebuilt`** because regular `vercel --prod`
  started erroring with "Unexpected error" mid-session — likely transient
  Vercel platform issue. Workaround flow:
  ```
  npx vercel pull --yes --environment production
  npx vercel build --prod --yes
  npx vercel deploy --prebuilt --prod --yes
  ```

## Decisions & rationale

- **Renamed hermes-swarm → hive-swarm** to be agent-runtime-agnostic.
  Hermes Agent stays as one of several supported runtimes alongside
  OpenClaw, NanoClaw, Claude Code, custom. Integration example renamed
  `hermes_integration.py` → `runtime_integration.py`.
- **Brains-vs-muscle separation in hive-swarm** — controller produces
  plans, caller supplies the `runner` callable. Controller has no opinion
  about *what* a "local agent" is, only *where* work goes.
  [`hive-swarm/docs/RFC.md`](../hive-swarm/docs/RFC.md).
- **Sister-site palette bridge: teal/cyan.** Memory Hive amber `#F59E0B`
  primary, Hive Swarm indigo `#6366F1` primary; both share teal/cyan as
  accent. Reads as a product family.
- **Site repos private, product repos public.** Public-facing READMEs and
  install URLs need product repos public. Site source has nothing useful
  for a third-party reader; private avoids leaking landing-page copy
  iteration.
- **Install command: `python3 -m pip`** over `pip` or `pip3`. Most
  universal; works on macOS Homebrew Python, Apple Python, Ubuntu, WSL2,
  fresh installs. `pip3` works on macOS but not always on Linux.
- **Inline markdown renderer** in `app/changelog/page.tsx` — hand-rolled,
  ~50 lines. Sufficient for our Keep-a-Changelog format. Swap for `marked`
  if format gets fancier.
- **Brittle / temporary**:
  - `/tmp/` is volatile — macOS will prune it. Site dirs now have GitHub
    backups, but the venv in `/tmp/hive-swarm/.venv` doesn't.
  - Vercel auto-deploy never fully wired up; manual deploy is the canon
    flow until reconnected.
  - `~/.zshrc` has a stale `source ~/.openclaw/completions/openclaw.zsh`
    line that errors on every new shell (OpenClaw was uninstalled). Not
    blocking anything — flagged for cleanup.

## Next steps (numbered, concrete)

1. **Decide what to do with the four untracked OG cards.** Either commit
   them to their respective product repos (`memory-hive/assets/og-card-v0.3.png`
   and `hive-swarm/assets/og-card-launch{,-4k}.png` + `og-card-v0.1.0.png`)
   or delete. Commit recommended — they document each launch. Verify:
   `git status` shows clean tree afterward.
2. **Push memory-hive HANDOFF.md update.** This file. Run `git add
   HANDOFF.md && git commit -m "codex handoff" && git push origin main`
   from `/tmp/memory-hive`.
3. **Reconnect Vercel auto-deploy** (when convenient). Open
   https://vercel.com/thricealwaysnice-7369s-projects/<project>/settings/git
   for each site project, click "Connect Git Repository" → pick the
   matching repo → set production branch to `main`. Verify: push a noop
   commit, watch a new deployment appear in `npx vercel ls <project>`.
4. **Ship X launch posts** if/when ready. Copy + 4K images already staged
   in `/tmp/mh-card-v3/card.png` and `/tmp/hs-info-card/card-4k.png`.
   File-upload via Chrome MCP is blocked by extension permissions in this
   environment; user must drag the image into the X composer.
5. **Live verify `memory-hive curate --apply`** against the user's actual
   hive at `~/.memory-hive`. CI smoke test passes; live verification
   would catch real-world template/prompt edge cases. `memory-hive curate`
   (dry-run) first, review summary, then `--apply` only if it looks
   reasonable.

## Environment & gotchas

- **Vercel CLI**: `npx vercel` (currently 50.39.0, latest is 52.0.0 —
  upgrade with `npm i -g vercel@latest`). Auth at
  `~/Library/Application Support/com.vercel.cli/auth.json`.
- **Python 3.11** is the canonical interpreter for `/tmp/hive-swarm/.venv`
  (3.10+ required). Recreate after `/tmp` prune with `/opt/homebrew/bin/python3.11
  -m venv .venv && .venv/bin/pip install -e '.[dev]'`.
- **GH CLI** authenticated as TJCurnutte; `gh auth status` shows scopes
  `gist read:org repo workflow`. Insufficient to query `/user/installations`
  (App-installation listing) — would need an App-authorized token.
- **DNS**: `memoryhive.neural-forge.io` and `hiveswarm.neural-forge.io`
  are both wired via `vercel domains add`. Parent domain `neural-forge.io`
  was already configured on Vercel before this session.
- **Do NOT commit** these scratch dirs: `/tmp/mh-card-v3/`, `/tmp/hs-card/`,
  `/tmp/hs-launch-card/`, `/tmp/hs-info-card/`. Throwaway HTML+PNG used to
  generate launch images.
- **Vercel team scope**: `team_DSASPJdmyzsqFRuI5vqGHRny` (slug
  `thricealwaysnice-7369s-projects`).
- **Vercel project IDs**: memory-hive-site `prj_t8iSF0t6TilZ9g84ZnDfk961svw7`,
  hive-swarm-site `prj_TWiljQIxeNbVzDTu06eaaq1cGP9G`.
- **Manual deploy fallback** when `vercel --prod` errors:
  `vercel pull --yes --environment production && vercel build --prod --yes
  && vercel deploy --prebuilt --prod --yes`.

## Open questions

- **OG cards** — keep them committed alongside each release, or only
  reference from CHANGELOG via the `/og-card-vX.png` URL on the live site
  (already serving)? Current state: not in git, served from
  `<site>/public/`.
- **Auto-deploy reconnection priority** — the manual flow works fine.
  Reconnecting only matters if you'll iterate on site copy frequently.
- **Live `curate --apply`** — never run on the user's hive. Worth doing
  before promising the verb is production-ready in v0.3.x. User wants to
  review the dry-run summary first.
- **Vercel Pro / Free tier limits** — both sites are deployed on the
  current account; no warnings hit yet, but worth confirming the team
  is on the right plan if launch traffic spikes.
