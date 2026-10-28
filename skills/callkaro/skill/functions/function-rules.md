<!-- graph-summary: Function contracts, execution order, global vs capability scope, P0 and placeholder rules, failure patterns. Use when writing any function or when one crashes a call or fights another. -->
<!-- source: TejasLamba2006/callkaro-skills skills/callkaro-functions/SKILL.md @ 1171578; adapted: ck commands, graph links, agreed decisions -->

# CallKaro Functions

Contracts, scope, order and patterns for custom function code. Skeleton code is in [templates](templates.md). What the runtime exposes (globals, `utils`, `ctx.session`, language switching internals) is in [runtime](runtime.md); read it before writing a function that needs more than its arguments. Design context: [agent design](../design/agent-design.md).

## Types and contracts

| Type | Code | Runs | Triggered by | Contract |
|---|---|---|---|---|
| `custom_pre_call`, `update_call_data: true` (P0) | Python | before the call, first of all pre-calls | platform | `async def name(call_data: dict) -> dict`. Mutate `call_data["metadata"]` in place. May create new metadata keys. |
| `custom_pre_call`, `update_call_data: false` | Python | before the call, after P0 | platform | `async def name(metadata: dict, system_prompt: str) -> str`. Start from `system_prompt`, replace placeholders, return a string on every path. Must not create new metadata keys. |
| `on_connected` | Python | once after connection, or once on entering its capability or node | platform | `async def name(ctx: JobContext, metadata: dict)`. Side effects only; return ignored. |
| `custom_in_call` | Python | during the call | the LLM, from the description and prompt | `async def name(ctx: RunContext, arg: str, ...) -> dict`. Typed params (str, int, float, bool, None). Return `{"status": "success", ...}` or `{"status": "error", "message": ...}`. |
| `custom_post_call` | JavaScript | after post-call analysis | platform | `async function name(context)`. Appends exactly one entry to `context.functions_called`. |
| Predefined | none | as configured | LLM or platform | `transfer`, `keep_call_on_hold`, `available` / `booking` (Cal.com only), `send_to_whatsapp`, `assign_chat_agent`. Preference: end calls through closing lines in `end_call_msg` rather than the `end` function; use `end` only when there is a reason to. |

Injected helpers need no import. Python: `httpx`, `logger`, `x_secrets`, `JobContext` / `RunContext`, `send_email`. JavaScript: `axios`, `moment`, `lodash` as `_`, `console`, `sendEmail`, `x_secrets`. Always set HTTP timeouts. Never use `eval`, `exec`, dynamic imports, filesystem or process APIs. Only the first `def` in a Python body runs, so nest helpers and import inside the body.

**Email helpers (`send_email` in Python pre/in-call, `sendEmail` in JS post-call):** neither raises on delivery failure — always `await` and check `result["status"] == "success"` (Python) or `result.status === "success"` (JS), keeping SMTP credentials in `x_secrets["SMTP_USERNAME"]` / `x_secrets["SMTP_APP_PASSWORD"]` and logging the outcome in `context.functions_called` without credentials.

**In-call Python parameter types:** use scalar types only (`str`, `int`, `float`, `bool`, `None`) and annotate `-> dict`. Never use `dict`, `list`, `Any` or `Union` in parameter annotations (breaks strict tool schema); for nested payloads take `str` (JSON) and `json.loads` inside `try/except`.

**`on_connected` sandbox:** signature is `async def <name>(ctx: JobContext, metadata: dict):`. Use `ctx.room`, `ctx.proc.userdata`, or `ctx.api` — `ctx.session`, `ctx.userdata` and `RunContext` are not available in `on_connected`.

## Execution order

1. P0 pre-call functions (`update_call_data: true`) first.
2. Then the prompt-rewriting pre-call functions.
3. The call runs; in-call functions fire when the LLM calls them.
4. Post-call analysis fills variables.
5. Post-call functions run, possibly concurrently: array order is not execution order, so each must be correct alone.
6. Webhook.

Pre-calls run once per capability at call start and again on the merged prompt (one call executed a single pre-call 7 times), so keep them idempotent and cheap; on the merged run `system_prompt` is not a plain `str` (see the runtime reference).

## Global vs capability or node scope

| Type | Global (top-level `functions`) | Inside a capability or node |
|---|---|---|
| Pre-call (prompt rewrite) | replaces its placeholders in the base prompt and every capability prompt it finds them in | replaces placeholders only in that capability's prompt |
| In-call | available to the LLM anywhere | available only while that capability or node is active |
| Post-call | runs after every call | runs only if that capability or node was visited at least once |
| on_connected | once after connection | once when the call enters that scope |

