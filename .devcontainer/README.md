# Devcontainer

Reproducible dev environment for the workshop.

- **Base image:** `mcr.microsoft.com/devcontainers/python:1-3.13-bookworm`
- **Customization:** all in [`Dockerfile`](./Dockerfile) — edit here to add
  system packages, CLIs, or tools.
- **First-run setup:** all in [`post-create.sh`](./post-create.sh) — edit here
  to add Python deps, `azd` extensions, one-time verifications.

Rebuild the container after editing either file: **VS Code → Command Palette →
Dev Containers: Rebuild Container.**

## What's installed

| Tool | Purpose |
|------|---------|
| Python 3.13 | Runtime |
| `az` (Azure CLI) | Authentication, resource inspection |
| `azd` (Azure Developer CLI) | Provisioning + hosted agent deploy |
| `gh` (GitHub CLI) | Repo operations |
| `jq`, `zip`, `unzip` | Shell utilities |

## Persistent coach state

Coach progress lives at `~/.contoso-coach/progress.json`. The devcontainer
mounts a named volume there so bookmarks and completion history survive
container rebuilds.
