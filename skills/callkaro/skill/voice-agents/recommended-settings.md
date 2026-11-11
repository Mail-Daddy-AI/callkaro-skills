# Recommended Voice Agent Settings
<!-- graph-summary: The recommended value of every voice-agent setting (language and silence, VAD, interruption, endpointing, LLM, voice, transcriber, filler, call start/end, call settings, call memory, post-call strategy) with its field name, and the rules for using them: fill them on create, keep them when re-sending a whole object, never push them onto a live agent unasked. -->

The values Callkaro recommends for a production voice agent. Use this page to **fill a new agent**,
to **fill the gaps when you must re-send a whole object**, and to **report deviations** when reviewing
an agent.

## How to use this page (read first)

- **Recommended is not "apply on update".** When the user asks for one change, change that one field.
  Never "tidy" other fields to match this page, even if they differ. A live agent's values were chosen
  for its use case; resetting them degrades the bot.
- **Create:** start from the [starter template](create-update.md) and take any field it doesn't set
  from here.
- **Whole-object fields** (`voice_configuration`, `transcriber`, `agentMemory`, `vad_configuration`
  and the others in [create-update.md](create-update.md)): read the current value, change only the
  requested key, send the complete object. If a sibling key is missing from the current value, use the
  value below, never an invented one.
- **Review:** list differences from this page as suggestions. Change them only if the user says so.
- **"As per agent/version"** means it depends on the use case, language or customer: **never set it
  unless the user asked**, and never copy it from another agent.
- Values are in the units the API stores. Where the dashboard shows a different scale, both are given.

## Language and silence

| Setting | Field | Recommended |
| --- | --- | --- |
| Default language | `default_language` | Depends on the version |
| Silence Message Count | `silence_count` | 2 |
| Wait till User Reply | `silence_wait` | 8 (seconds) |
| Silence Message Language | `silence_language` | The version's language |
| Silence Mode | `silence_mode` | `dynamic` |
| Silence Instructions | `silence_instructions` | "The user has been silent after your last response. Generate a brief reply to check if the user is still there on the call." |
| Silence Prompts (fixed lines) | `silence_prompts` | Only used when the mode is not `dynamic`. Per agent/version |
| Detect Gender | `detect_gender` | Off |
| Gender Detection Delay | `gender_detection_delay` | 30 (seconds). Only when Detect Gender is on |
| Gender Prompt Snippet | `gender_prompt_snippet` | Per agent/version. Only when Detect Gender is on |
| Language Switching | `language_switching` | Off |
| Language Switching V1 | `language_switching_v1` | Off. Legacy option |
| Switch Min Words, Lock-in Time, Allowed Languages, Instructions | | Per agent/version. Only when Language Switching is on |

## Voice detection (VAD) — `vad_configuration`

| Setting | Key | Recommended |
| --- | --- | --- |
| Silence Duration | `silence` | 555 (ms) |
| Threshold | `threshold` | 4 (the dashboard shows 0.4; stored ×10) |
| Prefix Padding | `prefix_padding_ms` | 206 (ms) |
| Minimum Speech Duration | `min_speech_duration` | 0.05 (s) |

## Interruption — `vad_configuration`

| Setting | Key | Recommended |
| --- | --- | --- |
| Interrupt Speech Duration | `interrupt_speech_duration` | 0.4 (s) |
| Interrupt Min Words | `interrupt_min_words` | 3 |
| Manual Interruption | `manual_interruption` | On |
| Manual Interruption Speech Duration | `manual_interruption_duration` | 1.1 (s) |
| Clear Buffer If Not Interrupted | `clear_buffer_if_not_interrupted` | Off |

## Endpointing and response — `vad_configuration`

| Setting | Key | Recommended |
| --- | --- | --- |
| Max Buffered Speech | `max_buffered_speech` | 10 (s) |
| Min Endpointing Delay | `min_endpointing_delay` | 0.3 (s) |
| Max Endpointing Delay | `max_endpointing_delay` | 5 (s) |
| Preemptive Synthesis | `preemptive_synthesis` | On |

## LLM model

| Setting | Field | Recommended |
| --- | --- | --- |
| Primary LLM Model | `model` | Arjuna 2.5 for single prompt, Arjuna 3.5 beta for multi prompt (ids: [llm-and-postcall.md](reference/llm-and-postcall.md) §7) |
| Primary LLM Temperature | `temperature` | 3 (dashboard 0.3; stored ×10) |
| Secondary LLM Model | `secondary_model` | A model from a different provider than the primary; balance performance and cost |
| Secondary LLM Temperature | | 0.3 |

## Voice

| Setting | Field | Recommended |
| --- | --- | --- |
| Provider, Name/ID, Category, Model, Language (primary and secondary) | `voice_configuration`, `secondary_voice_configuration` | Per agent/version (language and voice). Pick real ones with `ck voices` |
| Primary Voice Stability | `voice_stability` | 0.5 |
| Primary Voice Similarity Boost | `voice_similarity_boost` | 1 |
| Primary Voice Style | `voice_style` | 0.5 |
| Primary Voice Speed | `voice_speed` | 1 |
| Secondary Voice Provider | | A different provider from the primary |
| Secondary Voice Pitch | `voice_pitch` | 0.5 |
| Secondary Voice Speed | `voice_speed` | 1 |
| Secondary Voice Emotions | | Per agent/version |

## Transcriber

| Setting | Field | Recommended |
| --- | --- | --- |
| Use Multiple Transcribers | `useMultiTranscribers` | Off |
| Primary Transcriber | `transcriber` | Soniox, languages for the use case, without any context |
| Primary Transcriber Languages | | Per agent/version |
| General Context, Text Context, Translation Terms | | None |
| Keywords | | Per agent/version (maximum 20) |
| Secondary Transcriber | `secondary_transcriber` | Sarvam, languages for the use case, without any context |
| Secondary Model, Language, Prompt, Mode | | Per agent/version |

