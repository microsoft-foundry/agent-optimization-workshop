# `src/` — Contoso Travel Concierge (hosted agent)

This is the **working copy** of the hosted agent. Learners edit files here
during the labs (especially `instructions/concierge.md` in Core Lab 3).

To restore the pristine baseline at any time:

```bash
./scripts/reset.sh
```

That copies `src.original/` back over `src/`.

## Layout

| Path | Role |
|---|---|
| `main.py` | Agent Framework orchestrator + specialist tools (flights/hotels/cars) |
| `agent.yaml` / `agent.manifest.yaml` | Hosted-agent deployment descriptors |
| `Dockerfile` | Container build for the Foundry runtime |
| `requirements.txt` | Python runtime deps |
| `data/*.csv` | Bundled copy of the Contoso datasets (same shape as repo-root `data/`) |
| `instructions/concierge.md` | **Active** concierge system prompt (loaded at startup) |
| `instructions/versions/instructions-0.md` | Immutable baseline seed |
| `instructions/versions/instructions-N.md` | Snapshots taken during Lab 3 |
| `scripts/reset-instructions.sh` | Reset the active prompt back to baseline |
| `scripts/snapshot-instructions.sh` | Snapshot the active prompt as the next version |

## Running locally

<!-- TODO(nitya): confirm the exact `azd ai agent run` incantation once
     provisioning is validated end-to-end. -->

```bash
azd ai agent run
```

See `../labs/fundamentals/05-deploy-hosted-agent.md` for the full deploy flow.
