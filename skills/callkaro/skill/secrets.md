# Account Secrets

Use the account Secrets Vault for API keys, tokens, passwords, and other
credentials referenced by agent functions or webhook headers. Never place a
secret value in an agent JSON payload, prompt, chat message, command-line
argument, log, or generated source code.

## Commands

```bash
ck secrets list --json                    # names + masked values only
ck secrets set CRM_API_TOKEN              # hidden interactive prompt
printf '%s\n' "$VALUE" | ck secrets set CRM_API_TOKEN --stdin
ck secrets rename OLD_NAME NEW_NAME
ck secrets remove CRM_API_TOKEN           # confirms before removal
ck secrets remove CRM_API_TOKEN --yes      # non-interactive removal
```

Prefer the hidden prompt. Use `--stdin` only when the value already comes from
a protected runtime source; never put a value directly in the command or echo
it into visible output. Listing secrets never returns plaintext values.

## Authoring Workflow

Before creating or updating an agent that needs credentials:

1. Run `ck secrets list --json` and use only the returned secret names as LLM
   context. Never ask for or expose decrypted values.
2. Reuse a matching existing name when possible.
3. If no matching name exists, use a descriptive pending name such as
   `CRM_API_TOKEN`; do not invent a credential value.
4. Save the agent with the appropriate reference syntax below.
5. Report every missing name and tell the user to run `ck secrets set <name>`
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