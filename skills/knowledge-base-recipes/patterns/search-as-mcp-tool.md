# Knowledge Base Search as an MCP Tool

An external AI client (a company AI hub chat, Claude, Cursor) can search a recipe-type knowledge base through a Workato MCP server: a **callable recipe** does the search (see [templates/search-knowledge-base.json](../templates/search-knowledge-base.json)), and a **project-assets MCP server** exposes the recipe as a tool. The client's own LLM writes the answer from the returned passages.

Evidence: MCP server created on 2026-11-27 with one tool (recipe 4200723), called with JSON-RPC over HTTPS.

> Generic MCP-server authoring (genie-skill triggers, MCP apps) is outside this connector skill; this page records only what was verified for the knowledge-base search tool.

---

## 1. The callable recipe

- Trigger `workato_recipe_function` / `execute`, one required parameter `question` (`string`, `control_type: "text"`), with a `hint`.
- One `search_with_dynamic_filters` step, then `return_result` with a compact `context` (markdown) and `sources` (see [search-documents.md](search-documents.md)).
- **Recipe name and description become the tool name and description.** Write the description for the calling LLM: what the tool returns, which knowledge base, read-only.
- The recipe must be **running**; it is started like any recipe (`wk recipes start <id>`).

## 2. The MCP server

```bash
wk mcp servers create --name "IT wiki search" --folder-id <folder> --recipe <recipe_id>
```

The server is created with `asset_type: "project_assets"`, `auth_type: "hashed_token"`, and an `mcp_url` of the form `https://<number>.apim.mcp.<region>.workato.com`. Add or remove tools later with `wk mcp servers tools add|remove`.

What the server publishes for the recipe (`tools/list`):

| MCP field | Source |
|---|---|
| `name` | Recipe name, non-alphanumeric characters replaced: `[ITG] TST \| Search IT wiki knowledge base (tool)` became `ITG_TST_Search_IT_wiki_knowledge_base_tool` |
| `description` | Recipe description |
| `inputSchema.properties.<param>` | `parameters_schema_json`: `label` becomes `title`, `hint` becomes `description`, `optional: false` puts the name into `required` |
| `annotations` | `title` = recipe name; `readOnlyHint` was `false` although the recipe only reads |

## 3. Tokens

With `hashed_token` the token is not part of the create response, and `wk mcp servers token-renew` cannot print it. To get a token without the UI, create an extra token profile through the API; the response contains `plain_token` **once**:

```bash
curl -X POST "https://app.<region>.workato.com/api/mcp/mcp_servers/<handle>/tokens" \
  -H "Authorization: Bearer <workspace API token>" \
  -H "Content-Type: application/json" \
  --data '{"name":"ai-hub-client"}'
```

Store the token as a secret; one token per client makes revoking simple.

## 4. Calling the tool

The client sends the token as a bearer header:

```bash
curl -X POST "https://<number>.apim.mcp.<region>.workato.com" \
  -H "Authorization: Bearer <plain_token>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  --data '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"ITG_TST_Search_IT_wiki_knowledge_base_tool","arguments":{"question":"How do I set up a printer?"}}}'
```

- `tools/list` without a token returned HTTP 401 `auth_denied`, and so did a wrong token.
- The answer is `result.content[0].text`, a JSON string of `{"result": {<return_result fields>}}`.
- **Integer result fields arrive as strings** (`"hit_count": "152"` for a field declared `integer`). Clients must not rely on the JSON type.
- A call with reranking on took 2 to 3 seconds.

## Checklist

- [ ] Search recipe is callable, running, and returns a compact result (not the raw `documents` list)
- [ ] Recipe description written for the calling LLM
- [ ] Server created in the same project as the recipe (`--folder-id`)
- [ ] Client token created and stored as a secret; client sends `Authorization: Bearer`
- [ ] Client treats numeric result fields as strings
