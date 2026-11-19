# IVR Nodes — deterministic TTS + DTMF before the LLM starts
<!-- graph-summary: IVR nodes run pure text-to-speech and DTMF digit collection before any LLM capability activates. Pathway agents (systempromptType 3) only. Use for automated menus, language selection, consent gates, and any fixed-script sequence at the start of a call. Covers node_type "ivr", ivr_config fields, routing, post-call static values, wait nodes (node_type "wait", a timed silence between an IVR node and an LLM or IVR node), end_call nodes, and authoring rules. -->

> **Pathway agents only.** IVR nodes are a feature of `systempromptType: 3` (Pathway). They cannot be used in Basic (0), Advanced (1), or Multi-Prompt (2) agents.

An **IVR node** (`node_type: "ivr"`) runs at the very beginning of a call — before the LLM or STT pipeline starts. The agent speaks a fixed message via TTS and waits for the caller to press a DTMF key. Based on the key pressed (or lack of one), the call routes to the next IVR node or to an LLM capability node.

IVR nodes are **deterministic**: no transcript, no LLM inference, no STT during this phase. Everything is configured up front.

---

## When to use IVR nodes

- Language selection menus ("Press 1 for English, 2 for Hindi")
- Consent gates ("Press 1 to continue")
- Simple routing before the LLM ("Press 1 for Sales, 2 for Support")
- Playing a fixed announcement and hanging up
- Playing a message and immediately proceeding (no key required)

Do **not** use IVR nodes for conversations that require understanding free-form speech — use LLM capability nodes for those.

---

## How the IVR phase works

