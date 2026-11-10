# Reference: Variables, Filler, Call Memory, Voice Rotation & WhatsApp
<!-- graph-summary: Field reference for variable formatting and sources, knowledge bases, filler, pronunciation, switchable languages/agents, call memory and voice rotation (agentMemory), and WhatsApp functions and chat-agent handoff. -->

Part of the [version reference](../AGENT-VERSION-REFERENCE.md) (which document a field belongs to, topic map). Field index: [field-index.md](field-index.md).

## 14. Variables, formatting, knowledge, filler, pronunciation

| Field | Type / default | Meaning |
| --- | --- | --- |
| `knowledges` | ObjectId[], `[]` | Attached knowledge-base documents (RAG). Resolve names → ids from the account's knowledge bases; never invent ids. |
| `msg_while_executing_knowledge_base` | string[], `[]` | Lines the agent can say while a knowledge-base lookup is running. |
| `insert_metadata_in_prompt` | bool, `true` | Whether `{{metadata}}` values are injected into the system prompt at call start. Turn off when metadata should reach only functions, not the prompt. |
| `preFormatVariables` | `{ "<variable>": "<formatKey>" }`, `{}` | How a raw variable value is transformed **before it is spoken**. |
| `variableSource` | `{ "<variable>": {format, source, keyvalue, format_as_indian} }`, `{}` | Where each variable's value comes from **and** how it is formatted. `source` is an integration id the account has connected (e.g. `leadsquared`, `hubspot`, `hubspot-plus`, `heltar`, `aisensy`) or `""` for a plain call-metadata variable; `keyvalue` is the field name in that system; `format` is a format key (below); `format_as_indian` applies Indian number formatting. |
| `callPropertyMapping` | `{ "<externalProperty>": {field} }`, `{}` | Maps CallKaro call fields onto an external CRM's call properties for post-call write-back (HubSpot-Plus style). UI-exposed — check [§18](../AGENT-VERSION-REFERENCE.md). |
| `customPronunciations` | `{ "<word>": "<pronunciation>" }`, `{}` | Phonetic overrides for brand, product and place names the TTS mispronounces. Write the pronunciation the way it should sound in the target language. |
| `filler_config` | object, `{}` | Filler sounds while the agent thinks (below). |
| `switchableLanguages` | object[], `[]` | Rules for transferring the call to a DIFFERENT PUBLISHED VERSION of this agent in another language (below) — not the same-version `language_switching` behavior ([§12](call-settings.md)). |
| `switchableAgents` | object[], `[]` | Transfer-to-another-agent rules (below). |

**Format keys** (for `preFormatVariables` values and `variableSource.format`):
`No`, `Custom` (written as `Custom:<free-text description>` — an LLM formats the value per that
description), `Latin:Devanagari`, `Number:FullWords`, `Number:NearestHundreds`,
`Number:NearestThousands`, `Number:NearestLakhs`, `Number:DigitByDigit`, `Date:Day`,
`Date:DayMonth`, `Date:DayMonthYear`, `Time:HourMinuteAMPM`, `DateTime:FullSentence`,
`DateTime:SentenceWithoutYear`, `DateTime:HourMinuteAMPM`, `DateTime:Day`, `DateTime:DayMonth`,
`DateTime:DayMonthYear`.
Typical uses: an ISO datetime → `DateTime:FullSentence` so it is spoken as a sentence; an English
city name in a Hindi script → `Latin:Devanagari`; a loan amount → `Number:FullWords`; an account
number → `Number:DigitByDigit`.

**`filler_config`:**

| Field | Meaning |
| --- | --- |
| `filler_type` | `none` (default) / `dynamic` (LLM-generated filler) / `static` (random pick from `filler_phrases`) |
| `filler_phrases` | string[] — used when `static` |
| `filler_prompt` | prompt used when `dynamic` (default intent: return a filler phrase based on conversation context) |
| `model` / `temperature` | LLM for `dynamic` fillers (typical `llama-3.3-70b-versatile`, 0.5) |
| `trailing_silence_seconds` | silence appended after each filler before the agent resumes (0–3, default 0.6) |
| `dynamic_context_wait_seconds` | how long to wait for more context before generating (0–3, default 0.65) |
| `delay_seconds` | delay before playing the filler; `null`/0 = auto-calculated (max 3) |

Per-capability `use_filler` ([§4](capabilities-and-pathways.md)) gates fillers phase-by-phase once a filler type is set.

**`switchableLanguages[]`** — each entry:
`{language, when_to_transfer, end_msg_type: static|silent, end_msg, start_msg_type: static|dynamic, start_msg}`.
`when_to_transfer` is the natural-language rule for switching to that language; `end_msg` is said in
the *current* language while switching (empty when `silent`); `start_msg` is the first line in the
*new* language (empty when `dynamic`). **Never add an entry for the version's own
`default_language`** — a call cannot switch to the language it is already in.

