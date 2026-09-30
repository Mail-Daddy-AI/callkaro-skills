# Chat agents

Chat agents are separate from voice agents. Use `ck chat-agents`; do not send a
chat-agent payload to `ck agents`.

## Commands

| Command                                                                            | What it does                                                               |
| ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `ck chat-agents models [--json]`                                                 | List account-supported chat model IDs.                                     |
| `ck chat-agents templates --provider whatsapp [--json]`                          | List available WhatsApp template names and IDs.                            |
| `ck chat-agents template <templateId> --provider whatsapp [--json]`              | Fetch one complete WhatsApp template by ID.                                |
| `ck chat-agents list [--json]`                                                   | List chat agents.                                                          |
| `ck chat-agents get <agentId> [--versions <versionId>] [--json]`                 | Read the published or selected version.                                    |
| `ck chat-agents versions <agentId> [--json]`                                     | List versions and the published version ID.                                |
| `ck chat-agents create [json\|--file file.json]`                                  | Validate locally, fill defaults, then create an agent and initial version. |
| `ck chat-agents update <agentId> --set '{...}' [--versions <versionId>]`         | Patch agent or version fields.                                             |
| `ck chat-agents create-version <agentId> [json\|--file file.json]`                | Create a version, optionally with`cloneFrom`.                            |
| `ck chat-agents publish <agentId> --versions <versionId>`                        | Publish one version.                                                       |

Read commands support `--file output.json`. Create accepts inline JSON, `@file`,
`--file`, or stdin with the same parsing and validation. Prefer `--file` for
prompts and function source code.

## Assigning a WhatsApp number

There's no dedicated `assign-whatsapp` command — set it via `ck chat-agents
update`:

```bash
ck chat-agents update <agentId> --set '{"whatsappPhoneNumber":"<phoneNumberId>","whatsappDisplayPhN":"<display name>"}'
```

The number itself comes from Meta via the WhatsApp Business Account linked on
the **CallKaro dashboard** — not the CLI, and not buyable. Run `ck whatsapp
list` to see what's available (see `numbers.md` § WhatsApp numbers). Requires
an active WhatsApp subscription on the account.

## Create safely

1. Run `ck whoami`.
2. Run `ck chat-agents models --json`; copy model IDs exactly.
3. Run `ck chat-agents list --json` to avoid duplicates.
4. Create the agent.
5. Read it back with `ck chat-agents get <id> --versions <versionId> --json`.

The minimum payload is:

```json
{
  "chatAgentName": "Support Chat"
}
```

```bash
ck chat-agents create '{"chatAgentName":"Support Chat"}'
```

Omitted fields receive these important defaults:

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

The CLI checks shape, ranges, conditional requirements, function names, and
webhook settings before contacting the API. The backend is still authoritative
for account-dependent model availability.

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
function `name` must match the Python `async def` name. The CLI defaults
`timeout` to 30 seconds and `directSend` to false.

Predefined function types are `send_template`, `send_contact`, `send_call`,
`send_image`, `send_document`, `send_video`, and `send_audio`.

- `send_template` requires `templateId`. Never construct or provide the
  `template` object yourself; the CLI fetches the approved provider template,
  replaces `templateId` with that object, and sends the authoritative data.
- `send_contact` requires a phone number or email in `contactData`.
- `send_call` requires `callAgentId`; its call window must end after it starts.
- Function names must be unique within each function list.

Before creating or updating a template function, list the available WhatsApp
templates and copy the template ID exactly. Chat-agent authoring currently
supports only `provider: "whatsapp"`.

```bash
ck chat-agents templates --provider whatsapp
ck chat-agents template <templateId> --provider whatsapp --json
```

The template detail response includes `variables`. Use every `variables[].id`
as an exact `varDescriptions` key. Infer its meaning from `context` and
`example`, but describe where the agent obtains the real runtime value rather
than copying the example. Ask the user when the meaning is ambiguous. The CLI
rejects missing descriptions before creating or updating the agent.

Variable IDs are derived by the CLI from the provider template:

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
The CLI resolves it through the authoritative Meta WhatsApp template API before
saving the runtime configuration.

## Versions

Create a clone before substantial changes:

```bash
ck chat-agents create-version <agentId> \
  '{"versionName":"support-v2","cloneFrom":"<publishedVersionId>"}'
ck chat-agents update <agentId> --versions <newVersionId> \
  --set @chat-agent-patch.json
ck chat-agents get <agentId> --versions <newVersionId> --json
ck chat-agents publish <agentId> --versions <newVersionId>
```

`cloneFrom` must identify a version belonging to the same chat agent. Creating
or updating a version does not publish it. Omitting `--versions` from get or
update targets the currently published version.
