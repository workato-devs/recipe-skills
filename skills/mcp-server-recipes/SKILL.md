---
name: mcp-server-recipes
description: Build and wire Workato MCP servers and MCP Apps — tools callable over the Model Context Protocol by clients like Claude, plus interactive UI apps that render inside those clients. Covers the workato_skill trigger, manifest wiring, MCP App creation via the CLI, and the app-side JS SDK.
license: MIT
metadata:
  author: Workato
  version: "0.1.0"
---

# MCP Server Recipes Skill

> **DEPENDENCY: Load the `workato-recipes` base skill for general recipe JSON fundamentals** (recipe structure, datapills, formulas) if not already loaded. This skill covers everything specific to MCP: the trigger type, server wiring, and app creation.

Use this skill for any task involving: an MCP server, an MCP tool, an MCP App, connecting Claude (or another MCP client) to Workato, or anything using the `workato_skill` provider.

---

## The `workato_skill` Trigger

Use for recipes exposed as callable **MCP tools**. Sibling of the Genie Skill Trigger and Callable Recipe Trigger (documented in `workato-recipes`) — same general shape, different provider, different downstream wiring. Do not conflate the three.

| Field | Value |
|-------|-------|
| Provider | `workato_skill` |
| Trigger action | `start_workflow` |
| Return action | `workflow_return_result` |
| Config provider | `workato_skill` with `account_id: null` |

```json
{
  "as": "<8-char-hex>",
  "keyword": "trigger",
  "name": "start_workflow",
  "number": 0,
  "provider": "workato_skill",
  "uuid": "<uuid>",
  "description": "Start <span class=\"provider\">tool_name</span>",
  "input": {
    "description": "Plain-language description of what this tool does and when to call it.",
    "requires_user_confirmation": "false",
    "result_schema_json": "[{\"name\":\"final_message\",\"type\":\"string\",\"optional\":false,\"control_type\":\"text\",\"label\":\"Final message\"}]"
  },
  "block": [ /* action steps, then a workflow_return_result action */ ]
}
```

(Verified: golden recipes 278461, 278462, 278463, 278464, 309311, 310342, 314416, 314417.)

