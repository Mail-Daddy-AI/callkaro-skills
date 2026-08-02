# Functions — giving the agent abilities

Functions live in `functions[]` (version level = callable everywhere) or
`capabilities[i].functions[]` (only inside that capability/node). Field shapes
and predefined types (`end`, `transfer`, `keep_call_on_hold`, `available`,
`booking`, WhatsApp, `assign_chat_agent`):
[AGENT-VERSION-REFERENCE.md](AGENT-VERSION-REFERENCE.md) §6 and §15.

This file covers **when to choose basic vs advanced** and the exact **advanced
`source_code` protocols** the platform enforces (violations are rejected).

## Basic vs advanced

| | Basic | Advanced (`source_code`) |
|---|---|---|
| What it is | fixed API call described by fields (`api`, `method`, `parameters[]`, `headers[]`) | real code the platform executes |
| Choose when | one fixed URL, no logic | URL contains `{{variables}}`, branching/retries, payload built from variables, response needs processing |
| Language | — | pre-call & in-call: **Python** · post-call: **JavaScript** |

Common constraints (both): parameter rows only `{key_name, type:"string"|"number",
description}` (no boolean/object/enum — pass `"true"`/`"false"` strings);
methods `GET POST PUT DELETE` (no PATCH); placeholders for pending integrations
are normal (`https://api.example.com/…`, `Bearer YOUR_API_KEY_HERE`) — write
the function and say so, never block.

For `custom_in_call`, the `description` **is the trigger** — the model reads it
to decide when to call. Write it as a condition ("Call this when the user
confirms a slot and provides a pincode"), not a summary.

---

## Protocol 1 — In-call Python (`custom_in_call`, advanced)

Runs mid-call, model-triggered. Shape:

```python
async def tool_name(ctx: RunContext, lead_id: str, pincode: str) -> dict:
    """
    Fetch inspection slots for a pincode.
    Args: ctx: LiveKit RunContext. lead_id: Lead ID. pincode: 6-digit pincode.
    Returns: dict with status: "success"|"error", plus data or message.
    """
```

Hard rules:
- `async def`, **first parameter `ctx: RunContext`**, full type annotations,
  docstring with purpose/args/returns. Keep the code as small as possible.
- **Always return a dict** `{"status": "success"|"error", "message"?, ...}` —
  never raw strings, never `json.dumps`, never non-serializable objects.
- Validate inputs early (`if len(pincode) != 6 or not pincode.isdigit(): return {...error}`).

**Pre-injected environment — import NOTHING:**
`asyncio, httpx, json, pytz, datetime, timedelta, RunContext, get_job_context,
logger`, plus helpers:
- `num2words(raw_count, lang='en_IN')` — numbers to words
- `get_local_time(time, language)` — local time strings in `hi en ta kn te mr`
- `check_functions_called(job_ctx, function_name, parameters)` — was a function already called this call?
- `custom_llm_completion(system_prompt, user_prompt, model, temperature=0.0)` —
  LLM call inside the tool; models: `o4-mini, gpt-4.1-mini, gpt-4.1, gpt-5-mini, gpt-4o`

State & context:
- Shared state: `job_ctx = get_job_context()` → `job_ctx.proc.userdata["key"] = value`
- Update the live agent prompt ONLY via
  `agent = ctx.session.current_agent; await agent.update_instructions(...)`
- **Call metadata**: `data = getattr(ctx.session.current_agent, "dial_info", None)`
  then `metadata = data.get("metadata", {}) if data else {}`. `dial_info` is
  dict-LIKE (`.get()`, `["key"]`) but **NOT a dict** — never
  `isinstance(data, dict)` (returns False); guard with a None check. Keys:
  `to_number, from_number, metadata, extracted_variables, agent_id, user_id,
  version_id, default_language`. Read-only.

HTTP: `httpx.AsyncClient(timeout=10.0)`; max 3 retries with small backoff;
check `resp.status_code != 200` → error dict; catch `httpx.RequestError`.

Forbidden (function is rejected): `eval/exec/compile`, dynamic imports, ANY
filesystem access, `os.system/subprocess/multiprocessing`, env-var changes,
calling unknown external hosts / exfiltrating state, heavy loops, unawaited
`asyncio.create_task`, infinite loops/long sleeps, logging secrets or phone
numbers or prompts, tampering with helpers/logging.

---

## Protocol 2 — Pre-call Python (`custom_pre_call`, advanced)

Runs before the call connects. **Two protocols, chosen by `update_call_data`
(a boolean, never null):**

```python
# update_call_data: false — personalise the prompt
async def personalize(metadata: dict, system_prompt: str) -> str:
    final = system_prompt.replace("{customer_name}", str(metadata.get("customer_name") or ""))
    return final          # MUST return the prompt string on every path

# update_call_data: true — enrich call data
async def enrich(call_data: dict):
    md = call_data.setdefault("metadata", {})
    md["call_type"] = call_data.get("name", "")
    call_data["metadata"] = md    # mutate in place; return nothing
```

- Signatures are exact: `(metadata, system_prompt) -> str` for `false`,
  `(call_data)` for `true`. Never mix.
- **Brace convention:** prompts use `{{name}}`, but replacement code targets
  single-brace `{name}` — `.replace("{name}", …)`, never `"{{name}}"`.
- Only the `true` protocol may ADD metadata keys; `false` may only overwrite
  existing ones / change the prompt.
- Same HTTP + security rules as in-call.

## Protocol 3 — Post-call JavaScript (`custom_post_call`, advanced)

Runs after the call: CRM pushes, notifications, custom disposition logic.

```javascript
async function push_outcome(context) {
    // ALL data via the single `context` parameter. Returns nothing.
}
```

- `async function name(context)` — exactly one parameter; side-effect only.
- **Everything through `context`** (never bare names):
  `context.call_metadata?.lead_id`, `context.post_call?.interested`,
  `context.call_duration` (s), `context.hangup_reason`,
  `context.user_phone_number`, `context.agent_phone_number`, `context.callSid`,
  `context.recordingUrl`.
- **Mutable** — you may set: `context.conversion_status`,
  `context.disposition_reason`, `context.next_call_scheduled`,
  `context.post_call.<field>`, `context.post_call_detail.<field> = {value, comment}`,
  and push to `context.functions_called`.
- **Pre-imported, do NOT `require()`**: `axios`, `moment` (tz-aware), `_`
  (lodash), `console`.
- API calls: `axios({method,url,headers,data,timeout:10000})` in try/catch.
- **Always log the run** to `context.functions_called` with EXACTLY:
  `{name, parameters, success, response, timestamp}` — no extra fields.
- Retry/error handling lives inside the code — there is no retry field.
- `conditions[]` gates whether it runs at all (call_type / metadata /
  post-call-variable conditions — REFERENCE §6).

## Scoping & placement heuristics

- Attach a function to the **node that invokes it** ("transfer between node 3
  and node 4" = transfer function on node 3).
- One `end` function per agent is almost always wanted — without it the agent
  cannot hang up gracefully.
- Warm transfer (`warm_transfer: true`) **requires** a non-empty
  `warm_transfer_prompt`; on pathway agents both get lifted to version level at
  save (REFERENCE §6).
