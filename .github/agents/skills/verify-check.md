# Skill — verify-check

## Purpose

Walk the learner through the current lab's `✅ Verify` block. Ask what they
observe; compare to the expected signal in the lab file; mark the lab complete
when the learner reports a matching result.

## When to use

- The learner says "how do I verify?", "I think I'm done", "I finished lab NN".

## Behavior

1. Load the lab file via `lab-guide`'s reader (or read directly).
2. Extract the `✅ Verify` block.
3. Present the check as a **question**, not an answer:
   - Name the URL/CLI/artifact to inspect
   - Ask the learner what they see
4. Compare the learner's answer to the lab's stated expected signal.
5. If matched → call `progress-tracker.mark_complete` and point to `➡️ Next`.
6. If not matched → ask a diagnostic follow-up question (do not fix for them).

## Do not

- Do **not** paste the expected output verbatim before the learner reports theirs.
- Do **not** mark complete without the learner reporting a matching result.
- Do **not** run the verification command on the learner's behalf.

## Output template

```
✅ To verify **<phase>/<lab>**:
Open/run: <thing to check>.
What do you see?
```

After they respond:

```
Great — that matches the expected signal. Marking **<phase>/<lab>** complete.
Next up: **<phase>/<next lab>** — <one-line goal>.
```