- `result_schema_json` declares exactly one field, `final_message` (string), in every golden recipe — treat multi-field results as unverified, not unsupported.
- `code.input.description` does **not** reach the MCP client — see "The description that actually matters" below.
- No verified error-return convention exists (unlike the Genie trigger's `success: false` pattern).

### Input Parameters

Supported via `parameters_schema_json`, same convention as the sibling Genie and callable-recipe triggers. (Verified: real `tools/call` argument round-tripped correctly; `tools/list`'s `inputSchema` correctly reflected the schema as JSON Schema, including hand-extending it for a column beyond the connector skill's audited set.)

```json
"input": {
  "description": "...",
  "parameters_schema_json": "[{\"name\":\"row_number\",\"label\":\"Row number\",\"type\":\"integer\",\"control_type\":\"number\",\"optional\":false},{\"name\":\"new_status\",\"label\":\"New status\",\"type\":\"string\",\"control_type\":\"text\",\"optional\":false}]",
  "result_schema_json": "[{\"name\":\"final_message\",\"type\":\"string\",\"optional\":false,\"control_type\":\"text\",\"label\":\"Final message\"}]"
},
"extended_output_schema": [
  {
    "label": "Parameters",
    "name": "parameters",
    "type": "object",
    "properties": [
      {"control_type": "number", "label": "Row number", "name": "row_number", "type": "integer", "optional": false},
      {"control_type": "text", "label": "New status", "name": "new_status", "type": "string", "optional": false}
    ]
  }
]
```

Read a parameter with:

```
#{_dp('{"pill_type":"output","provider":"workato_skill","line":"<trigger-as-id>","path":["parameters","row_number"]}')}
```

Plain `#{}` interpolation is fine for a direct reference; use formula mode (`=`) only when calling a method on the result (`.to_json`, `.strftime`, etc.).

---

## The description that actually matters

Three places can hold a description string; only one reaches the MCP client:

| Location | What it's for |
|---|---|
| `code.input.description` (recipe trigger) | Feeds the agentic skill's own metadata inside Workato. |
| `.agentic_skill.json`'s `trigger_description` | Mirrors the trigger's description; not independently authoritative. |
| **MCP server manifest's `tools[].description`** | **This is what `tools/list` returns to an MCP client.** |

```
WRONG — description only on the trigger:
code.input.description = "Returns all pipeline items..."
manifest.tools[0].description = ""              // tools/list returns "" — model can't tell when to call this tool

CORRECT — same text duplicated onto the manifest entry:
code.input.description = "Returns all pipeline items..."
manifest.tools[0].description = "Returns all pipeline items..."   // tools/list returns the real text
```

(Verified: `tools/list` returned `"description": ""` with the manifest field blank, then the real text after duplicating it.) **Always populate all three with the same text.**

---

## Returning a Result

```json
{
  "as": "<8-char-hex>",
  "keyword": "action",
  "name": "workflow_return_result",
  "number": 1,
  "provider": "workato_skill",
  "uuid": "<uuid>",
  "extended_input_schema": [
    {"label": "Response", "name": "result", "type": "object", "properties": [
      {"control_type": "text", "label": "Final message", "name": "final_message", "optional": false, "type": "string"}
    ]}
  ],
  "extended_output_schema": [
    {"label": "Response", "name": "result", "type": "object", "properties": [
      {"control_type": "text", "label": "Final message", "name": "final_message", "optional": false, "type": "string"}
    ]}
  ],
  "input": { "result": { "final_message": "<string, often JSON-encoded>" } }
}
```

## Companion `.agentic_skill.json` File

Created via `wk agentic skills create --recipe-id <id>` — do not hand-author. Pull it down with `wk pull` (see Wiring below) to get its real content.

```json
{
  "name": "tool_name",
  "references": {
    "recipe_id": { "id": {"folder": "", "name": "tool_name", "zip_name": "tool_name.recipe.json"}, "type": "recipe" }
  },
  "trigger_description": "..."
}
```

---

## Wiring onto an MCP server

Creating the skill does **not** attach it to any MCP server. Full sequence:

```bash
wk agentic skills create --recipe-id <id>   # 1. wrap the recipe as a skill
wk clone "<project-folder-name>"            # 2. get a local, pushable copy of the project
                                             #    (needed even if you never touched this folder before —
                                             #    editing the manifest requires a local copy to push from)
# 3. edit <server-name>.mcp_server.json — add entries to references{} and tools[]
wk push                                     # 4. apply
```

Manifest entry:

```json
{
  "references": {
    "ref_0": { "id": {"folder": "", "name": "tool_name", "zip_name": "tool_name.agentic_skill.json"}, "type": "agentic_skill" }
  },
  "tools": [
    { "description": "<same text as the trigger's description>", "tool": "ref_0", "vua_required": false }
  ]
}
```

### Never use `wk mcp servers tools add`

```
WRONG:
wk mcp servers tools add <handle> --recipe <id>
→ Error: API error 400: Tools contains invalid asset(s): workato_skill ID '<id>'

CORRECT: the manifest-edit sequence above.
```

(Verified: `tools add` failed reproducibly, including against an already-attached recipe on its own already-working server. The manifest approach succeeded every time.) Confirm via a raw `tools/list` JSON-RPC call, not `wk mcp tools` — the CLI's summary can omit fields like `_meta`.

### Never reuse a skill name that has ever been orphaned

`wk agentic skills` has no delete or rename command. Deleting a recipe leaves its skill permanently orphaned.

```
WRONG — rebuild a deleted tool under its original name:
delete recipe_id=X (skill "update_content_status" now orphaned, points at nothing)
create new recipe, same name "update_content_status"
→ tools/list omits the tool entirely (name collision between the orphaned and live skill)
→ but a direct tools/call to the same name still executes — looks like a client bug, is actually a naming collision

CORRECT — pick a new name after any delete/rebuild:
create new recipe named "set_content_status" (never used before) → tools/list shows it correctly
```

### Don't rename an existing recipe — recreate it instead

```
WRONG: wk recipes update <id> renamed.json     // changes top-level "name" on an existing recipe
→ recipe accepts the request but never reaches running state (2m0s timeout, no diagnostic detail)

CORRECT: delete the recipe, then wk recipes import with the correct name from creation
```

### If pushed changes stop taking effect, rebuild — don't keep patching

A recipe edited very rapidly and repeatedly (alternating CLI pushes and UI saves, switching a connector action back and forth several times) can reach a state where `wk recipes export` no longer matches what actually executes, with no error. **Diagnostic:** send an argument value never used in that recipe before; if it doesn't appear in the result, you're not looking at current behavior. **Fix:** delete and rebuild once, cleanly (new name — see above).

---

## MCP Apps (interactive UI)

Two independently-verified wiring paths exist, and which one you're on determines which pattern doc applies:

- **`agentic_skill`-referenced tool** (the `workato_skill` trigger documented above, wrapped via `wk agentic skills create`) — see [patterns/mcp-apps.md](patterns/mcp-apps.md) for the app itself (manifest `apps[]`, `content_digest`, CSP) and app-side JS.
- **Recipe-referenced tool** (a plain `workato_api_platform` API endpoint recipe, referenced directly under a `tools_type: "project_assets"` server, no agentic-skill wrapping) — see [patterns/bound-html-apps.md](patterns/bound-html-apps.md). Bound apps (`apps[]`) do **not** work under `tools_type: "api_collection"` — confirmed with the platform team on that path.

**Not yet reconciled:** whether an `agentic_skill`-referenced server's `tools_type` is `project_assets`, `api_collection`, or something else entirely is unconfirmed — the two paths above were verified in separate builds without either one checking the other's manifest. Don't assume they're interchangeable.

---

## Validation Checklist

See [validation-checklist.md](validation-checklist.md).

## Related Documentation

- `workato-recipes` — general recipe JSON fundamentals, Genie Skill Trigger, Callable Recipe Trigger
- [patterns/mcp-apps.md](patterns/mcp-apps.md) — MCP App creation and app-side JS (`agentic_skill`-referenced path)
- [patterns/bound-html-apps.md](patterns/bound-html-apps.md) — MCP App creation for a recipe-referenced tool under `tools_type: "project_assets"`, including native-JSON `return_response` typing and runtime gotchas
