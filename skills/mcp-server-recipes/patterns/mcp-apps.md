# MCP App Creation

**MCP Apps** are an extension to the Model Context Protocol ([SEP-1865](https://modelcontextprotocol.io/extensions/apps/overview)) letting an MCP tool's result include a UI resource — HTML/JS the host renders in a sandboxed iframe, able to call back into the server's other tools. Protocol-level concept, not Workato-specific. Workato hosts the server side — the tool plus the UI resource — with no server code to write.

Read the [workato_skill trigger](../SKILL.md) first if you haven't.

---

## Creating the app: manifest only, no UI required

Add an `apps[]` entry to the MCP server's manifest and push a local HTML file:

```json
{
  "apps": [
    {
      "content_digest": "<sha256 of the html file, hex, 64 chars>",
      "meta": {
        "csp": {
          "baseUriDomains": [],
          "connectDomains": [],
          "frameDomains": [],
          "resourceDomains": ["https://cdn.jsdelivr.net"]
        }
      },
      "name": "human-readable app name",
      "tool": "ref_0"
    }
  ]
}
```

- `tool` — the `ref` (already present in `references`/`tools`) of the **opener** tool: the tool whose call causes an MCP-Apps-aware client to render this app.
- `content_digest` — sha256 of the HTML file (`shasum -a 256 <file>`). Recompute and update on every HTML change; a stale digest is why UI changes don't show up in the client.
- `meta.csp.resourceDomains` (and sibling CSP arrays) — list external origins the HTML loads directly (e.g. a CDN for the app SDK). Leave empty until one is actually needed.
- The HTML file can have any filename.

Confirm registration with a raw `tools/list` call (not `wk mcp tools`, which omits this) — the opener tool's response includes `"_meta": {"ui": {"resourceUri": "ui://..."}}` when wired correctly.

(Verified: `wk mcp` has no `app`-related subcommand at all; the manifest-only approach registered correctly with zero UI interaction.)

---

## The app HTML

```js
import {App} from 'https://cdn.jsdelivr.net/npm/@modelcontextprotocol/ext-apps@1.3.1/dist/src/app-with-deps.js';
const app = new App({name: 'My App', version: '1.0.0'});
await app.connect();
```

- `app.ontoolresult` fires when the opener tool's result arrives — render the initial UI here.
- `app.callServerTool({name, arguments})` calls any tool already present in the manifest's `tools[]`, by its real name.
- CSP (`meta.csp.resourceDomains`) must list any external origin the HTML loads directly.

### Unwrapping tool results

```
WRONG:
const rows = JSON.parse(JSON.parse(result.content[0].text).result.final_message)
// breaks if the nesting depth ever differs

CORRECT:
function unwrap(value) {
  while (typeof value === 'string') {
    try { value = JSON.parse(value); } catch (e) { break; }
  }
  return value;
}
let data = unwrap(result?.content?.[0]?.text ?? result);
if (data?.result?.final_message !== undefined) data = unwrap(data.result.final_message);
```

### Debugging with no devtools access

MCP-App hosts may not expose a console for the rendered iframe. Add a visible debug panel to the HTML instead of guessing — log every call, its arguments, its result, and any caught error into a DOM element, plus `window.onerror`/`window.onunhandledrejection`:

```js
function logDebug(label, value, isError) {
  const el = document.getElementById('debug');
  el.textContent = `[${new Date().toISOString()}] ${label}: ${JSON.stringify(value)}\n` + el.textContent;
  el.classList.toggle('error', !!isError);
}
window.addEventListener('unhandledrejection', e => logDebug('unhandledrejection', String(e.reason?.message || e.reason), true));
```

(Verified: this surfaced `MCP error -32602: tool 'X' not found` from a button that otherwise appeared to silently no-op — see the naming-collision gotcha in the [workato_skill trigger doc](../SKILL.md#never-reuse-a-skill-name-that-has-ever-been-orphaned).)

---

## Connecting an MCP client (e.g. Claude Desktop)

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "<mcp_url>?wkt_token=<token>", "--transport", "http-first"]
    }
  }
}
```

- `--transport http-first` is required for `app.callServerTool` to work — without it, button clicks silently do nothing.
- Multiple MCP servers can coexist as separate keys under `mcpServers`.
- Fully quit and reopen the client after any change to its config, the manifest's `tools[]`, or the app HTML — these clients cache by `content_digest` and by the server's tool list.

### Getting a tokenized connection URL requires the Workato UI — there is no CLI or API path

Workato UI → MCP server → **Authentication method → Token based access → Edit → Create new token** gives `<mcp_url>?wkt_token=<token>`. `wk mcp servers token-renew` returns a bare URL with no token — not usable for this. There is no documented API endpoint for minting this token either.

**If you don't have a way to complete this step (no browser/computer-use tool available), you cannot perform live MCP verification yourself.** `wk mcp servers tools list <handle>` (the admin API, authenticated via your `wk` CLI profile, no token needed) only confirms the server is configured correctly — it is not the same as a real MCP `tools/call`, which requires the `wkt_token` regardless of whether you're calling it via `curl` or through an actual client. Do not report a tool or app as "working" based on admin-API checks alone. State explicitly that live protocol-level verification is unconfirmed and needs a human with UI access to mint a token, rather than implying success.
