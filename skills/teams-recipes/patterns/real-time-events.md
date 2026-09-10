# The `new_event` Trigger (Real-Time Events)

Workato's own Workbot for Microsoft Teams documentation does not mention this trigger at all. It was discovered by browsing the `teams_bot` connector's own trigger picker in the Workato recipe editor (picker label: **"New real-time event"**, described as *"Triggers when selected event occurs in Microsoft Teams"*, marked Beta).

## It's one generic trigger, not a family

Unlike `bot_command` (one trigger per registered command) or `help_event` (one fixed shape), `new_event` is a **single polymorphic trigger**. Its `event_name` input selects which specific real-time event it receives, and the trigger's *output schema changes depending on which event is selected* — this is a dynamic-schema (`dynamicPickListSelection`) trigger, not a static one.

```json
{
  "number": 0,
  "provider": "teams_bot",
  "name": "new_event",
  "as": "some-trigger-001",
  "keyword": "trigger",
  "dynamicPickListSelection": {
    "event_name": "Typeahead search (application/search)"
  },
  "input": {
    "event_name": "application/search"
  }
}
```

## `event_name` is a live-search field, not a static list

The recipe editor's "Event name" field is a typeahead search box (it has its own "Find" control), not a dropdown that shows every option up front. In this workspace, searching it for `tab`, `task`, `card`, `fetch`, `adaptive`, and `compose` all returned **no matches** — the only event that ever surfaced was:

- **Typeahead search** — `event_name` value: `application/search`

## What this means for Tab opened / Show tab using Adaptive Cards

Workato's documentation describes a separate "Tab opened trigger" and a "Show tab using Adaptive Cards" action. Given `new_event`'s polymorphic design, "Tab opened" is very likely just another `event_name` option on this same trigger (probably something like a `tab/fetch` Bot Framework invoke event) — not a distinct trigger the way the docs present it. Since no tab- or task-module-related event name surfaced when searched in this workspace, **it appears these are not available on this bot at all**, most likely because Workato's docs gate tab/file features behind an "Enterprise Workbot" tier/manifest that this connection isn't provisioned with. This is a checked, live finding (search returned zero matches across six plausible terms), not merely an untested gap — but it's still workspace-specific: a different `teams_bot` connection provisioned as an Enterprise Workbot might expose more `event_name` options. Re-check the picker on any new connection before assuming this holds universally.

## The `application/search` (Typeahead search) event's real schema

Confirmed live in the recipe editor (not activation-fired, but the editor resolved and returned this schema directly from the connector):

```json
{
  "name": "id",
  "channelId": "...",
  "serviceUrl": "...",
  "from": {
    "id": "...",
    "name": "...",
    "aadObjectId": "..."
  },
  "conversation": {
    "isGroup": false,
    "conversationType": "...",
    "tenantId": "...",
    "id": "..."
  },
  "recipient": {
    "id": "...",
    "name": "..."
  },
  "entities": [
    { "locale": "...", "country": "...", "platform": "...", "timezone": "...", "type": "..." }
  ],
  "channelData": {
    "channel": { "id": "..." },
    "team": { "id": "..." },
    "tenant": { "id": "..." },
    "source": { "name": "..." },
    "legacy": { "replyToId": "..." }
  },
  "replyToId": "...",
  "value": {
    "queryText": "...",
    "queryOptions": { "skip": 0, "top": 0 },
    "dataset": "..."
  },
  "locale": "...",
  "localTimezone": "...",
  "timestamp": "...",
  "localTimestamp": "..."
}
```

**Important structural difference from `bot_command`/`help_event`:** the caller-identity field is `from.aadObjectId` at the **top level** of the output, not nested under a `context` object (`context.from.aadObjectId`). Do not reuse the `bot_command`/`help_event` datapill path convention here without adjusting for this.

`value.queryText`/`value.queryOptions`/`value.dataset` is the actual search request — this event exists to let a recipe populate a dynamic, server-side-searched dropdown (an Adaptive Card `Input.ChoiceSet` with a `dynamic` style) as the user types.

## The paired `invoke_response` action

The picker's **"Response to real-time event"** action — internal name **`invoke_response`** — is how a recipe returns results back to Teams for a `new_event` firing. It's polymorphic the same way `new_event` is: an `event_name` input selects which event you're responding to (currently only `application/search` confirmed available, same constraint as the trigger), and a same-named nested object holds the event-specific response fields. Both its `extended_input_schema` and `extended_output_schema` were materialized live by the connector (not guessed):

```json
{
  "provider": "teams_bot",
  "name": "invoke_response",
  "keyword": "action",
  "dynamicPickListSelection": {
    "event_name": "Typeahead search (application/search)"
  },
  "input": {
    "event_name": "application/search",
    "application/search": {
      "type": "application/vnd.microsoft.search.searchResponse",
      "value": {
        "results": [
          { "title": "...", "value": "..." }
        ]
      }
    }
  }
}
```

- `application/search.type` is fixed/read-only — the connector's own schema marks it `default: "application/vnd.microsoft.search.searchResponse"` with `ngIf: false` (not user-editable). Always this exact string.
- `application/search.value.results` is an array of `{title, value}` objects — in practice populated via a dynamic list datapill from a search/lookup action earlier in the recipe (the doc's "Using dynamic lists in action fields" pattern), not typed in literally.

This exactly matches Microsoft Bot Framework's public dynamic-search invoke-response format — useful confirmation that Workato's connector is a thin, faithful wrapper here, but this shape was pulled from the live connector's own schema, not assumed from that external knowledge.

## What's still missing for a full round trip

The schema on both ends (`new_event`'s `value.queryText` in, `invoke_response`'s `value.results` out) is now confirmed. What hasn't been built or tested: an actual Adaptive Card with a dynamic `Input.ChoiceSet` posted somewhere in Teams, a real user typing into it, and this action returning real results that show up in the UI. That requires figuring out how to post a card with a dynamic search field in the first place — `post_blocks_message`'s `blocks` array has no known block type for this; it likely requires the raw-JSON mode on `post_bot_message`/`post_bot_reply` (`use_json: true`, unexplored — see `lint-rules.json`'s `_notes.post_bot_message`) to send an arbitrary Adaptive Card body.

## Verification status

`new_event`, `invoke_response`, and their full schemas for the `application/search` event specifically, are all confirmed live via the recipe editor's connector picker (including materialized `extended_input_schema`/`extended_output_schema`, not just accepted field names). The *absence* of tab/task-related events was confirmed by live search returning no matches for six plausible terms. A full end-to-end typeahead-search recipe (a real card, a real typed query, a real returned result) has not been built or activation-tested yet.
