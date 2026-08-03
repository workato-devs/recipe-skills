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

## Verification Honesty

- [ ] A real MCP `tools/call` (with a `wkt_token` obtained via the Workato UI) was made and its effect confirmed by re-reading data — not just that the call returned "success"
- [ ] If no token/UI access was available, the report explicitly says live verification is unconfirmed rather than implying it succeeded based on admin-API checks alone
