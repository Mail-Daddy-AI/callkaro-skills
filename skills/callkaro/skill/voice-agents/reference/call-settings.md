# Reference: Call Initiation, Behaviour & Call Settings
<!-- graph-summary: Field reference for opening and ending a call (speakfirst, end_call_msg, time limits), silence, language switching, gender and VAD, and call settings (noise, voicemail, DTMF, transfers, webhook). -->

Part of the [version reference](../AGENT-VERSION-REFERENCE.md) (which document a field belongs to, topic map). Field index: [field-index.md](field-index.md).

## 11. Call initiation & termination

| Field | Type / default | Meaning |
| --- | --- | --- |
| `speakfirst` | `{value, customMsg, message_interruption}`, default `{value: 1, message_interruption: false}` | **Outbound.** `value: 0` = the caller speaks first (agent silent until spoken to); `1` = the agent opens with a **dynamic** greeting generated from the prompt; `2` = the agent opens with `customMsg` **verbatim** (supports `{{variables}}`). `message_interruption` = may the caller talk over the opening line. `customMsg` only matters when `value: 2`. |
| `speakfirst_inbound` | same shape | **Inbound** equivalent. Inbound often wants `0` (traditional phone behaviour). |
| `initial_pause_outbound` | int seconds, `1` | Delay before the agent speaks on outbound — a small pause avoids clipping the connect tone. |
| `initial_pause_inbound` | int seconds, `1` | Same for inbound. |
| `end_call_msg` | string[], `[]` | See [§3](script-and-types.md) — uttering one of these **ends the call**. |
| `hold_disconnect_timeout` | int seconds, `30` | How long to wait before disconnecting a held/stalled call. |
| `time_limit` | int seconds, `300` | Hard cap on total call duration. |

---

## 12. Agent behaviour — silence, language switching, gender, VAD

| Field | Type / default | Meaning |
| --- | --- | --- |
| `silence_wait` | int, `6` | Seconds of caller silence before the agent says a silence prompt. |
| `silence_count` | int, `2` | How many times the silence prompt repeats before the call ends. |
| `silence_mode` | `default` \| `custom` \| `dynamic` \| `ignore`, `default` | `default` = platform prompts; `custom` = pick from `silence_prompts`; `dynamic` = the model generates one from context; `ignore` = never re-prompt on silence. |
| `silence_prompts` | string[], `[]` | Used when `silence_mode: "custom"`. |
| `silence_instructions` | string \| null, `null` | Instructions for how the agent should behave when the caller is silent. Used only when `silence_mode` is `dynamic` or `ignore`. Optional — leave unset unless the user asks for it. |
| `silence_language` | enum + `multi`, `en` | Language of those prompts. |
| `language_switching` | bool, `false` | Switch language based on the caller's **last message** (reactive, no confirmation). Makes the agent SPEAK a different language mid-call while staying on this SAME version/script — no transfer. Do not confuse with `switchableLanguages` ([§14](variables-memory-whatsapp.md)), which hands the call off to a DIFFERENT PUBLISHED VERSION authored in that language. |
| `language_switching_instructions` | string \| null, `null` | Instructions for how the agent should switch language mid-call. Used only when `language_switching` is true. Optional — leave unset unless the user asks for it; the platform falls back to a built-in multilingual detection prompt. |
| `language_lockin_time` | number \| null, `null` | Seconds to lock onto a language after switching, before switching again. Used only when `language_switching` is true. |
| `allowed_languages` | string[], `[]` | Whitelist of languages the agent may switch into. Empty means unrestricted. Used only when `language_switching` is true. |
| `language_switch_min_words` | int, `3` | Minimum caller words required before a switch triggers. Used only when `language_switching` is true. |
| `language_switching_v1` | bool, `false` | Switch language only after the caller's **explicit consent/request**. Pair either flag with `language_switch_snippet` and `switchableLanguages`. |
| `detect_gender` | bool, `false` | Detect the caller's gender from audio and adapt address forms. |
| `gender_prompt_snippet` | string \| null | Prompt injected when `detect_gender` is on. |
| `formatToNumberAsIndian` | bool, `false` | Speak/format numbers in the Indian system (lakh/crore, Indian digit grouping). |

**`vad_configuration`** — voice-activity / barge-in / endpointing tuning. Treat it as
**system-owned**: leave it out unless the user explicitly asks to tune interruption behaviour, and
change one field at a time. Fields, ranges and platform defaults:

