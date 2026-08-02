# Voices

`ck voices` lists the TTS voices available to **this user** (the catalog is
resolved per-account, same as the dashboard's voice picker). Providers: Azure,
Eleven Labs, Cartesia (Sarvam and Open AI voices are fixed lists, below).

```bash
ck voices [--provider azure|elevenlabs|cartesia] [--language hi] [--gender female] [--json]
```

Output rows: `provider, name, id, language, gender, styles/category`.
`--language` matches base subtags (`hi` matches `hi-IN`). If a provider is
listed in a "providers failed" note, its voices are just missing this call —
retry or pick another provider.

## How to pick a voice (the ai-fde policy)

1. `ck voices --language <lang> --json` and choose by language → gender → style.
2. **Never invent `voice_name`/`voice_id`** — copy both from the listing.
3. If the user names a specific voice, search **without** `--gender` (the
   filter could hide it).
4. Default gender when the user gives no signal: masculine for `hi en kn gu ml`,
   feminine for `mr ta te bn`.
5. Set a **`secondary_voice_configuration` from a DIFFERENT provider** as the
   fallback (Sarvam `bulbul:v3` is the standard partner choice).

## `voice_configuration` shapes per provider

**Eleven Labs** (most used):
```json
{ "voice_provider": "Eleven Labs", "voice_name": "...", "voice_id": "...",
  "voice_model": "eleven_flash_v2_5", "voice_language": "hi", "voice_speed": 1.0,
  "voice_stability": 0.5, "voice_similarity_boost": 1, "voice_style": 0.5,
  "voice_category": "professional" }
```
Models: `eleven_flash_v2_5` (default), `eleven_turbo_v2_5`, `eleven_turbo_v2`,
`eleven_flash_v2`. Speed 0.7–1.2.

**Cartesia**:
```json
{ "voice_provider": "Cartesia", "voice_name": "...", "voice_id": "...",
  "voice_model": "sonic-3", "voice_language": "hi", "voice_speed": 0,
  "voice_category": "similarity", "cartesia_emotions": [] }
```
Models: `sonic-3.5, sonic-3, sonic-turbo, sonic-2, sonic`. Speed −1…1 (0 = normal).

**Sarvam** (fixed catalog; Indian languages):
```json
{ "voice_provider": "Sarvam", "voice_id": "<sarvam voice>", "voice_model": "bulbul:v3",
  "voice_language": "hi-IN", "voice_speed": 1.0, "voice_pitch": 0.5 }
```
Models: `bulbul:v3`, `bulbul:v3-beta` (`bulbul:v2` legacy). No `voice_name` key.

**Azure**:
```json
{ "voice_provider": "Azure", "voice_name": "<DisplayName>", "voice_id": "<ShortName>",
  "voice_language": "hi-IN", "voice_speed": 0.2 }
```
Azure `id` is the ShortName (e.g. `hi-IN-SwaraNeural`); styles come from the
listing's styles column. No `voice_model`.

**Open AI** (only valid with `*realtime*` LLM models): fixed voices
`sage, alloy, ash, ballad, coral, echo, shimmer, verse` —
`{ "voice_provider": "Open AI", "voice_name": "sage" }`.

## Language ↔ voice ↔ transcriber must agree

Keep `default_language`, `voice_language`, and `transcriber_language`
consistent (e.g. `hi` / `hi` or `hi-IN` / `hi-IN` per provider convention), or
the agent will speak one language and transcribe another.


Full per-provider field sets, ranges, and transcriber pairing rules:
[AGENT-VERSION-REFERENCE.md](AGENT-VERSION-REFERENCE.md) §9 (voice); transcriber pairing: [transcriber.md](transcriber.md).
