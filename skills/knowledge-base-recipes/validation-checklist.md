# Knowledge Base Validation Checklist

> **Run the base checklist first:** See [workato-recipes/validation-checklist.md](../workato-recipes/validation-checklist.md) for base recipe validation.

The following checks are specific to recipes using the `enterprise_context` connector (Knowledge base by Workato).

---

## Config

- [ ] Config includes `enterprise_context` with `"name": "enterprise_context"` and `"account_id": null`
- [ ] Action `name` matches a valid name in `lint-rules.json`

## Knowledge Base Selection

- [ ] Search actions use `knowledge_bases`; all other actions use `knowledge_base_id`
- [ ] The value is the knowledge base handle (`kb-...`), not its name
- [ ] `toggleCfg` sets the pick-list field to `true`; `dynamicPickListSelection` carries the label
- [ ] No `extended_input_schema` entry for `knowledge_base_id` / `knowledge_bases`

## Search Steps

- [ ] `page_size` is a literal between `"1"` and `"100"` (no formula)
- [ ] `enable_llm_reranking` is set explicitly
- [ ] Datapills read `["documents"]` and `["count"]`, no `["body"]` wrapper
- [ ] The result passed on (LLM context, MCP tool result) is a compact block, not the raw `documents` list

## Upsert Steps

- [ ] `documents.____source` maps the list; each field uses a `current_item` pill
- [ ] `document_id` is a stable source id
- [ ] `updated_at` and `url` are mapped
- [ ] Documents deleted at the source are removed with `delete_document` (upsert never deletes)

## After Import

- [ ] `wk recipes get <id> --json` shows every input key that was generated (unknown names are stripped silently)
- [ ] The recipe activates (`wk recipes start <id>`)
