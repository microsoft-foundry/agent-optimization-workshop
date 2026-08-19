# Lab 05 — Deploy the Hosted Agent

> **What you'll do:** Deploy the containerized **Contoso Travel Concierge** hosted agent to Foundry.
> **Time:** ~10 min · **Prerequisites:** [Lab 03](./03-deploy-models.md)

## 🎯 Goal

Get the hosted agent (multi-agent orchestrator in `src/`) live in Foundry so
Core Lab 05 (the capstone) has something to observe, evaluate, and optimize.

## 🧭 Where this fits

```mermaid
flowchart LR
    Plan([Plan]) --> Build([Build]) --> Evaluate([Evaluate]) --> Deploy([Deploy]):::active --> Monitor([Monitor]) --> Optimize([Optimize]) --> Evaluate
    Monitor --> Protect([Protect]) --> Evaluate

    classDef active fill:#0ea5e9,stroke:#0369a1,color:#fff;
```

> 🧭 **This lab covers:** _Deploy_ — publishing a containerized agent to Foundry.

### 📍 You are here

```mermaid
flowchart LR
    L0["00<br/>overview"] --> L1["01<br/>azd"]
    L0 --> L2["02<br/>portal"]
    L1 --> L3["03<br/>models"]
    L2 --> L3
    L3 --> L4["04<br/>prompt agent"] --> L5["05<br/>hosted agent"]:::active --> L6["06<br/>verify"]
    classDef active fill:#0ea5e9,stroke:#0369a1,color:#fff;
```

## Before you start

The hosted agent is **not** deployed by `azd provision` in Lab 01 — that step
only stands up the Foundry substrate and models. Deploying the container is its
own deliberate step, which is what you do here.

The hosted agent is declared as a **service** in [`azure.yaml`](../../azure.yaml)
(`host: azure.ai.agent`). Deploying it needs two things that Lab 01 didn't set
up: the `azure.ai.agents` **azd extension** (the CLI commands) and the
**hosted-agent hosting** infrastructure (a container registry + agent capability
host). You'll enable both below.

## 📋 Steps

> 🧭 **Path check — portal-first only.** If you provisioned via the portal
> (Lab 02) and this is your first `azd` step, run the linker script **once**
> before Step 1 so `azd provision` reuses your existing resource group
> instead of creating a second one:
>
> ```bash
> ./scripts/link-portal-rg.sh
> ```
>
> The script auto-discovers the RG, Foundry account, and project, then binds
> them into an `azd env` named `contoso-travel`. Idempotent — safe to re-run.
> **Skip this if you did Lab 01 (`azd`) already.**

1. **Make sure the hosted-agents extension is installed.**
   The `azd ai agent` commands and hosted `azd deploy` come from the
   **`azure.ai.agents`** azd extension. The workshop devcontainer installs it
   for you — but to check (and install if missing) manually:
   ```bash
   azd extension list --installed | grep azure.ai.agents \
     || azd extension install azure.ai.agents
   ```
   Keep it current with `azd extension upgrade azure.ai.agents`.

2. **Enable hosted-agent hosting and provision it.**
   The container registry and agent capability host aren't created by the
   default `azd provision` in Lab 01. Turn them on, then provision:
   ```bash
   azd env set ENABLE_HOSTED_AGENTS true
   azd provision
   ```
   This adds the registry + capability host to your existing resource group.

   > ⚠️ **Gotcha — `invalid character 'n' after object key:value pair`.**
   > A stale `AI_PROJECT_DEPLOYMENTS` env value breaks `azd provision`. Clear
   > it with `azd env set AI_PROJECT_DEPLOYMENTS "[]"` and re-run. Details in
   > [Troubleshooting · `invalid character 'n'`](../TROUBLESHOOTING.md#azd-provision-fails-with-invalid-character-n-after-object-keyvalue-pair).

3. **Deploy the hosted agent.**
   ```bash
   azd deploy contoso-travel-concierge
   ```
   `azd` reads the `contoso-travel-concierge` service in
   [`azure.yaml`](../../azure.yaml), zips `src/`, and lets Foundry build and
   publish it. Wait for it to report **Ready**.

   <!-- TODO(nitya): screenshot of a successful `azd deploy contoso-travel-concierge` -->

4. **Check that `azd` sees the hosted agent.**
   ```bash
   azd ai agent show contoso-travel-concierge
   ```
   You should see the agent name, endpoint, status **Ready**, and the model
   deployment it uses.

5. **Look at what was deployed.**
   ```bash
   ls src/
   ```
   Everything in `src/` is what shipped inside the container:
   - `main.py` — Agent Framework orchestrator + specialist tools
   - `agent.yaml` — hosted-agent descriptor (protocol, resources, env vars)
   - `instructions/concierge.md` — the **active** concierge system prompt
     (loaded at container startup)
   - `instructions/versions/instructions-0.md` — the immutable baseline seed
   - `data/*.csv` — the Contoso datasets bundled into the image

6. **Invoke it once.**
   ```bash
   azd ai agent invoke contoso-travel-concierge \
     '{"input": "What business-class flights leave Chicago for Rome?"}'
   ```
   You should get a JSON response with a grounded answer.

   <!-- TODO(nitya): screenshot of a successful `azd ai agent invoke` output -->

7. **Open it in the playground.**
   In the Foundry portal → **Build → Agents → contoso-travel-concierge → Try in
   playground**. Ask the same question. Same answer, richer trace.

> 🧭 **No portal path?** Correct — the current Foundry portal can **view and
> manage** hosted agents but does not have a *create* flow for them. `azd
> deploy` is the one supported way to publish a hosted agent today.

> ⚠️ **Gotcha — 409 Conflict on `azd deploy`.** Stale Foundry data-plane
> state after a torn-down deploy. Recovery needs a fresh `azd env` name.
> Details in [Troubleshooting · 409 Conflict](../TROUBLESHOOTING.md#409-conflict-on-azd-deploy).

> ⚠️ **Gotcha — 404 `Subdomain does not map to a resource` on `azd deploy`.**
> Stale bearer token (not the resource). Re-auth **both** `az` and `azd`.
> Details in [Troubleshooting · 404 Subdomain does not map](../TROUBLESHOOTING.md#404-subdomain-does-not-map-to-a-resource-on-azd-deploy).

## Redeploying after a code change

Any time you edit `src/main.py` or `src/instructions/concierge.md`:

```bash
azd deploy contoso-travel-concierge --no-prompt
```

To go back to the pristine baseline first:

```bash
./scripts/reset.sh
```

## ✅ Verify

- `azd ai agent show contoso-travel-concierge` prints status **Ready** with an endpoint URL.
- The Foundry portal shows the agent under **Build → Agents** with type **Hosted**.
- A single `invoke` (curl or `azd ai agent invoke`) returns a grounded JSON response.

## 🧠 Recap

- The hosted agent is a **container** whose image was built from `src/` and
  published to Foundry.
- The concierge system prompt lives in a file (`src/instructions/concierge.md`)
  so it can evolve independently of code.
- `azd deploy` is your redeploy loop; `./scripts/reset.sh` is your undo.

## ➡️ Next

**[Lab 06 — End-to-end verification](./06-verify.md)**
