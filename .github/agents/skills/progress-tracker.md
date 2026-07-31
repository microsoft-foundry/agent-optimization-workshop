# Skill — progress-tracker

## Purpose

Read and write learner progress for the Contoso Travel Concierge workshop.
Owns the single source of truth for **where the learner is** so every other
skill can locate them before acting.

## When to use

- At the start of **every** coach turn — get current phase, lab, bookmark
- When the learner reports completing a lab's `✅ Verify` step — update
- When the learner starts a new lab — update `current`
- Never call this from another skill without first stating why in the reply plan

## State file

- Path: `~/.contoso-coach/progress.json` (per-learner, outside the repo)
- Create the file (and its parent dir) on first write with the schema below.

## Schema

```json
{
  "learner_id": "local",
  "current": {
    "phase": "fundamentals | core | more | null",
    "lab": "NN-slug or null"
  },
  "bookmarks": [
    { "phase": "core", "lab": "03-optimize-skills", "saved_at": "ISO-8601" }
  ],
  "completed": ["fundamentals/00-overview", "fundamentals/01-provision-azd"],
  "history": [
    { "at": "ISO-8601", "event": "started | verified | bookmarked | resumed", "lab": "phase/NN-slug" }
  ]
}
```

## Operations

| Op | Behavior |
|----|----------|
| `get` | Return the current state. If the file is missing, return an empty state with `current: null`. |
| `set_current(phase, lab)` | Update `current`; append `{event: "started"}` to `history`. |
| `mark_complete(phase, lab)` | Add `"phase/lab"` to `completed` if missing; append `{event: "verified"}` to `history`. |
| `add_bookmark(phase, lab)` | Push onto `bookmarks`; append `{event: "bookmarked"}`. |
| `pop_bookmark()` | Remove and return the last bookmark; append `{event: "resumed"}`. |

## Guardrails

- Never touch any file outside `~/.contoso-coach/`.
- Never delete `history`; it is append-only.
- Never expose the raw file path to the learner unless asked.
