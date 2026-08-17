# Workshop Troubleshooting

Canonical home for **detailed** gotchas — infra and tool errors that recur
across labs or need multi-step recovery. Individual lab files keep short
`> ⚠️ **Gotcha:** …` callouts and link here for the full recipe.

> 💡 **Authoring convention.** See [`labs/_template/lab-template.md`](./_template/lab-template.md)
> and the "Callout conventions" section in [`AGENTS.md`](../AGENTS.md).
> Small, lab-specific mistakes stay inline. Anything recurring, cross-cutting,
> or > 5 lines lives here — one section per issue.

Every section below follows the same template:

- **Symptom** — the exact error message (or the observable behavior).
- **Cause** — what's really going on.
- **Fix** — the commands / clicks that unblock.
- **Prevent** — optional; how to avoid hitting it again.

---

## Provisioning (`azd provision`)

### Soft-deleted Cognitive Services account blocks re-provision

**Symptom.** `azd provision` fails with:

```text
ERROR: A soft-deleted resource with this name exists and is blocking deployment.
...
FlagMustBeSetForRestore: An existing resource with ID
'/subscriptions/…/providers/Microsoft.CognitiveServices/accounts/<name>'
has been soft-deleted.
```

`azd`'s hint text incorrectly labels this *"Azure Key Vault soft-delete
recovery"* — the inner error names the real resource type (most often a
Cognitive Services / Foundry account).

**Cause.** A previous run (or a deleted Codespace) tore the Foundry account
down; it remains in soft-delete for the retention window and blocks a
same-name re-provision.

**Fix (A — purge, then re-provision):**

```bash
az cognitiveservices account list-deleted -o table

az cognitiveservices account purge \
  --location <region> \
  --resource-group <rg> \
  --name <account-name>

azd provision
```

Purge needs `Microsoft.CognitiveServices/locations/deletedAccounts/delete` —
plain **Contributor** may not suffice. If you hit `AuthorizationFailed`, ask a
subscription **Owner** to purge (or use Fix B).

**Fix (B — sidestep with a fresh env name):**

```bash
azd env new contoso-travel-$(date +%m%d)
azd provision
```

A new env name changes the synthesized resource names, so the collision
disappears.

**Prevent.** `azd down --purge --force` purges the account as it tears down.
The trap is losing a Codespace (or the `.azure/` folder) before purging.

---

### `azd provision` fails with `invalid character 'n' after object key:value pair`

**Symptom.** `azd provision` fails immediately with:

```text
invalid character 'n' after object key:value pair
```

**Cause.** The four `*Json` params in `infra/main.parameters.json`
(`AI_PROJECT_DEPLOYMENTS`, `AI_PROJECT_CONNECTIONS`,
`AI_PROJECT_CREDENTIALS`, `AI_PROJECT_DEPENDENT_RESOURCES`) are
quoted-string substitutions like `"value": "${AI_PROJECT_DEPLOYMENTS=[]}"`.
azd 1.30 does not JSON-escape embedded `"` on substitution, so any
non-empty override breaks the parameters file.

**Fix.** Reset the override to `[]`; the defaults in `infra/main.bicep` still
deploy `gpt-5.4-mini` + `gpt-5.4-judge`:

```bash
azd env set AI_PROJECT_DEPLOYMENTS "[]"
azd provision
```

**Prevent.** Only set `AI_PROJECT_DEPLOYMENTS` (etc.) when you actually need
a non-default deployment set, and clear it before re-provisions that add
resources (e.g. enabling hosted agents in Lab 05). Structural fix tracked as
`TODO(nitya)` in `infra/main.bicep`: change the four params to `array` /
`object` types, drop the `json()` calls, and substitute without surrounding
quotes.

---

### Quota / capacity errors on `azd provision` or model deploy

**Symptom.** Either:

- `azd provision` fails with a quota / capacity error, or
- In the portal, the **Deploy** button on the model card is greyed out.

**Cause.** Your subscription doesn't have the requested capacity for the
target model in the target region.

**Fix.** Switch to a region with headroom (from the supported list):

```bash
azd env set AZURE_LOCATION swedencentral   # or northcentralus
azd provision
```

For the portal path: pick a different region on the model card, or open
**Management center → Quota** in Foundry and request an increase.

**Prevent.** Pre-flight the quota before provisioning — see the workshop's
pre-flight step 0.4 and the `microsoft-foundry` `quota` skill.

---

### `azd provision` reports `no project exists — run 'azd init'`

**Symptom.**

```text
ERROR: no project exists; to create a new project, run 'azd init'
```

**Cause.** You're running `azd` from a folder that doesn't contain
`azure.yaml`.

**Fix.** `cd` to the repo root (the folder that has `azure.yaml`) and re-run.

---

## Hosted-agent deploy (`azd deploy`)

### 409 Conflict on `azd deploy`

**Symptom.**

```text
RESPONSE 409: 409 Conflict … The resource already exists or was modified
concurrently. Please retry.
```

A plain retry doesn't clear it. The portal Agents blade may also show
*"Project not found"*. `azd ai agent doctor` finds nothing.

**Cause.** The Foundry agents data plane is holding a stale registration
keyed on the current project/agent name — even after a torn-down deploy.

**Fix.**

```bash
azd down --purge --force              # tear down + purge soft-delete
azd env new contoso-travel-v2         # any new name → new account+project hash
azd env set ENABLE_HOSTED_AGENTS true
azd provision
azd deploy contoso-travel-concierge
```

