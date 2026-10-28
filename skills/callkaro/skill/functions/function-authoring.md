<!-- graph-summary: Field-level authoring rules per function variant plus a review checklist. Read before writing, updating or reviewing any custom function's JSON or source_code. -->
<!-- source: authoring-pipeline/pre-call-basic-agent.md, in-call-basic-agent.md, post-call-basic-agent.md, advanced-pre-call-agent.md, advanced-in-call-agent.md, advanced-post-call-agent.md, function-critic-agent.md, function-planner-agent.md, script-analyzer-for-functions-agent.md (production prompts, condensed) -->

# Function authoring rules

The exact rules for each variant of `custom_pre_call`, `custom_in_call` and `custom_post_call`, as basic (declarative) or advanced (`source_code`), followed by the checklist to run over every function before saving. This node adds to the served references and does not repeat them. Read those first:

- Field sets, allowed methods and parameter types, secrets in headers, `conditions[]`, predefined types: [reference §6](../agents/AGENT-VERSION-REFERENCE.md).
- Signatures, execution order, scope, P0 and placeholder patterns, post-call log fields: [function-rules.md](function-rules.md).
- Globals and `ctx` contents measured at runtime: [runtime.md](runtime.md). Skeletons: [templates.md](templates.md).
- Which type to pick, and basic vs advanced: [functions.md](../agents/functions.md).

If this node and one of those disagree, follow the served reference.

## Rules for every custom function

- **`name`**: `snake_case`, at most 4 words, specific to the business action (`fetch_lead_details`, `check_loan_eligibility`, `log_call_outcome`). Never generic names like `custom_pre_call_function`, `api_call` or `my_function`. If the user gave a name, use it exactly.
- **`description`**: for pre-call and post-call, one sentence saying what the function fetches, prepares, transforms or sends. For in-call it is the trigger condition (see the in-call sections). If the user gave a description, use it; for in-call you may rewrite it into trigger form.
- **No extra fields.** Write only the fields of the variant's field set. Never add fields outside it.
- **Create or update.** Before creating, check existing functions in that scope by name, then by purpose. If one with the same name or the same purpose exists, update it, even for large changes. Never leave two functions with the same name in one scope.
- **Predefined first.** If the purpose matches a predefined type exactly (`transfer`, `keep_call_on_hold`, `available`, `booking`, `send_to_whatsapp`, `assign_chat_agent`), use it instead of a custom function. To end calls, prefer closing lines in `end_call_msg` over the `end` function. For `transfer`, always decide warm or cold: warm needs the exact `warm_transfer_prompt`; cold is explicitly `warm_transfer: false`.
- **Updates are surgical.** Change only what was asked and leave every other field exactly as it was. In `source_code`, keep the function name, signature and unrelated logic, and keep existing `x_secrets` references unless asked to change them.
- **Missing integration data never blocks.** Missing URL, headers, parameters, auth or sample payload: use placeholders and carry on (reference §6). Never leave `api` empty on create. Ask the user only when the function's *purpose* is unclear.
- **Flags.** `update_call_data` and `execute_while_switching` are always booleans, never null. `execute_while_switching` is `false` unless the user explicitly asked for it.

## Basic functions: rules shared by all three

- **`api_mapping` is always present and always `{}`.** Never put parameter mappings, constants, response paths or anything else in it.
- **`parameters` rows** are `{key_name, type, description}`. The key is `key_name`, not `name`. Never add `required`. Write `key_name` in camelCase (`leadId`, `phoneNumber`). `description` says what the value holds and where it comes from. Use parameters the user supplied; otherwise infer only ones that fit the function's purpose.
- **`headers`** is a plain `{ "Header-Name": "value" }` object, never an array. Convert `[{key, value}]` rows into that object. Always include `"Content-Type": "application/json"` for `POST` and `PUT`. Add `Authorization` only when the user mentions an API key or token, and then as an `x_secrets` reference (reference §6).
- **`method`**: the user's method if one was given, otherwise `POST`. Use `GET` only when the context clearly makes it a read-only lookup.
- **`api`**: the user's URL if one was given, otherwise a placeholder. Never an empty string.

## Basic pre-call (`custom_pre_call`, no `source_code`)

