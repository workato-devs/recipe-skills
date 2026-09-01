# CLI Workflow: `wk` and the Recipe Linter

How to validate and deploy recipe JSON using the `wk` CLI and the `recipe-lint` plugin, once a recipe has been generated using this skill (or a connector skill that extends it).

## Daily Workflow

```bash
# 1. Write or generate a recipe (manually, or via an agent with a skill loaded)

# 2. Lint it
wk lint my-recipe.recipe.json --skills-path /path/to/recipe-skills/skills

# 3. Fix any diagnostics, then push
wk push
```

The pre-push hook automatically lints all `.recipe.json` files in the push set. If any rule at `error` level fails, the push is blocked.

**The pre-push hook does not pass `--skills-path` automatically.** For connector-aware linting on push, either configure the skills path as part of the project's own workflow, or run `wk lint --skills-path ...` on demand before pushing.

---

## What the Linter Validates

4 tiers, all run by default; use `--tiers 0,1` to run a subset.

### Tier 0: Schema Validation (raw JSON)

| Rule | Level | What It Checks |
|------|-------|----------------|
| `INVALID_JSON` | error | Recipe file is valid JSON |
| `CODE_WRAPPED_IN_RECIPE` | error | Top-level has no `"recipe"` wrapper key |
| `MISSING_TOP_LEVEL_KEYS` | error | Required keys present: `name`, `version`, `private`, `concurrency`, `code`, `config` |
| `CODE_NOT_OBJECT` | error | `"code"` value is a JSON object, not array |
| `CONFIG_INVALID` | error | `"config"` is an array of objects with `keyword: "application"` |
| `STEP_MISSING_KEYWORD` | error | Every step has a `"keyword"` field |
| `STEP_MISSING_NUMBER` | error | Every step has a `"number"` field |
| `NUMBER_NOT_INTEGER` | error | Step `"number"` is a JSON number, not a string |
| `STEP_MISSING_UUID` | error | Every step has a `"uuid"` field |
| `UUID_TOO_LONG` | error | UUID is 36 characters or fewer |

If Tier 0 produces any errors, the linter stops — later tiers need a parseable recipe.

### Tier 1: Step-Level Rules

Validates individual steps, connector action names, formulas, datapills, and extended schemas. **This is where each connector skill's `lint-rules.json` is used.**

| Rule | Level | What It Checks |
|------|-------|----------------|
| `ACTION_NAME_VALID` | error | Action `name` is in the connector's `valid_action_names` from `lint-rules.json` |
| `STEP_NUMBERING` | warn | Steps numbered sequentially: 0, 1, 2, ... |
| `UUID_UNIQUE` | error | No duplicate UUIDs |
| `UUID_DESCRIPTIVE` | warn | UUID is not a standard v4 hex UUID |
| `TRIGGER_NUMBER_ZERO` | error | Trigger step has `number: 0` |
| `FILENAME_MATCH` | warn | Recipe `name` matches the filename |
| `CONFIG_NO_WORKATO` | warn | `"workato"` is not listed as a config provider |
| `CONFIG_PROVIDER_MATCH` | warn | Every step's `provider` appears in the config section |
| `NO_ELSIF` | error | No `elsif` keyword (use nested if/else instead) |
| `IF_NO_PROVIDER` / `ELSE_NO_PROVIDER` / `CATCH_PROVIDER_NULL` | warn | Control-flow steps have no `provider` |
| `CATCH_HAS_AS` | warn | `catch` steps have a non-empty `as` field |
| `CATCH_HAS_RETRY` | info | `catch` input has `max_retry_count` |
| `RESPONSE_CODES_DEFINED` | info | API platform triggers define response codes |
| `FORMULA_METHOD_INVALID` | warn | Formula methods are in the supported allowlist |
| `FORMULA_FORBIDDEN_PATTERN` | warn | No forbidden formula patterns (e.g., `.parse_json['key']`) |
| `DP_VALID_JSON` | error | Datapill `_dp()` payload is valid JSON |
| `DP_LHS_NO_FORMULA` | warn | Condition LHS uses datapill, not formula-mode expression |
| `DP_INTERPOLATION_SINGLE` | warn | Single datapills use `#{}` interpolation, not `=` formula mode |
| `DP_FORMULA_CONCAT` | warn | Concatenation expressions use `=` formula mode, not `#{}` |
| `DP_NO_OUTER_PARENS` | info | Formula-mode expressions don't have outer parentheses wrapping |
| `DP_NO_BODY_NATIVE` | warn | Native connector datapills don't use `["body"]` wrapper |
| `DP_CATCH_PROVIDER` | warn | Catch-block datapills use `"provider": "catch"` |
| `EIS_MIRRORS_INPUT` | warn | `extended_input_schema` fields match `input` keys |
| `EIS_NESTED_MATCH` | warn | Nested `input` objects have matching nested `properties` in EIS |
| `EIS_NAME_MATCH` | warn | EIS field names exactly match input field names |
| `EIS_NO_CONNECTOR_INTERNAL` | warn | Connector-internal fields (from `connector_internals` in `lint-rules.json`) are not in EIS |

