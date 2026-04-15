# Workato CLI Guidance (Untracked)

> **Status:** Future/fast follow. This document captures CLI tips and workarounds discovered during testing. Not part of any skill yet — intended for potential inclusion later.

---

## Provider Names

When using `wk` CLI commands that require a provider name, use the exact provider string from the recipe JSON:

| Provider | CLI Value |
|----------|-----------|
| Generic REST connector | `--provider rest` |
| Salesforce | `--provider salesforce` |
| Stripe | `--provider stripe` |
| Slack Bot | `--provider slack_bot` |
| Gmail | `--provider gmail` |

---

## Known Workarounds

### `wk push` pre-push hook type mismatch

Pre-push hooks may fail with a type mismatch error. Workaround: use `--skip-hooks` flag.

```bash
wk push --skip-hooks
```

**Note:** This is a CLI plugin/interface bug. File with CLI team.

### `wk recipes start` returns 200 but recipe doesn't start

The CLI returns a 200 status immediately but the recipe may not actually start. Always verify recipe status after starting:

```bash
wk recipes start <recipe-path>
# Then verify:
wk recipes status <recipe-path>
```

**Note:** CLI should poll/report actual activation status. File with CLI team.

### `wk connectors list` is broken

`wk connectors list` fails with a JSON unmarshaling error. No workaround — use the Workato UI to view connectors.

**Note:** JSON unmarshaling bug in CLI. File with CLI team.

### Import failure messages lack detail

When `wk push` fails on import, the error message doesn't include specific validation details. Check the Workato UI for the actual import error.

**Note:** CLI should fetch and display error details. File with CLI team.

### Linter doesn't catch all formula errors (partial fix in progress)

The `wk` linter now validates:
- **Invalid action names** (e.g., `__adhoc_http_action` on a `rest` provider) — covered by `ACTION_NAME_VALID` rule via `valid_action_names` in connector `lint-rules.json`

The `wk` linter does **not yet** validate:
- Invalid formula methods (e.g., `now.utc`) — planned for Phase 2, allowlist-based validation against ~120 supported Workato methods
- `.parse_json['key']` bracket notation

Until formula validation ships, **only use methods from the [Supported Formula Methods allowlist](../skills/workato-recipes/SKILL_INSTRUCTIONS.md#supported-formula-methods-complete-allowlist)**. Invalid formulas block recipe activation with no clear error message.

**Note:** Formula linter tracked in `wk-lint-beta` ADR 0002.

---

## API Platform Commands

### Collections

```bash
# List all API collections
wk api collections list
wk api collections list --json

# Create a new API collection
wk api collections create --name "my-api" --version "1.0" --handle "my-api-v1"
```

### Endpoints

```bash
# List all API endpoints
wk api endpoints list
wk api endpoints list --json

# Enable/disable an endpoint
wk api endpoints enable <endpoint-id>
wk api endpoints disable <endpoint-id>
```

**Note:** After pushing a recipe with API endpoint artifacts, the endpoint must be enabled via `wk api endpoints enable` or the Workato UI before it will accept requests.

### Connections

```bash
# List connections
wk connections list
wk connections list --json

# Get connection details
wk connections get <connection-id>

# Create a connection (credentials configured separately)
wk connections create --name "My REST Connection" --provider rest

# Update/delete
wk connections update <connection-id> --name "New Name"
wk connections delete <connection-id>

# Disconnect (revoke auth, keep config)
wk connections disconnect <connection-id>
```

**Provider name gotcha:** Use `--provider rest` for the generic REST/HTTP connector (NOT `--provider http`). Provider names match the `provider` field in recipe JSON.

---

## wk-meta.json Artifact Types

The `wk` CLI generates `.wk-meta.json` sidecar files during pull. Known `type` values:

| Artifact | `type` value |
|----------|-------------|
| Recipe | `"recipe"` |
| Connection | `"connection"` |
| API Endpoint | `"unknown"` |
| API Collection | `"unknown"` |

**Note:** API endpoint and collection artifacts are stored as `type: "unknown"` — the CLI doesn't fully recognize these artifact types yet. This doesn't affect push/pull functionality.

---

## CLI Bug Tracker

| # | Issue | Status |
|---|-------|--------|
| 1 | `wk push` pre-push hook type mismatch | Workaround: `--skip-hooks` |
| 2 | `wk recipes start` returns 200 but recipe doesn't start | Workaround: verify after start |
| 3 | `wk connectors list` JSON unmarshaling error | No workaround |
| 4 | Import failure messages lack detail | Check Workato UI |
| 5 | Linter doesn't catch invalid actions/formulas | Action names fixed; formula validation in progress (ADR 0002) |
| 6 | `wk-meta.json` marks API endpoint/collection artifacts as `type: "unknown"` | Non-blocking — push/pull works, but lint/status can't operate on type |
| 7 | `wk api collections list` missing `handle`, `version`, `description` fields | Cannot determine endpoint URLs from CLI output alone |
| 8 | `wk api endpoints list` missing `method`, `path`, `recipe_id` fields | Cannot determine routing from CLI output alone |
