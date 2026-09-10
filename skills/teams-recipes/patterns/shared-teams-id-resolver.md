# Shared Teams ID Resolver (Callable Recipe)

Every `post_blocks_message` action needs a Teams user ID in its `channel` field. If the calling context doesn't already have one (for example, an automated job driven by a record ID from another system, not a live `bot_command` invocation), the recipe first has to resolve that record's owner down to a Teams user ID.

Observed in production: instead of repeating a "look up the external system's user → get their email → `get_user_by_principal_name`" chain inside every recipe that needs to notify someone, that chain is factored out into one shared **callable recipe** that any other recipe can call with `call_recipe` and get back a single `teamsId` field.

## Why this pattern

- **Avoids duplicating the lookup action.** Any recipe needing "notify this record's owner in Teams" calls one function instead of re-implementing the email lookup + `get_user_by_principal_name` action.
- **Keeps the external-system lookup out of Teams-specific recipes.** The resolver recipe owns the "how do I get this person's email" logic (which may be system-specific); recipes that only need to post a Teams message don't need to know how that email was found.

## Shape

**Resolver recipe** — a `workato_recipe_function` (`execute`) trigger with one required input, one required result field:

```json
{
  "number": 0,
  "provider": "workato_recipe_function",
  "name": "execute",
  "as": "resolver-trigger-001",
  "keyword": "trigger",
  "input": {
    "parameters_schema_json": "[{\"name\":\"external_user_id\",\"type\":\"string\",\"optional\":false,\"label\":\"external_user_id\",\"control_type\":\"text\"}]",
    "result_schema_json": "[{\"name\":\"teamsId\",\"type\":\"string\",\"optional\":false,\"label\":\"teamsId\",\"control_type\":\"text\"}]"
  },
  "block": [
    {
      "number": 1,
      "provider": "teams_bot",
      "name": "get_user_by_principal_name",
      "as": "lookup-002",
      "keyword": "action",
      "input": {
        "principal_name": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"<source-system-provider>\",\"line\":\"<email-lookup-step>\",\"path\":[\"emailAddress\"]}')}"
      },
      "uuid": "lookup-002"
    },
    {
      "number": 2,
      "provider": "workato_recipe_function",
      "name": "return_result",
      "as": "return-003",
      "keyword": "action",
      "input": {
        "result": {
          "teamsId": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"teams_bot\",\"line\":\"lookup-002\",\"path\":[\"id\"]}')}"
        }
      },
      "uuid": "return-003"
    }
  ],
  "uuid": "resolver-trigger-001"
}
```

Note the resolver uses `principal_name` (email/UPN), not `id` (Azure AD object ID) — because at this point in the flow there is no `bot_command` trigger context to pull an `aadObjectId` from. This is the opposite of the `bot_command`-driven case in the main [Common Patterns](../SKILL.md#common-patterns) flow, where `id` is used because `context.from.aadObjectId` is already available.

**Caller recipe** — any recipe, `call_recipe`'d, then feeds the returned `teamsId` straight into `post_blocks_message`'s `channel` field:

```json
{
  "number": 7,
  "provider": "workato_recipe_function",
  "name": "call_recipe",
  "as": "resolve-teams-id-004",
  "keyword": "action",
  "input": {
    "flow_id": "<resolver recipe's numeric ID>",
    "parameters": {
      "external_user_id": "#{_dp('{...path to the record owner id...}')}"
    }
  },
  "uuid": "resolve-teams-id-004"
}
```

```json
{
  "channel": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"resolve-teams-id-004\",\"path\":[\"result\",\"teamsId\"]}')}"
}
```

## When to use this vs. a direct lookup

- **Direct `get_user_by_principal_name`** (see the main [Common Patterns](../SKILL.md#common-patterns) section) — use when the recipe is itself a `bot_command` and already has `context.from.aadObjectId`, or when it's a one-off recipe that isn't going to be duplicated elsewhere.
- **Shared resolver callable recipe** — use when multiple recipes across the project need to turn the *same* external-system identifier (not a Teams-native one) into a Teams user ID. Centralizing it means the source-system lookup only needs to be built and maintained once.
