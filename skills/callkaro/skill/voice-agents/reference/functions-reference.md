# Reference: Functions (types, fields, predefined, conditions)
<!-- graph-summary: Field reference for functions[]: timings and authoring styles, constraints for every custom function, field sets per variant (in-call, post-call, transfer, etc.), predefined functions, and conditions[] for post-call and assignment functions. -->

Part of the [version reference](../AGENT-VERSION-REFERENCE.md) (which document a field belongs to, topic map). Field index: [field-index.md](field-index.md).

## 6. `functions[]` — what the agent can *do*

Functions live either at version level (`functions[]`, callable everywhere) or on a capability
(`capabilities[i].functions[]`, callable only inside it). Names must be unique **within a scope**;
the name is the update/delete key. Use `snake_case`, e.g. `check_availability`.

### Timings and authoring styles

| `type` | When it runs | Basic | Advanced |
| --- | --- | --- | --- |
| `custom_pre_call` | before the call connects | fixed API call | **Python** async `source_code` |
| `on_connected` | once after connection, or once upon entering its capability/node | fixed API call | **Python** async `source_code` |
| `custom_in_call` | mid-call, model-triggered | fixed API call | **Python** async `source_code` |
| `custom_post_call` | after the call ends | fixed API call | **JavaScript** async `source_code` |

Choose **advanced** when the URL contains `{{variables}}`, there is branching or retry logic, or the
payload is built from post-call variables. Advanced is always safe; basic is only for a fixed URL
with no logic.

### Constraints that apply to every custom function

- Parameter rows support **only** `{key_name, type: "string"|"number", description}`. No boolean /
  object / enum / required / default — express boolean intent as the string `"true"`/`"false"` and
  normalise inside `source_code`.
- HTTP methods: **`GET`, `POST`, `PUT`, `DELETE`** only. No `PATCH`.
- `api_mapping` and `parameters_mapping` persist as **objects/records** (`{key: value}`), not entry
  arrays.
- Absent optional fields are normal — never treat a missing optional as an error.
- Placeholder URLs and non-secret values are expected while integrations are pending
  (`https://api.example.com/endpoint`, `+910000000000`, `event_id_placeholder`). Credentials must
  use a descriptive `x_secrets.NAME` reference. Never block on missing integration details: write
  the function with placeholders and say so.
- The basic-function UI edits `headers` as `{key_name, value}` rows, then saves them as a
  `{headerName: value}` object. `Content-Type: application/json` is the usual default.
- For a basic function header, use the exact reference as the stored value, for example
  `"Authorization": "x_secrets.CRM_AUTH_HEADER"`; store the complete `Bearer <token>` value under
  that name. Advanced `source_code` reads the runtime object/dict with
  `x_secrets["CRM_API_TOKEN"]` and constructs `Bearer <token>` in code, where the registered secret
  is only the token. Never duplicate the `Bearer ` prefix.
- Run `ck secrets list --json` before authoring. After saving, report every missing secret name and
  tell the user to run `ck secrets set <name>`, add it at
  https://callkaro.ai/dashboard/settings/secrets, or ask their admin to update the registry.

### Field sets per custom variant

**`custom_pre_call`** — runs before the call; enriches metadata or rewrites the prompt.
Basic: `type`, `name`, `description?`, `api`, `method`, `headers?`, `parameters[]`, `api_mapping{}`,
`update_call_data?`, `execute_while_switching?`.
Advanced: `type`, `name`, Python `source_code`, `update_call_data` (**boolean, never null**), API
fields optional.

**`custom_in_call`** — triggered mid-call by the model.
Basic: `type`, `name`, `description` (**the trigger condition** — this text is what the model reads
to decide when to call it, so write it as a condition, not a summary), `msg_while_executing_type`
(`dynamic` \| `static`), `msg_while_executing[]` (`[]` when dynamic), `api`, `method`, `headers?`,
`parameters[]`, `api_mapping{}`, `update_call_data?`, `execute_while_switching?`.
Advanced: same, minus API fields, plus Python `source_code`.

**`custom_post_call`** — side effects after the call: CRM push, logging, notifications.
Basic: `type`, `name`, `api`, `method`, `parameters` (**a JSON payload string**, not typed rows),
`parameters_mapping{}`, `api_mapping{}`, `conditions[]`.
Advanced: `type`, `name`, JavaScript `source_code`; retry/error handling lives **inside the code** —
there is no retry field.