1. The call connects. The IVR runner starts on the **`is_starting`** node that has `node_type: "ivr"`.
2. The runner walks IVR nodes — speaking messages, collecting keys — without starting the LLM or STT.
3. On reaching the first **non-IVR** node (an LLM capability), the runner hands off and the normal voice-agent pipeline begins. [Wait nodes](#wait-nodes) are part of the IVR phase too: the runner passes through them on its way. Reaching an `end_call` node hangs up.
4. IVR nodes are **not reachable** via `switch_capability` once the LLM phase has started — the guard is enforced in the runtime.

---

## Capability schema for an IVR node

```json
{
  "capability": "language_select",
  "node_type": "ivr",
  "is_starting": true,
  "msg_while_switching_type": "static",
  "msg_while_switching": "Please wait while we connect you.",
  "use_ivr_postcall": false,
  "ivr_postcall": [],
  "ivr_config": {
    "message": "Welcome. Press 1 for English, press 2 for Hindi.",
    "timeout_secs": 8,
    "max_retries": 2,
    "skip_input": false,
    "hangup_after_message": false,
    "no_input_next": "no_response_end",
    "invalid_key_retries": 2,
    "invalid_key_message": "Sorry, that is not a valid option. Please press 1 or 2.",
    "invalid_key_next": "no_response_end",
    "conditions": [
      { "condition": "(metadata.language == 'english')", "next_capability": "english_agent" }
    ],
    "options": [
      { "key": "1", "next_capability": "english_agent" },
      { "key": "2", "next_capability": "hindi_agent" }
    ]
  }
}
```

`conditions` lives **inside `ivr_config`**, next to `options`. A `conditions` array placed directly on the capability is ignored by the IVR runner (capability-level `transitions` are only for LLM nodes).

---

## `ivr_config` field reference

| Field | Type | Default | Meaning |
|---|---|---|---|
| `message` | string | `""` | TTS text spoken when this node is entered. Supports `{{variable_name}}` placeholders from call metadata. |
| `timeout_secs` | number | `8` | Seconds to wait for a key press after speaking. |
| `max_retries` | number | `2` | Total number of times the message plays before routing to `no_input_next`. E.g. `2` means: play once, if no key → play again, if still no key → route. `0` or empty is treated as `2`. |
| `skip_input` | bool | `false` | Speak the message and immediately route to `no_input_next` without waiting for a key. Use for announcements or pass-through nodes. **Set `no_input_next`** — if it is empty the node routes to itself and the message replays forever. |
| `hangup_after_message` | bool | `false` | Speak the message and end the call. Use for rejection/termination nodes. |
| `no_input_next` | string | same node | Capability name to route to when `max_retries` exhausts with no input. **Empty = this same node**, so the message replays indefinitely — it does **not** end the call. |
| `invalid_key_retries` | number | `1` | Total invalid key presses allowed on this node before routing to `invalid_key_next`. `1` routes on the first invalid key. Only takes effect when `invalid_key_message` is set. |
| `invalid_key_message` | string | `""` | Spoken after an invalid key while retries remain. The runner says **only** this message (the main `message` is not replayed) and waits for a key again. Supports `{{variable_name}}`. |
| `invalid_key_next` | string | same node | Capability name to route to once `invalid_key_retries` is used up. **Empty = this same node**: the full message replays and the invalid-key count starts over, so the caller can loop forever. |
| `conditions` | array | `[]` | Metadata conditions checked after the message, before DTMF. See [Metadata conditions](#metadata-conditions). |
| `options` | array | `[]` | DTMF routing table. Each entry: `{ "key": "1", "next_capability": "cap_name" }`. `key` is a single digit 0–9 or `*`/`#`. |

### Routing rules

- `no_input_next` and `invalid_key_next` **can point to another IVR node** (re-prompt) or to an LLM capability node.
- **An IVR node never hangs up on its own when input is missing or wrong.** If `no_input_next` / `invalid_key_next` is empty, the runner routes back to the same node and replays it until the caller hangs up. To end the call, point them at a terminal IVR node with `hangup_after_message: true` (e.g. "We did not receive a valid input. Goodbye.").
- If a target capability name does not exist, the IVR phase ends and the call is hung up.
- `options` targets can be IVR nodes (chain menus) or LLM capability nodes (hand off).
- Only one node in a pathway can have `is_starting: true` — make it the first IVR node.
- Any IVR route can also point at a [wait node](#wait-nodes) (pause, then continue) or an `end_call` node (`node_type: "end_call"`, hangs up straight away with nothing spoken).

### `skip_input` vs `hangup_after_message`

| | `skip_input: true` | `hangup_after_message: true` |
|---|---|---|
| Speaks message | ✅ | ✅ |
| Waits for key | ❌ | ❌ |
| After message | Routes to `no_input_next` | **Ends the call** |

Use `skip_input` for pass-through announcements mid-flow. Use `hangup_after_message` as a terminal rejection/end node.

---

## Wait nodes

A **wait node** (`node_type: "wait"`) keeps the line silent for a set number of seconds, then moves on. Use it between an IVR node and the next LLM or IVR node — for example to give a system time to look something up, or to space out two announcements.

```json
{
  "capability": "hold",
  "node_type": "wait",
  "is_starting": false,
  "system_prompt": "",
  "wait_config": { "seconds": 5, "next_capability": "sales" }
}
```

| Field | Type | Meaning |
|---|---|---|
| `wait_config.seconds` | number, required | Silence before moving on. Any value above `0`; there is no upper limit. |
| `wait_config.next_capability` | string, required | Node to go to afterwards: an LLM node (`normal` / `global`) or an `ivr` node. |

Rules (the backend rejects anything else):

- Only **IVR routes** (`options`, `conditions`, `no_input_next`, `invalid_key_next`) can lead to a wait node. LLM `transitions` cannot.
- A wait node **cannot be the start node**.
- `next_capability` must be an LLM or IVR node — not `end_call` and not another wait node.
- The caller hears silence. Keys pressed during the wait are dropped when the next IVR node starts speaking.
- Wait nodes have no `system_prompt`, `functions`, `transitions` or `ivr_config`.

---

## `msg_while_switching` on IVR nodes

IVR nodes support `msg_while_switching_type` / `msg_while_switching`, just like LLM nodes. When the runner transitions **into** a node for the first time (not on a retry), it plays the switch message first — useful for "please wait" filler between menus.

- Only `msg_while_switching_type: "static"` is meaningful for IVR (no LLM).
- The switch message is skipped on the very first node of the call and on retries of the same node.

---

## Metadata conditions

After the message is spoken, the IVR runner evaluates a list of **conditions** before waiting for a key press. The first condition that matches immediately routes the call to its target node — no DTMF needed.

`conditions` is a field of **`ivr_config`** (not of the capability itself):

```json
"ivr_config": {
  "message": "...",
  "conditions": [
    { "condition": "(metadata.language == 'english')", "next_capability": "english_agent" },
    { "condition": "(metadata.opted_out == True)",      "next_capability": "opt_out_node"   }
  ],
  "options": [ ... ]
}
```

### Rules

- Conditions are evaluated **in order** — first match wins.
- If no condition matches, the runner falls through to normal DTMF routing.
- Conditions are not re-checked on an invalid-key retry (only the first pass of the node).
- Only **`metadata.*`** operands are allowed. `extract_variables` are not available during the IVR phase (no STT/LLM runs).
- Only **expression-type** (`condition_type: 1`) logic is supported — no natural-language / prompt conditions.
- The grammar is identical to pathway expression conditions (see [capabilities-and-pathways.md](reference/capabilities-and-pathways.md)):

```
Comparison   := '(' operand op operand ')'
LogicalExpr  := '(' Expression ('AND'|'OR') Expression+ ')'
operand      := metadata.<key> | 'string' | True | False | number
op           := == | != | > | < | >= | <=
```

Examples:
```
(metadata.language == 'english')
(metadata.opted_out == True)
((metadata.score > 5) AND (metadata.tier == 'gold'))
```

### When to use conditions vs key options

| Use case | Approach |
|---|---|
| Route based on pre-call data (campaign field, CRM attribute) | **Condition** — no user input required |
| Route based on what the caller presses | **Key option** |
| Both | Conditions are checked first; if none match, DTMF runs |

---

## Static post-call variables (`use_ivr_postcall`)

Pure IVR calls (calls that never reach an LLM node) have no transcript for the LLM to analyse. You can configure each IVR node to save **static post-call variable values** instead of running LLM inference.

| Toggle | Effect |
|---|---|
| `use_ivr_postcall: false` (default) | LLM runs post-call analysis on whatever transcript exists (may be very short). |
| `use_ivr_postcall: true` | Static values from `ivr_postcall` are used. LLM post-call is skipped entirely. |

The values from the **last IVR node the call was on when it ended** are the ones applied. This lets each routing branch carry its own outcome:

```json
{
  "use_ivr_postcall": true,
  "ivr_postcall": [
    { "name": "conversation_status", "value": "false", "type": "boolean" },
    { "name": "disposition_reason",  "value": "Hung up during IVR menu", "type": "string" }
  ]
}
```

### `ivr_postcall[]` entry fields

| Field | Values | Notes |
|---|---|---|
| `name` | string | Must match a post-call variable name defined on the agent. |
| `value` | string | The value to assign. Cast by `type` when saved. |
| `type` | `string` \| `boolean` \| `number` \| `selector` \| `object` | `boolean`: `"true"`/`"false"` → JS boolean. `number`: cast with `Number()`. `object`: JSON-parsed. |

**Always configure `conversation_status` and `disposition_reason`** at minimum — these are the two post-call variables that drive analytics, workflow triggers, and CRM updates.

---

## Authoring checklist

- [ ] Exactly one node has `is_starting: true` and it is an IVR node (or the first LLM node if no IVR phase).
- [ ] Every `next_capability` in `options`, `conditions`, `no_input_next`, and `invalid_key_next` matches an existing `capability` name in the version.
- [ ] Every menu node sets `no_input_next` and `invalid_key_next` to a **different** node (usually a terminal `hangup_after_message` node). Leaving them empty loops the menu forever.
- [ ] `invalid_key_retries ≥ 2` is paired with an `invalid_key_message`; without the message, the first invalid key routes straight away.
- [ ] Terminal IVR nodes use `hangup_after_message: true` (not an empty `options` list).
- [ ] `conditions` is inside `ivr_config`, not on the capability.
- [ ] `skip_input: true` nodes do not need `options`, but must set `no_input_next`.
- [ ] IVR nodes have no `system_prompt`, no `functions`, no `extract_variables`, no `transitions` — those fields are for LLM nodes.
- [ ] `use_ivr_postcall: true` nodes have `ivr_postcall` populated with at least `conversation_status` and `disposition_reason`.
- [ ] Every wait node has `wait_config.seconds` above 0 and a `wait_config.next_capability` that is an LLM or IVR node, and is reached only from an IVR route.

---

## Full example — language-select IVR before LLM hand-off

```json
{
  "systempromptType": 3,
  "capabilities": [
    {
      "capability": "lang_menu",
      "node_type": "ivr",
      "is_starting": true,
      "ivr_config": {
        "message": "Hello {{customer_name}}. Press 1 for English, press 2 for Hindi.",
        "timeout_secs": 8,
        "max_retries": 2,
        "no_input_next": "no_response_end",
        "invalid_key_retries": 2,
        "invalid_key_message": "Sorry, that is not a valid option. Press 1 for English, press 2 for Hindi.",
        "invalid_key_next": "no_response_end",
        "options": [
          { "key": "1", "next_capability": "english_main" },
          { "key": "2", "next_capability": "hindi_main" }
        ]
      },
      "use_ivr_postcall": true,
      "ivr_postcall": [
        { "name": "conversation_status", "value": "false",            "type": "boolean" },
        { "name": "disposition_reason",  "value": "No IVR response", "type": "string"  }
      ]
    },
    {
      "capability": "no_response_end",
      "node_type": "ivr",
      "is_starting": false,
      "ivr_config": {
        "message": "We did not receive a valid input. Thank you for your time. Goodbye.",
        "hangup_after_message": true
      },
      "use_ivr_postcall": true,
      "ivr_postcall": [
        { "name": "conversation_status", "value": "false",                         "type": "boolean" },
        { "name": "disposition_reason",  "value": "No valid IVR input, call ended", "type": "string"  }
      ]
    },
    {
      "capability": "english_main",
      "node_type": "normal",
      "is_starting": false,
      "system_prompt": "You are an English-speaking sales agent...",
      "msg_while_switching_type": "static",
      "msg_while_switching": "Connecting you now, please hold.",
      "use_ivr_postcall": false
    },
    {
      "capability": "hindi_main",
      "node_type": "normal",
      "is_starting": false,
      "system_prompt": "आप एक हिन्दी बोलने वाले सेल्स एजेंट हैं...",
      "msg_while_switching_type": "static",
      "msg_while_switching": "अभी कनेक्ट कर रहे हैं, कृपया प्रतीक्षा करें।",
      "use_ivr_postcall": false
    }
  ]
}
```

---

## Common mistakes

| Mistake | Result | Fix |
|---|---|---|
| Leaving `no_input_next` / `invalid_key_next` empty | Node routes to itself; the menu replays until the caller hangs up | Point both at a terminal `hangup_after_message` node (or another real node) |
| `invalid_key_retries: 2` with no `invalid_key_message` | Retries are ignored; first invalid key routes to `invalid_key_next` | Set an `invalid_key_message` |
| `conditions` placed on the capability instead of `ivr_config` | Conditions are ignored | Move `conditions` inside `ivr_config` |
| Setting `max_retries: 0` expecting no retries | `0` is treated as the default `2` | Use `1` for a single play |
| `no_input_next` points to a non-existent capability | Runtime hangs up the call | Check that every target name exists |
| Putting `system_prompt` on an IVR node | Field is ignored; may confuse future editors | Leave it empty or omit it |
| Trying to `switch_capability` to an IVR node from an LLM node | Blocked by the runtime guard | IVR nodes are only enterable at call start |
| `hangup_after_message` + non-empty `options` | `options` is ignored when `hangup_after_message: true` | Remove `options` from hangup nodes |
| `use_ivr_postcall: true` with empty `ivr_postcall` | No static values saved; post-call runs with no data | Populate at least `conversation_status` and `disposition_reason` |
| An LLM `transition` pointing at a wait node | Rejected on save | Wait nodes follow IVR routes only |
| Wait node pointing at `end_call` or another wait node | Rejected on save | Point it at an LLM or IVR node; to hang up after a pause, wait → IVR node with `hangup_after_message: true` |
