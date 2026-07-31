# Skill — lab-guide

## Purpose

Load the current lab file and produce **next-step guidance** for the learner
without revealing the answer or the outcome of the `✅ Verify` block.

## When to use

- After `progress-tracker.get` resolves the current lab
- Whenever the learner asks "what's next?", "how do I…", or "I'm stuck on step N"

## Behavior

1. Read the lab file at `labs/<phase>/<lab>.md`.
2. Identify:
   - The `🎯 Goal` (1–2 sentences)
   - The current step the learner is on (ask if unknown)
   - The **next atomic action** in the `📋 Steps` list
3. Produce guidance that:
   - Restates the goal in one line
   - Names the current step without pasting the entire step body
   - Asks a small, checkable question ("what do you see when you open X?")
   - Points to the relevant callout (`💡 Tip` or `⚠️ Gotcha`) if applicable

## Do not

- Do **not** paste the full step body or code block.
- Do **not** describe what the `✅ Verify` output looks like.
- Do **not** perform the step for the learner.
- Do **not** invoke `verify-check` — the learner requests that explicitly.

## Output template

```
🧭 You're on **<phase>/<lab>** — <one-line goal>.
Current step: **<step N>** — <step title>.
Before you do it, quick check: <one small question>?
```
