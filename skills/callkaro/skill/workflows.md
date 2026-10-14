# Workflows

A workflow is a **graph of steps run per contact**: call them, wait, WhatsApp
them, branch on what happened, update their CRM record. The dashboard draws it
on a canvas; the CLI reads and writes the same JSON (`{ nodes, edges }`).
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

Run `ck workflows schema` for a sample of **every** node type, the edge rules,
and the condition ops/sources. That output is the authority; this file is the
method.

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
- `conversion_status` is `"true"`/`"false"`. The `hangup_reason` values are printed by `ck workflows schema`.
- `update-lead` and `contact`-source values use **CRM attribute names** (the `name`, not the display label). They must already exist — see [contacts.md](contacts.md).
- **`wa-template` `parameters`**: one row per template variable, `{key, source, value}`, with `key` = `ORIGIN::token` (`BODY::{{1}}`, `HEADER::MEDIA`, `BUTTON_URL[0]::{{1}}`). `context` prints the exact keys per template — copy them, don't compose them.
- `fn_response` fields are `<apiNodeId>.returned.<key>`.

## Commands

| Command | What it does |
|---|---|
| `ck workflows schema` | The graph reference: every node type with a sample, edges, condition ops/sources |
| `ck workflows list [--search] [--json]` / `get <id> [--json]` | Browse. `get --json` is the full graph |
| `ck workflows create <name> [--file graph.json]` | Create (no graph = just Start and End) |
| `ck workflows import --file x.json [--name]` | Create from a dashboard export or a bare graph |
| `ck workflows update <id> [--name] [--file graph.json]` | **Replaces the whole graph** (and/or renames) |
| `ck workflows validate [<id>] [--file graph.json]` | Dry-run: every problem, each with its `nodeId`. Nothing is saved |
| `ck workflows export <id> [--file]` / `duplicate <id> [--name]` / `delete <id> [--yes]` | As the dashboard |
| `ck workflows add-node <id> --type T [--after <nodeId> [--handle h]] [--name] [--set <json\|@file>]` | Add one node. With `--after` it is **spliced into the chain** |
| `ck workflows set-node <id> <nodeId> [--set <json\|@file>] [--name]` | Merge fields into a node (id and type are fixed) |
| `ck workflows remove-node <id> <nodeId> [--reconnect] [--yes]` | Remove a node and its edges; `--reconnect` bridges its neighbours |
| `ck workflows connect <id> --from A --to B [--handle h]` / `disconnect <id> --from A [--handle h]` | Edit a link |
| `ck workflows leads <id>` / `lead <id> <phone>` / `run <id> <phone>` / `journey <id> <phone>` | Results — see below |

## Generate a workflow from a request

```bash
ck workflows schema                        # 1. learn the shapes
# 2. gather real ids — never invent them:
ck agents list --json                      # agentId for Send Call (prefer agentStatus "live")
ck whatsapp list --json                    # phoneNumberId + display number for WhatsApp nodes
ck chat-agents templates --json            # template id / name / language / status (use APPROVED)
ck chat-agents template <templateId> --json   # its variables[].id = the exact parameters[].key values
ck contacts attributes list --json         # CRM attribute names for update-lead / contact conditions
ck agents get <agentId> --json             # publishedVersionId
ck agents get <agentId> --versions <publishedVersionId> --json   # postcall[].name = post_call_variables fields (skip type call_drop_off_reason)
# 3. write graph.json using ONLY ids/names from those listings
ck workflows validate --file graph.json    # 4. fix every reported problem, repeat
ck workflows create "Name" --file graph.json
ck workflows get <id> --json               # 5. read back what was saved
```

If a listing is empty (no WhatsApp number linked, no APPROVED template, no live agent), do
not build a node that needs it — tell the user.

When a value can't be listed — a `fn_response` or `call_metadata` key — **ask the user**;
don't guess.

## Edit an existing workflow

Prefer the small edits; they touch only what you name and re-validate on save:

```bash
ck workflows add-node <id> --type wait --after <callNodeId> --set '{"minutes":120}'
ck workflows set-node <id> <nodeId> --set @patch.json
ck workflows connect <id> --from <condId> --handle <exitId> --to <nodeId>
ck workflows remove-node <id> <nodeId> --reconnect --yes
```

- After a `conditions` node, `add-node --after` needs `--handle <exitId>` (the error lists them).
- `add-node` saves immediately, so types with no sensible default need `--set` up front — `send-call` (`agentId`), `wa-template` (`templateId`…), `wa-message` (`message`…), `api-basic` (`url`), `update-lead` (`updates`). The error shows an example. A new `conditions` node starts as a complete "did the call connect?" rule (`connected_call` = true); change it with `set-node --set @exits.json`.
- Replacing a conditions node's `exits` via `set-node` drops the edges of exits you removed.
- Inline `--set '{…}'` is fragile in shells; for anything non-trivial write a file and use `@file`.
- The server validates on every save; an edit that would leave **no path to End** is rejected with the reason. Read it, fix, retry.
- The last save wins — don't edit a workflow someone else may be editing.
- **Editing a workflow that has leads running** may change what they do next. This pack has not verified how in-flight runs react — confirm with the user first.

## Read results

```bash
ck workflows leads <id> --json             # who is enrolled, status, current step, call count
ck workflows lead <id> <phone>             # one lead's call totals + enrolment time
ck workflows run <id> <phone>              # that lead's latest run, step by step (why it branched)
ck workflows run <id> <phone> --json       # + each step's results and the run variables
ck workflows journey <id> <phone>          # every call to/from that number in this workflow
```

`run` is the debugging tool: the step table shows each node, its status, the
handle taken, and any error; `--json` adds the variables a Conditions node was
testing against.
