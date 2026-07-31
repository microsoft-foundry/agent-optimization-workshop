# `src.original/` — pristine baseline for the hosted agent

**Do not edit files in this directory directly.** This is the reset target for
`scripts/reset.sh`. It must always represent a clean starting state so learners
can re-run the labs from scratch.

If you legitimately need to update the baseline (e.g., bump a dependency), do
it in a single coordinated PR that touches both `src/` and `src.original/` so
they stay in sync. `tests/test_reset.py` guards this.
