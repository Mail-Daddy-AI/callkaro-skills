# Reference: Agent Type, Script Fields & How a Call Runs
<!-- graph-summary: Version field reference for the prompt type (systempromptType 0-3) and which script fields are live, the script fields (systemprompt, role, goal, callFlow, snippets, variable namespaces, language and persona rules), and how a call runs. -->

Part of the [version reference](../AGENT-VERSION-REFERENCE.md) (which document a field belongs to, topic map). Field index: [field-index.md](field-index.md).

## 2. Agent type (`systempromptType`) — decides which script fields are live

| Type | Name | Script surface |
| --- | --- | --- |
| 0 | Basic | one `systemprompt`. `role`/`goal`/`callFlow` = `""`, `instructions`/`guardrails`/`rebuttals` = `[]` |
| 1 | Advanced | `role`, `goal`, `callFlow`, `instructions[]`, `guardrails[]`, `rebuttals[]`. `systemprompt` = `""` |
| 2 | Multiprompt | base `systemprompt` + `capabilities[]`, each with its own `system_prompt`. Type-1 fields empty. Switching is **prose** inside the prompts. |
| 3 | Pathway | base `systemprompt` + `capabilities[]` as **graph nodes**. Switching is **data** (`transitions[]`), never prose. Type-1 fields empty. |

Rules:

- Fields belonging to another type must be **emptied, not left stale** — a type-2 version with a
  leftover `role` is inferred as type 1 when `systempromptType` is missing.
- Types 2 and 3 share the same `capabilities[]` array; type 3 is distinguished purely by the
  presence of node fields.
- Type conversion is a structural reshape. 2↔3 is a direct edge; everything else pivots through the
  single-scope shape. Collapsing 2/3 → 0/1 hoists capability `functions`/`postcall` to version level
  (version-level wins on a name/type collision) and promotes the **starting** capability's `llms` to
  version `model`/`secondary_model`/`temperature` (×10 — see [§7](llm-and-postcall.md)). Expanding 0/1 → 2/3 seeds one empty
  starting capability. Prompt prose is never auto-authored: after a conversion the prompts for the
  target shape still have to be written.
- Pathway (3) is the strongest default when the call has real branching, gating, or repeated
  cross-cutting interruptions. Basic (0) fits short single-purpose calls.

---

## 3. Script fields (version level)

| Field | Type / default | What it does at call time |
| --- | --- | --- |
| `systemprompt` | string, `"You are a helpful assistant."` | Type 0: the whole script. Types 2/3: the **shared base** — persona, brand, standing rules, tone, universal rebuttals, language rules, persona gender. Prepended to the active capability/node prompt unless that node sets `overwrite: true`. **Must not contain a call flow** on 2/3. |
| `role` | string, `""` | Type 1. Identity, expertise, persona, tone. |
| `goal` | string, `""` | Type 1. Objectives and desired outcomes. |
| `callFlow` | string, `""` | Type 1. Step-by-step conversation structure. |
| `instructions` | string[], `[]` | Type 1. Standing behavioural rules. |
| `guardrails` | string[], `[]` | Type 1. Hard boundaries. |
| `rebuttals` | string[], `[]` | Type 1. Objection-handling lines. |
| `end_call_msg` | string[], `[]` | **A hang-up trigger, not decoration.** If the agent utters any line in this array the call is cut immediately. Only 2–3 exact final closing lines belong here. |
| `callFlow_json` | object \| null | Visual flow-builder graph. Replaced wholesale on update ([§16](versioning-and-preflight.md)). |
| `useCallFlow_json` | bool, `false` | Use the builder graph instead of the text `callFlow`. |
| `default_language` | enum `en hi kn ta te mr gu bn ml`, `"en"` | The language the agent speaks. **Also the publishing key** — one published version per `default_language`. |
| `silence_language` | same set + `multi`, `"en"` | Language of silence re-prompts. |
| `conversion_reason` | string, `""` | What outcome counts as a successful conversion, for post-call analysis. |

### The five behaviour snippets

Prompt fragments injected alongside the script. Each has a platform default applied at save time
when the value is absent — so **omit** them to get the default; writing `""` suppresses it.

