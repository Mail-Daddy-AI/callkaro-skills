# Workflow chat agents
<!-- graph-summary: Workflow WhatsApp chat agents (agentMode workflow): a code-run graph with no prompt or model; flowGraph shape, every step type, code-step runtime, sources and counters, a full create example, editing and publish checks. -->

A Workflow agent (`agentMode: "workflow"`, the dashboard's Chat Center
Workflow) has **no prompt and no model**. On every inbound WhatsApp message,
code walks its `flowGraph` from the start: it runs Python code steps, checks
rules, sends messages, and can hand the message to a Basic or Advanced
WhatsApp agent, which then answers with its own model.

Use it for deterministic routing: keyword menus, button menus, order lookups,
spam or rate limits, and sending each chat to the right agent. Model, prompt,
function and follow-up settings are stored but unused. The type is fixed at
creation; the commands are the usual `ck chat-agents` ones from
[Chat agents](chat-agents.md).

## How a run works

- A run ends at an `end` step, at an `assign_agent` or `assign_version` step, or at an unwired
  exit.
- Sends are collected and delivered when the run ends. A send is **not** the
  end: any step can follow it.
- The graph may not loop — every message must reach an end. A run is capped at
  40 steps and 60 seconds.

## flowGraph shape

```json
{ "startNodeId": "start", "nodes": [ { "id": "start", "type": "start", "exits": [{ "id": "e1", "next": "route" }] } ] }
```

Every step: `id` (1–64 letters, digits, `_`, `-`; unique), `type`, optional
`name`, `exits: [{ "id", "label", "next" }]`. `next` is another step's `id` or
`""`. Exactly one `start`; at most 100 steps and 12 exits per step.

## Step types