- Fields: `type: "custom_pre_call"`, `name`, `description`, `msg_while_executing_type: "dynamic"`, `msg_while_executing: []`, `api`, `method`, `parameters`, `headers`, `api_mapping: {}`.
- `msg_while_executing_type` is always `"dynamic"` and `msg_while_executing` is always `[]`. Nothing is spoken before the call.
- Parameters are usually metadata variables such as `phoneNumber`, `customerId`, `leadId`, `accountId` or `campaignId`.
- For `GET`, omit `Content-Type` unless the user supplied it.

## Basic in-call (`custom_in_call`, no `source_code`)

- Fields: `type: "custom_in_call"`, `name`, `description`, `msg_while_executing_type`, `msg_while_executing`, `api`, `method`, `parameters`, `headers`, `api_mapping: {}`.
- **`description` is a trigger**, in the form `"Call this function when the user asks about [X]."` or `"Call this function when [condition]."`. Be exact about the condition.
- **Execution message**: `msg_while_executing_type` defaults to `"dynamic"`, and then `msg_while_executing` is `[]`. Use `"static"` only when the user gave exact waiting phrases; `msg_while_executing` is then exactly those phrases, unedited.
- Use `GET` for simple lookups when the context clearly implies it.

## Basic post-call (`custom_post_call`, no `source_code`)

- Field set and the `parameters` shape (a JSON payload string, plus `parameters_mapping{}` and `conditions[]`): see [reference §6](../agents/AGENT-VERSION-REFERENCE.md). `api_mapping` is still `{}`.
- If you set the execution-message fields, use `msg_while_executing_type: "dynamic"` and `msg_while_executing: []`, because the call has ended.
- The payload holds only fields relevant to this use case. Typical ones: `callId`, `phoneNumber`, `callDuration`, `callOutcome`, `disposition`, `agentNotes`, `leadStatus`, `customerName`, `interestLevel`, `followUpDate`, `recordingUrl`, `transcriptSummary`.
- Use `PUT` when the call clearly updates an existing record.
- **Use basic only for a fixed URL** with no conditional logic on post-call variables and no retry. Switch to advanced when any of these is true:
  - post-call variables build or filter the payload;
  - logic branches on outcome fields (`escalation_flag`, `disposition`);
  - retry or error handling is needed;
  - post-call variables are non-trivial (boolean flags, selector fields, outcome mapping).

  Do not downgrade to basic just because the URL is simple.

## Advanced pre-call (`custom_pre_call` + Python)

