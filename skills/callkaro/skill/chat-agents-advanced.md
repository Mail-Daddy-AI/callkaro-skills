# Advanced chat agents
<!-- graph-summary: Advanced WhatsApp chat agents (agentMode advanced): role, goal, instructions, rebuttals and a step flow the model follows; flowGraph shape, every step type, value sources, a full create example, editing and publish checks. -->

An Advanced agent (`agentMode: "advanced"`) is a WhatsApp chat agent whose
prompt is built from structured parts plus a **flow** of steps. The flow is not
walked by code: it is compiled into numbered steps `[S1]`, `[S2]`, … that the
model follows, and code does the deterministic parts — sends exact messages,
fills template variables from the contact or a function result, and checks rule
conditions. The model only decides what needs judgement.

Everything from [Chat agents](chat-agents.md) still applies: same `ck
chat-agents` commands, model, functions, follow-ups, webhook, versions and
WhatsApp number assignment. The type is fixed at creation.

## Version fields

| Field                       | Type                              | Use                                                                         |
| --------------------------- | --------------------------------- | --------------------------------------------------------------------------- |
| `role`                    | string                            | Who the agent is.                                                           |
| `goal`                    | string                            | What the conversation should achieve.                                       |
| `instructions`            | string[]                          | Rules, in order.                                                            |
| `rebuttals`               | `[{objection, response}]`       | Objection handling: answer along these lines, then return to the step.      |
| `flowGraph`               | object                            | The steps (below).                                                          |
| `functions`               | array                             | A `function` step calls one of these custom code functions by name.         |

`chatAgentSystemPrompt` is **not used** — the compiled role, goal,
instructions, flow, global intents and rebuttals replace it.

## flowGraph shape

```json
{ "startNodeId": "start", "nodes": [ { "id": "start", "type": "start", "exits": [{ "id": "e1", "next": "greet" }] } ] }
```

- Every step: `id` (1–64 letters, digits, `_`, `-`; unique), `type`, optional
  `name`, and `exits: [{ "id", "label", "next" }]`.
- `next` is another step's `id`, or `""` for an unwired exit (nothing more is
  planned there). Edges live **only** in `exits[].next`.
- Exactly one `start`. At most 150 steps and 12 exits per step. `layout`
  (`{ <id>: {x, y} }`) is optional canvas positioning.
- Steps are numbered breadth-first from the start, then from each global
  intent — the same `[S3]` you see on the dashboard canvas and in Test Chat.

## Step types

| `type`           | Fields                                                                                                                                                                                                              | Exits                                                                                                                                       |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `start`        | —                                                                                                                                                                                                                  | 1                                                                                                                                           |
| `text`         | `mode` `exact` (code sends `message` verbatim) or `guided` (`message` is guidance, the model writes it); `message`; `waitForReply` (default false)                                                   | 1                                                                                                                                           |
| `interactive`  | `mode`, `message`, `footer` (≤60), `buttonText` (≤20, the list button)                                                                                                                                      | buttons `{label ≤24, description?}` (1–10; ≤3 send as reply buttons, more as a list), then AI branches, then one `{"fallback": true}`. Always waits. |
| `template`     | `templateId`, `variables {<varId>: source}`, `trackClicks` (default true), `waitForReply` (default true)                                                                                                 | one per QUICK_REPLY button (`label` = button text exactly), AI branches, fallback — or one plain exit if the template has no quick replies |
| `media`        | `mediaType` image/video/audio/document, `link` (source; fixed must be `https://`), `filename` (document), `caption` (not audio), `waitForReply`                                                     | 1                                                                                                                                           |
| `function`     | `functionName` (a custom code function of this version), `message` (when/how to call it), `waitForReply` (true when the function sends its own message, e.g. a payment link)                              | 2 by position: success, failure                                                                                                            |
| `update_contact` | `assign: [{attribute, source}]` (≤20)                                                                                                                                                                          | 1                                                                                                                                           |
| `condition`    | —                                                                                                                                                                                                                  | each `{label, condition, next}`, then `{"fallback": true}` = otherwise                                                                   |
| `ask`          | `mode`, `message` (the question), `inputType` text/email/phone/number/date/url, `attribute` (contact attribute that stores the answer), `retryMessage` (never sent for text), `skipIfKnown` (default true) | 1. Waits.                                                                                                                                  |
| `global`       | `trigger` (when it applies, from anywhere in the chat)                                                                                                                                                            | 1, must be wired. When its branch ends the chat returns to the step it was on.                                                             |
| `call`         | `callAgentId` (a voice agent — `ck agents list`), `workflowId`, `callWindowStart`/`callWindowEnd` (hours 0–24, end after start), `callWindowOutside` defer/cancel, `message` (when to call)                | 1                                                                                                                                           |
| `contact_card` | `contactData {firstName, lastName, formattedName, phoneNumber, email, organization}` — a name and a phone or email                                                                                             | 1                                                                                                                                           |
| `end`          | `mode`, optional closing `message`                                                                                                                                                                                | none                                                                                                                                        |

