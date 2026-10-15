# Writing Advanced Function Code
<!-- graph-summary: Rules for advanced function code: in-call Python (typed scalar parameters, status-dict returns, helpers) and post-call JavaScript (context fields, mandatory functions_called log, forbidden APIs). -->

Rules for the `source_code` of advanced `custom_in_call` (Python) and `custom_post_call`
(JavaScript) functions. Advanced pre-call and email helpers are in
[AGENT-VERSION-REFERENCE.md](AGENT-VERSION-REFERENCE.md) §6; choosing the function type and
where to attach it is in [functions.md](functions.md).

## In-call (Python)

Runs during the live call. The model reads `description` to decide when to call it, so write it as
a trigger: "Call this function when the user asks about X."

```python
async def check_loan_eligibility(ctx: RunContext, pan: str, income: int) -> dict:
    """Checks eligibility.

    Args:
        ctx: run context
        pan: str — the caller's PAN
        income: int — monthly income in rupees

    Returns:
        dict: {status: "success" | "error", ..., message: str on error}
    """
    if not pan or income <= 0:
        return {"status": "error", "message": "PAN and a positive income are required"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"pan": pan})
    except httpx.RequestError as e:
        return {"status": "error", "message": f"Network error: {e}"}
    return {"status": "success", "eligible": resp.json().get("eligible")}
```

- `async def`, a docstring (purpose, typed args, return shape), and every parameter plus `-> dict`
  annotated. `ctx: RunContext` comes first, business parameters after.
- **Parameter types: `str`, `int`, `float`, `bool`, `None` only.** Never `dict`, `list`, `Any`,
  unstructured `Union`, file objects, classes or lambdas, because they break the model's strict tool
  schema. For a nested payload take a `str`, say in the docstring that it is a JSON string, and parse
  it with `json.loads` inside `try/except`.
- Validate inputs first and return `{"status":"error","message":...}` before doing any work.
- Always return a dict with `status`: `success` plus result fields, or `error` plus `message`.
- HTTP uses the pre-imported `httpx.AsyncClient` with a timeout (10 s by default) inside
  `try/except httpx.RequestError`.
- Pre-imported, so do not import them: `asyncio, httpx, json, pytz, datetime, timedelta, re, math,
  logger, get_job_context, RunContext, num2words, get_local_time, check_functions_called,
  custom_llm_completion, send_email, x_secrets`.
- Secrets: `x_secrets["NAME"]` (a dict, never attribute access). Never accept a fixed credential as
  a model-supplied parameter, and never log or return a secret.
- Set `msg_while_executing_type` to `dynamic` (the model improvises a filler) with
  `msg_while_executing: []`, unless the user gave exact phrases, in which case use `static`.
- `update_call_data: false` unless the function deliberately mutates call data;
  `execute_while_switching: false` unless asked.
- Names are `snake_case`, at most 4 words, specific to the action (`verify_otp`, `get_order_status`).

## Post-call (JavaScript)

Runs after the call ends, for side effects only (CRM, webhooks, logging, analytics). The return
value is ignored. Typical job: send the values the AI extracted (`context.post_call.*`) to an
external system, using `context.call_metadata.*` to identify the record.

```javascript
async function updateCrmRecord(context) {
  const functionLog = {
    name: "updateCrmRecord",
    parameters: { lead_id: context.call_metadata.lead_id ?? null },
    success: false,
    response: null,
    timestamp: new Date().toISOString()
  };
  try {
    if (context.post_call.interested !== undefined) {
      const res = await axios({
        method: "POST", url: "https://api.example.com/leads",
        headers: { Authorization: `Bearer ${x_secrets["CRM_API_TOKEN"]}` },
        data: { lead_id: functionLog.parameters.lead_id, interested: context.post_call.interested },
        timeout: 10000
      });
      functionLog.response = res.data;
    }
    functionLog.success = true;
  } catch (error) {
    functionLog.response = error.message;
  } finally {
    context.functions_called.push(functionLog);
  }
}
```

- `async function name(context)`, exactly one parameter, everything read through `context.*`.
- **Read-only:** `agent`, `userId`, `call_duration`, `hangup_reason`, `callSid`, `recordingUrl`,
  `user_phone_number`, `agent_phone_number`, `name`, `call_metadata.<name>`.
  Guard every metadata read with `?? null` and every post-call read with `!== undefined`; names are
  known when you write the code, values only arrive at call time.
- **Writable:** `conversion_status`, `disposition_reason`, `next_call_scheduled`,
  `post_call.<field>`, `post_call_detail.<field>` (`{value, comment}`), `functions_called`.
- **Logging is mandatory.** Push one entry to `context.functions_called` in a `finally`, with exactly
  `name, parameters, success, response, timestamp` and no other fields. The whole body is in
  `try/catch/finally`.
- Pre-imported: `axios`, `moment` (use `moment.tz(...)`), `_` (lodash), `console`, `sendEmail`,
  `x_secrets`. Use `context.call_metadata`, not `context.metadata`.
- Forbidden: `require()`, `process`/`process.env`, `__dirname`, `eval`/`Function`, `fs`,
  `child_process`, `fetch`, hardcoded credentials, and logging or returning anything read from
  `x_secrets`.
- Optional `conditions` field only when the user asks for conditional execution.
- Names are `snake_case`, at most 4 words, specific to the side effect (`update_crm_record`).

## Updating existing function code

Read the existing `source_code` first and change only what was asked, keeping the name, signature,
logging and every `x_secrets` reference as they are. For pre-call, change `update_call_data` and the
signature together or not at all.

Reviewing generated functions: [verify-and-review.md](verify-and-review.md).
