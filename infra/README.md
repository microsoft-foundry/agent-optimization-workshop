# `infra/` — Azure Bicep for the Contoso Travel Concierge workshop

This is the Bicep + parameters used by **`azd up`** during the self-guided
provisioning path (see `labs/fundamentals/01-provision-azd.md`).

If you're following the **portal path** instead
(`labs/fundamentals/02-provision-portal.md`), you don't need anything here.

## Layout

| Path | Role |
|---|---|
| `main.bicep` | Top-level template — Foundry project, hosting env, monitoring, search |
| `main.parameters.json` | `azd`-managed parameters (env-driven) |
| `abbreviations.json` | Azure resource-type abbreviations for naming |
| `core/ai/` | Foundry project + connections + role assignments |
| `core/host/` | Container registry for the hosted agent image |
| `core/monitor/` | Log Analytics + Application Insights + starter dashboard |
| `core/search/` | Azure AI Search + Bing grounding connections |
| `core/storage/` | Backing storage account |

## Notes

- Naming derives from the `azd` environment name; abbreviations come from
  `abbreviations.json`. This keeps every resource under a single prefix so
  cleanup is one `azd down` away.
- Model deployment is **not** provisioned by this template on purpose.
  Learners deploy models in `labs/fundamentals/03-deploy-models.md` so they
  learn the model-picker flow.

<!-- TODO(nitya): confirm region + SKU choices for the models you standardize on. -->