Nothing may point at `start` or at a `global` step.

**AI branches** (on `interactive` and `template`) are exits the model decides
on: `{ "label": "Asks about price", "reply": true, "condition": { "kind":
"prompt", "prompt": "the user asks about pricing" }, "next": "..." }`. A button
can carry a prompt condition too: "taps it, or <condition>".

**Conditions** on a `condition` step's exits:

- `{ "kind": "rule", "source": {"type": "contact", "attribute": "city"}, "op": "eq", "value": "Pune" }`
- `{ "kind": "rule", "source": {"type": "function", "function": "check_slots", "path": "data.available"}, "op": "eq", "value": "true" }`
- `{ "kind": "prompt", "prompt": "the user sounds unhappy" }`

`op`: `eq`, `ne`, `contains`, `gt`, `lt`, `empty`, `not_empty`.

## Value sources

Used by template `variables`, media `link`/`filename`/`caption` and
`update_contact` rows:

| Source                                           | Value                                                                       |
| ------------------------------------------------ | --------------------------------------------------------------------------- |
| `{"type": "fixed", "value": "..."}`            | As written; may use `{{contact.city}}`, `{{check_slots.data.slot}}`, `{{x.y\|default}}` |
| `{"type": "contact", "attribute": "city"}`     | A contact attribute (`phone_number` is the CRM column)                     |
| `{"type": "function", "function": "fn", "path": "data.slot"}` | A field of that function's latest result                     |
| `{"type": "ai", "prompt": "..."}`              | The model fills it                                                          |

`fixed`, `contact` and `function` may carry `"fallback"` for when they have no
value. Exact-mode messages use the same `{{…}}` placeholders.

## Template steps

Same rule as `send_template` functions: never write the `template` object
yourself. List templates, read one, and put its ID on the step:

```bash
ck chat-agents templates --provider whatsapp
ck chat-agents template <templateId> --provider whatsapp --json
```

```json
{ "id": "offer", "type": "template", "templateId": "1234567890123456",
  "variables": { "BODY::{{1}}": { "type": "contact", "attribute": "name", "fallback": "there" } },
  "exits": [{ "id": "q1", "label": "Yes please", "next": "book" }, { "id": "fallback", "fallback": true, "next": "" }] }
```

The CLI swaps `templateId` for the approved template and refuses the payload
until every `variables[].id` the template returns (except `HEADER::FILENAME`)
has a source.

## Create example

Write the payload to a file and create it (this exact flow passes the publish
checks):

