# CallKaro Agents & Versions — Complete Reference

**Read this before doing ANYTHING with agents or versions** — creating, editing,
scripts, prompts, capabilities/pathways, functions, voice, transcriber, LLM,
post-call variables, publishing. It defines every field on both documents, its
allowed values, and the traps that silently drop data.

---
## 1. Field routing — agent doc vs version doc

The API splits one flat request body by an allow-list. Exactly these keys go to the **agent**
document; **every other key** goes to the version document:

```
folderId · name · systempromptType · phoneNumber · inboundPhoneNumbers ·
outboundPhoneNumber · secondaryOutboundPhoneNumber · whatsappPhoneNumber ·
whatsappInboundPhoneNumber · publishedVersionId · lastpublisedDate ·
abTestVersions · abTestEnabled · advancedAbTestEnabled · advancedAbTestRules ·
_id · default_agent_language ·
useMultiTranscribers · publishedVersionsByLanguage · agentStatus
```

(`lastpublisedDate` is spelled exactly like that in the allow-list; the stored field is
`lastPublishedDate`.)

### Agent-document fields

| Field | Type | Meaning |
| --- | --- | --- |
| `name` | string, **required** | Display name, e.g. `"Riya – Sales Outreach"`. |
| `folderId` | ObjectId \| null | Folder, for organisation only. |
| `default_agent_language` | `en hi kn ta te mr gu bn ml` | The agent's primary language. The per-version `default_language` is what actually drives a call. |
| `outboundPhoneNumber` | ObjectId | Number used to place outbound calls. |
| `secondaryOutboundPhoneNumber` | ObjectId | Fallback outbound number. |
| `inboundPhoneNumbers` | ObjectId[] | Numbers whose inbound calls route to this agent. |
| `phoneNumber` | string[] | Legacy plain-string numbers. |
| `whatsappPhoneNumber` / `whatsappInboundPhoneNumber` | string | WhatsApp routing. Assigning an inbound WhatsApp number detaches it from any other agent holding it. |
| `publishedVersionsByLanguage` | `[{versionId, lastPublishedDate}]` | **The live version per language.** At most one entry per version `default_language`. |
| `publishedVersionId` | ObjectId | The version the app UI opens by default. |
| `lastPublishedDate` | Date | Set alongside `publishedVersionId`. |
| `agentStatus` | `live` \| `in-progress` | `in-progress` = still being built. |
| `abTestEnabled` / `abTestVersions` | bool / `[{versionId, ratio 0–100}]` | Traffic split across versions. **Never modify as a side effect** of another change. |
| `advancedAbTestEnabled` / `advancedAbTestRules` | bool / rule array | **Rule-based A/B**: ordered if/elseif/else chain over call `metadata.*`, evaluated BEFORE the ratio A/B (only when no version is pinned). Each rule: `{kind: if\|elseif\|else, condition, returnType: version\|language, targets:[{versionId\|language, ratio}]}`. `version` short-circuits (that version runs); `language` only overrides language and resolution continues. Conditions use the §4 expression grammar with `metadata.*` operands; ratios are integers summing to 100 per rule. Manage via `ck agents ab-advanced`. |
| `useMultiTranscribers` | bool | Run the primary and secondary transcriber simultaneously instead of primary-with-fallback. |
| `systempromptType` | int 0–3 | Routed here, but **not stored** — see the trap below. |

### ⚠️ The `systempromptType` trap

`systempromptType` sits in the agent allow-list, but the agent document does not declare it — so a
value sent through `POST /v2agent`, `PUT /v2agent/:id`, `createNewVersion` or `importVersions` is
routed to the agent doc and then dropped, leaving the **version** at its default `0`.

Consequences:

1. Through those endpoints, express the type **structurally** (§2) rather than relying on the field.
2. When the stored value is absent the type is *inferred*: non-empty `capabilities[]` → **2**, or
   **3** if any capability carries `node_type` / `transitions` / `extract_variables` /
   `when_to_jump`; else non-empty `role` / `goal` / `callFlow` → **1**; else **0**.
3. Writers that create versions through the internal service layer *do* set it explicitly, and it is
   authoritative when present. If your path can set it, set it — and keep it consistent with the
   structure, because a mismatch (`systempromptType: 2` with no capabilities) yields an agent that
   behaves like neither type.

---

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
  version `model`/`secondary_model`/`temperature` (×10 — see §7). Expanding 0/1 → 2/3 seeds one empty
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
| `callFlow_json` | object \| null | Visual flow-builder graph. Replaced wholesale on update (§16). |
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

`gender_prompt_snippet` (§12) is a sixth, gated snippet used only when `detect_gender` is on.

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
never speaks an empty placeholder. `insert_metadata_in_prompt` (§14) controls whether metadata
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
  choice (§9) must match it.
- Never translate capability/node names, function names, or `{{placeholder}}` names.

---

## 4. `capabilities[]` — type-2 capabilities and type-3 nodes

Shared fields (both types):

| Field | Type | Meaning |
| --- | --- | --- |
| `capability` | string, `snake_case`, unique | The identity key. Transitions target it by this exact string; renaming it is a graph-wide operation. Never translate it. |
| `is_starting` | bool | Entry point. **Exactly one** in the final set — save-time normalisation keeps the first `true` (or index 0) and clears the rest. |
| `system_prompt` | string | What the agent does and says **while this capability is active**. |
| `overwrite` | bool, `false` | `false` → the version `systemprompt` is **merged** with this prompt, so write only the phase-specific part. `true` → the base is **excluded** and this prompt must be fully self-contained (persona, tone, rules), or the agent changes character mid-call. |
| `msg_while_switching_type` | `silent` \| `static` \| `dynamic` | What the caller hears while switching **into** this capability. `silent` (default) = nothing; `static` = speak `msg_while_switching` verbatim; `dynamic` = `msg_while_switching` is a *prompt* for generating a bridging line. |
| `msg_while_switching` | string | The literal line, or the generation prompt. `""` for `silent`. |
| `llms` | `{primary_model, secondary_model, temperature}` | Per-capability model choice — how you control cost/quality per phase (cheap model for the greeting, stronger for negotiation). Defaults `gpt-4.1-mini` / `gpt-4.1-nano` / `0.2`. **`temperature` here is 0–1** (§7). |
| `functions` | object[] | Functions callable while inside this capability (§6). |
| `postcall` | object[] | Post-call variables scoped to this capability (§8). |
| `use_filler` | bool | Use filler sounds during this capability. Only meaningful when version `filler_config.filler_type` ≠ `none`. |

Type-2 only:

| Field | Type | Meaning |
| --- | --- | --- |
| `stick_capability` | bool, `false` | `true` → once entered, this prompt stays appended for the rest of the call instead of being swapped out. Ignored on type 3 (persisted as `false`). |

Type-3 node-only fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `node_type` | `normal` \| `global` | `normal` = reachable only via an inbound transition. `global` = reachable from **anywhere**; the runtime tests `when_to_jump` every turn, jumps in, then **returns to the node it came from with context intact**. |
| `when_to_jump` | string | **Global nodes only** — natural-language trigger. Must be non-empty for `global` and empty for `normal`; both directions are validated. |
| `transitions` | object[] | Outgoing edges. Terminal nodes have `[]`; globals normally have `[]` because they return rather than route. |
| `extract_variables` | object[] | Values captured live inside this node. |
| `position` | `{x, y}` | Visual layout only, never semantic. |

Use `global` nodes for cross-cutting concerns: objection handling, "talk to a human", FAQ/knowledge
answers, opt-out/DND, abusive-caller handling. A global node is never "unreachable" for lacking an
inbound edge.

`transitions[]` entry:

