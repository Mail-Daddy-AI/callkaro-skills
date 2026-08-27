# Creating & Updating Agents

## Create

`ck agents create` takes ONE JSON object mixing agent-level + version-level
fields (the server splits them). `name` is required; `versionName` defaults to
`v1`. **The new agent is immediately published** (its first version becomes the
published version for its language).

### Recommended starter template (type 0)

```json
{
  "name": "Pricing Assistant",
  "default_agent_language": "en",
  "agentStatus": "in-progress",

  "versionName": "v1",
  "systempromptType": 0,
  "default_language": "en",
  "systemprompt": "You are Riya, a friendly sales agent for Acme. Greet {{name}} by name if provided. Explain our pricing plans clearly. If asked for discounts, explain we have none but offer a demo. Keep answers under 3 sentences. Speak naturally, never mention you are an AI unless asked directly.",

  "model": "gpt-4.1-mini",
  "secondary_model": "gpt-4.1-nano",
  "temperature": 3,

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

  "speakfirst": { "value": 1, "message_interruption": false },
  "speakfirst_inbound": { "value": 1, "message_interruption": false },
  "time_limit": 300,
  "end_call_msg": [],
  "punctuations_to_remove": [],
  "noise_cancellation": true,
  "noise_cancellation_strategy": "aicoustics",
  "noise_cancellation_strength": 1,
  "functions": [
    { "type": "end", "name": "end_call", "description": "End the call when the conversation is complete or the user asks to stop." }
  ],
  "postcall": [
    { "type": "boolean", "name": "interested", "description": "Did the customer show interest in a demo or purchase?" }
  ],
  "conversion_reason": "Customer agreed to a demo or asked for a follow-up",
  "postcallmodel": "gpt-5-nano",
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
For Hindi (or others): `default_agent_language`/`default_language`: `"hi"`,
pick a `hi` voice, transcriber language `hi` (Sarvam `saarika:v2.5` + `hi-IN`
is a strong choice), and write the prompt in the target language/register.

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

Rules:
- **Never include database-managed fields** in any payload: `_id`, `__v`,
  `createdAt`, `updatedAt`, `userId`, `agentId`. MongoDB/the server creates
  these itself — the CLI rejects them with an explanation. JSON from
  `ck agents get --json` contains them: strip before reuse, or use
  `ck agents export` (already sanitized).
- Which level a field is on: [AGENT-VERSION-REFERENCE.md](AGENT-VERSION-REFERENCE.md) §1/§17. Version fields without
  `--versions` → 400. The CLI pre-validates enums and tells you which fields
  need a version.
- **`--set` patches (merges) — it does not replace the version.** But object
  fields like `voice_configuration`, `transcriber`, `filler_config`,
  `capabilities` are replaced whole — send the complete object, not one key.
  Read-modify-write: `ck agents get <id> --versions <vid> --json`, edit, send back.
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
