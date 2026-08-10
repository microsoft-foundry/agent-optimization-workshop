# Contributing

> 🚧 This document is a work in progress. Please wait for final guidance to be released.

## Process

This is a **living resource** that is built and maintained with the help of coding agents. Follow these steps when you want to propose an addition or modification:

1. Update [`.github/PLAN.md`](./.github/PLAN.md) with the intent
2. Update the relevant spec in [`specs/`](./specs/) so tests know the new truth
3. Update or add tests in [`tests/`](./tests/)
4. Implement the change
5. `pytest -q` passes → open a PR

CI runs the spec suite on every PR
([`.github/workflows/verify-course.yml`](./.github/workflows/verify-course.yml)).

## Feedback

Issues and PRs welcome. See [`LICENSE`](./LICENSE) for terms.