| Field | Type | Meaning |
| --- | --- | --- |
| `condition_type` | `0` \| `1` | `0` = **prompt**: `condition` is natural-language intent judged by the model. `1` = **expression**: a deterministic boolean over variables. |
| `condition` | string | The intent text, or the expression. |
| `next_capability` | string | Exact name of an **existing** node. A dangling target fails validation. |

Prefer `condition_type: 1` whenever the branch depends on a value you already capture — it is
deterministic and debuggable. Use `0` only for genuinely intent-shaped branches no variable encodes.
Write the highest-priority edge first.

`extract_variables[]` entry:

| Field | Type | Meaning |
| --- | --- | --- |
| `type` | `string` \| `number` \| `boolean` | Only these three. |
| `name` | `snake_case` | What `condition_type: 1` expressions reference. |
| `description` | string | The complete spec for the extractor — be concrete. |
| `is_required` | bool | **A GATE.** `true` → the node takes **no** outgoing transition until this value is captured; the agent stays and keeps asking. `false` → optional, never blocks. |

`is_required: true` couples the prompt and the graph: write the gathering behaviour (re-ask,
rephrase, handle refusal) into `system_prompt`, and **never** mark a variable required if the caller
might legitimately refuse it — the gate blocks *every* outgoing edge including the "not interested"
escape, trapping the call. Prefer `true` for any variable an expression routes on, otherwise the
expression evaluates against a missing value. A variable is declared on the node that captures it
and stays readable by downstream nodes' expressions.

### Expression grammar (`condition_type: 1`) — strictly parsed

```
Comparison        := '(' operand comp_op operand ')'
LogicalExpression := '(' Expression (AND|OR) Expression [...] ')'
Expression        := Comparison | LogicalExpression
```

Every comparison gets its own parentheses; a joined expression gets **one more outer pair**, so a
logical operator never appears outside the outermost parens. Operators `== != >= <= > <`; logical
`AND` / `OR` **uppercase only**; booleans `True` / `False`; operands are an `extract_variables` name,
`metadata.some_var`, a number, or a `'quoted string'`.

| | |
| --- | --- |
| ✅ | `(escalation_needed==False)` |
| ✅ | `((escalation_needed==False) AND (complaint_resolved==True))` |
| ✅ | `((a==True) AND (b==False) AND (c==True))` |
| ✅ | `(((a==True) AND (b==False)) OR (c==True))` |
| ✅ | `((metadata.age > 18) AND (plan == 'pro'))` |
| ❌ | `(a==False) AND (b==True)` — no outer parens |
| ❌ | `age > 18` — no parens |
| ❌ | `((a==True) and (b==False))` — lowercase logic |

### Save-time normalisation of `capabilities[]`

Every capability is rewritten to exactly: `capability` (defaulting to `capability_<n>`),
`is_starting` (exactly one), `system_prompt` (`""`), `overwrite` (`false`), `stick_capability`
(`false`), `msg_while_switching_type` (`silent`), `msg_while_switching` (`""`), `llms` (defaults
filled), `functions` (`[]`), `postcall` (`[]`) — plus the four node fields when the capability looks
like a node (`node_type` `normal`, `transitions` `[]`, `extract_variables` `[]`, `when_to_jump` `""`).
Any per-capability `metadata` key is stripped. Don't rely on other ad-hoc keys surviving a save
through that path.

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

---

## 6. `functions[]` — what the agent can *do*

Functions live either at version level (`functions[]`, callable everywhere) or on a capability
(`capabilities[i].functions[]`, callable only inside it). Names must be unique **within a scope**;
the name is the update/delete key. Use `snake_case`, e.g. `check_availability`.

### Timings and authoring styles

| `type` | When it runs | Basic | Advanced |
| --- | --- | --- | --- |
| `custom_pre_call` | before the call connects | fixed API call | **Python** async `source_code` |
| `custom_in_call` | mid-call, model-triggered | fixed API call | **Python** async `source_code` |
| `custom_post_call` | after the call ends | fixed API call | **JavaScript** async `source_code` |

Choose **advanced** when the URL contains `{{variables}}`, there is branching or retry logic, or the
payload is built from post-call variables. Advanced is always safe; basic is only for a fixed URL
with no logic.

### Constraints that apply to every custom function

- Parameter rows support **only** `{key_name, type: "string"|"number", description}`. No boolean /
  object / enum / required / default — express boolean intent as the string `"true"`/`"false"` and
  normalise inside `source_code`.
- HTTP methods: **`GET`, `POST`, `PUT`, `DELETE`** only. No `PATCH`.
- `api_mapping` and `parameters_mapping` persist as **objects/records** (`{key: value}`), not entry
  arrays.
- Absent optional fields are normal — never treat a missing optional as an error.
- Placeholder URLs and non-secret values are expected while integrations are pending
  (`https://api.example.com/endpoint`, `+910000000000`, `event_id_placeholder`). Credentials must
  use a descriptive `x_secrets.NAME` reference. Never block on missing integration details: write
  the function with placeholders and say so.
- The basic-function UI edits `headers` as `{key_name, value}` rows, then saves them as a
  `{headerName: value}` object. `Content-Type: application/json` is the usual default.
- For a basic function header, use the exact reference as the stored value, for example
  `"Authorization": "x_secrets.CRM_AUTH_HEADER"`; store the complete `Bearer <token>` value under
  that name. Advanced `source_code` reads the runtime object/dict with
  `x_secrets["CRM_API_TOKEN"]` and constructs `Bearer <token>` in code, where the registered secret
  is only the token. Never duplicate the `Bearer ` prefix.
- Run `ck secrets list --json` before authoring. After saving, report every missing secret name and
  tell the user to run `ck secrets set <name>`, add it at
  https://callkaro.ai/dashboard/settings/secrets, or ask their admin to update the registry.

### Field sets per custom variant

**`custom_pre_call`** — runs before the call; enriches metadata or rewrites the prompt.
Basic: `type`, `name`, `description?`, `api`, `method`, `headers?`, `parameters[]`, `api_mapping{}`,
`update_call_data?`, `execute_while_switching?`.
Advanced: `type`, `name`, Python `source_code`, `update_call_data` (**boolean, never null**), API
fields optional.

**`custom_in_call`** — triggered mid-call by the model.
Basic: `type`, `name`, `description` (**the trigger condition** — this text is what the model reads
to decide when to call it, so write it as a condition, not a summary), `msg_while_executing_type`
(`dynamic` \| `static`), `msg_while_executing[]` (`[]` when dynamic), `api`, `method`, `headers?`,
`parameters[]`, `api_mapping{}`, `update_call_data?`, `execute_while_switching?`.
Advanced: same, minus API fields, plus Python `source_code`.

**`custom_post_call`** — side effects after the call: CRM push, logging, notifications.
Basic: `type`, `name`, `api`, `method`, `parameters` (**a JSON payload string**, not typed rows),
`parameters_mapping{}`, `api_mapping{}`, `conditions[]`.
Advanced: `type`, `name`, JavaScript `source_code`; retry/error handling lives **inside the code** —
there is no retry field.

Two flags worth knowing:

- `update_call_data` — on advanced pre-call it selects the protocol (below). Elsewhere it marks a
  function that mutates call data rather than just returning a value.
- `execute_while_switching` — allow the function to run during a capability/node switch instead of
  being deferred until the new node is active.

### Advanced pre-call: two protocols, chosen by `update_call_data`

```python
# update_call_data: false — modify the system prompt
async def personalize_system_prompt(metadata: dict, system_prompt: str) -> str:
    """Replaces customer placeholders in the system prompt."""
    final_prompt = system_prompt
    final_prompt = final_prompt.replace("{customer_name}", str(metadata.get("customer_name") or ""))
    return final_prompt            # MUST return the prompt string on every path

# update_call_data: true — prepare / enrich call data
async def update_call_metadata(call_data: dict):
    """Adds call type to metadata for later use."""
    metadata = call_data.setdefault("metadata", {})
    metadata["call_type"] = call_data.get("name", "")
    call_data["metadata"] = metadata   # mutate in place; return nothing
```

