# Reference: Advanced Pre-call Protocols & Email Helpers
<!-- graph-summary: Advanced pre-call functions (the two protocols chosen by update_call_data) and the email helpers available in advanced function code. -->

Part of the [version reference](../AGENT-VERSION-REFERENCE.md) (which document a field belongs to, topic map). Field index: [field-index.md](field-index.md).

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

### Email helpers in advanced functions

Python pre-call and in-call functions receive the pre-imported `send_email` helper. It never raises
for delivery failures; await it and check `result["status"]`. The frontend supports `to` as one
address, a comma-separated string, or a list, plus optional `cc`, `bcc`, `html_body`, `reply_to`,
`from_name`, and `attachments`. Keep fixed mailbox credentials in `x_secrets`.

```python
result = await send_email(
    to=recipient_email,
    subject="Appointment confirmed",
    body="See you at 4pm.",
    username=x_secrets["SMTP_USERNAME"],
    password=x_secrets["SMTP_APP_PASSWORD"],
    reply_to=x_secrets.get("SUPPORT_EMAIL"),
    from_name="CallKaro",
)
if result["status"] != "success":
  logger.error("Email failed: %s", result["message"])
# Then follow the enclosing pre-call or in-call function's required return contract.
```

Advanced post-call JavaScript receives the pre-imported `sendEmail` helper. It always resolves to a
result object for delivery failures, so await it and check `result.status`. Record the delivery
outcome in the function's mandatory `context.functions_called` entry without logging credentials.

```javascript
const result = await sendEmail({
  to: context.call_metadata.email_id,
  subject: `Call summary for ${context.callSid}`,
  body: "Thanks for your time today.",
  username: x_secrets["SMTP_USERNAME"],
  password: x_secrets["SMTP_APP_PASSWORD"],
  replyTo: x_secrets["SUPPORT_EMAIL"],
  fromName: "CallKaro"
});
functionLog.success = result.status === "success";
functionLog.response = result.message;
```
