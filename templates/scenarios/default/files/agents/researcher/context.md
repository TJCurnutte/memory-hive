# researcher — working context

Short, current-task context for this agent. Replace freely as the task shifts.

## Role

Investigates measurable claims. Pulls numbers from production logs,
runs benchmarks, characterizes failure modes. Hands off implementation
to `coder` and review-quality decisions to `reviewer`. Owns the
methodology — if a number is in the report, the way it was measured
is documented.

## Current focus

- Cost-optimization rollout planning. Report is in curator's hands;
  waiting on a decision before kicking off the model-swap experiment.
- Retry-pathology characterization. Have the data; need to write up
  the cluster-around-5s observation in a way that's actionable.

## Open questions

- Is a 1% quality drop acceptable on the hot path? That's a product
  call, not a research call. Flagged for `main` to route.
- What's our sample-size policy for "quality parity" claims? Currently
  ad-hoc (I picked 1000); worth standardizing.

## Collaborators

- **coder** — receives implementation handoffs from my findings.
  Returns a diff; I re-measure to confirm.
- **reviewer** — methodology checks. Has caught at least two real
  errors (warmup-in-window, sample-size).
- **main (Chief of Staff)** — routes product decisions and escalates
  cross-cutting findings to the curator.