- The signature is exact: `(metadata, system_prompt)` for `false`, `(call_data)` for `true`. Never
  mix them.
- **Brace convention:** the *script* uses `{{name}}`, the replacement *code* targets the
  single-brace `{name}` — read with `metadata.get("name")`, write `.replace("{name}", …)`. Never
  `.replace("{{name}}", …)`.
- Only the dynamic protocol (`true`) may **add** metadata keys; the normal protocol may only
  overwrite existing ones and/or change the prompt.
- HTTP: pre-imported `httpx.AsyncClient` with an explicit timeout, wrapped in
  `try/except httpx.RequestError`; `logger` is pre-injected. Handle non-2xx safely.
- Never `eval`/`exec`, never touch the filesystem or `os.environ`, never fabricate real secrets,
  never call a domain the request didn't supply.
- Advanced in-call Python receives a run context as its first parameter; business parameters follow.

### Predefined functions (no code)

| `type` | Required | Notes |
| --- | --- | --- |
| `end` | `name`, `description` | Nothing else. Ends the call. |
| `transfer` | `name`, `description`, `to_number`, `warm_transfer` | `to_number` is E.164 and is the primary destination. The builder also maintains `to_numbers[]` (ordered list, with `to_number` mirroring `to_numbers[0]`) for multi-destination attempts — write both when using a list. `warm_transfer: true` **requires** a non-empty `warm_transfer_prompt` (how to brief the human before handing over); cold transfer uses `false` + `""`. Also carries `msg_while_executing[]` and `msg_while_executing_type: "static"` for what the caller hears while connecting. |
| `keep_call_on_hold` | `name`, `description` | `hold_duration` seconds (default 20). Pairs with `hold_call_snippet` and `hold_disconnect_timeout`. |
| `available` | `name`, `description`, `api`, `event_id` | Check calendar availability (cal.com-style). |
| `booking` | `name`, `description`, `api`, `event_id` | Book the chosen slot. |
| `send_to_whatsapp` | `name`, `description`, `api` | Send a link/message to WhatsApp. |
| `assign_chat_agent` | `chat_agent_id` | Hand the contact to a chat agent after the call. Plus `conditions[]` and `scheduleFollowupAfterAssignment`. |

Two runtime tools are not stored as functions but are invoked when the corresponding feature is
enabled: the language-switch tool (see `switchableLanguages`, §14) and `collect_digits_via_dtmf`
(see `dtmf_collection_enabled`, §13 — the prompt must tell the agent to use it, with the expected
digit count).

**Pathway warm-transfer lift:** on type 3, per-function `warm_transfer` / `warm_transfer_prompt` are
stripped at save time and lifted to **version-level** `warm_transfer` / `warm_transfer_prompt` (last
warm transfer wins, traversing version functions then capabilities in order). Author them on the
transfer function; expect to read them back at version level.

### `conditions[]` — when a post-call / assignment function should run

```json
{ "id": "calltype_1731570000000_a1b2c3", "source": "call_type", "key": "connected" }
{ "id": "meta_1731570000001_d4e5f6", "source": "call_metadata", "key": "city", "value": "Pune", "other": false }
{ "id": "pcv_1731570000002_g7h8i9", "source": "post_call_variables", "name": "interested", "value": true, "other": false }
```

`source` is `call_type` \| `call_metadata` \| `post_call_variables`. For `call_type`, `key` is
`all` \| `connected` \| `not_connected`. `value` is a string or boolean — never a number or object.
`id` format `<prefix>_<unix-ms>_<6-char-alphanumeric>`. `[]` = always run. Include exactly one
`call_type` entry (default `all`) and add metadata / post-call entries only when asked.

---

## 7. LLM, temperature, caching

| Field | Type | Default | Notes |
| --- | --- | --- | --- |
| `model` | string | `gpt-4o-mini` (document default) / `gpt-4.1-mini` (builder default for new agents) | Primary LLM driving the conversation. |
| `secondary_model` | string | `gpt-4o-mini` / `gpt-4.1-nano` (builder) | Fallback LLM. |
| `temperature` | number | `8` | **Version-level scale is 0–10** (slider 0–10; new-agent default 3). Capability `llms.temperature` is **0–1** (default 0.2). Never copy one into the other without ×10 / ÷10. |
| `caching_strategy` | `response` \| `sentence` \| `none` | `response` | `response` caches whole responses (fastest repeats), `sentence` caches per sentence (more reuse, finer grain), `none` disables it. |