- Put an in-call function where the agent needs it; global only if it can be needed anywhere.
- Never tell the LLM to call a function that is not available in the active capability.
- The same function in several capabilities must be the identical object (name, description, parameters, code). Variants need different names.
- `execute_while_switching` is for a capability-scoped pre-call function that must run on entering that capability.

## Pre-call patterns

- **P0 first.** One function owns loading data (fetch lead data for inbound or follow-up calls; overwrite only keys that already exist in metadata). Everything else reads what P0 produced.
- **Split by responsibility**: one function per concern (pricing context, negotiation pointers, greeting, each optional pitch block), not one that fetches, calculates and rewrites everything.
- **Placeholders**: replace the ones the function owns, both `{x}` and `{{x}}` forms. Never leave a raw placeholder in the final prompt; substitute a safe default.
- **Missing or malformed data**: parse defensively (treat `None`, `""`, `"None"` as missing), fall back to a usable line, never crash the prompt. A pre-call exception is `PRE_CALL_FN_FAILED` and the whole call is lost.
- **Speech-ready output**: convert numbers to words before injection (`num2words(..., lang='en_IN')` plus "rupees"); format dates and validity windows as spoken text.
- **Choose blocks, don't describe logic**: the function picks the script block for the situation and injects only that.
- **Deterministic**: same inputs, same prompt.

## Internal metadata

- Values computed for internal use are stored with a leading underscore: `_pitch_scenario`, `_active_price_val`, `_rebuttal_cap`.
- In-call functions update them as the call progresses.
- A cleanup post-call function deletes every `_` key so internal state never shows in call history.
- Post-call functions may run concurrently, so one that needs an internal value reads it from `context.functions_called` (the immutable log of in-call results), not from metadata cleanup may already have removed.

## In-call functions

- Few, and only for live data, conversation-dependent calculation or unmissable actions.
- The `description` is the model-facing trigger: say exactly when to call, what must be collected first, what to do with each result.
- The detailed gates live in `function_calling_snippet`: preconditions, the line to speak before calling, result branches, anti-fabrication ("never claim an action that did not happen", e.g. never say "I spoke to my manager" without calling the escalation function).
- Revalidate inside the function before any side effect (price ceiling, identity, eligibility). The prompt alone is not a correctness boundary.
- Make repeated calls safe: return an already-done or no-op result instead of repeating a booking, write or escalation.
- Return compact data: status plus the next spoken value. Never return secrets, raw upstream payloads or internal limits the caller must not hear.
- Spoken message while running: `msg_while_executing` (`static`, `dynamic`, `silent`) or the prompt, never both. `silent` for checks that must finish before the agent speaks.
- Function-first for exact work (digit compare, length judging, math): the model gets these wrong, code gets them right ([field notes](../agents/field-notes.md), live lessons).

## Post-call functions

- **Override**: analysis runs first, so a function can correct its output (replace a value that came back 0 with the metadata value).
- **Failsafe**: any condition can be enforced after analysis by rewriting a post-call value.
- **Deterministic**: compute exact values from in-call results (final price from the approved closing result, else the escalated price, else the offered price).
- Write a derived value to both `context.post_call.<field>` and `context.post_call_detail.<field>` (`{value, comment}`).
- **One writer per field**: two post-call functions never update the same field.
- Wrap the body in try / catch / finally and always push exactly one log entry (`name`, `parameters`, `success`, `response`, `timestamp`).
- Build explicit outbound payloads; never send the whole context.

## Secrets

New code reads from the vault: `x_secrets["API_KEY"]` in Python and JavaScript, `"x_secrets.API_KEY"` as a header value in declarative configs and webhook headers. Older agents hardcode client keys in function code; that is common and not a review finding, but new code should use the vault. `ck secrets set NAME` creates one.

## Common function bugs

- A placeholder no function replaces, or a function replacing one that no longer exists.
- Two post-call functions writing one field; a post-call reading an internal key cleanup already deleted.
- Prompt tells the LLM to call a function that exists only in another capability.
- Expected values read from `ctx` metadata in an in-call function (not visible there): pass them as arguments.
- A side effect without an idempotency guard, so a retry books twice.
- Missing timeout on an HTTP call, stalling the live call.