| Field | Controls |
| --- | --- |
| `model_response_snippet` | How spoken output is shaped — no stage directions, how to spell email addresses and numbers aloud. |
| `security_guardrails_snippet` | Refusing internal/technical/operational disclosure; prompt-injection and abuse handling. |
| `function_calling_snippet` | How and when to invoke functions, and how to verbalise results instead of reading JSON aloud. |
| `language_switch_snippet` | Behaviour when the caller switches language (drives the language-switch capability). |
| `hold_call_snippet` | Behaviour when the caller asks to hold (drives `keep_call_on_hold`). |

`gender_prompt_snippet` ([§12](call-settings.md)) is a sixth, gated snippet used only when `detect_gender` is on.

### Variable namespaces — four different things, never mixed

| Namespace | Notation | Filled | Stored as a field? | Used for |
| --- | --- | --- | --- | --- |
| Metadata / pre-call | `{{customer_name}}` | before the call — campaign/batch row, API trigger payload, or a `custom_pre_call` function | no; parsed out of prompt text | personalisation; referenced in pathway expressions as `metadata.customer_name` |
| In-call variable | `{available_slots}` | during the call, by the LLM | no | freeform live values inside prompt text |
| `extract_variables` | plain name | during the call, structured, per node | **yes** — on the node | **routing** — read by `condition_type: 1` |
| Post-call variable | plain name | after the call, from the transcript | **yes** — `postcall[]` | reporting, CRM, disposition |

Hard rules: preserve brace syntax exactly (never convert `{{x}}` ↔ `{x}`); reproduce freeform
placeholders (`<car details here>`, `[vehicle info]`) verbatim — they are filled by a pre-call
function; never duplicate a node's `extract_variable` as a post-call variable on that same node;
every metadata reference needs a fallback (a prompt instruction or a pre-call default) so the agent
never speaks an empty placeholder. `insert_metadata_in_prompt` ([§14](variables-memory-whatsapp.md)) controls whether metadata
reaches the prompt at all.

### Language & persona conventions (apply to every prompt field)

- Spoken lines in the target language; **all operational text — headings, step labels, conditions,
  data-collection directions, tool guidance — always in English.**
- Indian languages in native script, never romanised. Mix in the English words real speakers use
  (`booking`, `slot`, `registration number`, `confirm`, `payment`). Everyday spoken vocabulary, not
  literary or textbook wording.
- Pick **one** persona gender for the whole version and keep every self-reference, verb ending and
  adjective consistent (Hindi: `बोल रही हूँ … कर सकती हूँ` **or** `बोल रहा हूँ … कर सकता हूँ`, never mixed).
  Declare it explicitly as an English line `Persona gender: male|female` in the role-bearing field —
  type 0/2/3 → inside `systemprompt`, type 1 → `role`. Default male when unspecified. The voice
  choice ([§9](voice-and-transcriber-fields.md)) must match it.
- Never translate capability/node names, function names, or `{{placeholder}}` names.

---

## 5. How a call runs (why these fields interact)

```
prompt = systemprompt (skipped if node.overwrite) + node.system_prompt + snippets
         + {{metadata}} substituted (if insert_metadata_in_prompt)
   ↓ start node (is_starting) — opening governed by speakfirst / initial_pause
   • node functions callable · extract_variables captured as the caller talks
   • any global node whose when_to_jump matches interrupts, handles, returns here
   ↓ all is_required variables captured?   no → stay in the node, keep asking
   ↓ evaluate transitions in order (type 1 = expression, type 0 = model judgement)
   ↓ match → speak msg_while_switching unless silent → rebuild prompt for the next node
   ↓ terminal node → agent says an end_call_msg line → call is cut
   ↓ after the call: post-call variables extracted (global + each visited node's),
     conversion_reason / disposition computed, post-call functions and webhook fire
```

Keep straight while authoring: `overwrite` decides what a node's prompt must contain; `is_required`
can block every edge; an expression over an undeclared variable silently never matches; a `silent`
global that interrupts mid-sentence feels abrupt (`dynamic` usually reads best); functions are scoped
to the node that **invokes** them — "transfer between node 3 and node 4" means attach the transfer
function to node 3.