Typical model families available: `gpt-4o`, `gpt-4o-mini`, `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`,
`gpt-5-mini`, `gpt-5-nano`, `gpt-5.1-chat`, `gpt-5.2-chat`, `gpt-5.4-mini`, `gpt-5.4-nano`,
`openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `gpt-4o-realtime-preview`,
`gpt-4o-mini-realtime-preview`, `gemini-2.5-flash`, `llama-3.1-8b-instant`,
`llama-3.3-70b-versatile`, `meta-llama/llama-4-scout-17b-16e-instruct`,
`moonshotai/kimi-k2-instruct`, `qwen/qwen3-32b`. Availability is account- and deployment-dependent —
query the platform's model list rather than hardcoding.

**Realtime models are special:** when `model` contains `realtime`, the voice provider must be
`Open AI` (and Open AI is not selectable for non-realtime models). Realtime agents also hide the
voice-speed control, so a realtime voice config carries only `voice_provider` and `voice_name`.

On type 3, version-level `model`/`secondary_model`/`temperature` do not drive routing — per-node
`llms` win — but keep sane values anyway.

---

## 8. Post-call analysis

| Field | Type | Default | Meaning |
| --- | --- | --- | --- |
| `postcall` | object[] | `[]` | Variables extracted from the transcript **after** the call. |
| `postcallmodel` | enum | `o4-mini` (document) / `gpt-5-nano` (builder) | Extraction model. Typical set: `o4-mini`, `gpt-4.1-mini`, `gpt-4.1`, `gpt-5-mini`, `gpt-5-nano`, `gpt-4o`, `gpt-5.4-nano`, plus Gemini options on some accounts. |
| `post_call_strategy` | object | per-bucket `gpt-5-nano` | Model **per call-duration bucket** — keys `1-10`, `11-30`, `31-60`, `>60` (seconds) and `only_agent_turns`. Values are model names or `DEFAULT_VALUES` (skip analysis). `only_agent_turns` defaults to `DEFAULT_VALUES` — don't spend a model on calls where only the agent spoke. Falls back to `postcallmodel` when the object is empty. |
| `post_call_analysis_prompt` | string | `""` | How to analyse the transcript. |
| `conversion_reason` | string | `""` | What counts as a conversion. |
| `default_disposition_reason` | string | `""` | Fallback disposition when none is extracted. |
| `useOthersDropOffReason` | bool | `false` | Allow a free-text "Others" drop-off reason instead of forcing a known bucket. |

`postcall[]` entry:

```json
{
  "type": "boolean",
  "name": "appointment_booked",
  "description": "Did the user book an appointment?",
  "defaultValue": false,
  "defaultValueConfig": { "source": "static_value", "key": "", "other": false }
}
```

- `type`: `text` \| `selector` \| `boolean` \| `number` (`selector` = pick one of a known set,
  enumerated in the `description`).
- `name`: `snake_case`; `description` **is** the extraction spec — write it as a question or a
  precise instruction.
- `defaultValue` matches the type (`""` / `0` / `false`) and is used when nothing is extracted.
- `defaultValueConfig.source`: `static_value` (use `defaultValue`) or `call_metadata` (fall back to
  the metadata `key`).

Capability-scoped variables go in `capabilities[i].postcall`; global ones at version level. Global
wins on a name collision when scopes are collapsed. Never restate a node's `extract_variables` here
— one is captured live and steers the call, the other is derived afterwards.

---

## 9. Voice — `voice_configuration` / `secondary_voice_configuration`

Both are objects; the secondary is the fallback and **should be a different provider** so one
provider outage cannot take both voices down. On a fresh create set **all four** of primary voice,
secondary voice, primary transcriber, secondary transcriber.

**Never invent `voice_id` / `voice_name` / `voice_model`.** Resolve them from the live catalogue for
that account and copy the values verbatim — IDs are provider-specific (Eleven Labs and Cartesia use
opaque IDs, Azure uses ShortNames, Sarvam uses lowercase names), and a remembered one goes stale or
belongs to another provider. Match the voice gender to the persona gender declared in the script.
Language format is *model*-dependent, not just provider-dependent — re-verify `voice_language` on
every provider or model change.

Write **only** the keys the provider uses:

| Provider | Fields | Ranges / defaults |
| --- | --- | --- |
| **Eleven Labs** | `voice_provider`, `voice_name`, `voice_id`, `voice_language`, `voice_model`, `voice_category`, `voice_speed`, `voice_stability`, `voice_similarity_boost`, `voice_style` | models `eleven_flash_v2_5` (default), `eleven_turbo_v2_5`, `eleven_turbo_v2`, `eleven_flash_v2`; speed **0.7–1.2** (1.0); stability / similarity / style **0–1** (0.5 / 1 / 0.5); category `professional` |
| **Cartesia** | `voice_provider`, `voice_name`, `voice_id`, `voice_language`, `voice_model`, `voice_category`, `voice_speed`, `voice_volume`, `cartesia_emotions[]` | models `sonic-3` (default), `sonic-3.5`, `sonic-turbo`, `sonic-2`, `sonic`; speed **−1.0–1.0** (0); volume **0.5–2.0** (1.0); category `similarity`; emotions `[]` unless asked. Voices also carry a sublanguage (`hinglish-IN` vs `hi-IN`) — pick per script style |
| **Sarvam** | `voice_provider`, `voice_id`, `voice_language`, `voice_model`, `voice_speed`, `voice_pitch` — **no `voice_name`, no `voice_category`** | models `bulbul:v3` (default), `bulbul:v3-beta` — never `bulbul:v2` (no longer offered, so a config naming it can't be edited in the UI); language like `hi-IN`; speed **0.7–1.2** (1.0); pitch **−2–2** (0.5). Voice categories `Customer Care` (default) / `Content Creation` / `International` select *which voices exist*; they are not stored |
| **Deepgram** | `voice_provider`, `voice_name`, `voice_id`, `voice_language`, `voice_model` | model `aura-2`; `voice_language` **`en` only**. Curated voices: `thalia` (default), `andromeda`, `helena`, `theia` (AU) / `apollo`, `arcas`, `aries`, `draco` (UK). No speed/pitch controls |
| **Speechify** | `voice_provider`, `voice_name`, `voice_id`, `voice_language`, `voice_model`, `speechify_loudness_normalization`, `speechify_text_normalization` | model `simba-multilingual`; locales `hi-IN en-IN en ur-IN bn-IN gu-IN mr-IN ta-IN te-IN`; both normalization flags default **false**. Voices are **locale-scoped** — resolve them for the chosen locale, they are not a fixed list |
| **Murf** (restricted / per account) | `voice_provider`, `voice_name`, `voice_id`, `voice_language`, `voice_model`, `voice_style`, `voice_speed`, `voice_pitch` | model `FALCON` only (GEN2 streaming deprecated 2026-08-16); 26 locales; `voice_id` is locale-prefixed (`hi-IN-aman`); `voice_style` e.g. `Conversation` (default), `Promo`, `Narration`, `Customer Support Agent`; speed / pitch default **0**. Curated voices exist for `hi-IN en-IN en-US en-UK en-AU ta-IN bn-IN` only. Don't select it unless the account exposes it |
| **Azure** | `voice_provider`, `voice_name`, `voice_id` (ShortName), `voice_language` (full locale, e.g. `hi-IN`), `voice_speed`, `voice_pitch`, `azure_voice_style`, `azure_voice_style_degree`, `azure_voice_volume` — **no `voice_model`** | speed **−1.0–1.0** (0.2); pitch **−2–2** (0); style `default`; style degree **0.1–2.0** (0.5); volume **0–100** (100) |
| **Open AI** | `voice_provider`, `voice_name` **only** | Voices `sage alloy ash ballad coral echo shimmer verse`. **Only** valid when `model` is a realtime model, and then it is the only valid provider. If an existing config is already on Open AI, leave provider/name/language alone unless explicitly asked. |
| **Callkaro** (restricted / admin-gated) | `voice_provider`, `voice_name`, `voice_id`, `voice_language`, `voice_model`, `voice_gender`, `voice_speed`, plus generation controls `temperature`, `top_p`, `top_k`, `repetition_penalty` | model `ck-tts-v1`; languages `hi`, `en`; voices `aaryan` `raju` `mahesh` (male) / `kanika` `priya` `tarini` (female) — set `voice_gender` to match; speed **0.7–1.2**; temperature **0–2** (0.4); top_p **0–1** (0.85); top_k **−1–100** (30); repetition_penalty **1.1–2** (1.1). Don't select it unless the account exposes it |

Discover all of this from the CLI rather than recalling it: `ck voices --providers` lists providers and
models, `ck voices --provider <name> --fields` prints exactly the keys and ranges one provider takes,
and `ck voices --provider <name> [--model m] [--language l] [--gender g]` lists the voices themselves
(Speechify needs `--language`).

Language coverage differs per provider: Cartesia, Azure and Eleven Labs are language-indexed (each
voice has a language/locale), while Sarvam voices are multilingual and not language-indexed — which
makes Sarvam the reliable secondary for a language only one provider covers.

Accounts have a **provider envelope**: the set of voice/transcriber providers and editable fields
allowed for that user. A config outside the envelope is one the user cannot see or undo in the UI.
Honour it, and never write a field the account has no control for.

---

## 10. Transcriber — `transcriber` / `secondary_transcriber`

| Provider | `transcriber_language` | `transcriber_model` | Extra fields / capabilities |
| --- | --- | --- | --- |
| **Deepgram** | **string**: `en hi kn mr ta te bn multi` | required. `nova-3` (best general), `nova-3-general`, `nova-3-medical`, `nova-2`, `nova-2-general`, en-only domain variants `nova-2-{meeting,phonecall,finance,conversationalai,voicemail,medical,drivethru,automotive}`, `nova-general`, `nova-phonecall`, `voicemail`, `flux-general`, `flux-general-multi` (hi+en) | `keywords[]`, `transcriber_language_detection`, domain-specific models |
| **Sarvam** | **string** BCP-47: `hi-IN en-IN bn-IN kn-IN ml-IN mr-IN od-IN pa-IN ta-IN te-IN gu-IN` (plus `doi as ur ne kok ks sd sa sat mni brx mai-IN` on `saaras:v3`), or `unknown` for auto-detect | required. `saarika:v2.5` (common default), `saarika:v2.0/v2/v1/flash`, `saaras:v2.5`, `saaras:v3` | `transcriber_mode` (**`saaras:v3` only**: `transcribe` \| `translate` \| `verbatim` \| `translit` \| `codemix`), `transcriber_prompt` (context hint, `saaras*`) |
| **Groq** | **string**: `en`, `hi` only | required. `whisper-large-v3-turbo`, `whisper-large-v3`, `distil-whisper-large-v3-en` | — |
| **Azure** | **array** of locales (`hi-IN en-IN en-US kn-IN mr-IN ta-IN te-IN bn-IN gu-IN ml-IN pa-IN as-IN or-IN ur-IN`) — never a plain string | **none** | simultaneous multi-language recognition, `keywords[]` |
| **Eleven Labs** | **string**: `hi en kn mr ta te bn gu ml multi` | required. `scribe_v2_realtime` (low latency — prefer for live calls), `scribe_v2` (higher accuracy) | code-mixing via `multi` |
| **Soniox** | **array** (40+ codes: all major Indic plus `es fr de it pt nl pl ru uk tr ar fa he id ms vi th ja ko zh cs da fi no sv el hu ro`) | **none** | `keywords[]`, `transcriber_general_context[{key,value}]`, `transcriber_text_context`, `transcriber_translation_terms[{source,target}]` |
| **Cartesia** | **string**: `hi en kn mr ta te bn gu ml` (`ink-2` is `en` only) | required. `ink-whisper` (default), `ink-2` | — |
| **Gnani** | **string**: `en-IN,hi-IN` (Hinglish — one comma-joined string, *not* an array), `hi-IN en-IN bn-IN gu-IN kn-IN ml-IN mr-IN pa-IN ta-IN te-IN` | **none** | `transcriber_format` (`verbatim` default \| `transcribe`), `transcriber_itn_native_numerals` (bool, default false — renders numbers in the language's own numerals) |
| **Callkaro** (restricted / admin-gated) | **array** | **none** | same context / keyword / translation fields as Soniox |

Guidance:

- Soniox is the strongest default primary (realtime, multi-language, richest context support);
  Azure — or Sarvam when Azure lacks the locale — is the usual secondary. Always pick a **different
  provider** for the secondary.
- A provider whose language field is a *string* cannot cover several languages at once. For genuinely
  mixed-language calls use an array provider (Azure, Soniox) or a code-mixing model (Deepgram
  `multi`, Eleven Labs `multi`, Sarvam `codemix` mode).
- Copy `transcriber_language` from the resolved catalogue value **verbatim** — do not reformat
  `["en-IN"]` → `"en"`, or `"hi"` → `"hi-IN"`, and never wrap a string provider's value in an array.
- `keywords[]` boosts recognition of brand/product/domain words and lives **inside** the transcriber
  object, not at version level.
- Some accounts have the transcriber language **locked** — leave it unchanged there.
- `useMultiTranscribers` (agent doc) makes the secondary run alongside the primary rather than only
  on failure.
- Discover this from the CLI instead of recalling it: `ck transcribers` lists every provider/model with
  its language field and languages, and `ck transcribers --provider <name> --fields` prints the exact
  keys that provider takes.

---

## 11. Call initiation & termination

| Field | Type / default | Meaning |
| --- | --- | --- |
| `speakfirst` | `{value, customMsg, message_interruption}`, default `{value: 1, message_interruption: false}` | **Outbound.** `value: 0` = the caller speaks first (agent silent until spoken to); `1` = the agent opens with a **dynamic** greeting generated from the prompt; `2` = the agent opens with `customMsg` **verbatim** (supports `{{variables}}`). `message_interruption` = may the caller talk over the opening line. `customMsg` only matters when `value: 2`. |
| `speakfirst_inbound` | same shape | **Inbound** equivalent. Inbound often wants `0` (traditional phone behaviour). |
| `initial_pause_outbound` | int seconds, `1` | Delay before the agent speaks on outbound — a small pause avoids clipping the connect tone. |
| `initial_pause_inbound` | int seconds, `1` | Same for inbound. |
| `end_call_msg` | string[], `[]` | See §3 — uttering one of these **ends the call**. |
| `hold_disconnect_timeout` | int seconds, `30` | How long to wait before disconnecting a held/stalled call. |
| `time_limit` | int seconds, `300` | Hard cap on total call duration. |

---

## 12. Agent behaviour — silence, language switching, gender, VAD

| Field | Type / default | Meaning |
| --- | --- | --- |
| `silence_wait` | int, `6` | Seconds of caller silence before the agent says a silence prompt. |
| `silence_count` | int, `2` | How many times the silence prompt repeats before the call ends. |
| `silence_mode` | `default` \| `custom` \| `dynamic` \| `ignore`, `default` | `default` = platform prompts; `custom` = pick from `silence_prompts`; `dynamic` = the model generates one from context; `ignore` = never re-prompt on silence. |
| `silence_prompts` | string[], `[]` | Used when `silence_mode: "custom"`. |
| `silence_language` | enum + `multi`, `en` | Language of those prompts. |
| `language_switching` | bool, `false` | Switch language based on the caller's **last message** (reactive, no confirmation). |
| `language_switching_v1` | bool, `false` | Switch language only after the caller's **explicit consent/request**. Pair either flag with `language_switch_snippet` and `switchableLanguages`. |
| `detect_gender` | bool, `false` | Detect the caller's gender from audio and adapt address forms. |
| `gender_prompt_snippet` | string \| null | Prompt injected when `detect_gender` is on. |
| `formatToNumberAsIndian` | bool, `false` | Speak/format numbers in the Indian system (lakh/crore, Indian digit grouping). |

**`vad_configuration`** — voice-activity / barge-in / endpointing tuning. Treat it as
**system-owned**: leave it out unless the user explicitly asks to tune interruption behaviour, and
change one field at a time. Fields, ranges and platform defaults:

| Field | Range | Default | Effect |
| --- | --- | --- | --- |
| `silence` | 0–10000 ms | `288` | Silence needed to decide the caller stopped speaking. |
| `threshold` | 0–10 | `3` | Speech-activation sensitivity. Lower = more sensitive to quiet speech and to noise. |
| `prefix_padding_ms` | 0–10000 ms | `200` | Audio kept before detected speech starts, so the first syllable isn't clipped. |
| `min_speech_duration` | 0–0.1 s | `0.01` | Minimum speech length that counts as a new utterance (filters coughs/clicks). |
| `interrupt_speech_duration` | seconds | `0.5` | How long the caller must speak to interrupt the agent. |
| `interrupt_min_words` | 0–4 | `3` | Minimum words required to interrupt — raise it when "hmm"/"haan" keeps cutting the agent off. |
| `clear_buffer_if_not_interrupted` | bool | `true` | Discard buffered caller audio that didn't amount to an interruption. |
| `manual_interruption` | bool | `true` | Enable the explicit interruption path. |
| `manual_interruption_duration` | 0–10 s | `1.6` | Speech duration for that path. |
| `max_buffered_speech` | 0–100 s | `5` | Cap on buffered caller speech. |
| `min_endpointing_delay` | 0–1 s | `0.5` | Minimum wait before treating the turn as finished. |
| `max_endpointing_delay` | 0–10 s | `6` | Maximum wait before force-ending the turn. |
| `preemptive_synthesis` | bool | `true` | Start synthesising the reply before the turn is fully closed (lower latency). |

---

## 13. Call settings

| Field | Type / default | Meaning |
| --- | --- | --- |
| `bgNoise` | bool, `true` | Ambient office noise so the line sounds human rather than studio-silent. |
| `bgNoiseVolume` | 0–1, `0.2` | Volume of that ambience. |
| `noise_cancellation` | bool, `true` | Suppress the **caller's** background noise before transcription. |
| `noise_cancellation_strategy` | `aicoustics` \| `dtln` \| `deepfilternet` \| `noisereduce`, `aicoustics` | Which denoiser to use. `aicoustics` is shown as CallKaro in the UI. |
| `noise_cancellation_strength` | 0.05–1, `1` | Strength of caller-noise reduction; used when noise cancellation is enabled. |
| `punctuations_to_remove` | string[], `[]` | Exact strings removed from caller transcriptions before they are processed. |
| `voicemail_msg` | bool, `true` | Leave a message when the call lands on voicemail. |
| `voicemail_custom_msg` | string, `""` | The message. **Empty = dynamic voicemail message** (generated from the prompt); non-empty = that exact text (supports `{{variables}}`). This single field encodes the "dynamic vs custom" choice the UI shows. |
| `dtmf_collection_enabled` | bool, `false` | Let the agent collect fixed-length digits (OTP, PIN, pincode) from the keypad. The prompt must also instruct the agent to call `collect_digits_via_dtmf` with the expected digit count. UI-exposed — check §18. |
| `auto_reschedule` | bool, `false` | Automatically reschedule when the caller says they're busy or asks for a callback. |
| `rescheduling_prompt` | string \| null | How the agent should pick the new time. |
| `rescheduled_follow_up_prompt` | string \| null | Extra prompt used **on** the rescheduled call so it carries context from the previous one. |
| `followup` | bool, `false` | Adapt the call flow using previous conversation history with this contact. |
| `followup_prompt` | string \| null | Instructions for building that follow-up flow. |
| `warm_transfer` / `warm_transfer_prompt` | bool `false` / string \| null | Version-level warm transfer. On types 0–2 these normally live on the `transfer` function; on type 3 they are lifted to version level at save (§6). |
| `webhook` | string URL, `""` | Version-level webhook receiving the call-ended payload. |
| `webhook_headers` | `[{key_name, value}]`, `[]` | Optional headers sent with the webhook. `value` is either a non-sensitive literal or an exact `x_secrets.NAME` reference. |
| `time_limit`, `hold_disconnect_timeout` | see §11 | Duration caps. |

Webhook header example:

```json
{
  "webhook": "https://api.example.com/call-ended",
  "webhook_headers": [
    { "key_name": "Authorization", "value": "x_secrets.CRM_AUTH_HEADER" },
    { "key_name": "Content-Type", "value": "application/json" }
  ]
}
```

Run `ck secrets list --json` before authoring sensitive headers and reuse matching names. Use exact
`x_secrets.NAME` values for API keys, tokens, passwords, and other credentials; never place their
literal values in an agent payload or chat. The saved secret must contain the complete header value
expected by the destination, including `Bearer ` when required. After every successful create or
update, report each missing name and tell the user to run `ck secrets set <name>`, add it at
`https://callkaro.ai/dashboard/settings/secrets`, or ask their admin to update the registry. See
[../secrets.md](../secrets.md) for source-code syntax and the full workflow.