```json
{
  "chatAgentName": "Demo Booking (Advanced)",
  "agentMode": "advanced",
  "role": "You are Riya, a friendly sales assistant for Acme CRM on WhatsApp.",
  "goal": "Qualify the lead and book a product demo.",
  "instructions": ["Keep replies under 3 short sentences.", "Never quote prices; offer the demo instead."],
  "rebuttals": [{ "objection": "It's too expensive", "response": "Plans start small and the demo shows the ROI for their team size." }],
  "flowGraph": {
    "startNodeId": "start",
    "nodes": [
      { "id": "start", "type": "start", "exits": [{ "id": "e1", "next": "greet" }] },
      { "id": "greet", "type": "text", "mode": "exact", "message": "Hi {{contact.name|there}}! I'm Riya from Acme CRM.", "exits": [{ "id": "e1", "next": "menu" }] },
      { "id": "menu", "type": "interactive", "mode": "exact", "message": "What would you like to do?", "exits": [
        { "id": "b_demo", "label": "Book a demo", "next": "ask_email" },
        { "id": "b_info", "label": "Just exploring", "next": "explain" },
        { "id": "r_price", "label": "Asks about price", "reply": true, "condition": { "kind": "prompt", "prompt": "the user asks about pricing or cost" }, "next": "explain" },
        { "id": "fallback", "fallback": true, "next": "explain" }
      ] },
      { "id": "explain", "type": "text", "mode": "guided", "message": "Explain in two sentences how Acme CRM helps a sales team, then offer a demo.", "waitForReply": true, "exits": [{ "id": "e1", "next": "ask_email" }] },
      { "id": "ask_email", "type": "ask", "mode": "exact", "message": "Great! What's your work email?", "inputType": "email", "attribute": "email", "retryMessage": "That doesn't look like an email. Could you check it?", "exits": [{ "id": "e1", "next": "book" }] },
      { "id": "book", "type": "function", "functionName": "book_demo", "message": "Book the demo with the email the user gave.", "exits": [{ "id": "ok", "next": "done" }, { "id": "error", "next": "sorry" }] },
      { "id": "done", "type": "end", "mode": "exact", "message": "You're booked! The invite is on its way to {{contact.email}}." },
      { "id": "sorry", "type": "end", "mode": "guided", "message": "Apologise that booking failed and say a teammate will reach out today." },
      { "id": "human", "type": "global", "trigger": "The user asks to talk to a human", "exits": [{ "id": "e1", "next": "handoff" }] },
      { "id": "handoff", "type": "end", "mode": "exact", "message": "Sure, a teammate will message you shortly." }
    ]
  },
  "functions": [{
    "name": "book_demo",
    "description": "Book a product demo for the user's email",
    "source_code": "async def book_demo(email: str):\n    return {\"status\": \"success\", \"slot\": \"tomorrow 11:00\"}"
  }]
}
```

```bash
ck chat-agents create --file advanced-agent.json
ck chat-agents get <agentId> --json --file current.json
```

## Editing the flow

`flowGraph` is replaced whole on every save — there are no per-step commands.
Read it back, edit the JSON, and send the complete graph to a **new version**:

```bash
ck chat-agents get <agentId> --json --file current.json      # copy .chatAgent.flowGraph
ck chat-agents create-version <agentId> '{"versionName":"flow-v2","cloneFrom":"<publishedVersionId>"}'
ck chat-agents update <agentId> --versions <newVersionId> --set @flow-patch.json   # {"flowGraph": {...}}
ck chat-agents publish <agentId> --versions <newVersionId>
```

Template steps read back with their `template` object; send them back as they
are. To change a step's template, replace `template` with a new `templateId`.

## Publish checks

Saving accepts a half-built flow. `ck chat-agents publish` refuses one with:
no steps after the start; an unconnected start; an exit pointing at a missing
step, the start or a global; an empty message or guidance; an interactive step
without buttons or with duplicate / over-24-character button text; a template
step with no template; an empty fixed value or an unpicked attribute; a
non-`https://` media link; a function step naming a function the version lacks;
an `update_contact` with no rows; a condition branch with no condition; a
global with no trigger or no target; a call with no `callAgentId`; a contact
card without a name and a phone or email. Unreachable steps print as warnings
and do not block.

Test before publishing with [Chat Simulations & Test Cases](chat-simulations/chat-simulation-playbook.md).
