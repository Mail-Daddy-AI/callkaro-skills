<!-- graph-summary: WhatsApp and Instagram chat agents via the chat-agent tools: create, version, publish, templates, predefined functions. Use for any chat-agent task; never send chat payloads to voice agents. -->
# Chat agents

Chat agents are separate from voice agents. Use the chat-agent tools (load the
`chat_agents` tool group first); never send a chat-agent payload to the voice
agent tools.

## Tools

| Tool | What it does |
| --- | --- |
| `list_chat_agent_models` | List account-supported chat model IDs. |
| `check_whatsapp_readiness` (`list_templates` / `get_template`, `provider`, `templateId`) | List approved WhatsApp templates, or fetch one complete template by ID. |
| `list_chat_agents` | List chat agents. |
| `get_chat_agent` (`agentId`, `versionId`) | Read the published or selected version. |
| `list_chat_agent_versions` (`agentId`) | List versions and the published version ID. |
| `create_chat_agent` (`payload`) | Create an agent and publish its first version. Waits for the user's approval; the backend validates the payload — fix what it reports and call again. |
| `update_chat_agent` (`agentId`, `versionId`, `updates`) | Patch agent or version fields. Waits for the user's approval. |
| `create_chat_agent_version` (`agentId`, `versionName`, `cloneFrom`) | Create a version, empty or with `cloneFrom`. |
| `publish_chat_agent_version` (`agentId`, `versionId`) | Publish one version. Waits for the user's approval. |

## Assigning a WhatsApp number

There's no dedicated assign step — set it with `update_chat_agent`, `updates`
`{"whatsappPhoneNumber":"<phoneNumberId>","whatsappDisplayPhN":"<display name>"}`
(`whatsappDisplayPhN` is a version field: without `versionId` it changes the live version).

The number itself comes from Meta via the WhatsApp Business Account linked on
the **CallKaro dashboard** — not buyable. `list_phone_numbers` (`whatsapp`)
shows what's available (see [numbers.md](numbers.md) § WhatsApp numbers).
Requires an active WhatsApp subscription on the account.

## Create safely

1. `list_chat_agent_models`; copy model IDs exactly.
2. `list_chat_agents` to avoid duplicates.
3. Create the agent (`create_chat_agent`).
4. Read it back with `get_chat_agent`.

The minimum payload is:

```json
{
  "chatAgentName": "Support Chat"
}
```

The CLI filled these defaults for omitted fields; the harness sends the payload as written, so set the fields you need (the backend's own defaults may differ):

| Field                                          | Default                                      |
| ---------------------------------------------- | -------------------------------------------- |
| `channel` / `agentMode` / `agentStatus`  | `whatsapp` / `ai` / `in-progress`      |
| `versionName`                                | `v1`                                       |
| `chatModel`                                  | `callkaro/arjuna-2.5`, temperature `0.5` |
| `secondaryChatModel`                         | `gpt-5.4-nano`, temperature `0.5`        |
| `contextLength` / `maxLLMRounds`           | `10` / `3`                               |
| `multipleMessages` / `messageGap`          | `true` / `0.1`                           |
| `numberOfFollowUps` / `followUpGapMinutes` | `0` / `60`                               |
| `functions` / `followUpFunctions`          | empty arrays                                 |
| `webhook` / `webhookEvents`                | empty / empty array                          |

The backend validates the payload and is authoritative, including for
account-dependent model availability: fix what it reports and call again.

## Prompt and model example

```json
{
  "chatAgentName": "Order Support",
  "chatAgentSystemPrompt": "Help customers check and resolve order issues. Ask for the order ID before discussing an order.",
  "chatModel": {
    "model": "callkaro/arjuna-2.5",
    "temperature": 0.3
  },
  "contextLength": 20
}
```

## Functions

Custom functions omit `type` and require `source_code` plus `description`. The
function `name` must match the Python `async def` name. Set `timeout`
(30 seconds is usual) and `directSend` (usually false) explicitly.

Predefined function types are `send_template`, `send_contact`, `send_call`,
`send_image`, `send_document`, `send_video`, and `send_audio`.

- `send_template` requires `templateId`. Never construct the `template` object
  yourself. The CLI resolved the approved template from `templateId` before
  saving; the harness does not, so after saving read the function back with
  `get_chat_agent`. If its template is not resolved, the user sets the
  template function up on the dashboard.
- `send_contact` requires a phone number or email in `contactData`.
- `send_call` requires `callAgentId`; its call window must end after it starts.
- Function names must be unique within each function list.

Before creating or updating a template function, list the available WhatsApp
templates (`check_whatsapp_readiness` `list_templates`, then `get_template`)
and copy the template ID exactly; plan a template function only when it
returns `canPlanTemplateFunction: true`, otherwise tell the user its guidance.
Chat-agent authoring currently supports only `provider: "whatsapp"`.

The template detail response includes `variables`. Use every `variables[].id`
as an exact `varDescriptions` key. Infer its meaning from `context` and
`example`, but describe where the agent obtains the real runtime value rather
than copying the example. Ask the user when the meaning is ambiguous. Give every
variable a description; the CLI refused a template function without them.

Variable IDs follow the provider template:

- Body placeholder: `BODY::{{1}}`
- Text-header placeholder: `HEADER::{{1}}`
- Image, video, or document header: `HEADER::MEDIA`
- Document display filename: `HEADER::FILENAME`
- Dynamic URL-button placeholder: `BUTTON_URL[0]::{{1}}`

Do not invent or rename these IDs. For each description, use the words around
the placeholder, the button label or URL, and the provider example to identify
the likely business value. A value such as `Priya` beside `Hi {{1}}` supports
"customer first name"; it is an example, not the runtime source. If several
meanings remain plausible, ask the user what the value represents and where the
agent should obtain it.

Use the ID in `functions` or `followUpFunctions`:

```json
{
  "name": "send_booking_confirmation",
  "type": "send_template",
  "provider": "whatsapp",
  "description": "Send after a booking is confirmed",
  "templateId": "1234567890123456",
  "varDescriptions": {
    "BODY::{{1}}": "Customer first name"
  },
  "trackClicks": true
}
```

Never place secret values in a payload. Use supported `x_secrets.NAME`
references in headers.

Use `provider: "whatsapp"` in both the template lookup and function payload.

## Versions

Create a clone before substantial changes:

1. `create_chat_agent_version` (`versionName` e.g. `support-v2`, `cloneFrom`
   the published version ID).
2. `update_chat_agent` with the new `versionId`.
3. `get_chat_agent` with that `versionId` to read it back.
4. `publish_chat_agent_version`.

`cloneFrom` must identify a version belonging to the same chat agent. Creating
or updating a version does not publish it. Omitting `versionId` from
`get_chat_agent` or `update_chat_agent` targets the currently published version.
