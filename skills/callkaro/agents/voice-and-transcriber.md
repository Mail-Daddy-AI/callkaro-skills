# Voice (TTS) & Transcriber (STT) — choosing them

> **Field tables live in [AGENT-VERSION-REFERENCE.md](AGENT-VERSION-REFERENCE.md)
> §9 (voice) and §10 (transcriber)** — every provider's exact keys, models,
> ranges and defaults. Don't restate them; look them up there.
> This file is *how to choose*. For the full production selection policy, the
> pipeline stage is [../authoring-pipeline/voice-transcriber-agent.md](../authoring-pipeline/voice-transcriber-agent.md).

## Find real voices — never invent one

```bash
ck voices --providers                      # every provider + its models
ck voices --provider cartesia --fields     # exact keys, ranges and defaults
ck voices --provider sarvam --model bulbul:v3 --language hi-IN --gender female
ck transcribers                            # every provider/model + languages
ck transcribers --provider gnani --fields
```

`ck voices` covers **all** providers — Eleven Labs, Cartesia, Sarvam, Azure,
Speechify, Deepgram, Open AI, Murf (`--all` adds admin-gated ones). `--language hi`
matches `hi-IN` too; Speechify **requires** `--language` because its voices are
locale-scoped. **Copy `voice_name`/`voice_id` verbatim** — a remembered id goes
stale or belongs to another provider.

`--fields` is the fastest way to write a correct config: it prints only the keys
that provider uses, so you never write one it ignores.

## Choosing a voice

1. Filter by language, then gender, then style.
2. If the user names a specific voice, search **without** `--gender` — the
   filter could hide it.
3. Default gender when nothing is stated: **masculine** for `hi en kn gu ml`,
   **feminine** for `mr ta te bn`.
4. Match the persona gender declared in the script ([prompts.md](prompts.md)).
5. Always set `secondary_voice_configuration` from a **different provider** so
   one provider outage can't take both voices down (Sarvam `bulbul:v3` is the
   standard partner).

## Choosing a transcriber

| Situation | Pick |
|---|---|
| Single Indian language | Sarvam `saarika:v2.5` (`hi-IN`) or Deepgram `nova-3` |
| English + a domain (finance, medical, phone) | Deepgram's domain models |
| Code-mixed / Hinglish | Deepgram `multi`, Eleven Labs `multi`, Sarvam `saaras:v3` with `transcriber_mode: "codemix"`, or Gnani `en-IN,hi-IN` |
| Caller may switch languages mid-call | An **array**-language provider: Soniox (best) or Azure |
| Brand/product words misheard | Add `keywords[]` **inside** the transcriber object |

**Standard pairing: Soniox primary + Azure secondary** (Sarvam secondary when
Azure lacks the locale). Always a different provider from the primary.
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

```bash
ck agents get <agentId> --versions <vid> --json    # did .transcriber / .voice_configuration round-trip?
ck calls make --agent <agentId> --to <number> --test   # real audio
```
Some accounts have the transcriber language locked (provider envelope) — if a
write doesn't round-trip, report it instead of claiming success.
