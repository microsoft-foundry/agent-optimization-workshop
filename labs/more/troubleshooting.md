# Lab — Troubleshoot a failing trace

> **What you'll do:** Take a specific failing trace apart span by span and identify the root cause.
> **Time:** ~20 min · **Prerequisites:** [Core Lab 04](../core/04-monitor-portal.md)

## 🎯 Goal

Practice the debugging loop: symptom → suspicious span → hypothesis → test.

## 🧭 Where this fits

```mermaid
flowchart LR
    Monitor([Monitor]):::active --> Optimize --> Evaluate
    classDef active fill:#0ea5e9,stroke:#0369a1,color:#fff;
```

## 📋 Steps

<!-- TODO(nitya): flesh out with concrete failing-trace examples once
     baseline traces are captured from Core Lab 01. -->

1. Open Tracing and filter for `status = error` or long latency.
2. Pick one trace. Expand every span.
3. Form a hypothesis about the root cause.
4. Test the hypothesis by replaying the same prompt with a small variation.

## ✅ Verify

You can point at **one specific span** and explain what went wrong there.

## 🧠 Recap

- Failures live in spans, not "the agent."
- One-variable changes prove hypotheses; many-variable changes prove nothing.

## ➡️ Next

**[Back to More Labs](./README.md)**
