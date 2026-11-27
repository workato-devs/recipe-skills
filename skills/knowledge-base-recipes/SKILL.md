---
name: knowledge-base-recipes
description: Knowledge base connector recipes for Workato (Knowledge base by Workato, provider enterprise_context). Enables AI agents to generate valid recipe JSON that upserts documents into recipe-type Agent Studio knowledge bases, searches them from a recipe (retrieval for an LLM call or an MCP tool), and lists or deletes documents.
license: MIT
metadata:
  author: Workato community
  version: "0.1.0"
---

# Knowledge Base Recipes Skill - Agent Instructions

> **DEPENDENCY: Load the `workato-recipes` base skill first if not already loaded.**
> This skill requires the base Workato knowledge for triggers, control flow, datapills, and recipe structure.

This skill covers the internal connector that reads and writes **Agent Studio knowledge bases of source type "recipe"**. The recipe editor shows it as *Knowledge base by Workato* (Workato's docs also call it *Enterprise context by Workato*); the provider in recipe JSON is **`enterprise_context`**. It needs no connection.

Typical jobs:

- **Fill a knowledge base** from another system (wiki, ticket system, file store) with a scheduled sync recipe.
- **Search a knowledge base from a recipe** to give an LLM call its context (retrieval without a genie), or to expose the search as an **MCP tool** to an external chat.
- **Keep it clean**: list what is stored, delete documents that no longer exist at the source.

---

## CRITICAL: Pre-Generation Checklist

### For EXISTING projects:
1. **Read an existing recipe that uses `enterprise_context`** (`wk recipes get <id> --json`) and copy its pick-list block (`input` + `toggleCfg` + `dynamicPickListSelection`) for the knowledge base.

### For GREENFIELD projects:
1. **Start from `templates/search-knowledge-base.json`** for a search recipe.
2. **Ask for the knowledge base handle** (`kb-...`, see `wk agentic kb list`) and its display name.

### ALWAYS:
1. **Action names come from `lint-rules.json`.** The editor labels differ from the internal names (`Search documents (advanced filters)` is `search_with_dynamic_filters`).
2. **Use the right pick-list field per action**: `knowledge_bases` for the two search actions, `knowledge_base_id` for all others. The wrong one is silently stripped on import.
3. **Config entry includes `name`** (platform provider, `account_id: null`).
4. **`page_size` is a literal number from 1 to 100.** A formula fails activation.
5. **After import, check the stored input** with `wk recipes get <id> --json`. Unknown keys and unknown action names do not raise an error; they disappear.

---

## Table of Contents

1. [When to Use This Skill](#when-to-use-this-skill)
2. [Config Requirements](#config-requirements)
3. [Native Connector Guidance](#native-connector-guidance)
4. [Pick-List Fields](#pick-list-fields)
5. [Datapill Paths](#datapill-paths)
6. [Search Gotchas](#search-gotchas)
7. [Common Patterns](#common-patterns)
8. [Validation](#validation)
9. [Templates](#templates)
10. [References](#references)

---

## When to Use This Skill

| Situation | Use |
|---|---|
| A recipe must write content into a knowledge base that a genie (or a recipe) searches later | `upsert_documents` (see [patterns/upsert-documents.md](patterns/upsert-documents.md)) |
| A recipe needs the most relevant passages for a question (RAG context, MCP tool, chatbot without a genie) | `search_with_dynamic_filters` (see [patterns/search-documents.md](patterns/search-documents.md)) |
| An external AI client (AI hub, Claude, Cursor) should search the knowledge base | Callable search recipe exposed through an MCP server (see [patterns/search-as-mcp-tool.md](patterns/search-as-mcp-tool.md)) |
| Remove documents that were deleted at the source | `delete_document` |
| Inventory or audit what is stored | `list_documents` / `list_with_dynamic_filters` |

**Not covered:** knowledge bases fed by Workato GO data sources (Confluence, SharePoint, Google Drive connectors in AI Hub). Workato's docs state that the search actions only work on recipe-type knowledge bases.

---

## Config Requirements

`enterprise_context` is a platform provider: no connection, `account_id: null`. Include `name`, set to the provider:

```json
{
  "keyword": "application",
  "name": "enterprise_context",
  "provider": "enterprise_context",
  "skip_validation": false,
  "account_id": null
}
```

Verified 2026-11-27 (recipe 4200723): the same recipe written with `wk recipes update` **without** `name` in its platform-provider entries failed activation with `missing adapter configuration: workato_recipe_function, enterprise_context`; with `name` it started. See the base skill's [config-section.md](../workato-recipes/fundamentals/config-section.md).

---

## Native Connector Guidance

The connector provides 6 native actions. See `lint-rules.json` for the authoritative list. Triggers were not enumerated.

### Choosing the right search action

- **`search_with_dynamic_filters`** (editor label *Search documents (advanced filters)*): the default. Semantic search over one or more knowledge bases, optional **LLM reranking** (`enable_llm_reranking`), optional metadata filters. Verified end to end.
- **`search_documents`**: the simpler search. Same pick-list field (`knowledge_bases`) and the same paging and reranking inputs as written by the editor; not run-verified.

Turn reranking on for question answering. Observed on a 408-page IT wiki, query "Wie beantrage ich ein Funktionspostfach?" (how do I request a functional mailbox): without reranking the top hit was an unrelated page (score 0.6); with reranking the page about functional mailboxes ranked first. Latency stayed at 2 to 3 seconds per call.

### Writing

- **`upsert_documents`**: insert or replace documents by `document_id`. Re-running with the same ids updates in place (a reload of 408 pages over a first load of 346 left 408 documents, no duplicates). Takes a list via `____source`. See [patterns/upsert-documents.md](patterns/upsert-documents.md).

### Removing and listing

- **`delete_document`**: removes one document. An upsert-only sync never removes anything, so pages deleted at the source stay searchable until you delete them. Only the `knowledge_base_id` input is verified; read the document-id field name from an editor-built step before generating it.
- **`list_documents`**: pages through stored documents (`page`, `page_size`).
- **`list_with_dynamic_filters`**: the same with filters and an `include_metadata` toggle.

---

## Pick-List Fields

The knowledge base is selected through a pick list. The editor writes three parts, and **no `extended_input_schema`** for these actions:

**Search actions** (`search_with_dynamic_filters`, `search_documents`): field `knowledge_bases`.

```json
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
```

**All other actions**: field `knowledge_base_id`, one knowledge base.

```json
"dynamicPickListSelection": {
  "knowledge_base_id": "IT Support Wiki (IT Support Genie)"
},
"toggleCfg": {
  "knowledge_base_id": true
},
"input": {
  "knowledge_base_id": "kb-AcRTkpxR-6Axekt-CE"
}
```

- The value is the knowledge base **handle** (`kb-...`), not its name.
- The `label` is cosmetic: the editor writes `<knowledge base name> (<project name>)`; a label with the bare name works too.
- **WRONG:** `"knowledge_base_ids": [...]` or `"knowledge_base_id"` on a search action, or `"knowledge_bases"` on upsert. All are stripped on import without an error (verified), and the action then has no knowledge base.

---

## Datapill Paths

Native action output is **not** wrapped in `body`.

| Value | Path (step `search_kb`) |
|---|---|
| Total number of matches (all pages) | `["count"]` |
| Result list | `["documents"]` |
| Field of the current item (inside a `foreach` over documents) | `["documents", {"path_element_type": "current_item"}, "title"]` |

Fields of each document (observed in live search results):

| Field | Content |
|---|---|
| `document_id` | The id given at upsert |
| `title` | Title given at upsert |
| `url` | URL given at upsert |
| `content` | **The matched passage** (chunk), not the full document: 1.4 to 10 k characters per hit observed, whole pages were up to 74 k |
| `score` | Relevance, a number (for example `0.6`) |
| `updated_date` | The `updated_at` given at upsert (for example the source's last-modified date) |
| `created_date` | Ingestion time |
| `content_type` | For example `text/html` |
| `owner_email` | Workspace user who owns the ingestion |
| `snippets` | List of `{snippet, score}`; repeats the passage |
| `metadata` | List of `{key, value}` with ingestion details (`content_size`, `ingestion_recipe_id`, `lang`, ...) |

---

## Search Gotchas

1. **`page_size` must be a literal from 1 to 100.** A datapill formula (for example a default via `.present? ? ... : 5`) fails activation with `Page size must be between 1 and 100 in input field (page_size)`; the check runs before any value exists. Expose a fixed size, or several recipes.
2. **Return a compact result.** Passing the raw `documents` list on (for example `.to_json`) carries `snippets` and `metadata` too: 5 hits were 63 k characters. Build a markdown block with `format_map` instead (see [Common Patterns](#common-patterns)).
3. **`count` is the total, not the page size.** Typical values were 100 to 152 for a page of 5.
4. **Wrong names fail silently on import.** With an unknown action name (for example `search_documents_advanced_filters`) every input key is stripped; with a wrong field name only that key is stripped. Neither raises an error at import. Always compare the stored input after `wk recipes import` / `update`.

---

## Common Patterns

### Build an LLM context block and a source list from search results

`format_map` works directly on the `documents` list with `%{field}` placeholders (verified):

```json
"context": "=_dp('{\"pill_type\":\"output\",\"provider\":\"enterprise_context\",\"line\":\"search_kb\",\"path\":[\"documents\"]}').format_map(\"### %{title}\\nLink: %{url}\\nLast updated: %{updated_date}\\nScore: %{score}\\n\\n%{content}\").join(\"\\n\\n---\\n\\n\")",
"sources": "=_dp('{\"pill_type\":\"output\",\"provider\":\"enterprise_context\",\"line\":\"search_kb\",\"path\":[\"documents\"]}').format_map(\"- %{title}: %{url}\").join(\"\\n\")"
```

Five hits gave 8 to 24 k characters of context instead of 63 k of raw JSON.

### Sync a source system into a knowledge base

Scheduled recipe: read changed items from the source, then one `upsert_documents` step over the list. See [patterns/upsert-documents.md](patterns/upsert-documents.md).

### Search as a tool for an external LLM

Callable recipe (template) exposed by a project-assets MCP server. See [patterns/search-as-mcp-tool.md](patterns/search-as-mcp-tool.md).

---

## Validation

See [validation-checklist.md](validation-checklist.md).

---

## Templates

| Template | Description |
|---|---|
| [search-knowledge-base.json](templates/search-knowledge-base.json) | Callable recipe: question in, 5 best passages as markdown plus source list out (`search_with_dynamic_filters`, reranking on). Validated: imported, activated, and called through an MCP server. |

---

## References

- [patterns/search-documents.md](patterns/search-documents.md)
- [patterns/upsert-documents.md](patterns/upsert-documents.md)
- [patterns/search-as-mcp-tool.md](patterns/search-as-mcp-tool.md)
- Workato docs: [Knowledge base by Workato connector](https://docs.workato.com/en/agentic/agent-studio/connectors/enterprise-context-connector/enterprise-context-connector), [Search documents (advanced filters)](https://docs.workato.com/en/agentic/agent-studio/connectors/enterprise-context-connector/actions/search-documents-advanced-filters)