### Tier 2: Structure Rules (control-flow graph analysis)

| Rule | Level | What It Checks |
|------|-------|----------------|
| `CATCH_LAST_IN_TRY` | error | Catch block is the last child in its try block |
| `ELSE_LAST_IN_IF` | error | Else block is the last child in its if block |
| `SUCCESS_BEFORE_CATCH` | warn | Success (2xx) responses are in try body, not catch block |
| `TERMINAL_COVERAGE` | warn | Every declared response code has a corresponding `return_response` |
| `ALL_PATHS_RETURN` | warn | Every control flow path terminates with `return_response` or `return_result` |
| `CATCH_RETURNS_ALL_FIELDS` | warn | Catch-path return responses include all required response body fields |
| `RECIPE_CALL_ZIP_NAME` | warn | Recipe function calls include `input.flow_id.zip_name` |

### Tier 3: Data Flow Rules (cross-step datapill resolution)

| Rule | Level | What It Checks |
|------|-------|----------------|
| `DP_LINE_RESOLVES` | warn | Datapill `line` field matches an actual step `as` alias |
| `DP_PROVIDER_MATCHES` | warn | Datapill `provider` matches the referenced step's actual provider |
| `DP_STEP_REACHABLE` | warn | Referenced step executes before the consuming step in control flow |
| `DP_TRIGGER_PATH` | info | API endpoint trigger datapill paths start with `"request"` |

The linter does **not** read `SKILL.md`, `validation-checklist.md`, templates, or patterns — only `lint-rules.json`. Those other files are for agent/human consumption, not the linter.

---

## Configuration (Optional)

`.wklintrc.json` in the project root overrides rule severities or ignores files:

```json
{
  "version": "1",
  "profile": "standard",
  "rules": { "UUID_DESCRIPTIVE": "off", "FILENAME_MATCH": "off" },
  "ignore_files": ["*.template.json"]
}
```

Pass explicitly with `--config-path .wklintrc.json`. Two bundled profiles: `standard` (structural rules error, most others warn) and `strict` (escalates `ACTION_NAME_VALID`, `FORMULA_METHOD_INVALID`, `EIS_MIRRORS_INPUT`, `ALL_PATHS_RETURN`, `TERMINAL_COVERAGE`, `DP_LINE_RESOLVES`, `DP_PROVIDER_MATCHES`, `DP_STEP_REACHABLE`, and others to errors). Severity precedence, lowest to highest: bundled profile → project profile (`.wklint/profiles/`) → `.wklintrc.json`.

---

## Provider Names

Use the exact provider string from the recipe JSON when a `wk` command requires one:

| Provider | Value |
|----------|-------|
| Salesforce | `salesforce` |
| Stripe | `stripe` |
| Slack (native) | `slack` |
| Slack (Workbot) | `slack_bot` |
| Gmail | `gmail` |
| Jira | `jira` |
| Asana | `asana` |
| Google Sheets | `google_sheets` |
| Generic REST | `rest` |

---

## Useful Commands

```bash
wk lint my-recipe.recipe.json --skills-path /path/to/recipe-skills/skills
wk lint recipes/*.recipe.json --skills-path /path/to/recipe-skills/skills
wk lint my-recipe.recipe.json --tiers 0,1                     # fast, no graph analysis
wk lint my-recipe.recipe.json --profile strict --skills-path /path/to/recipe-skills/skills

wk push                        # pre-push hook runs automatically

wk recipes list
wk recipes export <id> --json
wk recipes import my-recipe.recipe.json --folder <folder-id>
wk recipes update <id> <file>  # replaces an EXISTING recipe's code/config; recipe must be stopped first
wk recipes start <id>
wk recipes stop <id>
```

For MCP server / Agent Studio-specific CLI gotchas (agentic skills, MCP tool wiring), see the separate `mcp-server-recipes` skill — not duplicated here since it's specific to that trigger type, not general CLI usage.
