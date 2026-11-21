<!-- graph-summary: Skeleton code for P0 and prompt-rewriting pre-call, on_connected, in-call and post-call functions. Fill from the design; delete what the agent does not need. -->
<!-- source: TejasLamba2006/callkaro-skills skills/callkaro-functions/TEMPLATES.md @ 1171578; adapted: harness tools, graph links, agreed decisions -->

# Function skeletons

Skeletons only. Fill them from the design, delete what the agent does not need. Rules behind them are in [function rules](function-rules.md).

## P0 pre-call (update_call_data: true)

```python
async def update_call_data_metadata(call_data: dict) -> dict:
    metadata = call_data.get("metadata", {})
    lead_id = metadata.get("lead_id")
    if not lead_id:
        return call_data
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.example.com/lead",
                params={"lead_id": lead_id},
                headers={"client-secret": x_secrets["CLIENT_SECRET"]},
            )
        response.raise_for_status()
        data = response.json().get("data", {})
        for key, value in data.items():
            if key in metadata:          # only refresh known keys
                metadata[key] = value
        call_data["metadata"] = metadata
    except Exception as e:
        logger.error("P0 fetch failed for lead_id=%s: %s", lead_id, str(e))
    return call_data
```

## Prompt-rewriting pre-call

```python
async def fill_example_block(metadata: dict, system_prompt: str) -> str:
    final_prompt = system_prompt or ""
    value = metadata.get("some_field")
    if value in (None, "", "None"):
        block = "<safe default line>"
    elif <condition decided from metadata>:
        block = "<line or script block for case A>"
    else:
        block = "<line or script block for case B>"
    for token in ("{example_block}", "{{example_block}}"):
        final_prompt = final_prompt.replace(token, block)
    return final_prompt
```

On the merged run `system_prompt` can be a `CapabilitySystemPrompt`, not a `str`: guard with `isinstance(system_prompt, str)` before string methods (runtime reference).

## In-call function

```python
async def check_something(ctx: RunContext, customer_value: str) -> dict:
    """Check <what> for the caller. Call only after <precondition>.

    Args:
        ctx: LiveKit RunContext
        customer_value: str, the value the caller gave

    Returns:
        dict: {status: "success" | "error", result_words: str (on success), message: str (on error)}

    Side effects: none.
    """
    # Imports this function needs go here, inside it, under the docstring (e.g. from rapidfuzz import fuzz).

    if not isinstance(customer_value, str) or not customer_value.strip():
        return {"status": "error", "message": "customer_value is required"}
    async with httpx.AsyncClient(timeout=10.0) as client:   # one client for every request of this call
        for attempt in range(3):
            try:
                response = await client.post(
                    "https://api.example.com/check",
                    json={"value": customer_value},
                    headers={"Authorization": "Bearer " + x_secrets["API_KEY"]},
                )
            except httpx.RequestError as e:
                if attempt == 2:
                    logger.error(f"check_something failed: {e}")
                    return {"status": "error", "message": "service unavailable"}
                await asyncio.sleep(0.5 * 2 ** attempt)    # transient: back off and retry
                continue
            if response.status_code >= 500 and attempt < 2:
                await asyncio.sleep(0.5 * 2 ** attempt)
                continue
            if response.status_code != 200:
                return {"status": "error", "message": f"check API error: {response.status_code}"}
            return {"status": "success", "result_words": response.json().get("result_words")}
```

Drop the retry loop for a call that books, pays or sends: a retried side effect can happen twice unless the API is idempotent.

## On-connected function

```python
async def notify_crm_on_connect(ctx: JobContext, metadata: dict):
    """Tell the CRM the call has started, once, right when the call (or this capability) connects."""
    lead_id = metadata.get("lead_id")
    if not lead_id:
        return
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                "https://crm.example.com/api/call-started",
                json={"lead_id": lead_id},
                headers={"Authorization": f"Bearer {x_secrets['CRM_API_KEY']}"},
            )
    except httpx.RequestError as e:
        logger.error(f"Failed to notify CRM on connect: {e}")
```

No `RunContext`, no `ctx.session`; the return value is ignored.

## Post-call override

```javascript
async function fixFieldFromMetadata(context) {
  context.functions_called ||= [];
  context.post_call ||= {};
  context.post_call_detail ||= {};
  const log = { name: "fixFieldFromMetadata", parameters: {}, success: false, response: null, timestamp: new Date().toISOString() };
  try {
    const extracted = context.post_call.some_field;
    if (extracted === 0 || extracted === "0" || extracted === undefined) {
      const fallback = context.call_metadata?.some_field ?? null;
      context.post_call.some_field = fallback;
      context.post_call_detail.some_field = { value: fallback, comment: "replaced from metadata" };
    }
    log.success = true;
    log.response = { some_field: context.post_call.some_field };
  } catch (error) {
    log.response = error?.message || String(error);
  } finally {
    context.functions_called.push(log);
  }
}
```

## Internal metadata cleanup

```javascript
async function cleanupInternalMetadata(context) {
  context.functions_called ||= [];
  const log = { name: "cleanupInternalMetadata", parameters: {}, success: false, response: null, timestamp: new Date().toISOString() };
  try {
    const metadata = context.call_metadata || {};
    const keys = Object.keys(metadata).filter(k => k.startsWith("_"));
    keys.forEach(k => delete metadata[k]);
    log.success = true;
    log.response = { deleted: keys.length };
  } catch (error) {
    log.response = error?.message || String(error);
  } finally {
    context.functions_called.push(log);
  }
}
```

Because post-call functions can run concurrently, any function that needs an internal value reads it from `context.functions_called` instead of metadata.
