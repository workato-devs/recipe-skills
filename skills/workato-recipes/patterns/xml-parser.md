# XML Parser

Workato's built-in "XML Parser" connector exposes an `xml_parser` provider with a `parse_xml` action — parses an XML string into a structured, datapill-navigable object whose schema is inferred from a design-time sample document.

**This is a thin pattern doc** — only one real recipe using `parse_xml` has been verified. Treat it as a starting point, not an exhaustive reference.

---

## When to Use

Use `parse_xml` when a recipe receives or retrieves XML content (e.g. a cXML punch-out request, an XML API response) and needs structured field access via datapills, rather than string manipulation. The verified real-world use is parsing an inbound Ariba cXML `PunchOutSetupRequest` payload.

---

## Config Entry

```json
{
  "keyword": "application",
  "provider": "xml_parser",
  "skip_validation": false,
  "account_id": null
}
```

Platform provider — no external connection, `account_id: null`.

---

## Action Structure

```json
{
  "number": 1,
  "provider": "xml_parser",
  "name": "parse_xml",
  "as": "parse_request",
  "keyword": "action",
  "input": {
    "type": "xml",
    "sample_document": "<cXML payloadID=\"...\" timestamp=\"...\">\n<Header>...</Header>\n<Request>...</Request>\n</cXML>",
    "document": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_webhooks\",\"line\":\"webhook_trigger\",\"path\":[\"payload\"]}')}"
  },
  "uuid": "parse-request-001"
}
```

### Key structural rules

- **`type`** — `"xml"` is the verified value.
- **`sample_document`** — a real, representative XML sample used **at design time** to infer the action's output schema (via the `extended_output_schema`, generated to mirror the sample's structure exactly, down to nested elements and repeated groups). This is embedded once when the action is configured in the Workato UI — it is not re-parsed at runtime.
- **`document`** — the actual XML content to parse at runtime, typically a datapill from an upstream trigger/action (e.g. a webhook payload or an HTTP response body). This is the field that varies per execution; `sample_document` does not.

### Output Shape

The output schema's root element name matches the sample document's root XML element (`cXML` in the verified example), and nested structure mirrors the sample exactly — including `parse_output`/`render_input` conversions Workato infers for typed fields (e.g. a `timestamp` attribute inferred as `date_time` with `date_time_conversion`). Repeated child elements are wrapped as an array with `parse_output: "item_array_wrap"` even when the sample only contains a single occurrence — verified on the sample's `Credential` elements.

```json
"path": ["cXML", "payloadID"]
"path": ["cXML", "Header", "From", "Credential"]                                    // array, even for a single-occurrence element
"path": ["cXML", "Header", "From", "Credential", {"path_element_type": "current_item"}, "Identity"]
```

Because the output schema is entirely derived from whatever `sample_document` you provide, there is no fixed/authoritative schema for this action beyond what you configured — re-derive it from a fresh sample if the actual XML shape changes.

---

## Validation Checklist

- [ ] Config includes `xml_parser` with `account_id: null`
- [ ] `type` is `"xml"`
- [ ] `sample_document` is a real, representative sample of the XML this action will actually receive at runtime — the output schema is generated from it, so an unrepresentative sample produces a wrong/incomplete schema
- [ ] `document` (the runtime input) is a datapill, not confused with `sample_document` (the design-time schema source)
- [ ] Repeated elements are accessed as arrays (with `current_item` decomposition), even if the sample only showed one occurrence

For cross-cutting validation (UUIDs, numbering, config, datapills), see [validation-checklist.md](../validation-checklist.md).

---

## Related Documentation

- [Webhook Trigger](../triggers/webhook.md) — a common source of the raw XML `document` input (e.g. an XML-type webhook payload)
- [Adhoc HTTP Actions](adhoc-http-actions.md) — another common source, when the XML comes from an HTTP response body
