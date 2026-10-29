# Chat agents
<!-- graph-summary: Chat agents are a separate entity from voice agents: the three agent types (Basic, Advanced, Workflow), ck chat-agents usage, WhatsApp number assignment, safe creation, functions, pinned values and versions. -->

Chat agents are separate from voice agents. Use `ck chat-agents`; never send a
chat-agent payload to `ck agents`. Run `ck chat-agents --help` (and
`<command> --help`) for commands and flags. Payloads accept inline JSON,
`@file`, `--file` or stdin; prefer `--file` for prompts and function code.

## Agent types

`agentMode` is picked at creation and **cannot change afterwards** — to switch
type, create a new agent or (WhatsApp) a new version of the type you want:
each WhatsApp version carries its own `agentMode`, set by `create-version`, and
`ck chat-agents versions` shows it. All three run on WhatsApp.

| `agentMode`      | What it is                                                                                                                                                                  | Guide                                                    |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| `ai` (default) | **Basic**: a system prompt plus functions; the model answers every message. Everything below on this page.                                                                 | this page                                                |
| `advanced`     | **Advanced**: role, goal, instructions, objection handling and a step flow (`flowGraph`) the model follows. Code sends exact messages, fills template variables and checks rules. | [Advanced chat agents](chat-agents-advanced.md)          |
| `workflow`     | **Workflow**: no prompt, no model. Code walks a graph on every inbound message — runs Python, checks rules, sends messages, hands off to a Basic/Advanced agent or version.   | [Workflow chat agents](chat-agents-workflow.md)          |

Pick by the job: free-form conversation → `ai`; a guided conversation with a
planned script, buttons and branches → `advanced`; deterministic routing or
lookups with no LLM (keyword menus, order status, hand-off to the right agent)
→ `workflow`.

The CLI refuses `role`/`goal`/`instructions`/`rebuttals` unless the agent is
`advanced`, and a non-empty `flowGraph` unless it is `advanced` or `workflow`.
On `update` and `create-version` it reads the agent's mode first and checks the
patch against it.

## Create safely

1. `ck whoami`, then pick the agent type (see [Agent types](#agent-types)).
2. `ck chat-agents models --json` (copy model IDs exactly) and
   `ck chat-agents list --json` (avoid duplicates).
3. `ck chat-agents create '{"chatAgentName":"Support Chat"}'`: that is the
   minimum. Omitted fields get safe defaults (`whatsapp`/`ai`/`in-progress`,
   version `v1`, model `callkaro/arjuna-2.5`, contextLength 10, no follow-ups
   or functions).
4. Read it back: `ck chat-agents get <id> --versions <versionId> --json`.

The CLI validates shape, ranges, function names and webhooks locally; the
backend still decides model availability.

## WhatsApp number

No `assign-whatsapp` command; set it with update:

```bash
ck chat-agents update <agentId> --set '{"whatsappPhoneNumber":"<phoneNumberId>","whatsappDisplayPhN":"<display name>"}'
```

Numbers come from Meta via the WhatsApp Business Account linked on the
dashboard (not buyable here). `ck whatsapp list` shows them (`numbers.md`).
Needs an active WhatsApp subscription.

## Functions

Custom functions omit `type` and need `source_code` + `description`; `name`
must match the Python `async def` name; names are unique per list. Predefined
types: `send_template`, `send_contact`, `send_call`, `send_image`,
`send_document`, `send_video`, `send_audio`.

- `send_template`: give `templateId` only. Never build the `template` object;
  the CLI fetches the approved Meta template and substitutes it. Look it up with
  `ck chat-agents templates --provider whatsapp` / `template <id> --json` and
  copy the ID exactly. `provider` is always `"whatsapp"`.
- `varDescriptions`: one entry per `variables[].id` from the template detail,
  using those IDs verbatim (`BODY::{{1}}`, `HEADER::{{1}}`, `HEADER::MEDIA`,
  `HEADER::FILENAME`, `BUTTON_URL[0]::{{1}}`). Describe where the agent gets the
  real runtime value, not the template's example. Ask the user if unclear; the
  CLI rejects missing descriptions, except for variables pinned in `varSources`.
- `send_contact`: a phone number or email in `contactData`.
- `send_call`: `callAgentId`; the call window must end after it starts.
- A media send's `link` (and a document's `filename`, and the `caption`) come
  from the model unless pinned in `sources` (below).
- Never put secrets in a payload; use `x_secrets.NAME` in headers.

```json
{"name":"send_booking_confirmation","type":"send_template","provider":"whatsapp",
 "description":"Send after a booking is confirmed","templateId":"1234567890123456",
 "varDescriptions":{"BODY::{{1}}":"Customer first name"},"trackClicks":true}
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

## Versions

Clone before substantial changes. Creating or updating never publishes; omit
`--versions` on get/update to target the published version. `cloneFrom` must be
a version of the same agent.

```bash
ck chat-agents create-version <agentId> '{"versionName":"v2","cloneFrom":"<versionId>"}'
ck chat-agents update <agentId> --versions <newVersionId> --set @patch.json
ck chat-agents publish <agentId> --versions <newVersionId>
```

A Workflow version can hand a message to a Basic/Advanced version of the *same*
agent (`assign_version`) or to another agent (`assign_agent`); see
[Workflow chat agents](chat-agents-workflow.md). With `assign_version` every
message keeps the same `agentId` and only `versionId` differs, so agent-keyed
lookups and audit strategies still cover them.

### Delete, import and commit history

```bash
ck chat-agents delete-version <agentId> --versions <versionId>
ck chat-agents import-versions <agentId> --file versions.json   # add versions to this agent
ck chat-agents import --file v1.json --file v2.json             # create a new agent
ck chat-agents commits <agentId> [--versions <versionId>] [--page 2]
ck chat-agents commit <commitId> --json                         # the commit's full saved state
ck chat-agents revert <agentId> <commitId>
```

- **Delete is permanent.** It removes the version and its commit history, so it
  cannot be restored. It is refused for the published version and for a version
  another version's `assign_version` step routes to — publish another version or
  remove that step first.
- **Import files** are exported JSON: one object per version, as an array or a
  single object; repeat `--file` for several files. Every entry is validated
  before any is written, so one bad entry means nothing is imported.
- **`import-versions`** adds versions to an existing agent. Agent-level fields in
  the file (name, phone numbers, published version) are ignored.
- **`import`** creates a new agent. Several entries become **one agent with that
  many versions**, not several agents; the first entry is published. Agent-level
  fields (`chatAgentName`, `channel`, `agentStatus`, `instagramAgentType`) must be
  identical across entries, or it fails listing the mismatches. On WhatsApp the
  version type (`agentMode`) may differ per entry. WhatsApp numbers and the
  exported `publishedVersionId` are never carried over.
- **Commits** record every create, save, duplicate and import of a version, each
  holding the version's full state. `commits` lists them newest first.
- **`revert`** sets a version back to a commit's state. The revert is itself
  recorded as a new commit, so it can be undone the same way; the version keeps
  its own type.

## Testing

Use chat simulations before publishing: an AI plays the user, the agent replies
in test mode, a grader scores each conversation. Start with
[Chat Simulations & Test Cases](chat-simulations/chat-simulation-playbook.md);
commands are under `ck chat-sim`.
