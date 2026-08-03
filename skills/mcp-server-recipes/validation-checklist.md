# MCP Server Recipes Validation Checklist

> **Run the base checklist first:** See [workato-recipes/validation-checklist.md](../workato-recipes/validation-checklist.md) for base recipe validation.

## Trigger

- [ ] Provider is `workato_skill`; trigger `start_workflow`; return `workflow_return_result`
- [ ] `code.input.description` is populated
- [ ] If the tool takes arguments, `parameters_schema_json` is present with `name`/`label`/`type`/`control_type`/`optional` per field
- [ ] `result_schema_json` and every `workflow_return_result.input.result` key agree

## Server Wiring

- [ ] Wired onto the target server via a manifest edit + `wk push` (after `wk clone` to get a local pushable copy), not `wk mcp servers tools add`
- [ ] The MCP server manifest's `tools[].description` is populated with the same text as the trigger's description — this, not the trigger's description, is what an MCP client sees
- [ ] Skill name checked against `wk agentic skills list` for orphaned duplicates pointing at nonexistent recipe IDs
- [ ] After any manifest change, confirmed via a raw `tools/list` call (with a real `wkt_token`, not just `wk mcp servers tools list`) that the tool appears with a non-empty description and correct `inputSchema`

## MCP App (if building one)

- [ ] `apps[].content_digest` matches the current sha256 of the actual HTML file
- [ ] `apps[].tool` points at a `ref` that is a real opener tool already in `references`/`tools`
- [ ] `meta.csp.resourceDomains` lists every external origin the HTML loads directly
- [ ] Tool results are unwrapped with a loop, not a fixed number of chained `JSON.parse` calls

## Bound HTML Apps (recipe-referenced tool, `tools_type: "project_assets"`)

See [patterns/bound-html-apps.md](patterns/bound-html-apps.md) for the full pattern.

- [ ] Server manifest is `tools_type: "project_assets"` with `references[]` pointing at the recipe(s) directly (`type: "recipe"`) — not `api_collection`, which doesn't support bound apps
- [ ] `.bin` file is named `<mcp_server_file_basename>_<app_name_lowercased_underscored>.bin`; `content_digest` matches its current sha256
- [ ] The app HTML's `extractResponse`-style shim handles `content[0].text` (a JSON *string*) wrapped as `{http_status_code, response: {...}}` — not a top-level `structuredContent` field
- [ ] Every field in `return_response`'s `input.response` that should be a native number/array/object is bound with formula mode (`=_dp(...)`), not `#{}` interpolation, which silently stringifies non-string values
- [ ] `return_response`'s `extended_input_schema` and `extended_output_schema` are identical AND both fully model the nested shape of every structured field, not just its top-level type
- [ ] Datapill JSON inside `_dp(...)` is compact and singly-escaped (build with `json.dumps(..., separators=(',',':'))`, don't hand-escape twice)
- [ ] `py_eval` inputs that parse an optional upstream datapill guard against the literal string `"null"` (from `.to_json` on an absent value), not just falsiness
- [ ] Optional `api_trigger` inputs used in downstream formulas are defaulted in an early `py_eval` step, not referenced raw (they're `nil` at runtime regardless of schema defaults)
- [ ] `wk lint` `errors: 0`; any `DP_LINE_RESOLVES`/`DP_STEP_REACHABLE` warnings inside a `foreach` are treated as expected noise once a real `tools/call` confirms the step works
- [ ] Live verification used the actual `mcp_url` (JSON-RPC `tools/list`, `resources/list`, `resources/read`, `tools/call`), not just `wk mcp servers tools list`/other admin-API summaries — `resources/read`'s returned HTML hashes to the same value as `apps[].content_digest`

## Verification Honesty

- [ ] A real MCP `tools/call` (with a `wkt_token` obtained via the Workato UI) was made and its effect confirmed by re-reading data — not just that the call returned "success"
- [ ] If no token/UI access was available, the report explicitly says live verification is unconfirmed rather than implying it succeeded based on admin-API checks alone
