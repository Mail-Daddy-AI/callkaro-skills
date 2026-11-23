<!-- graph-summary: Choosing the voice (TTS) and transcriber (STT) for a language and persona, and fixing mishearing. Use when setting or changing voice or transcriber; field tables are in the reference. -->
# Voice (TTS) & Transcriber (STT) — choosing them

> **Field tables live in [AGENT-VERSION-REFERENCE.md](AGENT-VERSION-REFERENCE.md)
> §9 (voice) and §10 (transcriber)** — every provider's exact keys, models,
> ranges and defaults. Don't restate them; look them up there.
> This file is *how to choose*. For the full production selection policy, the
> pipeline stage is [../authoring-pipeline/voice-transcriber-agent.md](../authoring-pipeline/voice-transcriber-agent.md);
> its LANGUAGE DEFAULTS predate the house defaults below, which win.

## House defaults

`create_agent_in_db` sets these on every **new** agent: the voice by `voiceGender`, the languages by the agent's
language. An existing agent, and a new version of one, keeps its own unless the user asks to change it. When the
persona's gender is not stated, ask the user before creating the agent; never guess.

| Setting | Default |
|---|---|
| `transcriber` | Soniox, `transcriber_language` `["en", "hi"]` (for an agent in another language, only that language, e.g. `["ta"]`), empty `transcriber_general_context`, `transcriber_translation_terms` and `keywords` |
| `secondary_transcriber` | Sarvam, `transcriber_model` `saaras:v4`, `transcriber_language` `unknown`, `transcriber_mode` `transcribe` |
| `voice_configuration`, male | Eleven Labs "Raju - Human-like Customer Care Voice", `voice_id` `pzxut4zZz4GImZNlqQ3H`, `eleven_v4_turbo`, category `professional`, stability 0.5, similarity boost 1, style 0.5, speed 1 |
| `voice_configuration`, female | Eleven Labs "Tarini -  Calm & Assertive Recovery Agent", `voice_id` `kiaJRdXJzloFWi6AtFBf`, same model and settings |
| `secondary_voice_configuration`, male | Sarvam `ashutosh_hi_conversational`, `bulbul:v4-flash`, speed 1 |
| `secondary_voice_configuration`, female | Gnani "Chitra" (`voice_id` `Chitra`), `timbre-v2.5`, `voice_language` `auto`, speed 1 |
| `model` / `secondary_model` | `callkaro/arjuna-2.5` / `gpt-5.4-mini`; each stage's `llms` the same, temperature 0.2 |
| `post_call_strategy` | `callkaro/krishna-2.5` for `1-10`, `11-30` and `31-60`; `gpt-6-luna` for `>60`; `only_agent_turns` `DEFAULT_VALUES` |
| `secondary_post_call_strategy` | `gpt-6-luna` for `1-10`, `11-30` and `31-60`; `callkaro/krishna-2.5` for `>60`; `only_agent_turns` `DEFAULT_VALUES` |
| `formatToNumberAsIndian` | `false` (phone numbers are dialled as given) |

`voice_language` matches the agent's language: `hi` (Eleven Labs), `hi-IN` (Sarvam). Gnani stays `auto`.
For any other voice the user asks for, search with `list_voices` and copy its values exactly.

## Find real voices — never invent one

Load the voices tools and use `list_voices`: with no `provider` it lists the
providers (and models) this account may use; with a `provider` it searches that
provider's voices by `model`, `language`, `gender` or `query`. It covers Eleven
Labs, Cartesia, Sarvam, Azure, Speechify, Deepgram, Open AI and Murf. Speechify
**requires** a language because its voices are locale-scoped. **Copy
`voice_name`/`voice_id` verbatim** — a remembered id goes stale or belongs to
another provider. Transcriber providers, models and languages: reference §10.

The reference tables list only the keys each provider uses, so you never write
one it ignores.

## Choosing a voice

1. Filter by language, then gender, then style.
2. If the user names a specific voice, search **without** a gender — the
   filter could hide it.
3. When nothing states the gender, ask the user (house defaults above).
4. Match the persona gender declared in the script ([prompts.md](prompts.md)).
5. Always set `secondary_voice_configuration` from a **different provider** so
   one provider outage can't take both voices down (the house defaults above pair
   Eleven Labs with Sarvam v4 `ashutosh` or Gnani v2.5 `chitra`).

## Choosing a transcriber

| Situation | Pick |
|---|---|
| Single Indian language | Sarvam `saaras:v3` (`hi-IN`) or Deepgram `nova-3` |
| English + a domain (finance, medical, phone) | Deepgram's domain models |
| Code-mixed / Hinglish | Deepgram `multi`, Eleven Labs `multi`, Sarvam `saaras:v3`/`saaras:v4` with `transcriber_mode: "codemix"`, or Gnani `en-IN,hi-IN` |
| Low-latency streaming + Indian languages | Smallest AI `pulse` — single-string language, use `"multi"` for auto-detection |
| Caller may switch languages mid-call | An **array**-language provider: Soniox (best) or Azure |
| Brand/product words misheard | Add `keywords[]` **inside** the transcriber object |

**Standard pairing: Soniox primary + Sarvam secondary** (house defaults above).
Always a different provider from the primary.
`useMultiTranscribers` is deprecated: never change it.

## The two traps

1. **Language format is provider-specific and strict.** Some take a *string*
   (`"hi"` Deepgram, `"hi-IN"` Sarvam), others an **array** (`["hi-IN"]` Azure,
   `["hi","en"]` Soniox). Copy the format from the reference table verbatim —
   never reshape `"hi"` ↔ `"hi-IN"` ↔ `["hi-IN"]`.
2. **Keep the three languages consistent**: `default_language`,
   `voice_language`, `transcriber_language` must tell the same story (each in
   its own provider's format), or the agent speaks one language and transcribes
   another. If `language_switching` is on, the transcriber must cover every
   language in `switchableLanguages` — use an array provider.

Realtime LLM models (`*realtime*`) force `voice_provider: "Open AI"`; see
reference §7.

## Verify after writing

Read the saved version back with `read_version`: did `transcriber` /
`voice_configuration` round-trip? For real audio, the user places a test call
from the CallKaro dashboard.
Some accounts have the transcriber language locked (provider envelope) — if a
write doesn't round-trip, report it instead of claiming success.
