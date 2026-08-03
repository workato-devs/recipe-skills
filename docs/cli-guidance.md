# wk CLI + Recipe Lint Guide

How the `wk` CLI, the `recipe-lint` plugin, and recipe-skills work together for recipe development.

---

## Setup

### Install the wk CLI

```bash
go install github.com/workato-devs/wk-cli-beta/cmd/wk@latest
```

### Install the Recipe Lint Plugin

```bash
wk plugins install github.com/workato-devs/wk-lint-beta@latest
```

### Clone Recipe Skills

```bash
git clone https://github.com/workato/recipe-skills.git
```

This registers two capabilities:
- **`wk lint`** command -- run the linter on-demand
- **`pre-push` hook** -- automatically lint `.recipe.json` files before `wk push`

### No Other Configuration Required

Once the plugin is installed and you have a local clone of recipe-skills, you're ready to develop. There is no per-project setup, environment variable, or config file required to get started.

---

## Daily Workflow

```bash
# 1. Write or generate a recipe
#    (manually, or via an AI agent with a skill loaded)

# 2. Lint it
wk lint my-recipe.recipe.json --skills-path /path/to/recipe-skills/skills

# 3. Fix any diagnostics, then push
wk push
```

The pre-push hook automatically lints all `.recipe.json` files in the push set. If any rule at `error` level fails, the push is blocked.

---

## What the Linter Validates

The linter runs 4 tiers of checks. By default all tiers run; use `--tiers 0,1` to run a subset.

### Tier 0: Schema Validation (raw JSON)

Catches malformed recipe structure before parsing.

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

If Tier 0 produces any errors, the linter stops (later tiers need a parseable recipe).

### Tier 1: Step-Level Rules (parsed recipe + connector rules)

Validates individual steps, connector action names, formulas, datapills, and extended schemas. **This is where `lint-rules.json` from recipe-skills is used.**

| Rule | Level | What It Checks |
|------|-------|----------------|
| `ACTION_NAME_VALID` | error | Action `name` is in the connector's `valid_action_names` from `lint-rules.json` |
| `STEP_NUMBERING` | warn | Steps numbered sequentially: 0, 1, 2, ... |
| `UUID_UNIQUE` | error | No duplicate UUIDs |
| `UUID_DESCRIPTIVE` | warn | UUID is not a standard v4 hex UUID (should be descriptive like `search-contact-001`) |
| `TRIGGER_NUMBER_ZERO` | error | Trigger step has `number: 0` |
| `FILENAME_MATCH` | warn | Recipe `name` matches the filename |
| `CONFIG_NO_WORKATO` | warn | `"workato"` is not listed as a config provider |
| `CONFIG_PROVIDER_MATCH` | warn | Every step's `provider` appears in the config section |
| `NO_ELSIF` | error | No `elsif` keyword (use nested if/else instead) |
| `IF_NO_PROVIDER` | warn | `if` steps have no provider |
| `ELSE_NO_PROVIDER` | warn | `else` steps have no provider |
| `CATCH_PROVIDER_NULL` | warn | `catch` steps have no provider |
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

### Tier 2: Structure Rules (inter-step graph analysis)

Validates control flow structure and return path completeness using an intermediate graph model (IGM).

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

Validates that datapill references resolve to real steps and are reachable in the control flow.

| Rule | Level | What It Checks |
|------|-------|----------------|
| `DP_LINE_RESOLVES` | warn | Datapill `line` field matches an actual step `as` alias |
| `DP_PROVIDER_MATCHES` | warn | Datapill `provider` matches the referenced step's actual provider |
| `DP_STEP_REACHABLE` | warn | Referenced step executes before the consuming step in control flow |
| `DP_TRIGGER_PATH` | info | API endpoint trigger datapill paths start with `"request"` |

---

## How the Linter Uses Recipe Skills

When you pass `--skills-path`, the linter walks the directory tree for `lint-rules.json` files. Each file declares a connector name and its valid actions:

```json
{
  "connector": "salesforce",
  "valid_action_names": ["upsert_sobject", "search_sobjects", ...],
  "connector_internals": ["sobject_name", "limit"]
}
```

The linter uses this data for three rules:
- **`ACTION_NAME_VALID`** -- rejects action names not in `valid_action_names` for that provider
- **`CONFIG_PROVIDER_MATCH`** -- skips providers listed in `connector_internals`
- **`EIS_NO_CONNECTOR_INTERNAL`** -- flags connector-internal fields that appear in `extended_input_schema`

The linter does **not** read `SKILL.md`, `validation-checklist.md`, templates, or patterns. Those files are for AI agents and human developers, not the linter.

---

## Configuration (Optional)

### `.wklintrc.json`

Place in your project root to override rule severities or ignore files:

```json
{
  "version": "1",
  "profile": "standard",
  "rules": {
    "UUID_DESCRIPTIVE": "off",
    "FILENAME_MATCH": "off"
  },
  "ignore_files": [
    "*.template.json"
  ]
}
```

Pass it explicitly: `wk lint my-recipe.recipe.json --config-path .wklintrc.json`

### Profiles

The plugin bundles two profiles:

**`standard`** (default-like) -- most rules emit warnings, structural rules emit errors.

**`strict`** -- escalates key rules to errors: `ACTION_NAME_VALID`, `FORMULA_METHOD_INVALID`, `EIS_MIRRORS_INPUT`, `ALL_PATHS_RETURN`, `TERMINAL_COVERAGE`, `DP_LINE_RESOLVES`, `DP_PROVIDER_MATCHES`, `DP_STEP_REACHABLE`, and others.

Use a profile: `wk lint my-recipe.recipe.json --profile strict`

Project-level profiles can be placed in `.wklint/profiles/` and override or extend bundled profiles via the `extends` field.

### Severity Precedence

1. Bundled profile (lowest)
2. Project profile (`.wklint/profiles/`)
3. `.wklintrc.json` rules (highest -- always wins)

Set any rule to `"off"` to suppress it entirely.

---

## Pre-Push Hook

The `recipe-lint` plugin registers a `pre-push` hook. When you run `wk push`, the hook automatically:

1. Filters the push file set to `.recipe.json` files
2. Lints each recipe (all 4 tiers)
3. Blocks the push if any rule at `error` level fires

The hook does **not** pass `--skills-path` automatically. To get connector-aware linting on push, configure the skills path in your workflow or use on-demand `wk lint` with `--skills-path` before pushing.

---

## Provider Names

When using `wk` commands that require a provider name, use the exact provider string from the recipe JSON:

| Provider | Value |
|----------|-------|
| Salesforce | `salesforce` |
| Stripe | `stripe` |
| Slack (native) | `slack` |
| Slack (Workbot) | `slack_bot` |
| Gmail | `gmail` |
| Jira | `jira` |
| Asana | `asana` |
| Generic REST | `rest` |

---

## Useful Commands

```bash
# Lint a single recipe with connector rules
wk lint my-recipe.recipe.json --skills-path /path/to/recipe-skills/skills

# Lint multiple recipes
wk lint recipes/*.recipe.json --skills-path /path/to/recipe-skills/skills

# Run only Tier 0 + 1 (fast, no graph analysis)
wk lint my-recipe.recipe.json --tiers 0,1

# Use strict profile
wk lint my-recipe.recipe.json --profile strict --skills-path /path/to/recipe-skills/skills

# Push (pre-push hook runs automatically)
wk push

# Other recipe commands
wk recipes list
wk recipes export <id> -o recipe.json
wk recipes import my-recipe.recipe.json
wk recipes start <id>
wk recipes stop <id>
```
