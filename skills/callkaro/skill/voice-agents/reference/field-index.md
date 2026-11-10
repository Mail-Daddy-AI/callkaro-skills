# Reference: Complete Version Field Index
<!-- graph-summary: Every version field with its type, default and the reference topic that explains it. Use it to find which reference node to open for a field. -->

Part of the [version reference](../AGENT-VERSION-REFERENCE.md) (which document a field belongs to, topic map). Field index: this file.

## Complete version field index

Everything the version document declares, with its default and the topic that explains it.

Topic key -> open this node:

| Topic | Node |
| --- | --- |
| routing | [AGENT-VERSION-REFERENCE.md](../AGENT-VERSION-REFERENCE.md) |
| script | [script-and-types.md](script-and-types.md) |
| caps | [capabilities-and-pathways.md](capabilities-and-pathways.md) |
| functions | [functions-reference.md](functions-reference.md) (advanced pre-call: [functions-advanced-code.md](functions-advanced-code.md)) |
| llm | [llm-and-postcall.md](llm-and-postcall.md) |
| voice | [voice-and-transcriber-fields.md](voice-and-transcriber-fields.md) |
| call | [call-settings.md](call-settings.md) |
| vars | [variables-memory-whatsapp.md](variables-memory-whatsapp.md) |
| versions | [versioning-and-preflight.md](versioning-and-preflight.md) |


| Field | Type | Default | Topic |
| --- | --- | --- | --- |
| `versionName` | string | — | versions |
| `systempromptType` | int 0–3 | `0` | script |
| `isVersionActive` | bool | `true` | versions |
| `systemprompt` | string | `"You are a helpful assistant."` | script |
| `role`, `goal`, `callFlow` | string | `""` | script |
| `instructions`, `guardrails`, `rebuttals` | string[] | `[]` | script |
| `callFlow_json` | object | `null` | script |
| `useCallFlow_json` | bool | `false` | script |
| `capabilities` | object[] | `[]` | caps |
| `end_call_msg` | string[] | `[]` | 3, 11 |
| `model_response_snippet` | string | `null` → platform default | script |
| `security_guardrails_snippet` | string | `null` → platform default | script |
| `function_calling_snippet` | string | `null` → platform default | script |
| `language_switch_snippet` | string | `null` → platform default | script |
| `hold_call_snippet` | string | `null` → platform default | script |
| `gender_prompt_snippet` | string | `null` | call |
| `default_language` | enum | `"en"` | script |
| `silence_language` | enum + `multi` | `"en"` | call |
| `model` | string | `gpt-4o-mini` | llm |
| `secondary_model` | string | `gpt-4o-mini` | llm |
| `temperature` | number 0–10 | `8` | llm |
| `caching_strategy` | enum | `"response"` | llm |
| `voice_configuration` | object | platform default (Eleven Labs) | voice |
| `secondary_voice_configuration` | object | — | voice |
| `transcriber` | object | platform default (Deepgram `nova-3`) | voice |
| `secondary_transcriber` | object | — | voice |
| `vad_configuration` | object | see [§12](call-settings.md) | call |
| `filler_config` | object | `{}` | vars |
| `agentMemory` | object | see [§14b](variables-memory-whatsapp.md) | vars |
| `customPronunciations` | object | `{}` | vars |
| `speakfirst` | object | `{value: 1, message_interruption: false}` | call |
| `speakfirst_inbound` | object | same | call |
| `initial_pause_outbound` / `initial_pause_inbound` | int | `1` | call |
| `silence_count` | int | `2` | call |
| `silence_wait` | int | `6` | call |
| `silence_mode` | enum | `"default"` | call |
| `silence_prompts` | string[] | `[]` | call |
| `silence_instructions` | string \| null | `null` | call |
| `language_switching` | bool | `false` | call |
| `language_switching_instructions` | string \| null | `null` | call |
| `language_lockin_time` | number \| null | `null` | call |
| `allowed_languages` | string[] | `[]` | call |
| `language_switch_min_words` | int | `3` | call |
| `language_switching_v1` | bool | `false` | call |
| `detect_gender` | bool | `false` | call |
| `formatToNumberAsIndian` | bool | `false` | call |
| `bgNoise` | bool | `true` | call |
| `bgNoiseVolume` | number 0–1 | `0.2` | call |
| `noise_cancellation` | bool | `true` | call |
| `noise_cancellation_strategy` | enum | `"aicoustics"` | call |
| `noise_cancellation_strength` | number 0.05–1 | `1` | call |
| `punctuations_to_remove` | string[] | `[]` | call |
| `voicemail_msg` | bool | `true` | call |
| `voicemail_custom_msg` | string | `""` | call |
| `hold_disconnect_timeout` | int s | `30` | call |
| `time_limit` | int s | `300` | call |
| `auto_reschedule` | bool | `false` | call |
| `rescheduling_prompt` | string | `null` | call |
| `rescheduled_follow_up_prompt` | string | `null` | call |
| `followup` | bool | `false` | call |
| `followup_prompt` | string | `null` | call |
| `warm_transfer` | bool | `false` | 6, 13 |
| `warm_transfer_prompt` | string | `null` | 6, 13 |
| `functions` | object[] | `[]` | 6, 15 |
| `knowledges` | ObjectId[] | `[]` | vars |
| `msg_while_executing_knowledge_base` | string[] | `[]` | vars |
| `postcall` | object[] | `[]` | llm |
| `postcallmodel` | enum | `"callkaro/krishna-2.5"` | llm |
| `post_call_strategy` | object | per-bucket default | llm |
| `secondary_post_call_strategy` | object | per-bucket fallback | llm |
| `post_call_analysis_prompt` | string | `""` | llm |
| `default_disposition_reason` | string | `""` | llm |
| `useOthersDropOffReason` | bool | `false` | llm |
| `conversion_reason` | string | `""` | 3, 8 |
| `webhook` | string | `""` | call |
| `webhook_headers` | object[] | `[]` | call |
| `preFormatVariables` | object | `{}` | vars |
| `variableSource` | object | `{}` | vars |
| `insert_metadata_in_prompt` | bool | `true` | vars |
| `switchableAgents` | object[] | `[]` | vars |
| `switchableLanguages` | object[] | `[]` | vars |
