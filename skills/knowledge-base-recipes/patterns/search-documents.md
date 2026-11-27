# Search Documents

Use `search_with_dynamic_filters` (editor label *Search documents (advanced filters)*) to get the passages of a recipe-type knowledge base that best match a question. This is the retrieval step of a RAG flow: the passages become the context of an LLM call, or the result of an MCP tool.

Evidence: recipe 4200723 (callable, exposed as MCP tool), knowledge base of 408 wiki pages, live calls on 2026-11-27.

---

## Step Structure

```json
{
  "number": 1,
  "provider": "enterprise_context",
  "name": "search_with_dynamic_filters",
  "as": "search_kb",
  "keyword": "action",
  "uuid": "search-kb-001",
  "dynamicPickListSelection": {
    "knowledge_bases": [
      { "label": "IT Support Wiki (IT Support Genie)", "value": "kb-AcRTkpxR-6Axekt-CE" }
    ]
  },
  "toggleCfg": {
    "enable_llm_reranking": true,
    "knowledge_bases": true
  },
  "input": {
    "knowledge_bases": "kb-AcRTkpxR-6Axekt-CE",
    "query": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"trigger\",\"path\":[\"parameters\",\"question\"]}')}",
    "page": "1",
    "page_size": "5",
    "enable_llm_reranking": "true"
  }
}
```

No `extended_input_schema` and no `extended_output_schema` are needed: the editor writes none for this action, and a step imported without them keeps its inputs and returns its output at runtime.

## Inputs

| Key | Value | Notes |
|---|---|---|
| `knowledge_bases` | Knowledge base handle `kb-...` | Pick-list field; see SKILL.md "Pick-List Fields". Docs allow several knowledge bases; each one is a separate request against the rate limit. |
| `query` | Natural-language question or keywords | Map the user's question unchanged. |
| `page` | `"1"` | Pages start at 1. |
| `page_size` | `"1"` to `"100"`, **literal** | A formula fails activation: `Page size must be between 1 and 100 in input field (page_size)`. |
| `enable_llm_reranking` | `"true"` / `"false"` | Reorders the hits with an LLM. Recommended for question answering. |

Metadata filters ("Data filters" in the editor) exist per Workato's docs, but their input key was not captured here. Read it from an editor-built step before generating one.

## Reranking: observed effect

Same knowledge base, query "Wie beantrage ich ein Funktionspostfach?" (how do I request a functional mailbox):

| Reranking | Top hit | Latency |
|---|---|---|
| off | "Beantragung eines Servers" (requesting a server), score 0.6; the page on functional mailboxes was not in the top 5 | about 1 s |
| on | "E-Mail \| Funktions-Postfächer" (the right page), then two other mailbox pages | 2 to 3 s |

Two more queries (VPN problems at home, printer setup) returned the matching guides first with reranking on.

## Output

- `count`: total matches across all pages (observed 100 to 152 for 5 returned hits).
- `documents`: list of hits. Each hit carries `document_id`, `title`, `url`, `content` (the matched passage, 1.4 to 10 k characters), `score` (number), `updated_date`, `created_date`, `content_type`, `owner_email`, `snippets` (list of `{snippet, score}`), `metadata` (list of `{key, value}`).

## Turning the hits into LLM context

Do not pass the raw list on: with `snippets` and `metadata`, 5 hits serialised with `.to_json` were 63 k characters. `format_map` produces a compact block (8 to 24 k characters for 5 hits):

```json
"context": "=_dp('{\"pill_type\":\"output\",\"provider\":\"enterprise_context\",\"line\":\"search_kb\",\"path\":[\"documents\"]}').format_map(\"### %{title}\\nLink: %{url}\\nLast updated: %{updated_date}\\nScore: %{score}\\n\\n%{content}\").join(\"\\n\\n---\\n\\n\")"
```

To use the context in a raw JSON HTTP body (for example an OpenAI-compatible `chat/completions` call), build the body in a `py_eval` step and pass the context as an input field; see the base skill's [python-snippets.md](../../workato-recipes/patterns/python-snippets.md). Do not concatenate passages into a JSON string with formulas: passages contain quotes, newlines and markdown tables.

## Checklist for a search step

- [ ] Action name `search_with_dynamic_filters` (not the editor label)
- [ ] `knowledge_bases` holds the `kb-...` handle; `toggleCfg.knowledge_bases` is `true`
- [ ] `page_size` is a literal between 1 and 100
- [ ] `enable_llm_reranking` set explicitly
- [ ] Downstream steps read `["documents"]` / `["count"]` (no `body` wrapper)
- [ ] Result passed on as a compact block, not the raw list
