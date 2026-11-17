<!-- graph-summary: Creating an agent (agent and version fields together) and changing a version through the working draft. Use when assembling a new agent's fields or editing an existing version. -->
# Creating & Updating Agents

## Create

Create the agent shell with `create_agent_in_db` (`agentName`,
`systempromptType`, `default_agent_language`), write the version fields into the
draft with `trigger_single_pipeline` (`draftPatch`), check it with
`review_draft`, then save it with `save_version_to_db` (`versionName`, usually
`v1`). The agent-level fields come from `create_agent_in_db` (name, prompt
type, language); other agent-level fields written into the draft are not saved
([editing drafts](../harness/editing-drafts.md)). **The new agent is immediately published** (its first version becomes the
published version for its language).

### From-scratch validation contract

Never send database-managed fields (`_id`, `__v`, `createdAt`, `updatedAt`,
`userId`, `agentId`); `name` is required and must be a string. The backend applies language-specific defaults **only when
`systempromptType` is explicitly `0`, `1`, `2`, or `3`**, validates the completed
version, and returns HTTP 400 with structured `errors[]` containing `path`,
`code`, and `message` for every failure.

For a new agent, always set at least `name`, `systempromptType`, and the script
fields required by that mode. Rely on the backend for ordinary runtime defaults,
but do not omit `systempromptType`: an absent or invalid value skips default
application and causes many required-field errors.

Backend-enforced creation rules:

- **Prompt mode:** Basic (`0`) needs a non-empty `systemprompt`. Advanced (`1`)
  needs non-empty `role`, `goal`, and `callFlow`, plus array-valued
  `instructions`, `guardrails`, and `rebuttals`. Multi Prompt/Pathway (`2`/`3`)
  need a non-empty `capabilities` array with unique non-empty names, string
  `system_prompt` values, boolean `is_starting` values, and exactly one starting
  capability. Pathway transitions require `condition_type` `0` or `1`, string
  conditions/targets, an existing target capability, and no self-transition.
- **Models and media:** all model IDs must exist in the account-aware catalogue
  for their category (agent, capability, filler, or post-call). Voice provider
  names must be supported; Callkaro voice `temperature` is `0`–`2`. Transcriber
  provider/model/language/mode/format and whether language is a string or array
  must match the provider catalogue. Realtime LLMs require an Open AI voice.
  Use [AGENT-VERSION-REFERENCE.md](AGENT-VERSION-REFERENCE.md) §7 or an existing
  account-approved agent for model IDs; discover voices with `list_voices` (load
  the voices tools) and take transcriber values from reference §10. Never invent
  catalogue values.
- **Core shapes and ranges:** `versionName` must be non-empty; language is one of
  `en hi kn mr ta te bn gu ml`; top-level `temperature` is `0`–`10`;
  `time_limit` and `hold_disconnect_timeout` are greater than `0`;
  `bgNoiseVolume` is `0`–`1`; `noise_cancellation_strength` is `0.05`–`1`;
  initial pauses and silence values are non-negative. `speakfirst` and
  `speakfirst_inbound` use value `0`, `1`, or `2`; value `2` requires a non-empty
  `customMsg`. A custom silence mode requires at least one non-empty silence
  prompt. `silence_instructions` only takes effect when `silence_mode` is
  `dynamic` or `ignore`; leave it unset unless the user asks for it. Webhooks
  must be empty or valid URLs.
- **Nested records:** function `type`/`name`, HTTP method, parameters, headers,
  conditions, and execution-message shape are validated. Warm transfer requires
  a non-empty `warm_transfer_prompt`. Static switch messages must be non-empty.
  Post-call fields require a trimmed name, description, supported type, correctly
  typed default, and a valid default-value source. Filler settings, pre-format
  values, variable sources, call-property mappings, knowledge IDs, and post-call
  strategy bucket/model names are also validated.

