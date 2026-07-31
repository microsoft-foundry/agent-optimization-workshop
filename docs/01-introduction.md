# 1. Introduction

## Why optimize agents?

Most agents ship on "it seemed to work on my prompt." That's not a strategy —
it's a coin flip. Optimization means making the agent measurably better on a
task you care about, without regressing on the ones you already handle.

## What we mean by "optimize"

Any change that improves your target metrics on a held-out evaluation set:

- **Prompt** — instructions, few-shot examples, output schema
- **Tools** — which tools exist, their names, descriptions, and schemas
- **Model** — capability, latency, and cost trade-offs
- **Context** — retrieval, memory, and grounding
- **Control flow** — planning, reflection, guardrails

## Success criteria for this workshop

By the end you will have:

- A baseline agent with a documented task
- An evaluation set and harness you can rerun in one command
- At least one optimized variant that wins on your metrics
- A clear rationale for why it won

## TODO

- Add a concrete example task (e.g., structured extraction, Q&A over docs)
- Add screenshots of a sample trace