---

## 14. Variables, formatting, knowledge, filler, pronunciation

| Field | Type / default | Meaning |
| --- | --- | --- |
| `knowledges` | ObjectId[], `[]` | Attached knowledge-base documents (RAG). Resolve names → ids from the account's knowledge bases; never invent ids. |
| `msg_while_executing_knowledge_base` | string[], `[]` | Lines the agent can say while a knowledge-base lookup is running. |
| `insert_metadata_in_prompt` | bool, `true` | Whether `{{metadata}}` values are injected into the system prompt at call start. Turn off when metadata should reach only functions, not the prompt. |
| `preFormatVariables` | `{ "<variable>": "<formatKey>" }`, `{}` | How a raw variable value is transformed **before it is spoken**. |
| `variableSource` | `{ "<variable>": {format, source, keyvalue, format_as_indian} }`, `{}` | Where each variable's value comes from **and** how it is formatted. `source` is an integration id the account has connected (e.g. `leadsquared`, `hubspot`, `hubspot-plus`, `heltar`, `aisensy`) or `""` for a plain call-metadata variable; `keyvalue` is the field name in that system; `format` is a format key (below); `format_as_indian` applies Indian number formatting. |
| `callPropertyMapping` | `{ "<externalProperty>": {field} }`, `{}` | Maps CallKaro call fields onto an external CRM's call properties for post-call write-back (HubSpot-Plus style). UI-exposed — check §18. |
| `customPronunciations` | `{ "<word>": "<pronunciation>" }`, `{}` | Phonetic overrides for brand, product and place names the TTS mispronounces. Write the pronunciation the way it should sound in the target language. |
| `filler_config` | object, `{}` | Filler sounds while the agent thinks (below). |
| `switchableLanguages` | object[], `[]` | Mid-call language-switch rules (below). |
| `switchableAgents` | object[], `[]` | Transfer-to-another-agent rules (below). |