| `type`             | Fields                                                                                                                                         | Exits                                                                        |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `start`          | —                                                                                                                                             | 1                                                                            |
| `code`           | `key` (variable name, unique, not `contact`/`message`), `code` (Python with `async def run():`), `timeout` (1–30 s, default 10) | 2 by position: success, failure                                             |
| `condition`      | —                                                                                                                                             | each `{label, condition, next}`; first that holds wins; then `{"fallback": true}` |
| `update_contact` | `assign: [{attribute, source}]` (≤20)                                                                                                      | 1                                                                            |
| `send_text`      | `message` with `{{contact.x}}`, `{{message.text}}`, `{{<key>.<path>}}`, `{{x.y\|default}}`                                     | 1                                                                            |
| `send_template`  | `templateId`, `variables {<varId>: source}`, `trackClicks` (default true)                                                              | 1                                                                            |
| `send_media`     | `mediaType` image/video/audio/document, `link` (fixed must be `https://`), `filename` (document), `caption` (not audio)            | 1                                                                            |
| `send_interactive` | `message`, `footer`, `buttonText`, `buttons: [{id, title ≤24, description?}]` (1–10)                                                | 1                                                                            |
| `assign_agent`   | `agentId` (a Basic or Advanced WhatsApp chat agent of this account, with a published version), `note` (context for that agent's turn)  | none — ends the run                                                         |
| `assign_version` | `versionId` (a Basic or Advanced version of **this same agent**; a workflow version can't be the target), `note` | none — ends the run |
| `end`            | —                                                                                                                                             | none                                                                         |

A button tap from `send_interactive` arrives as the **next** message. Route on
it at the top of the graph with a condition on `{"type": "message", "field":
"button_id"}`.

## Code steps

```python
async def run():
    async with httpx.AsyncClient(timeout=8) as client:
        r = await client.get("https://api.example.com/orders/latest",
                             params={"phone": x_context["user_phone_number"]})
    if r.status_code != 200:
        return {"status": "error", "message": r.text}
    return r.json()
```

In scope: `x_message` (`text`, `type`, `button_id`, `media_link`),
`x_history` (oldest first: `role`, `text`, `type`, `time`, `media_link`,
`agent_id`, `workflow_node`, `flow_step`), `x_results` (earlier code steps'
results by key), `x_contact`, `x_context` (`user_phone_number`,
`agent_phone_number`, `user_id`, `agent_id`, `msg_id`, `current_time`,
`current_date`, `timezone`, `is_test`, `contact`), `x_secrets` (see
[Account Secrets](secrets.md)), `update_contact_custom`, plus `asyncio`,
`httpx` and `json`.

The return value is kept under the step's `key` for every later step, as
`{{key.path}}` or a `result` source. Returning a dict whose `status` is
`"error"`, raising, or timing out takes the **failure** exit. Never put a
credential in the code; read it from `x_secrets`.

## Sources and conditions

| Source                                                        | Value                                                    |
| ------------------------------------------------------------- | -------------------------------------------------------- |
| `{"type": "fixed", "value": "..."}`                         | As written, with the placeholders above                  |
| `{"type": "contact", "attribute": "city"}`                  | A contact attribute                                      |
| `{"type": "result", "key": "order", "path": "status"}`      | A field of a code step's result                          |
| `{"type": "message", "field": "text"}`                      | `text`, `type`, `button_id` or `media_link` of the inbound message |

`contact`, `result` and `message` may carry `"fallback"`. Conditions can also
read:

- `{"type": "last_reply", "field": "agent"}` or `"node"` — who sent the last
  reply (an agent id or a workflow step id).
- `{"type": "counter", "counter": ..., "windowHours": 0}` — messages in this
  chat since it was last cleared: `user_messages`, `same_text` (the user sent
  this exact text), `node_sends` (with `"nodes": [stepIds]`), or
  `agent_replies` (with `"agentId"` and optional `"steps"`, Advanced step
  ids). `windowHours: 0` means no time window.

A condition is `{ "source": {...}, "op": "...", "value": "..." }`. `op`: `eq`,
`ne`, `contains`, `gt`, `lt`, `empty`, `not_empty`, `any_keyword` (`value`
is comma-separated keywords), `regex`.

## Template steps

Never write the `template` object. Put the ID from `ck chat-agents templates
--provider whatsapp` on the step as `templateId`, and give every variable id
from `ck chat-agents template <id> --provider whatsapp --json` (except
`HEADER::FILENAME`) a source. Workflow sources have no `ai` type — use
`fixed`, `contact`, `result` or `message`.

## Create example

Get the hand-off agent's id from `ck chat-agents list --json` (it must be a
Basic or Advanced WhatsApp agent with a published version), then:

```json
{
  "chatAgentName": "Inbound Router (Workflow)",
  "agentMode": "workflow",
  "flowGraph": {
    "startNodeId": "start",
    "nodes": [
      { "id": "start", "type": "start", "exits": [{ "id": "e1", "next": "route" }] },
      { "id": "route", "type": "condition", "exits": [
        { "id": "r_tap", "label": "tapped Orders", "condition": { "source": { "type": "message", "field": "button_id" }, "op": "eq", "value": "orders" }, "next": "lookup" },
        { "id": "r_menu", "label": "asked for menu", "condition": { "source": { "type": "message", "field": "text" }, "op": "any_keyword", "value": "hi, hello, menu" }, "next": "menu" },
        { "id": "fallback", "fallback": true, "next": "to_agent" }
      ] },
      { "id": "menu", "type": "send_interactive", "message": "How can we help?", "buttonText": "Options", "buttons": [{ "id": "orders", "title": "My orders" }, { "id": "support", "title": "Talk to support" }], "exits": [{ "id": "e1", "next": "" }] },
      { "id": "lookup", "type": "code", "key": "order", "timeout": 10, "code": "async def run():\n    async with httpx.AsyncClient(timeout=8) as client:\n        r = await client.get('https://api.example.com/orders/latest', params={'phone': x_context['user_phone_number']})\n    if r.status_code != 200:\n        return {'status': 'error', 'message': r.text}\n    return r.json()", "exits": [{ "id": "ok", "next": "status" }, { "id": "error", "next": "to_agent" }] },
      { "id": "status", "type": "send_text", "message": "Your order {{order.id|}} is {{order.status|being processed}}.", "exits": [{ "id": "e1", "next": "" }] },
      { "id": "to_agent", "type": "assign_agent", "agentId": "<basic-or-advanced-agent-id>", "note": "Routed by the inbound workflow." }
    ]
  }
}
```

```bash
ck chat-agents create --file workflow-agent.json
```

## Editing

`flowGraph` is replaced whole on every save. Read it back with `ck chat-agents
get <agentId> --json`, edit, and send the complete graph to a new version with
`ck chat-agents update <agentId> --versions <id> --set @patch.json`, then
publish — the same loop as [Advanced chat agents](chat-agents-advanced.md#editing-the-flow).

## Publish checks

`ck chat-agents publish` refuses a workflow with: no steps; an unconnected
start; a loop; an exit pointing at a missing step or the start; a code step
without `async def run():`; a condition with no rules, a rule with an unpicked
attribute, missing keywords/pattern, or a counter missing its agent or steps; a
`result` source naming no code step's key; an empty send; a
`send_interactive` without buttons or with duplicate titles; a template step
with no template; a non-`https://` media link; an `assign_agent` with no
agent, or one naming an agent that is not a published Basic or Advanced
WhatsApp agent of the account; an `assign_version` with no version, or one
naming a version that is missing, belongs to another agent, or is a workflow
version. Half-wired decision steps and unreachable steps
print as warnings.

Test before publishing with [Chat Simulations & Test Cases](chat-simulations/chat-simulation-playbook.md):
code steps are mocked by their `key` (see
[Workflow agents](chat-simulations/how-chat-simulation-works.md#workflow-agents)).