These are save-time validity rules, not the complete authoring schema. Before
constructing non-trivial nested fields, use
[AGENT-VERSION-REFERENCE.md](AGENT-VERSION-REFERENCE.md) for exact enums and
provider-specific shapes.

### Recommended production-safe starter template (type 0)

This is intentionally explicit even though create-time defaults fill many of
these fields. It gives a new agent predictable call behavior and makes later
reviews and updates easier. Replace the example prompt, post-call field, and
catalogue-backed voice values for the use case. Do not copy phone assignments,
A/B rules, IDs, customer-specific prompts/functions, or credentials from a
production export.

```json
{
  "name": "Pricing Assistant",
  "default_agent_language": "en",
  "agentStatus": "in-progress",

  "versionName": "v1",
  "systempromptType": 0,
  "default_language": "en",
  "systemprompt": "You are Riya, a friendly sales agent for Acme. Greet {{name}} by name if provided. Explain our pricing plans clearly. If asked for discounts, explain we have none but offer a demo. Keep answers under 3 sentences. Speak naturally, never mention you are an AI unless asked directly.",

  "model": "callkaro/arjuna-2.5",
  "secondary_model": "gpt-5.4-nano",
  "temperature": 3,
  "caching_strategy": "response",
  "insert_metadata_in_prompt": true,

  "voice_configuration": {
    "voice_provider": "Eleven Labs",
    "voice_name": "<from list_voices>",
    "voice_id": "<from list_voices>",
    "voice_model": "eleven_flash_v2_5",
    "voice_language": "en",
    "voice_speed": 1.0,
    "voice_stability": 0.5,
    "voice_similarity_boost": 1,
    "voice_style": 0.5,
    "voice_category": "professional"
  },
  "transcriber": {
    "transcriber_provider": "Deepgram",
    "transcriber_model": "nova-3",
    "transcriber_language": "en",
    "transcriber_language_detection": false
  },

  "speakfirst": { "value": 1, "message_interruption": false },
  "speakfirst_inbound": { "value": 1, "message_interruption": false },
  "initial_pause_outbound": 1,
  "initial_pause_inbound": 1,
  "time_limit": 300,
  "hold_disconnect_timeout": 30,
  "silence_count": 2,
  "silence_wait": 6,
  "silence_mode": "default",
  "silence_prompts": [],
  "silence_instructions": null,
  "silence_language": "en",
  "end_call_msg": ["Thank you for your time, have a good day."],
  "bgNoise": true,
  "bgNoiseVolume": 0.2,
  "voicemail_msg": true,
  "voicemail_custom_msg": "",
  "punctuations_to_remove": [],
  "noise_cancellation": true,
  "noise_cancellation_strategy": "aicoustics",
  "noise_cancellation_strength": 1,
  "functions": [],
  "postcall": [
    {
      "type": "boolean",
      "name": "interested",
      "description": "Did the customer show interest in a demo or purchase?",
      "defaultValue": false,
      "defaultValueConfig": { "source": "static_value", "key": "", "other": false }
    }
  ],
  "conversion_reason": "Customer agreed to a demo or asked for a follow-up",
  "postcallmodel": "callkaro/krishna-2.5",
  "post_call_strategy": {
    "1-10": "callkaro/krishna-2.5",
    "11-30": "callkaro/krishna-2.5",
    "31-60": "callkaro/krishna-2.5",
    ">60": "callkaro/krishna-2.5",
    "only_agent_turns": "DEFAULT_VALUES"
  },
  "secondary_post_call_strategy": {
    "1-10": "gpt-5.4-nano",
    "11-30": "gpt-5.4-nano",
    "31-60": "gpt-5.4-nano",
    ">60": "gpt-5.4-nano",
    "only_agent_turns": "DEFAULT_VALUES"
  },
  "webhook": "",
  "webhook_headers": []
}
```

The call ends when the agent speaks a line listed in `end_call_msg`, so the example has no `end` function. Prefer `end_call_msg` over the `end` function; the prompt's closing lines must match these entries exactly.

