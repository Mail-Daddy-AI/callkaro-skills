# Verifying a Built or Updated Agent
<!-- graph-summary: Check a built or updated agent before publishing: does it deliver the request, update-without-damage rules, and function review (duplicates, scope, credentials, transfer fields, fix in place or redo). -->

Run this after every create or update, before you publish. The field-level pre-flight checklist is
[AGENT-VERSION-REFERENCE.md](AGENT-VERSION-REFERENCE.md) §19. This file checks the other half: did
the version do what the user asked, and are the functions right. Behaviour is then tested with
[simulations](../simulations/simulation-playbook.md).

Read the version back first: `ck agents get <agentId> --versions <vid> --json`.

## 1. Did it deliver the request?

List every explicit request from the conversation. A later message overrides an earlier one on the
same topic, and anything the user retracted is dropped. Then check each against the version:

| Request | Check |
|---|---|
| "Create a [domain] agent" | The script clearly matches the domain, and the functions it implies exist (booking, transfer, end call, lookup, data capture). |
| "Speak [language]" | `default_language`, the script's language and script, voice and transcriber all match. |
| "Add a [function]" | It exists in `functions[]`, or in the right `capabilities[i].functions[]`. |
| "Extract whether the customer was interested / booked" | A matching post-call variable exists, and `post_call_analysis_prompt` is non-empty where needed. |
| "Change X to Y" | The new text is present and the old text is gone. |
| "Remove X" | X is absent from the final version. |
| "Add or update capability X" (type 2) | It exists in `capabilities[]` with a non-empty `system_prompt` that reflects the change. |
| "Set model / temperature / voice / transcriber" | The right field changed. Temperature is stored 0–10, so 0.9 is stored as 9; that is correct. |
| "Don't change X" | X is identical to the previous version. |

Type 2: exactly one capability has `is_starting: true`, and every capability has a non-empty
`system_prompt`.

Consistency, not wording: functions, post-call variables, capabilities and call parameters must still
agree with the final script. Only call a script problem real with positive evidence, such as an empty
required field, requested text still present, new text missing, or a visible change nobody asked for.
A truncated diff you can't verify is inconclusive, not a failure.

**Provider changes:** when the transcriber provider or model changed, `transcriber_language` is
allowed to change with it, because language codes differ per provider. Check it against the new
provider's format (for example `en-IN` for Azure) instead of against the old version.

## 2. Updating without damaging

- Change only what was asked, and leave every other field as it was.
- Keep the existing format and style: same headers, delimiters, dialogue format and tone.
- Keep the agent name, brand and persona exactly, unless the user asked to change identity.
- Keep custom placeholders (`<car details here>`, `[INSERT PRICE]`) as the user wrote them, and don't
  convert them to `{{variable}}` syntax.
- If a language-bearing field no longer matches the target language (a Hindi script with
  `default_language: "en"`), correct it.

## 3. Reviewing functions

For every scope you touched (version level and each capability):

1. **Duplicates:** two functions with the same name in one scope is a failure. Remove one.
2. **Plan items:** created functions exist with the right name, type and fields, updated ones carry
   the change, and deleted ones are gone.
3. **Scope:** a function missing from the capability that needs it is a failure even if it exists
   globally.
4. **Quality:**
   - Type, name and description match the request, and `description` reads as a trigger condition.
   - No hardcoded, dummy or placeholder credential; fixed credentials use a descriptive `x_secrets`
     reference. A placeholder non-secret URL is fine and is never grounds to reject.
   - Pre-call: `update_call_data` is a boolean and matches the signature (`false` →
     `(metadata, system_prompt) -> str`; `true` → `(call_data)`).
   - In-call and post-call code follows [function-code.md](function-code.md).
   - Transfer: `warm_transfer` is present (true or false); if true, `warm_transfer_prompt` is
     non-empty; if the user asked for a message while connecting, `msg_while_executing` is a
     non-empty array.
   - If email was requested, the code uses `send_email` or `sendEmail`, awaits it and checks the
     result status.

**Fix in place or redo?** Delete and recreate when the type is wrong, the purpose is wrong, it is a
duplicate, or the code is broken beyond a targeted fix. Fix in place when the name and type are right
and one detail is wrong (a URL, a field, a missing condition). Whichever you pick, write the
correction as one self-contained instruction (name, scope and every detail), because it may be read
without the rest of the conversation.
