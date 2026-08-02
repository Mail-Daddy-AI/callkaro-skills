# Transcribers (STT) — choosing and configuring

The transcriber converts the caller's speech to text; a bad match here makes a
perfect prompt useless. Config lives in the version's `transcriber` (+
`secondary_transcriber`) object. Full per-provider table:
[AGENT-VERSION-REFERENCE.md](AGENT-VERSION-REFERENCE.md) §10.

## Object shape

```json
{ "transcriber_provider": "Deepgram", "transcriber_model": "nova-3",
  "transcriber_language": "hi", "transcriber_language_detection": false }
```

`transcriber_language` format is **provider-specific and strict**:
- **string** for Deepgram (`hi`), Sarvam (`hi-IN`), Groq (`hi`), Eleven Labs (`hi`), Cartesia
- **array** for Azure (`["hi-IN"]`) and Soniox (`["hi","en"]`) — never a plain string
- copy values verbatim; never reformat `"hi"` ↔ `"hi-IN"` ↔ `["hi-IN"]`

## Provider cheat sheet

| Provider | Model to start with | Languages | Strengths |
|---|---|---|---|
| **Deepgram** | `nova-3` | `en hi kn mr ta te bn multi` (string) | strong general default; en-only domain models (`nova-2-phonecall`, `-finance`, `-medical`…); `multi` for code-mixing |
| **Sarvam** | `saarika:v2.5` | `hi-IN en-IN bn-IN kn-IN ml-IN mr-IN ta-IN te-IN gu-IN pa-IN od-IN` + `unknown` (auto) | best Indic coverage; `saaras:v3` adds `transcriber_mode`: `transcribe\|translate\|verbatim\|translit\|codemix` and `transcriber_prompt` context |
| **Soniox** | (no model key) | 40+ codes, **array** | strongest realtime multi-language primary; context boosts: `keywords[]`, `transcriber_general_context[{key,value}]`, `transcriber_text_context`, `transcriber_translation_terms[{source,target}]` |
| **Azure** | (no model key) | Indic + `en-US` locales, **array** | simultaneous multi-language recognition; solid secondary |
| **Eleven Labs** | `scribe_v2_realtime` | `hi en kn mr ta te bn gu ml multi` | low latency (`scribe_v2` = higher accuracy, slower); `multi` code-mixing |
| **Groq** | `whisper-large-v3-turbo` | `en`, `hi` only | cheap and fast for en/hi |
| **Cartesia** | `ink-whisper` | string | — |

## How to choose

1. **Single language, Indian**: Sarvam `saarika:v2.5` (`hi-IN` etc.) or
   Deepgram `nova-3`. English-only with a domain: Deepgram's domain models.
2. **Code-mixed / Hinglish**: Deepgram `multi`, Eleven Labs `multi`, or Sarvam
   `saaras:v3` with `transcriber_mode: "codemix"`.
3. **Truly multi-language calls** (caller may switch): an array provider —
   Soniox (best) or Azure. String providers can't hold two languages at once.
4. **Secondary transcriber**: ALWAYS set one, ALWAYS a different provider.
   Standard pairing: **Soniox primary + Azure secondary** (Sarvam secondary
   when Azure lacks the locale). `useMultiTranscribers: true` (agent-level)
   runs both simultaneously instead of failover.
5. **Brand/product words being misheard**: add `keywords[]` INSIDE the
   transcriber object (Deepgram/Azure/Soniox); Soniox also takes translation
   terms and free-text context.
6. Language switching enabled (`language_switching`)? The transcriber must
   cover every language in `switchableLanguages` — use an array provider.

Keep `default_language`, `voice_language`, and `transcriber_language` telling
the same story, each in its own provider's format.

## Verify after writing

```bash
ck agents get <agentId> --versions <vid> --json | # check .transcriber round-tripped
ck sim run <agentId> --tests <t> --versions <vid> # then a --test call for real audio
```
Some accounts have the transcriber language locked (provider envelope) — if a
write doesn't round-trip, report it instead of claiming success.