**Format keys** (for `preFormatVariables` values and `variableSource.format`):
`No`, `Custom` (written as `Custom:<free-text description>` — an LLM formats the value per that
description), `Latin:Devanagari`, `Number:FullWords`, `Number:NearestHundreds`,
`Number:NearestThousands`, `Number:NearestLakhs`, `Number:DigitByDigit`, `Date:Day`,
`Date:DayMonth`, `Date:DayMonthYear`, `Time:HourMinuteAMPM`, `DateTime:FullSentence`,
`DateTime:SentenceWithoutYear`, `DateTime:HourMinuteAMPM`, `DateTime:Day`, `DateTime:DayMonth`,
`DateTime:DayMonthYear`.
Typical uses: an ISO datetime → `DateTime:FullSentence` so it is spoken as a sentence; an English
city name in a Hindi script → `Latin:Devanagari`; a loan amount → `Number:FullWords`; an account
number → `Number:DigitByDigit`.

**`filler_config`:**

| Field | Meaning |
| --- | --- |
| `filler_type` | `none` (default) / `dynamic` (LLM-generated filler) / `static` (random pick from `filler_phrases`) |
| `filler_phrases` | string[] — used when `static` |
| `filler_prompt` | prompt used when `dynamic` (default intent: return a filler phrase based on conversation context) |
| `model` / `temperature` | LLM for `dynamic` fillers (typical `llama-3.3-70b-versatile`, 0.5) |
| `trailing_silence_seconds` | silence appended after each filler before the agent resumes (0–3, default 0.6) |
| `dynamic_context_wait_seconds` | how long to wait for more context before generating (0–3, default 0.65) |
| `delay_seconds` | delay before playing the filler; `null`/0 = auto-calculated (max 3) |

Per-capability `use_filler` (§4) gates fillers phase-by-phase once a filler type is set.

**`switchableLanguages[]`** — each entry:
`{language, when_to_transfer, end_msg_type: static|silent, end_msg, start_msg_type: static|dynamic, start_msg}`.
`when_to_transfer` is the natural-language rule for switching to that language; `end_msg` is said in
the *current* language while switching (empty when `silent`); `start_msg` is the first line in the
*new* language (empty when `dynamic`). **Never add an entry for the version's own
`default_language`** — a call cannot switch to the language it is already in.

**`switchableAgents[]`** — the same shape with `agentId` instead of `language`: transfer the live call
to another agent (a different specialist bot), with the same end/start message controls. Requires a
real agent id.

---

## 15. WhatsApp functions & chat-agent handoff

WhatsApp actions are stored in the same `functions[]` array, with their own types:

| `type` | When it runs | Fields |
| --- | --- | --- |
| `whatsapp_in_call` | mid-call, model-triggered | `name`, `provider`, `messageType`, `description` (trigger condition), `msg_while_executing_type` (`dynamic` default) + `msg_while_executing[]`, `linkToCall`, and when `linkToCall !== "off"`: `userTurnInstruction`, `replyDuringCall`, plus `agentTurnInstruction` unless `linkToCall === "user_only"` |
| `whatsapp_post_call` | after the call | `name`, `provider`, `messageType`, template/campaign fields, `conditions[]` (§6) |
| `assign_chat_agent` | after the call | `chat_agent_id`, `conditions[]`, `scheduleFollowupAfterAssignment` |

`messageType` is `template` or `text`. A **template** message carries the provider's template
identity — `templateId`, `templateName`, `languageCode`, `headerFormat` for standard WhatsApp;
`campaignName`/`templateName`, or `templateKey`/`campaignId`/`campaignName`, for campaign-based
providers — plus `parameters` mapping each template placeholder id to a source key. Every template
placeholder must be mapped or the save is rejected. A **text** message needs only `description`
(and the `linkToCall` fields). `linkToCall` controls whether the WhatsApp thread is linked into the
live call and whose turns feed it (`off` / `user_only` / both). Function names must be unique and
must not collide with reserved agent function names.

