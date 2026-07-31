# Skill — resume

## Purpose

Restore the learner's last bookmark and re-anchor them in the workshop.

## When to use

- The learner says "resume", "back to where I was", "let's continue", or similar
- After an exploratory detour concludes

## Behavior

1. Call `progress-tracker.pop_bookmark()`.
2. If no bookmark exists, fall back to `progress-tracker.get().current`.
3. Call `lab-guide` to produce a fresh next-step prompt for that lab.
4. Restate:
   - The lab's `🎯 Goal` in one line
   - The step the learner was on
   - The next small question

## Do not

- Do **not** skip labs or mark anything complete on resume.
- Do **not** repeat the entire lab back — just the anchor and next step.

## Output template

```
🔙 Back on **<phase>/<lab>** — <one-line goal>.
You were on step **<N>**. Next: <one small question or action>.
```