The new env name changes the `uniqueString()` hash used by the infra, giving
you a genuinely fresh Foundry project and clearing the cache.

---

### 404 `Subdomain does not map to a resource` on `azd deploy`

**Symptom.**

```text
RESPONSE 404: ResourceNotFound — Subdomain does not map to a resource
```

**Cause.** The Foundry agents data plane returns 404 (not 401) when the
caller's bearer token is expired or revoked — typically `AADSTS50173` after
a password change, credential rotation, or Conditional Access policy update
that moved `TokensValidFrom` past your issued-at time. The account is fine;
auth is stale.

**Fix.** `az` and `azd` cache tokens independently, so **both** must be
refreshed:

```bash
az logout && az login --tenant <your-tenant-id>
azd auth logout && azd auth login --tenant-id <your-tenant-id>
azd deploy contoso-travel-concierge
```

Quick sanity check that the resource itself is healthy (returns HTTP 200
even unauthenticated):

```bash
curl -sS -o /dev/null -w "%{http_code}\n" \
  "https://$(azd env get-value AZURE_AI_ACCOUNT_NAME).services.ai.azure.com/"
```

---

### `refresh token has expired due to inactivity` on `azd deploy`

**Symptom.**

```text
AzureDeveloperCLICredential: … The refresh token has expired due to
inactivity. The token was issued on <date> and was inactive for 90.00:00:00.
```

**Cause.** `azd`'s cached refresh token wasn't used within its inactivity
window (90 days).

**Fix.** Same recovery as the 404 above — refresh **both** `az` and `azd`
independently. See the 404 section for the commands.

---

## Auth & RBAC

### Missing RBAC roles for hosted-agent deploy

**Symptom.** `azd deploy` returns an authorization error even though `az`
and `azd` are freshly logged in; or `azd provision` succeeds but a later
step (e.g. Prompt Optimizer, LLM-judge evaluators) fails with a permissions
error.

**Cause.** `azd provision` assigns the roles the deploying user and the
project's managed identity need. If the caller lacked
`User Access Administrator` on the RG at provision time, the role
assignments in `infra/core/ai/ai-project.bicep` were silently skipped.

**Required roles.** Grounded in `infra/core/ai/ai-project.bicep`:

*Provision-time (the user running `azd provision`), on the subscription or RG:*

| Role | Why |
|------|-----|
| **Owner** *or* **Contributor** + **User Access Administrator** | Needed to create resources **and** create role assignments |

*Data-plane (the user running `azd deploy`), auto-granted on the Foundry account:*

| Role | Role definition ID | Why |
|------|--------------------|-----|
| **Azure AI User** (aka Foundry User) | `53ca6127-db72-4b80-b1b0-d745d6d5456d` | Auth to the project endpoint |
| **Azure AI Project Manager** | `eadc314b-1a2d-4efa-be10-5d325db5065e` | Create / update / delete hosted agents |
| **Cognitive Services OpenAI Contributor** | `a001fd3d-188f-4b5d-821b-7da978bf7442` | Prompt Optimizer (Core 03) |

The project's system-assigned managed identity also gets
**Cognitive Services OpenAI User** and **Azure AI User** on the account for
hosted-agent inference and LLM-judge evaluators.

**Check (CLI):**

```bash
ME=$(az ad signed-in-user show --query id -o tsv)
ACCOUNT_ID=$(az cognitiveservices account show \
  -g "$AZURE_RESOURCE_GROUP" -n "$AZURE_AI_ACCOUNT_NAME" --query id -o tsv)
az role assignment list --assignee "$ME" --scope "$ACCOUNT_ID" \
  --query "[].{role:roleDefinitionName, scope:scope}" -o table
```

Expected rows include `Azure AI User`, `Azure AI Project Manager`, and
`Cognitive Services OpenAI Contributor`.

**Check (portal).** Foundry account → **Access control (IAM)** →
**Role assignments** → filter by your UPN. Same three roles.

**Fix.** Ask a subscription Owner to assign the three roles at the Foundry
account scope, or re-run `azd provision` as an Owner.

---

## Mixed provisioning paths

### UI provision + CLI deploy creates a second resource group

**Symptom.** You provisioned via the portal (Lab 02), then ran
`azd env new … && azd provision` in Lab 05 — and Azure now shows **two**
resource groups (the portal RG + `rg-<new-env-name>`).

**Cause.** `azd env new` doesn't discover existing portal-created resources.
Without `AZURE_RESOURCE_GROUP` (and the Foundry account/project) seeded into
the env, `azd provision` synthesizes fresh names and creates a second RG.

**Fix.** Run the linker script **once** before your first `azd` step:

```bash
./scripts/link-portal-rg.sh
```

The script (idempotent) auto-discovers the portal-created RG, Foundry
account, and project, then seeds the `azd env` with `AZURE_RESOURCE_GROUP`,
`AZURE_AI_ACCOUNT_NAME`, `AZURE_AI_PROJECT_NAME`, and
`USE_EXISTING_AI_PROJECT=true`. After that, `azd provision` reuses the
portal RG.

**Prevent.** If you took the portal path in Lab 02, always run the linker
before your first `azd env new … && azd provision`.

---

## Notes

- Single-turn agent behavior failures (evaluator score anomalies, wrong
  specialist, hallucinated IDs) live in
  [`labs/more/troubleshooting.md`](./more/troubleshooting.md) — that's a
  diagnosis lab, not an infra reference.
- Report new gotchas by opening an issue or adding a section here following
  the Symptom / Cause / Fix / Prevent template.
