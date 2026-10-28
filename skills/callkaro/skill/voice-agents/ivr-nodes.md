# IVR Nodes — deterministic TTS + DTMF before the LLM starts
<!-- graph-summary: IVR nodes run pure text-to-speech and DTMF digit collection before any LLM capability activates. Pathway agents (systempromptType 3) only. Use for automated menus, language selection, consent gates, and any fixed-script sequence at the start of a call. Covers node_type "ivr", ivr_config fields, routing, post-call static values, and authoring rules. -->

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
3. On reaching the first **non-IVR** node (an LLM capability), the runner hands off and the normal voice-agent pipeline begins.
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
    "no_input_next": "language_select",
    "invalid_key_next": "language_select",
    "options": [
      { "key": "1", "next_capability": "english_agent" },
      { "key": "2", "next_capability": "hindi_agent" }
    ]
  }
}
```

---

## `ivr_config` field reference

| Field | Type | Default | Meaning |
|---|---|---|---|
| `message` | string | `""` | TTS text spoken when this node is entered. Supports `{{variable_name}}` placeholders from call metadata. |
| `timeout_secs` | number | `8` | Seconds to wait for a key press after speaking. |
| `max_retries` | number | `2` | Total number of times the message plays before routing to `no_input_next`. E.g. `2` means: play once, if no key → play again, if still no key → route. |
| `skip_input` | bool | `false` | Speak the message and immediately route to `no_input_next` without waiting for a key. Use for announcements or pass-through nodes. |
| `hangup_after_message` | bool | `false` | Speak the message and end the call. Use for rejection/termination nodes. |
| `no_input_next` | string | same node | Capability name to route to when `max_retries` exhausts with no input. |
| `invalid_key_next` | string | same node | Capability name to route to when the caller presses a key not in `options`. |
| `options` | array | `[]` | DTMF routing table. Each entry: `{ "key": "1", "next_capability": "cap_name" }`. `key` is a single digit 0–9 or `*`/`#`. |

### Routing rules

- `no_input_next` and `invalid_key_next` **can point to another IVR node** (re-prompt) or to an LLM capability node.
- If `no_input_next` is absent and `max_retries` exhausts, the call is hung up.
- `options` targets can be IVR nodes (chain menus) or LLM capability nodes (hand off).
- Only one node in a pathway can have `is_starting: true` — make it the first IVR node.

### `skip_input` vs `hangup_after_message`

| | `skip_input: true` | `hangup_after_message: true` |
|---|---|---|
| Speaks message | ✅ | ✅ |
| Waits for key | ❌ | ❌ |
| After message | Routes to `no_input_next` | **Ends the call** |

Use `skip_input` for pass-through announcements mid-flow. Use `hangup_after_message` as a terminal rejection/end node.

---

## `msg_while_switching` on IVR nodes

IVR nodes support `msg_while_switching_type` / `msg_while_switching`, just like LLM nodes. When the runner transitions **into** a node for the first time (not on a retry), it plays the switch message first — useful for "please wait" filler between menus.

- Only `msg_while_switching_type: "static"` is meaningful for IVR (no LLM).
- The switch message is skipped on the very first node of the call and on retries of the same node.

---

## Metadata conditions

After the message is spoken, the IVR runner evaluates a list of **conditions** before waiting for a key press. The first condition that matches immediately routes the call to its target node — no DTMF needed.

```json
"conditions": [
  { "condition": "(metadata.language == 'english')", "next_capability": "english_agent" },
  { "condition": "(metadata.opted_out == True)",      "next_capability": "opt_out_node"   }
]
```

### Rules

- Conditions are evaluated **in order** — first match wins.
- If no condition matches, the runner falls through to normal DTMF routing.
- Only **`metadata.*`** operands are allowed. `extract_variables` are not available during the IVR phase (no STT/LLM runs).
- Only **expression-type** (`condition_type: 1`) logic is supported — no natural-language / prompt conditions.
- The grammar is identical to pathway expression conditions (see `AGENT-VERSION-REFERENCE.md`):

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
- [ ] Every `next_capability` in `options`, `no_input_next`, and `invalid_key_next` matches an existing `capability` name in the version.
- [ ] Terminal IVR nodes use `hangup_after_message: true` (not an empty `options` list).
- [ ] `max_retries ≥ 1`. Setting `0` causes an immediate route on the first attempt.
- [ ] `skip_input: true` nodes do not need `options` (they always route to `no_input_next`).
- [ ] IVR nodes have no `system_prompt`, no `functions`, no `extract_variables`, no `transitions` — those fields are for LLM nodes.
- [ ] `use_ivr_postcall: true` nodes have `ivr_postcall` populated with at least `conversation_status` and `disposition_reason`.

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
        "no_input_next": "lang_menu",
        "invalid_key_next": "lang_menu",
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
| Setting `max_retries: 0` | Node routes immediately without waiting | Set `max_retries ≥ 1` |
| `no_input_next` points to a non-existent capability | Runtime hangs up the call | Check that every target name exists |
| Putting `system_prompt` on an IVR node | Field is ignored; may confuse future editors | Leave it empty or omit it |
| Trying to `switch_capability` to an IVR node from an LLM node | Blocked by the runtime guard | IVR nodes are only enterable at call start |
| `hangup_after_message` + non-empty `options` | `options` is ignored when `hangup_after_message: true` | Remove `options` from hangup nodes |
| `use_ivr_postcall: true` with empty `ivr_postcall` | No static values saved; post-call runs with no data | Populate at least `conversation_status` and `disposition_reason` |
