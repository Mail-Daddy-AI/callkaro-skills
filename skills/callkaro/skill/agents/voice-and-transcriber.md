<!-- graph-summary: Choosing the voice (TTS) and transcriber (STT) for a language and persona, and fixing mishearing. Use when setting or changing voice or transcriber; field tables are in the reference. -->
# Voice (TTS) & Transcriber (STT) — choosing them

> **Field tables live in [AGENT-VERSION-REFERENCE.md](AGENT-VERSION-REFERENCE.md)
> §9 (voice) and §10 (transcriber)** — every provider's exact keys, models,
> ranges and defaults. Don't restate them; look them up there.
> This file is *how to choose*. For the full production selection policy, the
> pipeline stage is [../authoring-pipeline/voice-transcriber-agent.md](../authoring-pipeline/voice-transcriber-agent.md);
> its LANGUAGE DEFAULTS predate the house defaults below, which win.

## House defaults

Use these unless the document or the user asks for something else. When a choice here is unclear
for this bot (the persona's gender is not stated, a default voice is not in `list_voices`), ask the
user; never guess.

| Setting | Default |
|---|---|
| `transcriber` | **Soniox**, with only the languages this version speaks. No keywords or context unless calls show a mishearing that decides the call. |
| `secondary_transcriber` | **Sarvam**, in the bot's main language (one language per Sarvam configuration). |
| `voice_configuration` | **Eleven Labs**: a voice of the persona's gender for the bot's language, found with `list_voices`. |
| `secondary_voice_configuration` | Male persona: **Sarvam v4** (`bulbul:v4` family), voice **`ashutosh`**. Female persona: **Gnani v2.5**, voice **`chitra`**. |
| `model` | **`callkaro/arjuna-2.5`**. |
| `secondary_model` | Chosen for this bot: see [reference §7](AGENT-VERSION-REFERENCE.md). |

- Copy the provider name, model and voice id exactly as `list_voices` returns them; the names above
  are what to search for, not ids to write from memory.
- The persona's gender comes from the document. When the document does not say, ask the user.

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
`useMultiTranscribers: true` (agent-level) runs both at once instead of failover.

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