## Filler

| Setting | Field | Recommended |
| --- | --- | --- |
| Filler Phrase Type | `filler_config.filler_type` | `none` |
| Filler Model, Filler Temperature | | Only when the type is not `none` |

## Call start and end

| Setting | Field | Recommended |
| --- | --- | --- |
| Call Initiation (outbound) | `speakfirst.value` | AI initiates with a dynamic begin message |
| Initial delay before AI speaks (outbound) | `initial_pause_outbound` | 1 (second) |
| Allow initial message interruption (outbound) | `speakfirst.message_interruption` | On |
| Custom Message (outbound) | `speakfirst.customMsg` | Only when outbound initiation is custom. Per agent/version |
| Call Initiation (inbound) | `speakfirst_inbound.value` | AI initiates with a custom begin message |
| Custom Message (inbound) | `speakfirst_inbound.customMsg` | Per agent/version (greeting in the version's language) |
| Initial delay before AI speaks (inbound) | `initial_pause_inbound` | 1 (second) |
| Allow initial message interruption (inbound) | `speakfirst_inbound.message_interruption` | Off |
| End Call Messages | `end_call_msg` | Per use case and agent/version (language) |

## Call settings

| Setting | Field | Recommended |
| --- | --- | --- |
| Format To Number As Indian | `formatToNumberAsIndian` | Off |
| Auto Rescheduling | `auto_reschedule` | Off |
| Rescheduling Prompt, Rescheduled Follow-up Prompt | | Per agent/version. Only when Auto Rescheduling is on |
| Followup | `followup` | Off |
| Followup Prompt | `followup_prompt` | Per agent/version. Only when Followup is on |
| Background Noise | `bgNoise` | On |
| Background Noise Volume | `bgNoiseVolume` | 0.2 |
| DTMF Input Collection | `dtmf_collection_enabled` | Off |
| Substrings to Remove from Speech | `substrings_to_remove` | The standard list of model turn markers (`<turn>`, `<end>`, `<eos>`, `[DONE]`, `<wait>` variants and similar). Copy it from an existing recommended agent, don't retype it |
| Noise Cancellation | `noise_cancellation` | On |
| Noise Cancellation Strategy | `noise_cancellation_strategy` | `aicoustics` |
| Noise Cancellation Strength | `noise_cancellation_strength` | 0.8 |
| Leave Voicemail Message | `voicemail_msg` | Off |
| Custom Voicemail Message | `voicemail_custom_msg` | Per agent/version. Only when Leave Voicemail Message is on |
| Time Limit | `time_limit` | 300 (seconds; platform default) |
| Disconnect Timeout | `hold_disconnect_timeout` | 30 (seconds; platform default) |

## Call memory — `agentMemory`

| Setting | Key | Recommended |
| --- | --- | --- |
| Enabled for Call | `enabled_for_call` | Off |
| Max Calls | `call_filters.maxCalls` | 10 |
| Only Connected Calls | `call_filters.onlyConnected` | On |
| Max Days | `call_filters.maxDays` | 30 |
| Additional Agents Mode | `call_filters.additionalAgents.mode` | `self` |
| Include Transcript | `call_filters.includeTranscript` | Off |

`agentMemory` is replaced as a whole, so it also holds `voice_rotation_config`. Never send
`call_filters` without the rest. Use `ck agents memory` / `ck agents voice-rotation` instead
([call-memory-and-rotation.md](call-memory-and-rotation.md)).

## Post-call strategy

| Setting | Field | Recommended |
| --- | --- | --- |
| Post Call Model | `postcallmodel` | `callkaro/krishna-2.5` |
| Primary strategy, 0–10 s | `post_call_strategy["1-10"]` | `DEFAULT_VALUES` |
| Primary strategy, 10–30 s | `post_call_strategy["11-30"]` | `callkaro/krishna-2.5` |
| Primary strategy, 30–60 s | `post_call_strategy["31-60"]` | `callkaro/krishna-2.5` |
| Primary strategy, over 60 s | `post_call_strategy[">60"]` | `callkaro/krishna-2.5` |
| Primary strategy, only agent turns | `post_call_strategy.only_agent_turns` | `DEFAULT_VALUES` |
| Secondary strategy | `secondary_post_call_strategy` | Same buckets, with `gpt-6-luna` in place of `callkaro/krishna-2.5` |

**What `DEFAULT_VALUES` means:** it is not a model. For a call whose duration falls in that bucket the
post-call analysis is **skipped**: no model runs, every post-call variable gets its configured default
value, and the default disposition reason is applied if one is set. It is valid on any bucket, not only
`only_agent_turns`. With `1-10` set to it, calls of 10 seconds or less are not analysed (cheaper, but a
"not interested" or callback said in those seconds is not captured). The primary strategy decides: the
secondary's value for a bucket only matters when the primary's is unset. Don't change a bucket to or
from `DEFAULT_VALUES` unless the user asks, because it changes what gets recorded on live calls.

Post-call variables, the default disposition reason, the analysis prompt and "Use Others Drop-off
Reason" are per agent/version.

## Not set by recommendation (per agent/version, or not applicable)

Agent name, version name, status and prompt type; A/B rules; caching strategy (`response`, the
default); insert-metadata-in-prompt; update-contacts; conversion reason; capabilities; prompt snippets;
functions and their code; knowledge bases (none); webhook URL and headers (none); switch-language
function; warm transfer and transfer numbers; phone numbers; WhatsApp; pre-format variables; custom
pronunciations; variable source; HubSpot property mapping.