| Field | Range | Default | Effect |
| --- | --- | --- | --- |
| `silence` | 0–10000 ms | `288` | Silence needed to decide the caller stopped speaking. |
| `threshold` | 0–10 | `3` | Speech-activation sensitivity. Lower = more sensitive to quiet speech and to noise. |
| `prefix_padding_ms` | 0–10000 ms | `200` | Audio kept before detected speech starts, so the first syllable isn't clipped. |
| `min_speech_duration` | 0–0.1 s | `0.01` | Minimum speech length that counts as a new utterance (filters coughs/clicks). |
| `interrupt_speech_duration` | seconds | `0.5` | How long the caller must speak to interrupt the agent. |
| `interrupt_min_words` | 0–4 | `3` | Minimum words required to interrupt — raise it when "hmm"/"haan" keeps cutting the agent off. |
| `clear_buffer_if_not_interrupted` | bool | `true` | Discard buffered caller audio that didn't amount to an interruption. |
| `manual_interruption` | bool | `true` | Enable the explicit interruption path. |
| `manual_interruption_duration` | 0–10 s | `1.6` | Speech duration for that path. |
| `max_buffered_speech` | 0–100 s | `5` | Cap on buffered caller speech. |
| `min_endpointing_delay` | 0–1 s | `0.5` | Minimum wait before treating the turn as finished. |
| `max_endpointing_delay` | 0–10 s | `6` | Maximum wait before force-ending the turn. |
| `preemptive_synthesis` | bool | `true` | Start synthesising the reply before the turn is fully closed (lower latency). |

---

## 13. Call settings

| Field | Type / default | Meaning |
| --- | --- | --- |
| `bgNoise` | bool, `true` | Ambient office noise so the line sounds human rather than studio-silent. |
| `bgNoiseVolume` | 0–1, `0.2` | Volume of that ambience. |
| `noise_cancellation` | bool, `true` | Suppress the **caller's** background noise before transcription. |
| `noise_cancellation_strategy` | `aicoustics` \| `dtln` \| `deepfilternet` \| `noisereduce`, `aicoustics` | Which denoiser to use. `aicoustics` is shown as CallKaro in the UI. |
| `noise_cancellation_strength` | 0.05–1, `1` | Strength of caller-noise reduction; used when noise cancellation is enabled. |
| `punctuations_to_remove` | string[], `[]` | Exact strings removed from caller transcriptions before they are processed. |
| `voicemail_msg` | bool, `true` | Leave a message when the call lands on voicemail. |
| `voicemail_custom_msg` | string, `""` | The message. **Empty = dynamic voicemail message** (generated from the prompt); non-empty = that exact text (supports `{{variables}}`). This single field encodes the "dynamic vs custom" choice the UI shows. |
| `dtmf_collection_enabled` | bool, `false` | Let the agent collect fixed-length digits (OTP, PIN, pincode) from the keypad. The prompt must also instruct the agent to call `collect_digits_via_dtmf` with the expected digit count. UI-exposed — check [§18](../AGENT-VERSION-REFERENCE.md). |
| `auto_reschedule` | bool, `false` | Automatically reschedule when the caller says they're busy or asks for a callback. |
| `rescheduling_prompt` | string \| null | How the agent should pick the new time. |
| `rescheduled_follow_up_prompt` | string \| null | Extra prompt used **on** the rescheduled call so it carries context from the previous one. |
| `followup` | bool, `false` | Adapt the call flow using previous conversation history with this contact. |
| `followup_prompt` | string \| null | Instructions for building that follow-up flow. |
| `warm_transfer` / `warm_transfer_prompt` | bool `false` / string \| null | Version-level warm transfer. On types 0–2 these normally live on the `transfer` function; on type 3 they are lifted to version level at save ([§6](functions-reference.md)). |
| `webhook` | string URL, `""` | Version-level webhook receiving the call-ended payload. |
| `webhook_headers` | `[{key_name, value}]`, `[]` | Optional headers sent with the webhook. `value` is either a non-sensitive literal or an exact `x_secrets.NAME` reference. |
| `time_limit`, `hold_disconnect_timeout` | see §11 | Duration caps. |

Webhook header example:

```json
{
  "webhook": "https://api.example.com/call-ended",
  "webhook_headers": [
    { "key_name": "Authorization", "value": "x_secrets.CRM_AUTH_HEADER" },
    { "key_name": "Content-Type", "value": "application/json" }
  ]
}
```

Run `ck secrets list --json` before authoring sensitive headers and reuse matching names. Use exact
`x_secrets.NAME` values for API keys, tokens, passwords, and other credentials; never place their
literal values in an agent payload or chat. The saved secret must contain the complete header value
expected by the destination, including `Bearer ` when required. After every successful create or
update, report each missing name and tell the user to run `ck secrets set <name>`, add it at
`https://callkaro.ai/dashboard/settings/secrets`, or ask their admin to update the registry. See
[../secrets.md](../../secrets.md) for source-code syntax and the full workflow.
