# Functions — giving the agent abilities

> **Field shapes** for every function type: [AGENT-VERSION-REFERENCE.md](AGENT-VERSION-REFERENCE.md) §6 (and §15 for WhatsApp).
> **Writing `source_code`**: use the production generator prompts —
> [advanced-pre-call-agent.md](../authoring-pipeline/advanced-pre-call-agent.md),
> [advanced-in-call-agent.md](../authoring-pipeline/advanced-in-call-agent.md),
> [advanced-post-call-agent.md](../authoring-pipeline/advanced-post-call-agent.md).
> They own the exact protocols (signatures, allowed imports, forbidden types,
> security rules) and are stricter than any summary. Review generated code with
> [function-critic-agent.md](../authoring-pipeline/function-critic-agent.md).
>
> This file is the **decision layer**: which function, basic or advanced, where to attach it.

Functions live at version level (`functions[]`, callable everywhere) or on a
capability (`capabilities[i].functions[]`, callable only inside it). Names must
be unique **within a scope** and are the update/delete key. Use `snake_case`.

## Which function type

| Need | Type |
|---|---|
| Hang up | `end` — one per agent, almost always wanted (without it the agent can't end gracefully) |
| Live transfer to a human | `transfer` — **always this type, never custom code** |
| Put the caller on hold | `keep_call_on_hold` |
| Check / book a calendar slot | `available` / `booking` |
| Call an external API mid-call | `custom_in_call` |
| Enrich metadata or rewrite the prompt before dialing | `custom_pre_call` |
| CRM push, notification, custom disposition after the call | `custom_post_call` |
| WhatsApp message during/after the call | `whatsapp_in_call` / `whatsapp_post_call` (§15) |
| Hand the contact to a chat agent | `assign_chat_agent` |

`transfer/end/keep_call_on_hold/available/booking` may each be added **once**.
The name `send_text_message_on_whatsapp` is reserved.

## Basic or advanced?

| | Basic | Advanced (`source_code`) |
|---|---|---|
| What it is | fixed API call described by fields (`api`, `method`, `parameters[]`, `headers{}`) | real code the platform executes |
| Choose when | one fixed URL, no logic | URL contains `{{variables}}`, branching/retries, payload built from variables, or the response needs processing |
| Language | — | pre/in-call: **Python** · post-call: **JavaScript** |

Advanced is always safe; basic is only for a fixed URL with no logic.

### Secrets in functions

In a basic function, the UI's **Headers → Key Name / Value** rows are stored as
a header object. Put the secret reference in **Value**:

```json
{
  "headers": {
    "Authorization": "x_secrets.CRM_AUTH_HEADER",
    "Content-Type": "application/json"
  }
}
```

Store the complete header value, such as `Bearer <token>`, under
`CRM_AUTH_HEADER` in the secrets registry. In advanced `source_code`, read the
runtime object/dict using `x_secrets["CRM_API_TOKEN"]` and construct the header
value in code. For example, JavaScript can use
``Authorization: `Bearer ${x_secrets["CRM_API_TOKEN"]}``` and Python can use
`{"Authorization": f"Bearer {x_secrets['CRM_API_TOKEN']}"}`. In that case the
stored secret is the token only. Never add `Bearer ` both in code and in the
stored secret.

Never put a real or dummy credential in a function. Run `ck secrets list
--json` first and reuse a matching name. If no matching registered secret
exists, use a descriptive pending name such as `CRM_API_TOKEN`. After a
successful save, report every missing name and tell the user to run `ck secrets
set <name>`, add it at https://callkaro.ai/dashboard/settings/secrets, or ask
their admin to update the secrets registry. See [../secrets.md](../secrets.md).

Constraints that bite either way (details in reference §6): parameter rows are
only `{key_name, type:"string"|"number", description}` — no boolean/object/enum,
so pass `"true"`/`"false"` strings and normalise inside; methods are
`GET POST PUT DELETE` only (no PATCH).

## Where to attach it

- Attach a function to the **node that invokes it** — "transfer between node 3
  and node 4" means the transfer function goes on node 3.
- Version level = callable in every phase; capability level = only inside it.
  Prefer capability scope so the model isn't offered irrelevant tools.
- Warm transfer (`warm_transfer: true`) **requires** a non-empty
  `warm_transfer_prompt`. On pathway agents (type 3) both are lifted to version
  level at save time (reference §6).

## `description` is the trigger

For `custom_in_call`, the model reads `description` to decide **when** to call
the function. Write it as a condition, not a summary:

> ✅ "Call this when the user confirms a slot and has provided a 6-digit pincode."
> ❌ "Checks availability."

## Integrations that aren't ready yet

Placeholders are expected and fine — `https://api.example.com/endpoint`,
`Bearer YOUR_API_KEY_HERE`, `+910000000000`. Build the function, then **tell the
user exactly what's placeholder**. Never block on missing credentials.
