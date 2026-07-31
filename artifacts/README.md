# Artifacts

Every lab that *generates* something (a dataset, an evaluator, a prompt) also
ships a **known-good reference** so the workshop stays reproducible even when
LLM non-determinism produces weak output.

```
artifacts/
├── datasets/{generated/, reference/}
├── evaluators/{generated/, reference/}
└── prompts/{generated/, reference/}
```

- **`reference/`** — versioned, ships in the repo, safe to copy over `generated/`.
- **`generated/`** — learner outputs; gitignored per subfolder.

To use a reference artifact instead of your own generation:

```bash
./scripts/use-reference.sh datasets sample-prompts-v1
```

See the [course plan](../.github/PLAN.md#artifacts-strategy--reproducible-lab-outputs)
for the full rationale.
