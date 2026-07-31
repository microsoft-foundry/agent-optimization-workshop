# AGENTS.md — guidance for coding agents in this repo

This file is read by Copilot and other coding agents that operate on this repo.
It defines **what to do**, **what to avoid**, and **where to look** when the
agent is helping the maintainer evolve the workshop.

## Repo purpose

A living workshop teaching the **Agent DevOps loop** on Microsoft Foundry,
using the fictitious **Contoso Travel Concierge** as the running scenario.
Two agent implementations (Prompt Agent, Hosted Agent) share one dataset.

Canonical plan: [`.github/PLAN.md`](./.github/PLAN.md).

## Scenario + branding

- Agent name: **Contoso Travel Concierge**
- Company: **Contoso** (fictitious)
- Data IDs: `CT-FL-*` (flights), `CT-HT-*` (hotels), `CT-CR-*` (car rentals)
- Never introduce real company/product names in scenario content

## Files agents must not touch

| Path | Why |
|------|-----|
| `data/*.csv`             | Change requires schema update in `specs/schemas/` and test bump. Coordinate with maintainer. |
| `src.original/**`        | Pristine baseline for `scripts/reset.sh`. Never edit unless intentionally bumping the baseline. |
| `artifacts/**/reference/**` | Versioned known-good outputs. Versioned via filename suffix (`-v1`, `-v2`), never overwritten. |

## Files agents should update in lockstep

When any of these change, update the others in the **same PR**:

1. `.github/PLAN.md` — the intent
2. `specs/course.yaml` and `specs/*.schema.json` — machine-readable truth
3. `tests/**` — verification of the truth
4. `labs/**` — learner-facing content

If tests fail after your change, that's the guardrail catching drift — fix
the mismatch rather than skipping the test.

## Pedagogy rules

Every file under `labs/{fundamentals,core,more}/*.md` **must** follow
[`labs/_template/lab-template.md`](./labs/_template/lab-template.md):

- H1 title starting with `Lab NN — ...`
- `🎯 Goal` · `🧭 Where this fits` · `📋 Steps` · `✅ Verify` · `🧠 Recap` · `➡️ Next`
- Callouts: `> 🎯` `> ✅` `> 💡` `> ⚠️` `> 🧭` `> 🧠`
- Every generative step ships a `reference/` artifact under `artifacts/`

## Workshop-Coach agent

Do **not** modify `.github/agents/workshop-coach.agent.md` behavior contract
casually. The coach must always:

- Guide, never do the task for the learner
- Locate the learner via `progress-tracker` before responding
- Refuse "do it for me" requests politely

## TODO comments

Use `<!-- TODO(nitya): ... -->` in markdown and `# TODO(nitya):` in code for
maintainer follow-ups (screenshots, exact commands, model pinning, etc.).

## Tests

Run before opening a PR:

```bash
pip install -r requirements-dev.txt
pytest -q
```

CI runs the same suite on every PR.
