<!-- graph-summary: Workflow graphs: steps (call, wait, WhatsApp, branch, CRM update), the JSON spec, validation rules and reading runs. Use to design a workflow the user builds on the dashboard. -->
# Workflows

A workflow is a **graph of steps run per contact**: call them, wait, WhatsApp
them, branch on what happened, update their CRM record. The dashboard draws it
on a canvas and imports/exports the same JSON (`{ nodes, edges }`). The user
creates, edits and runs workflows on the CallKaro dashboard; there is no
harness tool for workflows.
Enrolling contacts is in [contacts.md](contacts.md); the two together are in
[workflows-and-contacts.md](workflows-and-contacts.md).

Only **normal** workflows are editable. Older "AI" workflows are read-only and
are not covered here.

## The graph

```json
{
  "nodes": [
    {"id":"start-1","type":"start","name":"Start","x":320,"y":180},
    {"id":"wait-1","type":"wait","name":"Wait","minutes":2,"x":640,"y":180},
    {"id":"send-call-1","type":"send-call","name":"Send Call","agentId":"<agentId>","retries":0,"retryGapMinutes":30,"retryGaps":[],"x":960,"y":180},
    {"id":"cond-1","type":"conditions","name":"Picked up?","x":1280,"y":180,"exits":[
      {"id":"o_yes","label":"connected","next":"","condition":{"source":"connected_call","field":"","op":"eq","value":true}},
      {"id":"o_else","label":"otherwise","next":""}]},
    {"id":"end-1","type":"end","name":"End","x":1600,"y":180}
  ],
  "edges": [
    {"id":"e1","from":"start-1","fromHandle":"out","to":"wait-1"},
    {"id":"e2","from":"wait-1","fromHandle":"out","to":"send-call-1"},
    {"id":"e3","from":"send-call-1","fromHandle":"out","to":"cond-1"},
    {"id":"e4","from":"cond-1","fromHandle":"o_yes","to":"end-1"},
    {"id":"e5","from":"cond-1","fromHandle":"o_else","to":"end-1"}
  ]
}
```

The full spec — a sample of **every** node type, the edge rules, and the
condition ops/sources — is [platform/workflows-official-spec.md](platform/workflows-official-spec.md).

### Node types (exactly these — the dashboard's Add Node menu)

| Dashboard name | `type` | Must have |
|---|---|---|
| (created with the workflow) | `start` | exactly one; never added |
| End | `end` | at least one reachable from Start |
| Send Call | `send-call` | `agentId` |
| Send WhatsApp Template | `wa-template` | `templateId` (+ name, language, body, `parameters`, `phoneNumberId`, `displayPhoneNumber`, `provider`) |
| Send WhatsApp Message | `wa-message` | `message`, `phoneNumberId`, `displayPhoneNumber` |
| Wait | `wait` | `minutes` ≥ 1 |
| Conditions | `conditions` | `exits` (≥ 1) |
| API Call — Basic | `api-basic` | `url` |
| API Call — Advanced | `api-advanced` | `code` (`async function handler(context) {…}`) |
| Update Contact | `update-lead` | `updates: [{attribute, source, value}]` |

### Rules that bite

- **Ids are unique across the graph.** Node ids like `wait-<timestamp>`, edge ids like `edge-<timestamp>`, exit ids like `o_<random>`.
- **One edge per (node, handle).** A normal node's handle is `"out"`. A `conditions` node has one handle **per exit**, and the handle is the **exit's `id`**.
- **Nothing leaves an End; nothing enters Start.** There must be a path Start → End.
- A **dangling handle is legal** (the run ends there); an unreachable parked node is legal. Neither blocks a save.
- **Conditions**: the exit with **no** `condition` is the fallback (`label: "otherwise"`). Sources `phone_number`, `connected_call`, `voicemail`, `hangup_reason`, `call_duration`, `conversion_status` take **no** `field`; `contact`, `post_call_variables`, `call_metadata`, `fn_response`, `static_value` **need** one.
- `conversion_status` is `"true"`/`"false"`. The `hangup_reason` values are in the spec.
- `update-lead` and `contact`-source values use **CRM attribute names** (the `name`, not the display label). They must already exist — see [contacts.md](contacts.md).
- **`wa-template` `parameters`**: one row per template variable, `{key, source, value}`, with `key` = `ORIGIN::token` (`BODY::{{1}}`, `HEADER::MEDIA`, `BUTTON_URL[0]::{{1}}`). The exact keys come from the template's variables (`check_whatsapp_readiness` `get_template`) — copy them, don't compose them.
- `fn_response` fields are `<apiNodeId>.returned.<key>`.

## On the dashboard

The user creates (no graph = just Start and End), imports (a dashboard export
or a bare graph), duplicates, exports, deletes and edits workflows there.
Replacing a graph **replaces the whole graph**. Every save is validated: each
problem is reported with its `nodeId`, and nothing is saved until it is clean.

## Generate a workflow from a request

1. Learn the shapes from the spec.
2. Gather real ids — never invent them:
   - `list_agents` → `agentId` for Send Call (prefer a live, published agent).
   - `list_phone_numbers` (WhatsApp) → `phoneNumberId` + display number for WhatsApp nodes.
   - `check_whatsapp_readiness` → approved templates (id / name / language), and
     `get_template` for one template's variables = the exact `parameters[].key` values.
   - CRM attribute names for `update-lead` / contact conditions: ask the user
     (the dashboard lists them).
   - `read_version` on the agent's published version → `postcall[].name` =
     `post_call_variables` fields (skip type `call_drop_off_reason`).
3. Write the graph JSON using ONLY ids/names from those listings.
4. The user imports or creates it on the dashboard, which validates on save;
   fix every reported problem and repeat.
5. Have the user check the saved graph; walk each branch to an End.

If a listing is empty (no WhatsApp number linked, no APPROVED template, no live agent), do
not build a node that needs it — tell the user.

When a value can't be listed — a `fn_response` or `call_metadata` key — **ask the user**;
don't guess.

## Edit an existing workflow

The user edits on the dashboard canvas: adding, changing, removing and
connecting nodes.

- After a `conditions` node, a new node goes on one exit's handle.
- Types with no sensible default need their required fields set up front — `send-call` (`agentId`), `wa-template` (`templateId`…), `wa-message` (`message`…), `api-basic` (`url`), `update-lead` (`updates`). A new `conditions` node starts as a complete "did the call connect?" rule (`connected_call` = true).
- Replacing a conditions node's `exits` drops the edges of exits you removed.
- The server validates on every save; an edit that would leave **no path to End** is rejected with the reason. Read it, fix, retry.
- The last save wins — don't edit a workflow someone else may be editing.
- **Editing a workflow that has leads running** may change what they do next. This pack has not verified how in-flight runs react — confirm with the user first.

## Read results

On the dashboard the user sees who is enrolled (status, current step, call
count), one lead's call totals and enrolment time, that lead's latest run step
by step, and every call to/from that number in this workflow (its journey).

The run view is the debugging tool: each node, its status, the handle taken,
and any error, plus the variables a Conditions node was testing against.