Workflow: `list_voices` first to fill `voice_name`/`voice_id`; then
`create_agent_in_db`, `trigger_single_pipeline` with these fields as `draftPatch`,
`review_draft` and `save_version_to_db`; `list_versions` gives the version id for
simulations and publishing.

For Hindi (or another language), set the language in `create_agent_in_db` and
`default_language` and `silence_language` in the draft, together; resolve a matching voice
with `list_voices` and a transcriber from reference §10; and write the spoken lines and
fixed messages in the target language/register, the instructions in English
([prompt style](../writing/prompt-style.md)).

## Update

Load the version into the draft with `read_agent_state` (omit `versionId` for
the published one). Write the changed version fields with
`trigger_single_pipeline`: `draftPatch` for fields (e.g.
`{"systemprompt":"...","temperature":4}`), `edits` for one snippet. For a change
repeated across many nodes, functions or fields use `edit_draft_script`. Then
`review_draft` and `save_version_to_db`. `agentStatus` (`live` / `in-progress`)
is set with `manage_version_publishing` (`set_status`).

Webhook headers are version-level fields. For example, the draft fields can be:

```json
{
  "webhook": "https://api.example.com/call-ended",
  "webhook_headers": [
    { "key_name": "Authorization", "value": "x_secrets.CRM_AUTH_HEADER" }
  ]
}
```

Use non-sensitive literals directly and exact `x_secrets.NAME` values for credentials. Reuse an
existing secret name when one matches (secrets are listed and set on the CallKaro dashboard). After
saving, report each missing secret name and direct the user to
`https://callkaro.ai/dashboard/settings/secrets` or their admin.

Noise cancellation and transcription cleanup are also version-level fields:

```json
{
  "punctuations_to_remove": ["...", "—"],
  "noise_cancellation": true,
  "noise_cancellation_strategy": "aicoustics",
  "noise_cancellation_strength": 0.8
}
```

`punctuations_to_remove` is an array of exact strings removed from caller
transcriptions before processing. Noise-cancellation strength is `0.05`–`1`;
the strategy is `aicoustics`, `dtln`, `deepfilternet`, or `noisereduce`.

Rules:

- **Never include database-managed fields** in any payload: `_id`, `__v`,
  `createdAt`, `updatedAt`, `userId`, `agentId`. MongoDB/the server creates
  these itself. A version read back contains them: strip them before reusing
  it as a body.
- Which level a field is on: [AGENT-VERSION-REFERENCE.md](AGENT-VERSION-REFERENCE.md) §1/§17. Version fields without
  a version id → 400. `trigger_single_pipeline` validates the fields you write.
- **A `draftPatch` merges — it does not replace the version.** Objects such as
  `voice_configuration`, `transcriber`, `filler_config` are merged key by key, so
  a key cannot be removed that way (write the whole object with an `edits` `set`);
  arrays such as `capabilities` and `functions` are replaced whole. Read the
  current value from the draft (`read_version`), edit, write it back.
- A capability/node's `endpointing` is also one complete object. To change one nested
  value, read the current `{mode, min_delay, max_delay}`, modify only the requested
  value, and send all three back while preserving every other capability field.
- `temperature` is 0–10 (stored ×10). `time_limit` must be non-zero.
- Every version save records a commit snapshot (like a git commit), so changes
  are auditable/revertable in the dashboard.
- Changing a published version would change **live behavior**, so
  `save_version_to_db` always saves a published base as a new version, never
  over it. Publish or A/B the new version when it is ready (see
  [versions.md](versions.md)).

## Export / Import (cloning & templates)

Export and import are done on the CallKaro dashboard. Exports are sanitized (ids, publish state, phone assignments stripped) and get
an `x_agent_id` ownership marker; `whatsapp*` functions survive import only for
the same owner. An exported ARRAY imports as one agent with several versions. To use another
agent's version only as structural inspiration here, call `read_agent_state` with
`useAsTemplate` (it returns a structural view and loads nothing).
