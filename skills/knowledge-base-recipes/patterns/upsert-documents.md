# Upsert Documents

Use `upsert_documents` to write content from another system into a recipe-type knowledge base. Typical shape: a scheduled recipe reads changed items from the source (REST call, connector search), then one `upsert_documents` step writes them all.

Evidence: sync recipes 4180581 (nightly, changed pages) and 4198175 (one-off full load), 408 wiki pages ingested on 2026-11-26; the knowledge base is searched by a genie and by recipe 4200723.

---

## Step Structure

The list of documents is mapped with `____source` (the list pill) and per-field `current_item` pills, as for other list inputs in Workato:

```json
{
  "number": 4,
  "provider": "enterprise_context",
  "name": "upsert_documents",
  "as": "upsert_docs",
  "keyword": "action",
  "uuid": "upsert-docs-004",
  "dynamicPickListSelection": {
    "knowledge_base_id": "IT Support Wiki"
  },
  "toggleCfg": {
    "knowledge_base_id": true,
    "documents.content_type": true
  },
  "input": {
    "knowledge_base_id": "kb-AcRTkpxR-6Axekt-CE",
    "documents": {
      "____source": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"rest\",\"line\":\"get_pages\",\"path\":[\"response\",\"results\"]}')}",
      "document_id": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"rest\",\"line\":\"get_pages\",\"path\":[\"response\",\"results\",{\"path_element_type\":\"current_item\"},\"id\"]}')}",
      "title": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"rest\",\"line\":\"get_pages\",\"path\":[\"response\",\"results\",{\"path_element_type\":\"current_item\"},\"title\"]}')}",
      "body": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"rest\",\"line\":\"get_pages\",\"path\":[\"response\",\"results\",{\"path_element_type\":\"current_item\"},\"body\",\"storage\",\"value\"]}')}",
      "content_type": "text/html",
      "updated_at": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"rest\",\"line\":\"get_pages\",\"path\":[\"response\",\"results\",{\"path_element_type\":\"current_item\"},\"version\",\"when\"]}')}",
      "url": "https://wiki.example.com#{_dp('{\"pill_type\":\"output\",\"provider\":\"rest\",\"line\":\"get_pages\",\"path\":[\"response\",\"results\",{\"path_element_type\":\"current_item\"},\"_links\",\"webui\"]}')}"
    }
  }
}
```

(Source here: a Confluence REST search with `expand=body.storage,version`; the URL host is replaced by an example.)

## Document Fields

| Field | Use |
|---|---|
| `document_id` | Stable id from the source (page id, ticket number). It is the upsert key. |
| `title` | Shown as `title` in search results. |
| `body` | The content. HTML is accepted with `content_type` `text/html` and comes back as markdown in search results. |
| `content_type` | For example `text/html`; `toggleCfg["documents.content_type"]` is `true` when a literal is typed. |
| `updated_at` | The source's last-modified time; comes back as `updated_date` in recipe search results. |
| `url` | Link back to the source; comes back as `url`. |

## Behaviour Observed

- **Upsert by `document_id`**: a second full load over the same ids replaced documents in place. A first run that stopped at 346 pages plus a full reload ended with 408 documents, no duplicates.
- **No deletes**: an upsert-only sync never removes documents. Pages deleted (or excluded) at the source stay searchable until a `delete_document` step removes them.
- **Ingestion is asynchronous**: the recipe job finished in about 3 minutes, the documents kept appearing in the knowledge base for about 20 more minutes.
- **Job status of a large one-off load**: twice the job of the full-load recipe stayed at "pending" after all pages were written; the documents were complete. Check the knowledge base, not only the job status.
- **Markup leftovers**: HTML-to-markdown conversion keeps text of macros and layout elements (for example status labels, query fragments). Clean the body before the upsert if that noise matters.

## When a Genie Searches the Knowledge Base

Observed on 2026-11-26 in test conversations with a genie that has this knowledge base assigned:

- The genie's search results carried **id, title, URL and content only**: the `updated_at` date did not reach the LLM. To let the genie cite the date, write it **into the body**, for example a header line in front of the content:

  ```json
  "body": "=\"<p><strong>Page:</strong> \" + _dp('{...title...}') + \"<br/><strong>Link:</strong> \" + _dp('{...url...}') + \"<br/><strong>Last updated:</strong> \" + _dp('{...version.when...}').to_time.strftime(\"%d.%m.%Y\") + \"</p>\" + _dp('{...body.storage.value...}')"
  ```

- The genie also read the **knowledge base description** and quoted it to a user ("full load ...", "sync paused"). Keep the description user-facing; put technical notes in the recipe description instead.

## Checklist for an upsert step

- [ ] `knowledge_base_id` (not `knowledge_bases`) with the `kb-...` handle; `toggleCfg.knowledge_base_id` is `true`
- [ ] `documents.____source` maps the list; every field uses a `current_item` pill
- [ ] `document_id` is stable at the source (no generated values)
- [ ] `updated_at` and `url` are set (they come back in search results)
- [ ] A delete path exists if documents can disappear at the source
