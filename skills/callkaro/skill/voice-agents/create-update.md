# Creating & Updating Agents
<!-- graph-summary: Create, update, export and import agents with the ck CLI: the validation contract, a safe type-0 starter template, version-level versus agent-level patches, and cloning. -->

## Create

`ck agents create` takes ONE JSON object mixing agent-level + version-level
fields (the server splits them). `name` is required; `versionName` defaults to
`v1`. **The new agent is immediately published** (its first version becomes the
published version for its language).

### From-scratch validation contract

Creation has two validation layers. The CLI first rejects non-object/array JSON,
database-managed fields (`_id`, `__v`, `createdAt`, `updatedAt`, `userId`,
`agentId`), and a missing/non-string `name`; it supplies `versionName: "v1"` when
omitted. The backend then applies language-specific defaults **only when
`systempromptType` is explicitly `0`, `1`, `2`, or `3`**, validates the completed
version, and returns HTTP 400 with structured `errors[]` containing `path`,
`code`, and `message` for every failure.

For a new agent, always send at least `name`, `systempromptType`, and the script
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
  Use [llm-and-postcall.md](reference/llm-and-postcall.md) §7 or an existing
  account-approved agent for model IDs; discover media values with
  `ck voices --json` and `ck transcribers`. Never invent catalogue values.
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
[AGENT-VERSION-REFERENCE.md](AGENT-VERSION-REFERENCE.md) to find the topic node for exact enums and
provider-specific shapes.

### Recommended production-safe starter template (type 0)

This is intentionally explicit even though create-time defaults fill many of
these fields. Its values are the ones in [recommended-settings.md](recommended-settings.md); take
any field it doesn't set from there, and keep the two in step. It gives a new agent predictable call behavior and makes later
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
    "voice_name": "<from ck voices>",
    "voice_id": "<from ck voices>",
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

  "speakfirst": { "value": 1, "message_interruption": true },
  "speakfirst_inbound": { "value": 1, "message_interruption": false },
  "initial_pause_outbound": 1,
  "initial_pause_inbound": 1,
  "time_limit": 300,
  "hold_disconnect_timeout": 30,
  "silence_count": 2,
  "silence_wait": 8,
  "silence_mode": "dynamic",
  "silence_prompts": [],
  "silence_instructions": "The user has been silent after your last response. Generate a brief reply to check if the user is still there on the call.",
  "silence_language": "en",
  "end_call_msg": [],
  "bgNoise": true,
  "bgNoiseVolume": 0.2,
  "voicemail_msg": false,
  "voicemail_custom_msg": "",
  "punctuations_to_remove": [],
  "noise_cancellation": true,
  "noise_cancellation_strategy": "aicoustics",
  "noise_cancellation_strength": 0.8,
  "vad_configuration": {
    "silence": 555,
    "threshold": 4,
    "prefix_padding_ms": 206,
    "min_speech_duration": 0.05,
    "interrupt_speech_duration": 0.4,
    "interrupt_min_words": 3,
    "manual_interruption": true,
    "manual_interruption_duration": 1.1,
    "clear_buffer_if_not_interrupted": false,
    "max_buffered_speech": 10,
    "min_endpointing_delay": 0.3,
    "max_endpointing_delay": 5,
    "preemptive_synthesis": true
  },
  "functions": [
    { "type": "end", "name": "end_call", "description": "End the call when the conversation is complete or the user asks to stop." }
  ],
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
    "1-10": "DEFAULT_VALUES",
    "11-30": "callkaro/krishna-2.5",
    "31-60": "callkaro/krishna-2.5",
    ">60": "callkaro/krishna-2.5",
    "only_agent_turns": "DEFAULT_VALUES"
  },
  "secondary_post_call_strategy": {
    "1-10": "DEFAULT_VALUES",
    "11-30": "gpt-6-luna",
    "31-60": "gpt-6-luna",
    ">60": "gpt-6-luna",
    "only_agent_turns": "DEFAULT_VALUES"
  },
  "webhook": "",
  "webhook_headers": []
}
```

Workflow:

```bash
ck voices --language en --json          # fill voice_name/voice_id first
ck agents create --file agent.json      # returns the new agent id
ck agents versions <agentId> --json     # version id for sim/publish
```

For Hindi (or another language), change `default_agent_language`,
`default_language`, and `silence_language` together; resolve a matching voice
and transcriber from `ck voices` / `ck transcribers`; and write the prompt and
fixed spoken messages in the target language/register.

## Update

```bash
# agent-level fields — no --versions:
ck agents update <agentId> --set '{"name":"New Name","agentStatus":"live"}'

