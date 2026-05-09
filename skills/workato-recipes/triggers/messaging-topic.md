# Messaging Topic (Event Streams)

Use messaging topics for event-driven, decoupled pub/sub communication between recipes. Publishers send messages to a topic; subscriber recipes trigger on each new message. Multiple publishers can write to one topic, and multiple subscribers each receive all messages independently.

## Provider Details

| Field | Value |
|-------|-------|
| Provider | `workato_pub_sub` |
| Subscriber trigger | `subscribe_to_topic` |
| Publisher action | `publish_to_topic` |
| Batch variants | **None** — use `repeat` loop over `publish_to_topic` for batch |
| Config provider | `workato_pub_sub` with `account_id: null` |

---

## Topic Asset File

Each topic is represented by a `.topic.json` file in the project. This file defines the message schema and is referenced by both subscriber and publisher recipes.

```json
{
  "name": "golden-test-topic",
  "retention": 604800,
  "schema": [
    {"name": "event_type", "type": "string", "label": "Event type", "control_type": "text", "optional": false},
    {"name": "payload", "type": "string", "label": "Payload", "control_type": "text", "optional": true},
    {"name": "timestamp", "type": "string", "label": "Timestamp", "control_type": "text", "optional": true}
  ]
}
```

- `retention` is in seconds (default 604800 = 7 days)
- Schema fields follow the same format as request/response schemas: `name`, `type`, `label`, `control_type`, `optional`

---

## Topic ID Reference Format

Both `subscribe_to_topic` and `publish_to_topic` reference topics via a **reference object**, not a numeric ID:

```json
"topic_id": {
  "folder": "",
  "name": "golden-test-topic",
  "zip_name": "golden_test_topic.topic.json"
}
```

**CRITICAL:** Using a raw numeric ID (e.g. `"topic_id": "1121"`) causes `Unresolved 'Topic' reference` errors on import. Always use the reference object pointing to the `.topic.json` file.

---

## Subscriber Trigger

### Structure

```json
{
  "number": 0,
  "provider": "workato_pub_sub",
  "name": "subscribe_to_topic",
  "as": "trigger",
  "keyword": "trigger",
  "input": {
    "topic_id": {
      "folder": "",
      "name": "golden-test-topic",
      "zip_name": "golden_test_topic.topic.json"
    },
    "since_offset": "-3600"
  },
  "extended_output_schema": [
    {
      "label": "Message",
      "name": "message",
      "type": "object",
      "properties": [
        {"control_type": "text", "label": "Event type", "name": "event_type", "optional": false, "type": "string"},
        {"control_type": "text", "label": "Payload", "name": "payload", "optional": true, "type": "string"},
        {"control_type": "text", "label": "Timestamp", "name": "timestamp", "optional": true, "type": "string"}
      ]
    }
  ],
  "block": [],
  "uuid": "trigger-sub-001"
}
```

### Input Fields

| Field | Required | Description |
|-------|----------|-------------|
| `topic_id` | Yes | Reference object pointing to `.topic.json` |
| `since_offset` | No | Seconds offset for initial message pickup (string, e.g. `"-3600"` = 1 hour ago) |

### Extended Output Schema

The EOS defines a `message` object whose properties mirror the topic schema fields. This makes the message fields available as datapills.

### Datapill Paths

Message fields are nested under `message`:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_pub_sub\",\"line\":\"trigger\",\"path\":[\"message\",\"event_type\"]}')}"
```

| Field | Path |
|-------|------|
| Topic message field | `["message", "field_name"]` |

---

## Publish Action

Use `publish_to_topic` in any recipe to send a message to a topic. The publisher does not need to be a subscriber recipe — any trigger type can publish.

### Structure

```json
{
  "number": 1,
  "provider": "workato_pub_sub",
  "name": "publish_to_topic",
  "as": "publish_event",
  "keyword": "action",
  "input": {
    "topic_id": {
      "folder": "",
      "name": "golden-test-topic",
      "zip_name": "golden_test_topic.topic.json"
    },
    "message": {
      "event_type": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_api_platform\",\"line\":\"trigger\",\"path\":[\"request\",\"event_type\"]}')}",
      "payload": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_api_platform\",\"line\":\"trigger\",\"path\":[\"request\",\"payload\"]}')}",
      "timestamp": "=now"
    }
  },
  "extended_input_schema": [
    {
      "label": "Message",
      "name": "message",
      "type": "object",
      "properties": [
        {"control_type": "text", "label": "Event type", "name": "event_type", "optional": false, "type": "string"},
        {"control_type": "text", "label": "Payload", "name": "payload", "optional": true, "type": "string"},
        {"control_type": "text", "label": "Timestamp", "name": "timestamp", "optional": true, "type": "string"}
      ]
    }
  ],
  "uuid": "publish-event-001"
}
```

### Input Fields

| Field | Required | Description |
|-------|----------|-------------|
| `topic_id` | Yes | Reference object pointing to `.topic.json` |
| `message` | Yes | Object with fields matching the topic schema |

### Extended Input Schema

The EIS defines a `message` object whose properties mirror the topic schema. Without the EIS, the message field datapills break on metadata refresh.

### Output

`publish_to_topic` produces no usable output fields. There is no message ID or confirmation payload returned.

---

## Config

```json
"config": [
  {
    "keyword": "application",
    "provider": "workato_pub_sub",
    "skip_validation": false,
    "account_id": null
  }
]
```

The `workato_pub_sub` provider is a platform provider (`account_id: null`). No external connection is needed.

---

## Verification Status

| Recipe | ID | Status |
|--------|----|--------|
| Golden Msg Topic Publisher | 237643 | Verified end-to-end (API trigger + publish + return) |
| Golden Msg Topic Subscriber | 237639 | Verified end-to-end (trigger fired on published message) |
| Topic | 1121 | `golden-test-topic` with 3 fields |

Endpoint: `POST /golden-pub-topic` (endpoint ID 9552)

---

## Validation Checklist

- [ ] Provider is `workato_pub_sub`
- [ ] Subscriber trigger name is `subscribe_to_topic`
- [ ] Publisher action name is `publish_to_topic`
- [ ] `topic_id` uses reference object format (NOT numeric ID)
- [ ] `.topic.json` file exists in the project with the topic schema
- [ ] Subscriber EOS defines `message` object with topic schema fields
- [ ] Publisher EIS defines `message` object with topic schema fields
- [ ] Publisher `input.message` field names match topic schema field names
- [ ] Subscriber datapill paths use `["message", "field_name"]`
- [ ] Config includes `workato_pub_sub` with `account_id: null`
- [ ] No batch action names used (`batch_publish`, `batch_publish_to_topic`, etc. do NOT exist)

---

## Related Documentation

- [Recipe Structure](../fundamentals/recipe-structure.md)
- [Datapill Syntax](../fundamentals/datapill-syntax.md)
- [Config Section](../fundamentals/config-section.md)
- [API Endpoint Trigger](./api-endpoint.md) — use with `publish_to_topic` for API-triggered publishing
- [Data Table Trigger](./data-table.md) — similar pattern for data table events