- Fields: `type: "custom_pre_call"`, `name`, `description`, `source_code`, `update_call_data` (boolean), `execute_while_switching` (boolean, default `false`).
- **Choose the protocol before writing code.** If the request changes prompt text, use `update_call_data: false`. If it fetches or prepares data for later functions or for prompt rendering, use `true`. `update_call_data` must match the signature in `source_code`. If an update changes the protocol, change the flag and the signature together; otherwise keep the existing protocol.
- `async def`, with a full docstring: purpose, `Args` (with types) and `Returns`.
- **Metadata variables**: their names are known when you write the code (the script's `{{name}}` placeholders), but their values only arrive at call time. Read every value through `metadata.get("name", "")` with a safe fallback, and never hardcode an assumed value.
- **`update_call_data: false`**:
  - start from `final_prompt = system_prompt`;
  - overwrite a metadata key only behind `if "name" in metadata:`;
  - replace every placeholder the function owns, even when the value is an empty string;
  - end with `return final_prompt`.
- **`update_call_data: true`**:
  - open with `metadata = call_data.setdefault("metadata", {})`;
  - add or overwrite keys as needed;
  - assign the result back with `call_data["metadata"] = metadata`;
  - mutate in place, and never return a prompt or a replacement object.
- **HTTP**: use `httpx.AsyncClient(timeout=...)` (the source example uses 5.0), wrapped in `try/except httpx.RequestError`. On a non-200 status, `logger.error` the status code and fall back. Never let a failure escape.
- **Pre-imported, no import needed**: `asyncio`, `httpx`, `json`, `pytz`, `datetime`, `timedelta`, `re`, `math`, `logger`, `get_job_context`, `RunContext`, `num2words`, `get_local_time`, `check_functions_called`, `custom_llm_completion`, `send_email`, `x_secrets`. For `json`, follow the caveat in [runtime.md](runtime.md).
- **`x_secrets` is a dict.** Use `x_secrets["NAME"]` or `x_secrets.get("NAME")`, never attribute access. Never read credentials from metadata or hardcode them in source.

## Advanced in-call (`custom_in_call` + Python)

- Fields: `type: "custom_in_call"`, `name`, `description`, `msg_while_executing_type`, `msg_while_executing`, `source_code`, `update_call_data: false` (`true` only if the function intentionally mutates call data), `execute_while_switching` (default `false`).
- `description` and the execution message follow the same rules as basic in-call: a trigger sentence; `"dynamic"` with `[]` by default; `"static"` only with the user's exact phrases.
- Shape:

  ```python
  async def <name>(ctx: RunContext, <param>: <scalar type>, ...) -> dict:
      """Purpose. Args: ctx: LiveKit RunContext; <param>: <type> — <meaning>.
      Returns: dict {status: "success"|"error", <result fields>, message: str on error}"""
  ```

- **Annotations**: annotate every parameter and the return type.
  - Allowed parameter types: `str`, `int`, `float`, `bool`, `None`.
  - Forbidden: `dict`, `list`, `Any`, unstructured `Union`, file objects, custom classes, functions or lambdas.
  - For a nested payload, take a `str`, tell the model in the docstring to pass a JSON-encoded string, and parse it with `json.loads` inside `try/except`.
- **Validate every input at the top**, before any logic or side effect. Invalid input returns `{"status": "error", "message": "..."}`.
- **Return contract**: always a dict with `status`. Success is `{"status": "success", ...fields}`; error is `{"status": "error", "message": ...}`.
- **HTTP**: use `httpx.AsyncClient` for every request, with a 10-second default timeout. `except httpx.RequestError` returns `{"status": "error", "message": "Network error: ..."}`. Never raise into the call.
- **Email**: if `send_email` returns a non-success `result["status"]`, return `{"status": "error", "message": result["message"]}`.
- **Secrets**: use `x_secrets["NAME"]` dict indexing only. Never accept a fixed credential as a model-supplied parameter. Never return or log a secret value.
- Same pre-imported helpers as advanced pre-call.

## Advanced post-call (`custom_post_call` + JavaScript)

- Fields: `type: "custom_post_call"`, `name`, `description` (one sentence on the side effect), `source_code`, `conditions` (rules in [reference §6](../agents/AGENT-VERSION-REFERENCE.md)).
- **Shape**: `async function <name>(context) { ... }`. Exactly one parameter, `context`. No return value: it is ignored, so write the function for side effects only. Read all data through `context.*`.
- **Read-only, never modify**: `context.agent`, `userId`, `call_duration` (seconds), `hangup_reason`, `callSid`, `recordingUrl`, `user_phone_number`, `agent_phone_number`, `name`, and `call_metadata.<name>`.
- **Writable**: `context.conversion_status` (bool), `disposition_reason`, `next_call_scheduled` (bool), `post_call.<field>`, `post_call_detail.<field> = {value, comment}`, and `functions_called.push(...)`.
- **Metadata** is `context.call_metadata`, never `context.metadata`. Guard every read with `context.call_metadata.<name> ?? null`. Use metadata values as identifiers, to find which record to update (for example `lead_id`).
- **Post-call variables** (`context.post_call.<name>`) are the main payload to send. Guard each one with `if (context.post_call.<name> !== undefined)`. Use the exact `snake_case` names from the post-call configuration; those names are never renamed or translated. Variable types are `number`, `text`, `selector` and `boolean`.
- **Payload**: identifiers from `call_metadata` plus results from `post_call`.
- **Log entry**: the body is one `try/catch/finally`.
  - Build the log object first with `success: false` and `response: null`.
  - Set `success: true` and `response` on success.
  - In `catch`, put `error.message` into `response`.
  - Push in `finally`.
  - The entry has exactly `name`, `parameters`, `success`, `response` and `timestamp` (`new Date().toISOString()`), with no other fields such as `details` or `result`.
  - On an early exit (for example a missing recipient), set `response` to the reason before `return`, so `finally` still logs it.
- **Pre-imported, never `require()`**:
  - `axios`: `await axios({ method, url, headers, data, timeout: 10000 })`;
  - `moment`: for example `moment.tz("Asia/Kolkata")`;
  - `_` (lodash);
  - `console.log` and `console.error`;
  - `sendEmail`: await it and check `result.status`;
  - `x_secrets`: `x_secrets['NAME']`, with dot access only for names that are valid identifiers.

  Use `axios`, not `fetch`.
- **Secrets**: never log, return or hardcode a value read from `x_secrets`.

## Backend save checks (Python functions)

Saving a version runs these checks on every Python function (`custom_pre_call`, `custom_in_call`,
`on_connected`) and rejects the whole save on the first failure. They were read from the backend's
own 400 messages (October 2026).

- **Import allow-list.** Only these modules, and their submodules where shown, may be imported:
  `aiohttp asyncio audio.audio_handler base64 calendar collections copy dataclasses datetime decimal
  enum functools hashlib hmac html httpx itertools json livekit math num2words pytz random rapidfuzz re
  statistics string textwrap time typing unicodedata urllib.parse uuid zoneinfo`. For fuzzy matching
  use `rapidfuzz` (`from rapidfuzz import process, fuzz`), not `difflib`.
- **Docstring.** The function must have a docstring right under the `async def` line saying what it
  does and when the agent should call it. Keep it when rewriting the function.

## Code safety (all advanced functions)

- **Python, forbidden**: `eval`, `exec`, `compile`; any filesystem access (`open`, reading or writing files); `os.environ`; `os.system`, `subprocess`; dynamic imports (`importlib`, `__import__`); domains the user did not supply; hardcoded keys, passwords or tokens; returning or logging secret values; adding metadata keys under `update_call_data: false`.
- **JavaScript, forbidden**: `process`, `process.env`, `require()`, `__dirname`, `__filename`, `eval()`, `Function()`, `fs`, `child_process`; hardcoded keys, passwords or tokens; logging or returning values read from `x_secrets`.
- A placeholder URL is fine. A placeholder, dummy or hardcoded credential never is: every fixed credential is a descriptively named `x_secrets` reference.

## Review checklist (run over every function before and after saving)

1. **Scope listing**: read back every scope you touched (global and each capability). On type 2 agents, check each capability separately. A function that is needed in a capability but exists only globally is a failure.
2. **Duplicates**: two functions with the same name in one scope is an immediate failure. Remove the extra one before checking anything else.
3. **Planned operations**:
   - every create exists with the right name, type and fields;
   - every update shows the requested change;
   - every delete is really gone.
4. **Intent**: name, type and description match what the user asked for. `name`, `type` and `description` are all present.
5. **Credentials**: no hardcoded or dummy credentials; fixed credentials use `x_secrets`. A placeholder URL is acceptable; an empty one is not.
6. **Basic functions**:
   - `api_mapping` is exactly `{}`;
   - `parameters` rows use `key_name` and have no `required`;
   - `headers` is an object;
   - in-call `description` is a trigger;
   - `msg_while_executing` is `[]` whenever the type is `"dynamic"`.
7. **`custom_pre_call` (advanced)**: `update_call_data` is a boolean and pairs with exactly one signature:
   - `false` with `async def name(metadata: dict, system_prompt: str) -> str`;
   - `true` with `async def name(call_data: dict)` mutating in place.
8. **`custom_in_call` (advanced)**: async Python; `ctx: RunContext` first; typed scalar business parameters; `-> dict`; input validation at the top; `status`-based result dicts on every path.
9. **Python**: `httpx` for HTTP; `x_secrets` read by dict indexing, never attribute access; email through `send_email`, awaited, with `result["status"]` checked; every import on the allow-list; a docstring under `def`.
10. **`custom_post_call` (advanced)**:
    - async JavaScript taking exactly `context`;
    - `context.call_metadata`, not `context.metadata`;
    - `axios`, not `fetch` or `require`;
    - the mandatory `functions_called` entry with only the five fields;
    - email through `sendEmail` with `result.status` checked.
11. **`transfer`**:
    - `warm_transfer` is present as `true` or `false`;
    - if `true`, `warm_transfer_prompt` is a non-empty string;
    - if the user asked for a waiting message, `msg_while_executing` is a non-empty array.
12. **What counts**: accept a function that is functionally correct, even if imperfect. Reject it for structural or runtime-contract problems:
    - wrong type or purpose;
    - missing required fields;
    - signature and protocol mismatch;
    - unsupported helper or API;
    - missing post-call log;
    - a failed delete;
    - a duplicate;
    - a credential leak.
13. **Fix or recreate**:
    - delete and recreate when the type is wrong, the purpose is different, it is a duplicate, or the code is structurally broken beyond a targeted fix;
    - fix in place when the name and type are right and only a detail is wrong (URL, a field value, a missing condition, a small logic error).
