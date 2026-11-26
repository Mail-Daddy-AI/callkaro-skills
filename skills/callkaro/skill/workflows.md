# Workflows
<!-- graph-summary: Build and run workflow graphs per contact: every node type (Send Call, Wait, Conditions, WhatsApp, API, Update Contact, and the Inbound Call, Cancel Workflow and Resume Where They Were nodes for call-backs), the trigger window that keeps every node inside set hours, the rules that bite, commands, versions (draft, publish, which leads run on which), A/B testing between versions (split, rules, JS, results), generating a graph from a request using real ids, editing, and reading results. -->

A workflow is a **graph of steps run per contact**: call them, wait, WhatsApp
them, branch on what happened, update their CRM record. The dashboard draws it
on a canvas; the CLI reads and writes the same JSON (`{ nodes, edges }`).
Enrolling contacts is in [contacts.md](contacts.md); the two together are in
[workflows-and-contacts.md](workflows-and-contacts.md).

Only **normal** workflows are editable. Older "AI" workflows are read-only and
are not covered here.

Every workflow has **versions**, each with its own graph, and exactly one is
**live**. Everything below that reads or edits a graph works on the live
version unless you pass `--version-id <id>`. See [Versions](#versions).

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
| (created with the workflow) | `start` | exactly one; never added. Optional `triggerWindow` — see [Trigger window](#trigger-window) |
| Inbound Call | `inbound` | at most one; the second entry point |
| End | `end` | an `end` or `cancel` reachable from Start |
| Cancel Workflow | `cancel` | — (optional `reason`, shown in the run log) |
| Resume Where They Were | `resume` | — (needs an `inbound` node in the workflow) |
| Send Call | `send-call` | `agentId` (timing and other options: next section) |
| Send WhatsApp Template | `wa-template` | `templateId` (+ name, language, body, `parameters`, `provider`: `whatsapp` (default), `heltar` or `aisensy`; `phoneNumberId` and `displayPhoneNumber` for `whatsapp`) |
| Send WhatsApp Message | `wa-message` | `message`, `phoneNumberId`, `displayPhoneNumber`. `provider` is `whatsapp` (default) or `heltar`; free text is not sent on `aisensy`. Each `{{name}}` in the message is bound by a `parameters` row `{key: "{{name}}", source, value}` |
| Wait | `wait` | `minutes` ≥ 1 |
| Conditions | `conditions` | `exits` (≥ 1) |
| API Call — Basic | `api-basic` | `url` (+ `method`, default `POST`; `parameters`, `headers`, `body`, `bodyParameters`: see below) |
| API Call — Advanced | `api-advanced` | `code` (`async function handler(context) {…}`) |
| Update Contact | `update-lead` | `updates: [{attribute, source, value}]` |

### Send Call options (all optional)

| Field | Meaning |
|---|---|
| `scheduleMode` | `"datetime"` (default) or `"time"`. Picks which of the next two applies. |
| `scheduleAt` | `datetime` mode: hold the call until this IST date-time, `"YYYY-MM-DDTHH:mm:ss"`. A time already past calls straight away. |
| `scheduleTime` | `time` mode: a daily IST time, `"HH:mm:ss"`. A lead reaching the step before it is called at it that day; up to 5 minutes after, straight away; any later, at that time the next day. This is how to do "call at 10 am". |
| `minTriggerTime` / `maxTriggerTime` | `"HH:mm"` IST window for this step's calls **and its retries**. Empty = the workflow's own calling window (else `00:00`–`23:59`). |
| `carryOver` | Default `true`: a call that lands outside the window waits for the window to reopen. `false` drops it. |
| `retries` / `retryGapMinutes` / `retryGaps[]` | How many retries, and one gap in minutes per retry. A blank gap reuses the one before it (default 30). |
| `fromNumber` | The number to call from, digits without `+` (from `ck numbers list`). `""` = the agent's own number. A spammed or released number falls back to the agent's number. |
| `language` | Language code the agent speaks (`hi en kn mr ta te bn gu ml`). Left out = the workflow's language, else `"en"`; `""` = the agent's own default language. |
| `languageSource` / `languageValue` | Take the language from the lead: `languageSource` is `contact`, `call_metadata` or `fn_response`, `languageValue` the field (e.g. `contact` + `language`). `"hi"`, `"Hindi"` and `"hi-IN"` all work; a value it can't read falls back to `language`. `static_value` (the default) just uses `language`. |
| `metadata` | `[{key, source, value}]` rows sent to the agent as `{{metadata.<key>}}`, on top of what the lead was enrolled with. Sources as in Conditions. |

A scheduled time outside the window moves to the next window opening when `carryOver` is on; with it off, the call is not placed and the step moves on with `placed: false` and the reason in its result.

### Trigger window

`triggerWindow` on the `start` node limits **every node** of the workflow — calls, WhatsApp,
API calls, Update Contact, Wait, Conditions, End — to the hours it allows. A lead who reaches a
node outside the window **waits at that step** and carries on when the window next opens;
nothing is skipped or cancelled. Leads can be enrolled at any time. In the dashboard it is the
clock control beside "Find a node" on the canvas toolbar.

```json
{"enabled": true, "schedule": {
  "1": {"start": "10:00", "end": "19:00"}, "2": {"start": "10:00", "end": "19:00"},
  "3": {"start": "10:00", "end": "19:00"}, "4": {"start": "10:00", "end": "19:00"},
  "5": {"start": "10:00", "end": "17:00"}, "6": {"start": "11:00", "end": "14:00"}}}
```

- `schedule` keys are weekdays, `"0"` = Sunday … `"6"` = Saturday. A day left out is **closed**.
- Times are `"HH:mm"` India time (IST); end after start. `"23:59"` as the
  end means until midnight. No overnight ranges (`22:00`–`02:00`). At least one day open.
- No `triggerWindow` (or `enabled: false`) = runs at any time — how every older workflow behaves.
- Set it: `ck workflows set-node <id> <startNodeId> --set @window.json` with
  `{"triggerWindow": {…}}` in the file.
- It is **separate** from a Send Call's `minTriggerTime`/`maxTriggerTime` and from `--window` on
  `ck contacts assign`. The trigger window decides when the Send Call **node runs**; the call's
  own window still decides when the **call is placed**. Use the trigger window when WhatsApp and
  API steps must respect business hours too.
- A waiting lead shows in `ck workflows run` as a `waiting` step with the note *Outside the
  trigger window* and the time it resumes.

### Rules that bite

- **Ids are unique across the graph.** Node ids like `wait-<timestamp>`, edge ids like `edge-<timestamp>`, exit ids like `o_<random>`.
- **One edge per (node, handle).** A normal node's handle is `"out"`. A `conditions` node has one handle **per exit**, and the handle is the **exit's `id`**.
- **Nothing leaves an End, Cancel or Resume; nothing enters Start or Inbound.** There must be a path Start → End or Cancel.
- A **dangling handle is legal** (the run ends there — except after an Inbound node, where the lead is handed back instead); an unreachable parked node is legal. Neither blocks a save.
- **Conditions**: the exit with **no** `condition` is the fallback (`label: "otherwise"`). Sources `phone_number`, `connected_call`, `voicemail`, `hangup_reason`, `call_duration`, `conversion_status` take **no** `field`; `contact`, `post_call_variables`, `call_metadata`, `fn_response`, `static_value` **need** one.
- `conversion_status` is `"true"`/`"false"`. The `hangup_reason` values are printed by `ck workflows schema`.
- `update-lead` and `contact`-source values use **CRM attribute names** (the `name`, not the display label). They must already exist — see [contacts.md](contacts.md).
- **`wa-template` `parameters`**: one row per template variable, `{key, source, value}`, with `key` = `ORIGIN::token` (`BODY::{{1}}`, `HEADER::MEDIA`, `BUTTON_URL[0]::{{1}}`). `context` prints the exact keys per template — copy them, don't compose them.
- `fn_response` fields are `<nodeId>.<path into its result>`. An `api-basic` result is `{ok, status, body}` → `<nodeId>.body.data.id`, `<nodeId>.ok`. An `api-advanced` result is `{success, returned}` → `<nodeId>.returned.<key>`, `<nodeId>.success`.
- **`api-basic`**: `url` and `body` take `{{name}}` placeholders; `parameters` binds the URL's and `bodyParameters` the body's, each row `{key: "{{name}}", source, value}`. `body` is a JSON string: a placeholder inside quotes becomes text, a bare one a JSON value. `headers` rows are `{key, source, value}` with source `secret` (value = a name from `ck secrets list`) or `static_value`. Never put an API key in a `static_value` header.

## Commands

| Command | What it does |
|---|---|
| `ck workflows schema` | The graph reference: every node type with a sample, edges, condition ops/sources |
| `ck workflows list [--search] [--json]` / `get <id> [--version-id] [--json]` | Browse. `get --json` is the full graph of that version (live by default) plus the version list |
| `ck workflows create <name> [--file graph.json]` | Create (no graph = just Start and End) |
| `ck workflows import --file x.json [--name]` | Create from a dashboard export or a bare graph |
| `ck workflows update <id> [--name] [--file graph.json] [--version-id] [--commit <msg>]` | **Replaces a version's whole graph** (live by default) and/or renames the workflow |
| `ck workflows validate [<id>] [--version-id] [--file graph.json]` | Dry-run: every problem, each with its `nodeId`. Nothing is saved |
| `ck workflows export <id> [--file] [--version-id]` / `duplicate <id> [--name] [--version-id]` / `delete <id> [--yes]` | As the dashboard. A duplicate is a new workflow whose `v1` is that version |
| `ck workflows versions <id>` | Every version, which one is live |
| `ck workflows create-version <id> --name <name> [--from <versionId>]` | Draft copy of a version (default: the live one). Names are unique per workflow |
| `ck workflows publish <id> <versionId>` | Make a version live |
| `ck workflows delete-version <id> <versionId> [--yes]` | Delete a draft (not the live one, the last one, or one with leads running on it) |
| `ck workflows add-node <id> --type T [--after <nodeId> [--handle h]] [--name] [--set <json\|@file>]` | Add one node. With `--after` it is **spliced into the chain**. This and the other node edits below take `--version-id` |
| `ck workflows set-node <id> <nodeId> [--set <json\|@file>] [--name]` | Merge fields into a node (id and type are fixed) |
| `ck workflows remove-node <id> <nodeId> [--reconnect] [--yes]` | Remove a node and its edges; `--reconnect` bridges its neighbours |
| `ck workflows connect <id> --from A --to B [--handle h]` / `disconnect <id> --from A [--handle h]` | Edit a link |
| `ck workflows leads <id> [--version-id]` / `lead <id> <phone>` / `run <id> <phone>` / `journey <id> <phone>` | Results — see below |

## Versions

A workflow holds several versions; each has its own graph. Exactly one is **live**.

- **New leads run on the live version** (enrolled from the CRM, `ck contacts assign`, or the API),
  unless [A/B testing](#ab-testing) routes them elsewhere. To enrol into one version, pass
  `ck contacts assign … --workflow-version <versionId>` (this skips A/B).
- **A lead already running stays on the version it started on**, even after another version is
  published. Each run records its version, and every later step reads that version's graph.
- **Editing a version changes the path of leads running on it** — including the live one. To change
  a workflow that has leads running without touching them, edit a draft and publish it:

```bash
ck workflows versions <id>                                          # which is live
ck workflows create-version <id> --name "Shorter wait"              # draft copy of the live one
ck workflows set-node <id> <nodeId> --version-id <versionId> --set '{"minutes":60}'
ck workflows validate <id> --version-id <versionId>
ck workflows publish <id> <versionId>                               # ask the user first
```

- A new workflow (create, import or duplicate) starts with one live version, `v1`.
- Commits (the dashboard's history) are per version; reverting one puts the graph back on the version it came from.
- `ck workflows leads <id> --version-id <versionId>` shows only leads on that version; `--json` gives each lead's `workflow_version_id`.

## A/B testing

A/B testing decides which **version** a lead **starts** on when it is enrolled (`ck contacts assign
--workflow`, the dashboard, or the public assign API). The lead keeps that version for its whole run.
For each lead, in order:

1. The enrolment names a version (`--workflow-version <versionId>`): that version, A/B skipped.
2. A lead re-enrolled into the same workflow keeps its last run's version, if A/B can still reach it
   (not in JS mode).
3. **Advanced routing**: rules (first match wins; `else` always matches) or JavaScript `route(context)`.
4. **Traffic Split** by ratio. One bulk enrolment is shared exactly (1000 leads at 70/30 → 700/300).
5. The live version.

Workflow versions have no language: there are no language rules (unlike agent A/B), and the split
is one pool. Rule conditions read the lead's **CRM attributes** as `metadata.<attribute>`, with the
agent A/B grammar: `(metadata.city == 'Pune')`, `((metadata.score >= 80) AND (metadata.plan == 'pro'))`.

```bash
ck workflows ab <id>                                     # what is set, with version names
ck workflows versions <id>                               # SPLIT / IN RULES per version
ck workflows ab-split <id> --versions "Control=70,Short pitch=30"   # names or ids, total 100
ck workflows ab-rules <id> --file rules.json             # whole if/elseif/else chain
ck workflows ab-test-js <id> --file route.js --metadata '{"score":"91"}'   # dry run, saves nothing
ck workflows ab-js <id> --file route.js                  # JavaScript routing
ck workflows ab-split <id> --off                         # switch a half off; it stays stored
ck workflows results <id> --from 2026-11-20 --to 2026-11-27   # per-version runs, calls, connected, converted
```

```json
[
  { "kind": "if",   "condition": "(metadata.tier == 'gold')", "targets": [{ "versionId": "Gold flow" }] },
  { "kind": "else", "targets": [{ "versionId": "Control", "ratio": 50 }, { "versionId": "Short pitch", "ratio": 50 }] }
]
```

- **Every save changes live routing at once** and writes an `ab_testing` commit that cannot be
  reverted. Show the user the split or rules in version names and **ask before saving** (the CLI
  asks; `--yes` only when the user said so). Leads already running are never moved.
- `ab-split` / `ab-rules` **replace** the whole stored list or chain: read `ck workflows ab <id>
  --json` first and send everything that should stay.
- Every routed version needs steps; a version in the stored split or a rule **cannot be deleted**
  (even with A/B off) until it is taken out.
- JS: `route(context)` gets `{ metadata, versions }` and returns a version id or nothing. 5 s per
  lead; an error, timeout or unknown id falls through to the split, then the live version. It runs
  once per lead, so a bulk assign runs it thousands of times: decide from `metadata` where possible.
  Changed code is reviewed by the server on save.
- Scoring: compare `results` over the dates the test ran. `CONV %` is converted / connected calls.
  Give the counts with every rate and don't call a winner on a few dozen connected calls. To keep
  the winner: `ck workflows publish <id> <versionId>` (ask first), then switch the test off.
- MCP: `configure_workflow_ab_testing`, `test_workflow_ab_routing_code`, `get_workflow_version_stats`;
  the config itself is on `get_workflow`.

## Generate a workflow from a request

```bash
ck workflows schema                        # 1. learn the shapes
# 2. gather real ids — never invent them:
ck agents list --json                      # agentId for Send Call (prefer agentStatus "live")
ck whatsapp list --json                    # phoneNumberId + display number for WhatsApp nodes
ck chat-agents templates --json            # template id / name / language / status (use APPROVED)
ck chat-agents template <templateId> --json   # its variables[].id = the exact parameters[].key values
ck contacts attributes list --json         # CRM attribute names for update-lead / contact conditions
ck numbers list --json                     # fromNumber for Send Call (only if the user names a number)
ck secrets list                            # secret names for api-basic headers
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

Prefer the small edits; they touch only what you name and re-validate on save. They change the
live version unless given `--version-id`:

```bash
ck workflows add-node <id> --type wait --after <callNodeId> --set '{"minutes":120}'
ck workflows set-node <id> <nodeId> --set @patch.json
ck workflows connect <id> --from <condId> --handle <exitId> --to <nodeId>
ck workflows remove-node <id> <nodeId> --reconnect --yes
```

- After a `conditions` node, `add-node --after` needs `--handle <exitId>` (the error lists them).
- `add-node` saves immediately, so types with no sensible default need `--set` up front — `send-call` (`agentId`), `wa-template` (`templateId`…), `wa-message` (`message`…), `api-basic` (`url`), `update-lead` (`updates`). The error shows an example. `inbound`, `cancel` and `resume` need nothing set; add `inbound` without `--after` (nothing may lead into it). A new `conditions` node starts as a complete "did the call connect?" rule (`connected_call` = true); change it with `set-node --set @exits.json`.
- Replacing a conditions node's `exits` via `set-node` drops the edges of exits you removed.
- Inline `--set '{…}'` is fragile in shells; for anything non-trivial write a file and use `@file`.
- The server validates on every save; an edit that would leave **no path to End** is rejected with the reason. Read it, fix, retry.
- The last save wins — don't edit a workflow someone else may be editing.
- **Editing a version that has leads running** changes what they do next: each step reads the graph as it stands. Edit a draft and publish it instead (see [Versions](#versions)), or confirm with the user first.

### Inbound calls — the second entry point

An `inbound` node is where a live run jumps when the lead calls in on a number this workflow has called them from. It jumps **from wherever the lead had reached** — mid-Wait, suspended on a call — and carries on down the inbound branch. Conditions placed after it read **that** call: `post_call_variables`, `conversion_status`, `hangup_reason`, `call_duration`.

What the branch leads to decides what happens to the journey they were on:

| The inbound branch… | The run |
|---|---|
| reaches `cancel` | is cancelled, and any call an earlier `send-call` had scheduled is dropped |
| reaches `end` | is completed |
| reaches `resume` | goes back to the step the call interrupted — a `wait` keeps the time it had left, a call it was suspended on still wakes it |
| leads nowhere | the same as `resume` |

An `inbound` node with **no outgoing edge is a valid, useful configuration**: the call is recorded against the run — its post-call variables merge into the run's variables, so later steps can read them — and the lead is left exactly where they were. Use it when you want the call noted but the journey untouched.

Two things worth knowing before branching on an inbound call:

- `post_call` **accumulates** across every call in a run rather than being replaced, so a `post_call_variables` condition can match a value an **earlier** call set. The inbound call is usually answered by a different agent with a different post-call variable set, which makes this easy to hit. Branch on `conversion_status` for strictly-the-latest-call, or give the inbound agent the same post-call variables.
- Only the workflow of the lead's **most recent** call learns about an inbound call. A lead live in two workflows at once will not have both notified.

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