---

## 16. Versioning & publishing

Versions are append-only in practice: prefer creating a **new version** over editing a published one.
Every write also records a commit snapshot, so version history is queryable and comparable.

| Concern | Field / endpoint |
| --- | --- |
| Version label | `versionName` (version doc) |
| Enable / disable a version | `isVersionActive` (bool, default `true`) · `PUT /v2agent/toggleVersionActive/:id` |
| Publish for a language | `publishedVersionsByLanguage` — one entry per version `default_language`; publishing **replaces** the existing entry for that language · `PUT /v2agent/publishAgent/:id` |
| Version shown in the UI | `publishedVersionId` + `lastPublishedDate` |
| Live / not live | `agentStatus`: `live` \| `in-progress` |
| New agent (agent + first version in one body) | `POST /v2agent` — body split per §1; the first version auto-publishes for its language |
| New version on an existing agent | `POST /v2agent/createNewVersion/:id` — body `versionName` + version fields |
| Edit a version | `PUT /v2agent/:id?version=<versionId>` — **the `version` query param is required** for any version field, otherwise the request is rejected (400) |
| Read | `GET /v2agent/:id?version=<versionId>` — returns agent+version merged, plus all versions |
| Duplicate | `PUT /v2agent/duplicate/:id` |
| Export / import versions | `POST /v2agent/:id/export` (`{versionIds}`) · `POST /v2agent/:id/import-versions` (array of version payloads) |
| Delete a version | `DELETE /v2agent/deleteversion/:id` |
| Compare versions | `POST /v2agent/compareVersions` |

Behaviours to rely on:

- A brand-new version auto-publishes **only if** no version is published yet for its
  `default_language`; it never steals an existing published slot.
- On `PUT /:id`, plain objects are **merged key-by-key**, *except* `preFormatVariables`,
  `customPronunciations`, `transcriber`, `secondary_transcriber`, `voice_configuration`,
  `secondary_voice_configuration`, `callFlow_json`, `variableSource`, which are **replaced
  wholesale**. To remove one key from a merged object, send the whole object without it.
- Optimistic conflict detection: send `originalSystemPrompt`, `originalRole`, `originalGoal`,
  `originalCallFlow`, `originalModelResponseSnippet`, `originalSecurityGuardrailsSnippet` alongside
  your edit and you get a `409` with a line-level `conflicts[]` list if the server copy moved
  underneath you. Pass `commitMessage` to label the commit.
- Export strips ids, ownership, phone numbers, knowledge bases and switchable entities and adds an
  encrypted source-agent marker; WhatsApp-type functions are stripped when importing across accounts.

---

## 17. Complete version field index

Everything the version document declares, with its default and the section that explains it.

| Field | Type | Default | § |
| --- | --- | --- | --- |
| `versionName` | string | — | 16 |
| `systempromptType` | int 0–3 | `0` | 2 |
| `isVersionActive` | bool | `true` | 16 |
| `systemprompt` | string | `"You are a helpful assistant."` | 3 |
| `role`, `goal`, `callFlow` | string | `""` | 3 |
| `instructions`, `guardrails`, `rebuttals` | string[] | `[]` | 3 |
| `callFlow_json` | object | `null` | 3 |
| `useCallFlow_json` | bool | `false` | 3 |
| `capabilities` | object[] | `[]` | 4 |
| `end_call_msg` | string[] | `[]` | 3, 11 |
| `model_response_snippet` | string | `null` → platform default | 3 |
| `security_guardrails_snippet` | string | `null` → platform default | 3 |
| `function_calling_snippet` | string | `null` → platform default | 3 |
| `language_switch_snippet` | string | `null` → platform default | 3 |
| `hold_call_snippet` | string | `null` → platform default | 3 |
| `gender_prompt_snippet` | string | `null` | 12 |
| `default_language` | enum | `"en"` | 3 |
| `silence_language` | enum + `multi` | `"en"` | 12 |
| `model` | string | `gpt-4o-mini` | 7 |
| `secondary_model` | string | `gpt-4o-mini` | 7 |
| `temperature` | number 0–10 | `8` | 7 |
| `caching_strategy` | enum | `"response"` | 7 |
| `voice_configuration` | object | platform default (Eleven Labs) | 9 |
| `secondary_voice_configuration` | object | — | 9 |
| `transcriber` | object | platform default (Deepgram `nova-3`) | 10 |
| `secondary_transcriber` | object | — | 10 |
| `vad_configuration` | object | see §12 | 12 |
| `filler_config` | object | `{}` | 14 |
| `customPronunciations` | object | `{}` | 14 |
| `speakfirst` | object | `{value: 1, message_interruption: false}` | 11 |
| `speakfirst_inbound` | object | same | 11 |
| `initial_pause_outbound` / `initial_pause_inbound` | int | `1` | 11 |
| `silence_count` | int | `2` | 12 |
| `silence_wait` | int | `6` | 12 |
| `silence_mode` | enum | `"default"` | 12 |
| `silence_prompts` | string[] | `[]` | 12 |
| `language_switching` | bool | `false` | 12 |
| `language_switching_v1` | bool | `false` | 12 |
| `detect_gender` | bool | `false` | 12 |
| `formatToNumberAsIndian` | bool | `false` | 12 |
| `bgNoise` | bool | `true` | 13 |
| `bgNoiseVolume` | number 0–1 | `0.2` | 13 |
| `noise_cancellation` | bool | `true` | 13 |
| `noise_cancellation_strategy` | enum | `"aicoustics"` | 13 |
| `noise_cancellation_strength` | number 0.05–1 | `1` | 13 |
| `punctuations_to_remove` | string[] | `[]` | 13 |
| `voicemail_msg` | bool | `true` | 13 |
| `voicemail_custom_msg` | string | `""` | 13 |
| `hold_disconnect_timeout` | int s | `30` | 11 |
| `time_limit` | int s | `300` | 11 |
| `auto_reschedule` | bool | `false` | 13 |
| `rescheduling_prompt` | string | `null` | 13 |
| `rescheduled_follow_up_prompt` | string | `null` | 13 |
| `followup` | bool | `false` | 13 |
| `followup_prompt` | string | `null` | 13 |
| `warm_transfer` | bool | `false` | 6, 13 |
| `warm_transfer_prompt` | string | `null` | 6, 13 |
| `functions` | object[] | `[]` | 6, 15 |
| `knowledges` | ObjectId[] | `[]` | 14 |
| `msg_while_executing_knowledge_base` | string[] | `[]` | 14 |
| `postcall` | object[] | `[]` | 8 |
| `postcallmodel` | enum | `"o4-mini"` | 8 |
| `post_call_strategy` | object | per-bucket default | 8 |
| `post_call_analysis_prompt` | string | `""` | 8 |
| `default_disposition_reason` | string | `""` | 8 |
| `useOthersDropOffReason` | bool | `false` | 8 |
| `conversion_reason` | string | `""` | 3, 8 |
| `webhook` | string | `""` | 13 |
| `webhook_headers` | object[] | `[]` | 13 |
| `preFormatVariables` | object | `{}` | 14 |
| `variableSource` | object | `{}` | 14 |
| `insert_metadata_in_prompt` | bool | `true` | 14 |
| `switchableAgents` | object[] | `[]` | 14 |
| `switchableLanguages` | object[] | `[]` | 14 |

---

## 18. UI-exposed fields the version document may not persist

These appear in the web builder but are **not declared on the version document** in the deployment
this reference was written against, which means a plain write is silently discarded:

`dtmf_collection_enabled` · `callPropertyMapping`