**`switchableAgents[]`** — the same shape with `agentId` instead of `language`: transfer the live call
to another agent (a different specialist bot), with the same end/start message controls. Requires a
real agent id.

---

## 14b. Call memory & voice rotation — `agentMemory`

One object, two features. **The backend replaces `agentMemory` whole on update** — always send the
complete object (or use `ck agents memory` / `ck agents voice-rotation`, which merge for you).
Playbook and commands: [call-memory-and-rotation.md](../call-memory-and-rotation.md).

| Field | Type / default | Meaning |
| --- | --- | --- |
| `agentMemory.enabled_for_call` | bool, `false` | Switch for call memory: functions get `x_call_history` (earlier calls with the same contact, newest first). Off = the list is empty. |
| `call_filters.maxCalls` | int `-1`–`200`, `10` | Earlier calls to load. `-1` = all (capped at 200), `0` = none. |
| `call_filters.onlyConnected` | bool, `true` | Skip calls that never connected. |
| `call_filters.maxDays` | int `0`–`3650`, `30` | Only calls newer than this many days; `0` = no limit. |
| `call_filters.additionalAgents` | `{mode, agentIds}`, `{mode:"self",agentIds:[]}` | Whose calls to read: `self` (this agent), `all` (every agent on the account), `selected` (+ up to 50 ids in `agentIds`, each a 24-char agent id). |
| `call_filters.includeTranscript` | bool, `false` | Adds `transcript` to each item. Large; leave off unless a function needs the words. |
| `voice_rotation_config.enabled` | bool, `false` | Switch for voice rotation on retry. |
| `voice_rotation_config.trigger` | `{mode, previous_call_status, conditions}`, `{mode:"instant_hangup"}` | When the previous call (same contact, same version) means "use the next voice". `mode`: `instant_hangup` (previous call connected and the contact never spoke) or `custom`. For `custom`: `previous_call_status` `connected` (default) / `not_connected`, and up to 20 `conditions` that must all match. |
| `trigger.conditions[]` | `{source, field?, operator, value?}` | `source`: `post_call_variable` (needs `field`), `hangup_reason`, `call_duration`, `conversion_status`. `operator`: `equals`, `not_equals`, `empty`, `not_empty`, `eq`, `gt`, `gte`, `lt`, `lte`. `value` is not used with `empty` / `not_empty`. |
| `voice_rotation_config.voices` | object[], `[]` (max 5) | Retry voices, each a complete voice configuration (same shape as `voice_configuration`, [§9](voice-and-transcriber-fields.md); copy it unchanged from `ck voices` - the backend does not check the model against the provider). Step 1 = `voices[0]`. |
| `voice_rotation_config.on_exhausted` | `last` \| `primary` \| `cycle`, `last` | After the last voice: stay on it, go back to the primary voice, or restart from `voices[0]`. |

Default value of the whole object in a new agent:
`{"enabled_for_call":false,"call_filters":{"maxCalls":10,"onlyConnected":true,"maxDays":30,"additionalAgents":{"mode":"self","agentIds":[]},"includeTranscript":false},"voice_rotation_config":{"enabled":false,"trigger":{"mode":"instant_hangup"},"voices":[],"on_exhausted":"last"}}`.

---

## 15. WhatsApp functions & chat-agent handoff

WhatsApp actions are stored in the same `functions[]` array, with their own types:

| `type` | When it runs | Fields |
| --- | --- | --- |
| `whatsapp_in_call` | mid-call, model-triggered | `name`, `provider`, `messageType`, `description` (trigger condition), `msg_while_executing_type` (`dynamic` default) + `msg_while_executing[]`, `linkToCall`, and when `linkToCall !== "off"`: `userTurnInstruction`, `replyDuringCall`, plus `agentTurnInstruction` unless `linkToCall === "user_only"` |
| `whatsapp_post_call` | after the call | `name`, `provider`, `messageType`, template/campaign fields, `conditions[]` ([§6](functions-reference.md)) |
| `assign_chat_agent` | after the call | `chat_agent_id`, `conditions[]`, `scheduleFollowupAfterAssignment` |

`messageType` is `template` or `text`. A **template** message carries the provider's template
identity — `templateId`, `templateName`, `languageCode`, `headerFormat` for standard WhatsApp;
`campaignName`/`templateName`, or `templateKey`/`campaignId`/`campaignName`, for campaign-based
providers — plus `parameters` mapping each template placeholder id to a source key. Every template
placeholder must be mapped or the save is rejected. A **text** message needs only `description`
(and the `linkToCall` fields). `linkToCall` controls whether the WhatsApp thread is linked into the
live call and whose turns feed it (`off` / `user_only` / both). Function names must be unique and
must not collide with reserved agent function names.
