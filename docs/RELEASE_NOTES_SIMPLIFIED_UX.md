# Release notes — simplified install-once UX

Status: shipped in Memory Hive v1.2.0.

## Headline

Memory Hive now behaves like an install-once local memory layer instead of a toolbox that asks users to run several setup, health, recall, and curator commands manually.

The normal path is now:

```bash
curl -fsSL https://hive.neural-forge.io/install.sh | sh
memory-hive
memory-hive update
```

Optional:

```bash
memory-hive add coder --role coder
memory-hive recall "task context"
```

## Why this changed

The v1.1 HyperRecall work made Memory Hive more capable, but it also pushed internal plumbing into the onboarding path. A fresh user saw commands such as:

```bash
memory-hive doctor
memory-hive recall build --json
memory-hive recall doctor --json
memory-hive digest --week
memory-hive confidence
```

Those commands are useful for operators and CI, but they are the wrong public surface. The new release keeps the power tools while making the default experience simpler: install once, check status, let agents work, and update periodically.

## User-visible changes

### Bare `memory-hive` now shows status

Running `memory-hive` with no arguments now prints a one-screen receipt instead of the full help catalog. It reports:

- install path
- hive path
- active silo count
- recall index/helper state
- health status
- raw/distilled/stale memory counts
- last maintenance timestamp
- the few normal commands users actually need

### New `memory-hive status`

`memory-hive status` is the explicit form of the same receipt. Use it for scripts or docs that should not rely on bare-command behavior.

### New `memory-hive maintain`

`maintain` is the local periodic maintenance wrapper. It:

1. refreshes `registry/AGENTS.md`
2. refreshes citation registry output
3. builds or updates the HyperRecall index
4. runs the built-in Optimizer health pass
5. writes `hive/.last-maintained`
6. prints a short maintenance receipt

Normal users do not need to run it directly; `install.sh` and `memory-hive update` run it quietly.

### New `memory-hive update`

`memory-hive update` is now the preferred public refresh path. It delegates to the existing safe updater, preserves all private agent silos, refreshes shared/tool files, and runs quiet maintenance.

### Direct recall query sugar

Users can now run:

```bash
memory-hive recall "operator context"
```

instead of:

```bash
memory-hive recall query "operator context"
```

The old subcommands still work for advanced users.

### Automatic recall index maintenance

Recall queries and bundles now build/update the HyperRecall index automatically when needed. Fresh installs should not ask users to run `memory-hive recall build --json` before recall works.

## Advanced commands are still available

The command surface was simplified, not deleted. Internal/debug/curator commands moved behind:

```bash
memory-hive help --advanced
```

That surface still documents lifecycle, health, inspection, HyperRecall, and curator workflows for operators and CI.

## Fixed

### Issue #25 — PATH shim helper resolution

When `memory-hive` was invoked from a PATH shim or symlink, recall tried to load:

```text
$(dirname "$0")/memory_hive_recall.py
```

For a shim, `$0` can be `~/.local/bin/memory-hive`, so recall looked for:

```text
~/.local/bin/memory_hive_recall.py
```

The helper actually lives under the Memory Hive install directory:

```text
~/.memory-hive/memory_hive_recall.py
```

The recall wrapper now resolves helpers from the detected install directory first, then falls back to the repo checkout path for development/tests.

## Compatibility

Existing advanced commands remain available:

- `doctor`
- `recall build/update/doctor/stats`
- `lint`
- `dedup`
- `confidence`
- `promote`
- `curate`
- `conflicts`
- `stale`
- `checkpoint`
- `diff`
- `stats`
- `digest`
- `bundle`
- `citations`
- `reflect`
- `seed`

Scripts that call those commands should continue to work.

## Migration notes

No user migration is required.

After updating, run:

```bash
memory-hive update
memory-hive status
```

If you previously documented `memory-hive doctor` or `memory-hive recall build --json` as onboarding steps, replace them with:

```bash
memory-hive
```

or:

```bash
memory-hive status
```

## Verification target

The release is verified when:

- clean install creates a PATH-ready `memory-hive` command
- bare `memory-hive` prints status
- fresh PATH-shim invocation of `memory-hive recall query "Memory Hive" --json` succeeds
- `memory-hive recall "Memory Hive" --json` auto-builds the index if missing
- `memory-hive help` stays small
- `memory-hive help --advanced` still documents internal commands
- README quickstart no longer asks users to run doctor/recall build/recall doctor manually
