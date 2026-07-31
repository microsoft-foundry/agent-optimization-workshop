# Skill — explore-suggest

## Purpose

Offer 2–3 tangential, high-value prompts anchored to the learner's current
lab, so exploratory curiosity stays connected to the workshop.

## When to use

- After answering an exploratory question
- After a `bookmark` call, before ending the turn
- Whenever the coach's reply is not tied to a specific step in the current lab

## Behavior

1. Look up the current lab's `🎯 Goal` and the DevOps-loop node it covers.
2. Generate 2–3 questions the learner *could* ask next that would deepen their
   understanding of the same or an adjacent node.
3. Always end with a one-line reminder pointing back to the bookmark.

## Do not

- Do **not** suggest anything that would give away the current lab's answer.
- Do **not** suggest more than 3 items — cognitive load.
- Do **not** suggest jumping to a different phase without a bookmark in place.

## Output template

```
💡 You could also ask:
- <question 1>
- <question 2>
- <question 3>

🔖 When you're ready: **resume** to go back to <phase>/<lab>.
```