Before promising any of them to a user: write the value, read the version back, and confirm it
round-tripped. If it didn't, say so plainly instead of reporting success — the write returns 200
either way. (Nested keys inside free-form objects are unaffected and persist normally, including
`use_filler` and `to_numbers` inside `capabilities[]`/`functions[]` and every provider-specific
voice/transcriber key.)

Also treat as read-only unless explicitly asked: `vad_configuration` (system-tuned),
`abTestEnabled` / `abTestVersions` (traffic splitting), `position` on pathway nodes (layout).

---

## 19. Pre-flight checklist

Structural — a violation throws, or silently corrupts the agent:

- [ ] Every key is on the **right document** (§1) and declared (§18).
- [ ] Type-appropriate script fields populated; the other types' fields emptied.
- [ ] Types 2/3: exactly **one** `is_starting`; capability names unique and `snake_case`.
- [ ] Type 3: every `next_capability` exists; every `global` node has a non-empty `when_to_jump`; no
      `normal` node has one; every `condition_type: 1` expression is fully parenthesised with
      uppercase `AND`/`OR`; every expression variable is declared in some node's `extract_variables`
      (apart from `metadata.*`); no unreachable node; terminal nodes exist and are reachable.
- [ ] Voice/transcriber values copied verbatim from the resolved catalogue; only provider-valid keys
      present; `transcriber_language` in that provider's own format (array for
      Azure/Soniox/Callkaro).
- [ ] Realtime LLM ⇒ Open AI voice; non-realtime LLM ⇒ not Open AI.
- [ ] Function names unique within scope; parameters only `string`/`number`; no `PATCH`; post-call
      `parameters` is a JSON **string**; warm transfers have a non-empty prompt; every WhatsApp
      template placeholder mapped.
- [ ] `temperature` on the right scale — version 0–10, capability `llms` 0–1.
- [ ] `version` query param present when editing version fields.

Quality — nothing validates these, and they are what make the agent good:

- [ ] No routing prose inside a type-3 `system_prompt`.
- [ ] Every `is_required: true` variable has matching gathering instructions, and no required
      variable can trap a caller who legitimately refuses.
- [ ] `end_call_msg` contains only genuine final lines.
- [ ] One persona gender across the base prompt, every capability, every snippet, and the voice.
- [ ] Operational text in English; only spoken lines in the target language.
- [ ] No `extract_variable` duplicated as a post-call variable on the same node.
- [ ] `overwrite: true` prompts are genuinely self-contained.
- [ ] Every `{{metadata}}` reference has a fallback, so no empty placeholder is ever spoken.
- [ ] Post-call variable descriptions are precise enough to serve as an extraction spec.

---

## 20. Minimal payloads

**Type 0 (Basic) — new agent + first version**

```json
{
  "name": "Riya – Service Reminder",
  "default_agent_language": "hi",
  "outboundPhoneNumber": "<phoneNumberId>",

  "versionName": "v1",
  "default_language": "hi",
  "silence_language": "hi",
  "systemprompt": "Role\nPersona gender: female\n... full script ...",
  "role": "", "goal": "", "callFlow": "",
  "instructions": [], "guardrails": [], "rebuttals": [],
  "end_call_msg": ["आपका दिन शुभ हो!", "धन्यवाद, आपसे बात करके अच्छा लगा।"],
  "model": "gpt-4.1-mini",
  "secondary_model": "gpt-4.1-nano",
  "temperature": 3,
  "caching_strategy": "response",
  "voice_configuration": { "voice_provider": "Eleven Labs", "...": "resolved from the catalogue" },
  "secondary_voice_configuration": { "voice_provider": "Sarvam", "...": "different provider" },
  "transcriber": { "transcriber_provider": "Soniox", "transcriber_language": ["hi"], "keywords": [] },
  "secondary_transcriber": { "transcriber_provider": "Azure", "transcriber_language": ["hi-IN"] },
  "speakfirst": { "value": 1, "message_interruption": false },
  "speakfirst_inbound": { "value": 0, "message_interruption": false },
  "initial_pause_outbound": 1,
  "functions": [{ "type": "end", "name": "end_call", "description": "End the call when done" }],
  "postcall": [
    { "type": "boolean", "name": "reminder_acknowledged",
      "description": "Did the customer acknowledge the service reminder?",
      "defaultValue": false,
      "defaultValueConfig": { "source": "static_value", "key": "", "other": false } }
  ],
  "time_limit": 300
}
```

**Type 2 (Multiprompt) — capability block**

```json
{
  "systemprompt": "<shared persona, brand, standing rules, Persona gender: … — no call flow>",
  "capabilities": [
    {
      "capability": "greeting",
      "is_starting": true,
      "system_prompt": "<what to do/say in this phase; prose may say when to move on>",
      "overwrite": false,
      "stick_capability": false,
      "msg_while_switching_type": "silent",
      "msg_while_switching": "",
      "llms": { "primary_model": "gpt-4.1-mini", "secondary_model": "gpt-4.1-nano", "temperature": 0.2 },
      "functions": [],
      "postcall": []
    }
  ]
}
```

**Type 3 (Pathway) — node block with a global node**

```json
{
  "systemprompt": "<shared persona, brand, standing rules, Persona gender: … — no call flow>",
  "capabilities": [
    {
      "capability": "qualify_intent",
      "is_starting": true,
      "node_type": "normal",
      "system_prompt": "<what to do/say here — NO 'if X then go to Y'>",
      "overwrite": false,
      "extract_variables": [
        { "type": "boolean", "name": "buy_intent",
          "description": "True if the caller expresses intent to buy", "is_required": true }
      ],
      "transitions": [
        { "condition_type": 1, "condition": "(buy_intent==True)", "next_capability": "pitch_offer" },
        { "condition_type": 0, "condition": "The caller is not interested and wants to end the call",
          "next_capability": "soft_close" }
      ],
      "when_to_jump": "",
      "msg_while_switching_type": "silent",
      "msg_while_switching": "",
      "llms": { "primary_model": "gpt-4.1-mini", "secondary_model": "gpt-4.1-nano", "temperature": 0.2 },
      "functions": [],
      "postcall": []
    },
    {
      "capability": "talk_to_human",
      "is_starting": false,
      "node_type": "global",
      "when_to_jump": "The caller asks to speak to a human or becomes frustrated",
      "system_prompt": "<acknowledge, then execute the transfer>",
      "overwrite": false,
      "transitions": [],
      "extract_variables": [],
      "msg_while_switching_type": "dynamic",
      "msg_while_switching": "Say a short bridging line before connecting a human",
      "functions": [
        {
          "type": "transfer", "name": "transfer_to_agent",
          "description": "Transfer to a human agent on request",
          "to_number": "+910000000000",
          "to_numbers": ["+910000000000"],
          "warm_transfer": true,
          "warm_transfer_prompt": "Brief the agent: caller name and reason, then hand over.",
          "msg_while_executing": ["Please hold while I connect you."],
          "msg_while_executing_type": "static"
        }
      ],
      "postcall": []
    }
  ]
}
```

**Advanced post-call webhook function (JavaScript)**

```json
{
  "type": "custom_post_call",
  "name": "push_outcome_to_crm",
  "description": "Push the call outcome to the CRM after the call ends",
  "source_code": "async function pushOutcomeToCrm(context) {\n  const payload = {\n    phone: context.metadata?.phone,\n    interested: context.post_call?.interested ?? false\n  };\n  try {\n    const res = await fetch('https://api.example.com/crm/calls', {\n      method: 'POST',\n      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${x_secrets['CRM_API_TOKEN']}` },\n      body: JSON.stringify(payload)\n    });\n    if (!res.ok) console.error('CRM push failed', res.status);\n  } catch (err) {\n    console.error('CRM push error', err);\n  }\n}",
  "conditions": [
    { "id": "calltype_1731570000000_a1b2c3", "source": "call_type", "key": "connected" }
  ]
}
```
