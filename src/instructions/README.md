# Concierge Instructions — versioned prompt

The concierge system prompt lives in a file so you can iterate on it and trace
its evolution across the workshop, independently of the application code.

## Files

| Path | Role |
|---|---|
| `concierge.md` | **Active** prompt. This is what the deployed agent loads at runtime. |
| `versions/instructions-0.md` | Immutable **baseline seed** (intentionally basic). |
| `versions/instructions-N.md` | Frozen snapshot of `concierge.md` at iteration `N`. |

The agent loads `concierge.md` at startup. Override with the
`CONCIERGE_INSTRUCTIONS_FILE` environment variable if you want to point at a
specific version without editing the active file.

## Reset to baseline

Every fresh run of the optimize loop should start from the same under-optimized
seed. To restore the active prompt from the immutable baseline:

```bash
./scripts/reset-instructions.sh
```

This copies `versions/instructions-0.md` over `concierge.md` (and is a no-op if
they already match). The optimize-lab setup step runs this for you, so a re-run
in the same checkout doesn't accidentally start from a previously optimized
prompt.

## Iteration workflow (Lab 3)

1. Run an evaluation against the currently deployed agent and review failures.
2. Edit `concierge.md` to address the weaknesses you found.
3. Snapshot the new prompt so the evolution is traceable:

   ```bash
   ./scripts/snapshot-instructions.sh
   ```

   This copies `concierge.md` to the next free `versions/instructions-N.md`.
4. Redeploy the agent so the new prompt is live:

   ```bash
   azd deploy contoso-travel-concierge --no-prompt
   ```

5. Re-run the evaluation and compare against the previous run.

## Version log

| Version | Summary |
|---|---|
| 0 | Baseline seed. Asks clarifying questions on missing fields; no ID/price citation rule; no superlative grounding; weak multi-component handling. |
