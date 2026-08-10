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

## Before you start

The hosted agent is **not** deployed by `azd up` in Lab 01 — that step only
provisioned the Foundry substrate and models. Deploying the container is its own
deliberate step, which is what you do here.

The hosted agent is declared as a **service** in [`azure.yaml`](../../azure.yaml)
(`host: azure.ai.agent`). Deploying it needs two things that Lab 01 didn't set
up: the `azure.ai.agents` **azd extension** (the CLI commands) and the
**hosted-agent hosting** infrastructure (a container registry + agent capability
host). You'll enable both below.

## 📋 Steps — deploy with `azd`

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
   default `azd up`. Turn them on, then provision:
   ```bash
   azd env set ENABLE_HOSTED_AGENTS true
   azd provision
   ```
   This adds the registry + capability host to your existing resource group.

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

## 📋 Steps — deploying via the portal (portal path only)

1. **Open the portal → Build → Agents → + New agent → Hosted agent**.
2. Provide:
   - **Agent name:** `contoso-travel-concierge`
   - **Container image:** upload or point to a registry image built from `src/`
   - **Model deployment:** `gpt-5.4-mini` (from Lab 03)
3. Click **Deploy** and wait for status **Ready**.

<!-- TODO(nitya): screenshot of the portal hosted-agent deploy flow -->

> ⚠️ **Gotcha (portal path):** the container image must expose the Responses
> protocol on port 8088 — the shipped `Dockerfile` already does this. Build
> from `src/` unmodified for your first deploy.

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
