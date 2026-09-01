# Document Templates

Workato's "Templates" feature exposes a `workato_template` provider with a `create_document` action — it renders a pre-built document template (e.g. an OCI/cXML punch-out form, a PDF, a formatted document) by filling in named placeholder fields, including repeated rows for array data.

---

## When to Use

Use `create_document` when a recipe needs to produce a formatted document from a named, pre-built template (managed in the Workato UI) rather than assembling raw text/HTML/XML yourself. Common use: generating a punch-out (OCI) form to hand back to an external procurement system, or a formatted export document.

---

## Config Entry

```json
{
  "keyword": "application",
  "provider": "workato_template",
  "skip_validation": false,
  "account_id": null
}
```

Platform provider — no external connection, `account_id: null`.

---

## Action Structure

```json
{
  "number": 8,
  "provider": "workato_template",
  "name": "create_document",
  "as": "create_oci_form",
  "keyword": "action",
  "dynamicPickListSelection": {
    "template_id": "[WEB-PO] MSG | MPG OCI Form"
  },
  "input": {
    "template_id": "4747",
    "template_input": {
      "hookUrl": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_api_platform\",\"line\":\"api_trigger\",\"path\":[\"request\",\"hookUrl\"]}')}",
      "target": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_api_platform\",\"line\":\"api_trigger\",\"path\":[\"request\",\"target\"]}')}",
      "items": {
        "____source": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_variable\",\"line\":\"declare_items\",\"path\":[\"list_items\"]}')}",
        "uom": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_variable\",\"line\":\"declare_items\",\"path\":[\"list_items\",{\"path_element_type\":\"current_item\"},\"uom\"]}')}",
        "quantity": "=_dp('{\"pill_type\":\"output\",\"provider\":\"workato_variable\",\"line\":\"declare_items\",\"path\":[\"list_items\",{\"path_element_type\":\"current_item\"},\"Quantity\"]}').to_i",
        "description": "=_dp('{\"pill_type\":\"output\",\"provider\":\"workato_variable\",\"line\":\"declare_items\",\"path\":[\"list_items\",{\"path_element_type\":\"current_item\"},\"description\"]}').strip_tags",
        "No": "=_dp('{\"pill_type\":\"output\",\"provider\":\"workato_variable\",\"line\":\"declare_items\",\"path\":[\"list_items\",{\"path_element_type\":\"current_index\"}]}')+1",
        "priceUnit": "1"
      }
    }
  },
  "uuid": "create-oci-form-001"
}
```

### Key structural rules

- **`dynamicPickListSelection.template_id`** — the human-readable template name (as configured in the Workato UI), shown alongside the literal numeric `input.template_id`. This is the same dual-field pattern documented for other dynamic-picklist-backed inputs elsewhere in this skill (see [scheduler.md](../triggers/scheduler.md)'s `time_unit` note) — both fields are required together.
- **`template_input`** — an object whose top-level keys must match the template's own placeholder field names exactly (defined when the template was built in the Workato UI, not something this recipe controls).
- **Repeated/array template fields use the standard array-decomposition pattern**: `____source` points at the source array, and each per-item field is mapped with a `{"path_element_type": "current_item"}` path segment — exactly the pattern used elsewhere for list-to-array mappings (see [variables-and-lists.md](variables-and-lists.md)).
- **`{"path_element_type": "current_index"}`** gives the zero-based index of the current item within the array being decomposed — verified use: computing a 1-based line/row number (`current_index + 1`) for a repeated table row in the rendered document.
- **Field-level formulas are applied per-item inside the decomposition** — e.g. `.to_i` to coerce a quantity, `.strip_tags` to clean HTML-formatted text before it renders in the document. These are ordinary formula-mode (`=` prefix) transformations on the per-item datapill, not special `create_document` syntax.

---

## Datapill Reference

`create_document`'s own output was not observed with a populated `extended_output_schema` in the exported recipe (the recipe used this action purely as a side-effecting document-generation step, without reading its output downstream). If you need the generated document's content/URL, pull a fresh action from the Workato UI to see its exact output schema before mapping.

---

## Validation Checklist

- [ ] Config includes `workato_template` with `account_id: null`
- [ ] `dynamicPickListSelection.template_id` (human-readable name) and `input.template_id` (numeric ID) are both set and refer to the same template
- [ ] `template_input`'s top-level keys match the target template's actual placeholder field names — these are template-specific and not enumerable here; verify against the template definition in the Workato UI
- [ ] Repeated/array fields inside `template_input` use `____source` + `current_item` decomposition, not a bare list datapill assigned directly to an array field (see [variables-and-lists.md](variables-and-lists.md) for why a bare list datapill gets silently stripped on import)

For cross-cutting validation (UUIDs, numbering, config, datapills), see [validation-checklist.md](../validation-checklist.md).

---

## Related Documentation

- [Variables and Lists](variables-and-lists.md) — the same `current_item`/`current_index` array-decomposition pattern used more generally
- [Foreach Loops](../control-flow/foreach.md) — an alternative when you need per-item control flow rather than a template's built-in repeat rendering