**`on_connected`** — automatic side effects immediately after connection. A top-level copy runs
exactly once after the call connects; a capability/node copy runs exactly once when the call enters
that scope. It is never selected by the LLM and its return value is ignored.
Basic: `type`, `name`, `description`, `api`, `method`, `headers?`, `parameters[]`, optional static
execution message. Methods are `GET` | `POST` | `PUT` | `DELETE`; parameter types are `string` or
`number`.
Advanced: `type`, `name`, `description`, Python `source_code`, optional static execution message.
The source must define exactly `async def <name>(ctx: JobContext, metadata: dict):`. Use
`ctx.room`, `ctx.proc.userdata`, or `ctx.api`; do not use `ctx.session`, `ctx.userdata`, `RunContext`,
filesystem/process APIs, or dynamic imports. `JobContext`, `httpx`, `logger`, and `x_secrets` are
injected.

```json
{
  "type": "on_connected",
  "name": "record_call_connected",
  "description": "Record that the call connected.",
  "api": "https://api.example.com/calls/connected",
  "method": "POST",
  "parameters": [
    { "key_name": "lead_id", "type": "string", "description": "Lead identifier from metadata." }
  ],
  "headers": {
    "Authorization": "x_secrets.CRM_AUTH_HEADER"
  }
}
```

```python
async def record_call_connected(ctx: JobContext, metadata: dict):
    """Record the connection as a side effect."""
  try:
    async with httpx.AsyncClient(timeout=10.0) as client:
      response = await client.post(
        "https://api.example.com/calls/connected",
        json={"lead_id": metadata.get("lead_id")},
        headers={"Authorization": f"Bearer {x_secrets['CRM_API_TOKEN']}"},
      )
      response.raise_for_status()
  except httpx.HTTPError as error:
    logger.warning("Could not record call connection: %s", error)
```

Two flags worth knowing:

- `update_call_data` — on advanced pre-call it selects the protocol (below). Elsewhere it marks a
  function that mutates call data rather than just returning a value.
- `execute_while_switching` — allow the function to run during a capability/node switch instead of
  being deferred until the new node is active.


### Predefined functions (no code)

| `type` | Required | Notes |
| --- | --- | --- |
| `end` | `name`, `description` | Nothing else. Ends the call. |
| `transfer` | `name`, `description`, `to_number`, `warm_transfer` | `to_number` is E.164 and is the primary destination. The builder also maintains `to_numbers[]` (ordered list, with `to_number` mirroring `to_numbers[0]`) for multi-destination attempts — write both when using a list. `warm_transfer: true` **requires** a non-empty `warm_transfer_prompt` (how to brief the human before handing over); cold transfer uses `false` + `""`. Also carries `msg_while_executing[]` and `msg_while_executing_type: "static"` for what the caller hears while connecting. |
| `keep_call_on_hold` | `name`, `description` | `hold_duration` seconds (default 20). Pairs with `hold_call_snippet` and `hold_disconnect_timeout`. |
| `available` | `name`, `description`, `api`, `event_id` | Check calendar availability (cal.com-style). |
| `booking` | `name`, `description`, `api`, `event_id` | Book the chosen slot. |
| `send_to_whatsapp` | `name`, `description`, `api` | Send a link/message to WhatsApp. |
| `assign_chat_agent` | `chat_agent_id` | Hand the contact to a chat agent after the call. Plus `conditions[]` and `scheduleFollowupAfterAssignment`. |

Two runtime tools are not stored as functions but are invoked when the corresponding feature is
enabled: the language-switch tool (see `switchableLanguages`, [§14](variables-memory-whatsapp.md)) and `collect_digits_via_dtmf`
(see `dtmf_collection_enabled`, [§13](call-settings.md) — the prompt must tell the agent to use it, with the expected
digit count).

**Pathway warm-transfer lift:** on type 3, per-function `warm_transfer` / `warm_transfer_prompt` are
stripped at save time and lifted to **version-level** `warm_transfer` / `warm_transfer_prompt` (last
warm transfer wins, traversing version functions then capabilities in order). Author them on the
transfer function; expect to read them back at version level.

### `conditions[]` — when a post-call / assignment function should run

```json
{ "id": "calltype_1731570000000_a1b2c3", "source": "call_type", "key": "connected" }
{ "id": "meta_1731570000001_d4e5f6", "source": "call_metadata", "key": "city", "value": "Pune", "other": false }
{ "id": "pcv_1731570000002_g7h8i9", "source": "post_call_variables", "name": "interested", "value": true, "other": false }
```

`source` is `call_type` \| `call_metadata` \| `post_call_variables`. For `call_type`, `key` is
`all` \| `connected` \| `not_connected`. `value` is a string or boolean — never a number or object.
`id` format `<prefix>_<unix-ms>_<6-char-alphanumeric>`. `[]` = always run. Include exactly one
`call_type` entry (default `all`) and add metadata / post-call entries only when asked.
