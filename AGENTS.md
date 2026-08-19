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

### Callout conventions — Gotchas

Two-variant rule (guarded by `tests/test_lab_content.py`):

1. **Inline gotcha** — a single lab-specific mistake, ≤ 4 lines, fits in the
   step's flow. Format: `> ⚠️ **Gotcha:** <one-liner>.`
2. **Cross-cutting gotcha** — infra/tool errors that recur across labs, or
   need multi-step recovery. Author them **once** in
   [`labs/TROUBLESHOOTING.md`](./labs/TROUBLESHOOTING.md) under a stable H3
   using the **Symptom / Cause / Fix / Prevent** template. In the lab, keep
   the callout to one line:

   ```markdown
   > ⚠️ **Gotcha — <error phrase>.** Details in [Troubleshooting · <section>](../TROUBLESHOOTING.md#anchor).
   ```

`> ⚠️ **Cost:** …` and `> ⚠️ **Known limitation:** …` follow the same visual
style but are not enforced by the drift-check.

## Workshop-Coach agent

Do **not** modify `.github/agents/workshop-coach.agent.md` behavior contract
casually. The coach must always:

- Guide, never do the task for the learner
- Locate the learner via `progress-tracker` before responding
- Refuse "do it for me" requests politely

## TODO comments

Use `<!-- TODO(nitya): ... -->` in markdown and `# TODO(nitya):` in code for
maintainer follow-ups (screenshots, exact commands, model pinning, etc.).

## Known gotchas

Canonical entries live in [`labs/TROUBLESHOOTING.md`](./labs/TROUBLESHOOTING.md).
Bullets below are pointers — keep them in lockstep with the canonical section
anchors and the in-lab callouts that link to them.

- **`azd provision` — soft-deleted resource blocks re-provision.** Purge the
  Cognitive Services (Foundry) account or use a fresh `azd env` name.
  [Troubleshooting](./labs/TROUBLESHOOTING.md#soft-deleted-cognitive-services-account-blocks-re-provision)
  · Lab 01.
- **`azd provision` — `invalid character 'n' after object key:value pair`.**
  Non-empty `AI_PROJECT_DEPLOYMENTS` (or the other three `*Json` params) breaks
  the parameters file on azd ≤ 1.31. Workaround: `azd env set
  AI_PROJECT_DEPLOYMENTS "[]"`. Structural fix tracked as `TODO(nitya)` in
  `infra/main.bicep` (switch the four params to `array`/`object` types).
  [Troubleshooting](./labs/TROUBLESHOOTING.md#azd-provision-fails-with-invalid-character-n-after-object-keyvalue-pair)
  · Lab 03 + Lab 05.
- **`azd deploy` — 409 Conflict.** Reusing the same `azd env` name after a
  torn-down deploy hits stale Foundry data-plane state; recovery needs a fresh
  env name. [Troubleshooting](./labs/TROUBLESHOOTING.md#409-conflict-on-azd-deploy)
  · Lab 05.
- **`azd deploy` — 404 `Subdomain does not map to a resource`.** Stale bearer
  token, not a missing resource. Re-auth **both** `az` and `azd` (independent
  token caches). [Troubleshooting](./labs/TROUBLESHOOTING.md#404-subdomain-does-not-map-to-a-resource-on-azd-deploy)
  · Lab 05.
- **Mixed UI→CLI path creates a second resource group.** A portal-first
  learner running `azd env new … && azd provision` in Lab 05 creates a second
  RG. Fix: `bash scripts/link-portal-rg.sh` (idempotent).
  [Troubleshooting](./labs/TROUBLESHOOTING.md#ui-provision--cli-deploy-creates-a-second-resource-group)
  · Lab 05 "Path check" + Lab 00 overview warning.
- **Portal cannot *create* hosted agents.** The Foundry portal can view and
  manage hosted agents but has no create flow — `azd deploy` is the only
  supported creation path today. Do not add "portal path" instructions for
  hosted agents unless the portal ships that flow. *(No troubleshooting entry
  — this is a static product limitation, not an error.)*

## Tests

Run before opening a PR:

```bash
pip install -r requirements-dev.txt
pytest -q
```

CI runs the same suite on every PR.