# version-level fields — --versions REQUIRED:
ck agents update <agentId> --versions <vid> \
  --set '{"systemprompt":"...","temperature":4}' --commit "tighten prompt"

# big patches from a file:
ck agents update <agentId> --versions <vid> --set @patch.json --commit "rework"
```

Webhook headers are version-level fields. For example, `patch.json` can contain:

```json
{
  "webhook": "https://api.example.com/call-ended",
  "webhook_headers": [
    { "key_name": "Authorization", "value": "x_secrets.CRM_AUTH_HEADER" }
  ]
}
```

Use non-sensitive literals directly and exact `x_secrets.NAME` values for credentials. Run
`ck secrets list --json` before authoring the payload so existing names can be reused. After saving,
report each missing secret name and direct the user to `ck secrets set <name>`,
`https://callkaro.ai/dashboard/settings/secrets`, or their admin.

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

### Update only what was asked (minimal patches)

An update must contain **only the fields the user asked to change**. Every extra field is a chance to
overwrite a value that was chosen on purpose, and a live agent's quality depends on them.

- **Never send back the output of `ck agents get`** (or a whole export) as the patch. Build the patch
  from scratch with just the requested keys.
- **Never reset other fields to the recommended values** in [recommended-settings.md](recommended-settings.md)
  while making an unrelated change. That page is for creating agents, filling the missing keys of a
  whole object, and reviewing. Mention differences to the user instead.
- **Whole-replace objects** (`voice_configuration`, `secondary_voice_configuration`, `transcriber`,
  `secondary_transcriber`, `agentMemory`, `preFormatVariables`, `customPronunciations`, `variableSource`,
  `callPropertyMapping`, `callFlow_json`): the backend replaces the whole object. The CLI now merges a
  partial object onto the saved one before sending, but still send only the keys you are changing and
  never delete siblings. Prefer `ck agents memory` / `ck agents voice-rotation` for `agentMemory`.
- **One concern per update and per `--commit`** (for example "tighten the prompt" or "raise silence
  wait", not both).
- **Preview first:** run the same command with `--dry-run`. It lists the fields that would change and
  those already set (skipped) and saves nothing. Check the list matches the request, then run it for
  real.
- **The CLI stops big patches.** Fields that already hold the requested value are dropped automatically.
  If more than 8 fields would still change, it refuses unless you add `--yes`. Treat that refusal as a
  sign the patch is too big: trim it, and add `--yes` only when the user really asked for that many
  changes.

Rules:

- **Never include database-managed fields** in any payload: `_id`, `__v`,
  `createdAt`, `updatedAt`, `userId`, `agentId`. MongoDB/the server creates
  these itself — the CLI rejects them with an explanation. JSON from
  `ck agents get --json` contains them: strip before reuse, or use
  `ck agents export` (already sanitized).
- Which level a field is on: [AGENT-VERSION-REFERENCE.md](AGENT-VERSION-REFERENCE.md) §1 and [field-index.md](reference/field-index.md). Version fields without
  `--versions` → 400. The CLI pre-validates enums and tells you which fields
  need a version.
- **`--set` patches (merges) — it does not replace the version.** But object
  fields like `voice_configuration`, `transcriber`, `filler_config`,
  `capabilities` are replaced whole — send the complete object, not one key.
  Read-modify-write: `ck agents get <id> --versions <vid> --json`, edit, send back.
- A capability/node's `endpointing` is also one complete object. To change one nested
  value, read the current `{mode, min_delay, max_delay}`, modify only the requested
  value, and send all three back while preserving every other capability field.
- `temperature` is 0–10 (stored ×10). `time_limit` must be non-zero.
- Always pass `--commit "why"` on version changes — it snapshots the version
  (like a git commit) so changes are auditable/revertable in the dashboard.
- Changing a published version changes **live behavior** — for experiments,
  create a new version instead (see [versions.md](versions.md)) and A/B it.

## Export / Import (cloning & templates)

```bash
ck agents export <agentId> --versions <vid> --file template.json
ck agents import template.json --dry-run      # validate only
ck agents import template.json                # create the clone
```

Exports are sanitized (ids, publish state, phone assignments stripped) and get
an `x_agent_id` ownership marker; `whatsapp*` functions survive import only for
the same owner. An exported ARRAY imports as one agent with several versions.
