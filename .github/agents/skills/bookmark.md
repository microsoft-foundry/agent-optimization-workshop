# Skill — bookmark

## Purpose

Save the learner's current position when they detour into an unrelated topic
or a More Lab, so they can resume seamlessly.

## When to use

- The learner asks about a topic not covered in the current lab
- The learner wants to peek at a More Lab
- The learner opens a docs link and might be gone a while

## Behavior

1. Call `progress-tracker.add_bookmark(current.phase, current.lab)`.
2. Tell the learner exactly where the bookmark is set:
   > 🔖 Bookmarked **<phase>/<lab>** — say "resume" any time to return.
3. Proceed with the detour via `explore-suggest` or a short direct answer.

## Do not

- Do **not** bookmark the same lab twice in a row — check the stack top first.
- Do **not** clear `current`; the bookmark is separate from the active position.

## Output template

```
🔖 Bookmarked **<phase>/<lab>** at step <N>. Say "resume" to return.
```
