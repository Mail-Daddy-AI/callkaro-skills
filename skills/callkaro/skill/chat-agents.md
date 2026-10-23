# Chat agents
<!-- graph-summary: Chat agents are a separate entity from voice agents: the three agent types (Basic, Advanced, Workflow), ck chat-agents commands, WhatsApp number assignment, safe creation, prompt/model setup, functions and versions. -->

Chat agents are separate from voice agents. Use `ck chat-agents`; do not send a
chat-agent payload to `ck agents`.

## Agent types

`agentMode` is picked at creation and **cannot change afterwards** — to switch
type, create a new agent. All three run on WhatsApp.

| `agentMode`      | What it is                                                                                                                                                                  | Guide                                                    |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| `ai` (default) | **Basic**: a system prompt plus functions; the model answers every message. Everything below on this page.                                                                 | this page                                                |
| `advanced`     | **Advanced**: role, goal, instructions, objection handling and a step flow (`flowGraph`) the model follows. Code sends exact messages, fills template variables and checks rules. | [Advanced chat agents](chat-agents-advanced.md)          |
| `workflow`     | **Workflow**: no prompt, no model. Code walks a graph on every inbound message — runs Python, checks rules, sends messages, hands off to a Basic/Advanced agent.             | [Workflow chat agents](chat-agents-workflow.md)          |

Pick by the job: free-form conversation → `ai`; a guided conversation with a
planned script, buttons and branches → `advanced`; deterministic routing or
lookups with no LLM (keyword menus, order status, hand-off to the right agent)
→ `workflow`.

The CLI refuses `role`/`goal`/`instructions`/`rebuttals` unless the agent is
`advanced`, and a non-empty `flowGraph` unless it is `advanced` or `workflow`.
On `update` and `create-version` it reads the agent's mode first and checks the
patch against it.

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
2. Pick the agent type (see [Agent types](#agent-types)); it is fixed once created.
3. Run `ck chat-agents models --json`; copy model IDs exactly.
4. Run `ck chat-agents list --json` to avoid duplicates.
5. Create the agent.
6. Read it back with `ck chat-agents get <id> --versions <versionId> --json`.

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
- A media send takes its `link` — and a document's `filename`, and the
  `caption` — from the model at run time unless the function pins it in
  `sources`. See *Pinned values* below.
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
rejects missing descriptions before creating or updating the agent — except for
variables pinned in `varSources`, which the model is never asked for.

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

### Pinned values

A send function's media link — and a document's file name, and the caption —
can be fixed in the configuration instead of produced by the model. A pinned
field is dropped from the tool the model sees, so it is never asked for it and
the value cannot come back truncated, translated or invented.

- `send_template`: `varSources`, keyed by the same IDs as `varDescriptions`.
  In practice only `HEADER::MEDIA` is worth pinning. `HEADER::FILENAME` is not
  a parameter of the chat template tool, so pinning it does nothing.
- `send_image`, `send_document`, `send_video`, `send_audio`: `sources`, keyed
  by tool parameter — `link`, `filename` (document only), `caption` (not
  audio).

Each entry is `{"type": "fixed", "value": "..."}` or `{"type": "ai"}`. A field
with no entry is the model's, which is how every agent saved before this
existed behaves, so never add `sources` or `varSources` to a function you are
editing for an unrelated reason.

```json
{
  "name": "send_price_list",
  "type": "send_document",
  "description": "Send the price list when the customer asks about pricing",
  "sources": {
    "link": { "type": "fixed", "value": "https://cdn.example.com/price-list.pdf" },
    "filename": { "type": "fixed", "value": "Acme Price List 2026.pdf" },
    "caption": { "type": "ai" }
  }
}
```

Pin what identifies the file; leave the caption to the model so it follows the
conversation's language. A fixed `link` or `HEADER::MEDIA` must be `https://`,
and a fixed field with an empty value is rejected.

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

## Testing with simulations

Test a chat agent before publishing with chat simulations: an AI plays the
user, the agent replies in test mode, and a grader scores each conversation.
Start with [Chat Simulations & Test Cases](chat-simulations/chat-simulation-playbook.md);
commands are under `ck chat-sim`.
