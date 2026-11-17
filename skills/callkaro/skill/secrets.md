<!-- graph-summary: The account Secrets Vault: names-only discovery and the reference syntax for function code and webhook headers. Use whenever an integration needs an API key or token; never inline one. -->
# Account Secrets

Use the account Secrets Vault for API keys, tokens, passwords, and other
credentials referenced by agent functions or webhook headers. Never place a
secret value in an agent JSON payload, prompt, chat message, command-line
argument, log, or generated source code.

## On the dashboard

The user adds, renames and removes secrets on the CallKaro dashboard. Listing
secrets never returns plaintext values; never ask the user to paste a value
into chat.

## Authoring Workflow

Before creating or updating an agent that needs credentials:

1. Ask the user which secret names exist (the dashboard shows names and masked
   values only) and use only those names. Never ask for or expose decrypted values.
2. Reuse a matching existing name when possible.
3. If no matching name exists, use a descriptive pending name such as
   `CRM_API_TOKEN`; do not invent a credential value.
4. Save the agent with the appropriate reference syntax below.
5. Report every missing name and tell the user to add it on the dashboard
   or ask their account admin to configure it.

## Reference Syntax

Declarative function and webhook header values must be an exact reference:

```json
{ "key_name": "Authorization", "value": "x_secrets.CRM_AUTH_HEADER" }
```

Store the complete header value, including `Bearer ` when required, under
`CRM_AUTH_HEADER`. Embedded references such as
`"Bearer x_secrets.CRM_API_TOKEN"` are not resolved in declarative headers.

Advanced JavaScript and Python source code receives `x_secrets` as a runtime
object/dict. Use bracket access so names containing dashes also work:

```javascript
const token = x_secrets["CRM_API_TOKEN"];
const headers = { Authorization: `Bearer ${token}` };
```

```python
token = x_secrets["CRM_API_TOKEN"]
headers = {"Authorization": f"Bearer {token}"}
```

Do not write `x_secrets.CRM_API_TOKEN` inside source-code strings; that remains
literal text. Secret resolution is supported only in documented function
runtimes and declarative header fields, not in prompts, descriptions, URLs, or
arbitrary agent fields.