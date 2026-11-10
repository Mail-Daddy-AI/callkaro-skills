# Reference: Voice (TTS) & Transcriber (STT) Fields
<!-- graph-summary: Exact keys, models and provider-specific fields for voice_configuration / secondary_voice_configuration and transcriber / secondary_transcriber. -->

Part of the [version reference](../AGENT-VERSION-REFERENCE.md) (which document a field belongs to, topic map). Field index: [field-index.md](field-index.md).

## 9. Voice — `voice_configuration` / `secondary_voice_configuration`

Both are objects; the secondary is the fallback and **should be a different provider** so one
provider outage cannot take both voices down. On a fresh create set **all four** of primary voice,
secondary voice, primary transcriber, secondary transcriber.

**Never invent `voice_id` / `voice_name` / `voice_model`.** Resolve them from the live catalogue for
that account and copy the values verbatim — IDs are provider-specific (Eleven Labs and Cartesia use
opaque IDs, Azure uses ShortNames, Sarvam uses lowercase names), and a remembered one goes stale or
belongs to another provider. Match the voice gender to the persona gender declared in the script.
Language format is *model*-dependent, not just provider-dependent — re-verify `voice_language` on
every provider or model change.

Write **only** the keys the provider uses:

| Provider | Fields | Ranges / defaults |
| --- | --- | --- |
| **Eleven Labs** | `voice_provider`, `voice_name`, `voice_id`, `voice_language`, `voice_model`, `voice_category`, `voice_speed`, `voice_stability`, `voice_similarity_boost`, `voice_style` | models `eleven_flash_v2_5` (default), `eleven_turbo_v2_5`, `eleven_turbo_v2`, `eleven_flash_v2`; speed **0.7–1.2** (1.0); stability / similarity / style **0–1** (0.5 / 1 / 0.5); category `professional` |
| **Cartesia** | `voice_provider`, `voice_name`, `voice_id`, `voice_language`, `voice_model`, `voice_category`, `voice_speed`, `voice_volume`, `cartesia_emotions[]` | models `sonic-3` (default), `sonic-3.5`, `sonic-turbo`, `sonic-2`, `sonic`; speed **−1.0–1.0** (0); volume **0.5–2.0** (1.0); category `similarity`; emotions `[]` unless asked. Voices also carry a sublanguage (`hinglish-IN` vs `hi-IN`) — pick per script style |
| **Sarvam** | `voice_provider`, `voice_id`, `voice_language`, `voice_model`, `voice_speed`, `voice_pitch` — **no `voice_name`, no `voice_category`** | models `bulbul:v3` (default), `bulbul:v3-beta` — never `bulbul:v2` (no longer offered, so a config naming it can't be edited in the UI); language like `hi-IN`; speed **0.7–1.2** (1.0); pitch **−2–2** (0.5). Voice categories `Customer Care` (default) / `Content Creation` / `International` select *which voices exist*; they are not stored |
| **Deepgram** | `voice_provider`, `voice_name`, `voice_id`, `voice_language`, `voice_model` | model `aura-2`; `voice_language` **`en` only**. Curated voices: `thalia` (default), `andromeda`, `helena`, `theia` (AU) / `apollo`, `arcas`, `aries`, `draco` (UK). No speed/pitch controls |
| **Speechify** | `voice_provider`, `voice_name`, `voice_id`, `voice_language`, `voice_model`, `speechify_loudness_normalization`, `speechify_text_normalization` | model `simba-multilingual`; locales `hi-IN en-IN en ur-IN bn-IN gu-IN mr-IN ta-IN te-IN`; both normalization flags default **false**. Voices are **locale-scoped** — resolve them for the chosen locale, they are not a fixed list |
| **Murf** (restricted / per account) | `voice_provider`, `voice_name`, `voice_id`, `voice_language`, `voice_model`, `voice_style`, `voice_speed`, `voice_pitch` | model `FALCON` only (GEN2 streaming deprecated 2026-08-16); 26 locales; `voice_id` is locale-prefixed (`hi-IN-aman`); `voice_style` e.g. `Conversation` (default), `Promo`, `Narration`, `Customer Support Agent`; speed / pitch default **0**. Curated voices exist for `hi-IN en-IN en-US en-UK en-AU ta-IN bn-IN` only. Don't select it unless the account exposes it |
| **Azure** | `voice_provider`, `voice_name`, `voice_id` (ShortName), `voice_language` (full locale, e.g. `hi-IN`), `voice_speed`, `voice_pitch`, `azure_voice_style`, `azure_voice_style_degree`, `azure_voice_volume` — **no `voice_model`** | speed **−1.0–1.0** (0.2); pitch **−2–2** (0); style `default`; style degree **0.1–2.0** (0.5); volume **0–100** (100) |
| **Open AI** | `voice_provider`, `voice_name` **only** | Voices `sage alloy ash ballad coral echo shimmer verse`. **Only** valid when `model` is a realtime model, and then it is the only valid provider. If an existing config is already on Open AI, leave provider/name/language alone unless explicitly asked. |
| **Smallest AI** | `voice_provider`, `voice_name`, `voice_id`, `voice_language`, `voice_model`, `voice_speed` | models `lightning-v3.1` (default, 80+ voices) and many global; voices (English) `emily` `sophia` `james` `olivia`; voices (Hindi) `priya` `arjun` `ananya` `rohan` `meera` `vikram`; speed **0.5–2.0** (1.0) |
| **Callkaro** (restricted / admin-gated) | `voice_provider`, `voice_name`, `voice_id`, `voice_language`, `voice_model`, `voice_gender`, `voice_speed`, plus generation controls `temperature`, `top_p`, `top_k`, `repetition_penalty` | model `ck-tts-v1`; languages `hi`, `en`; voices `aaryan` `raju` `mahesh` (male) / `kanika` `priya` `tarini` (female) — set `voice_gender` to match; speed **0.7–1.2**; temperature **0–2** (0.4); top_p **0–1** (0.85); top_k **−1–100** (30); repetition_penalty **1.1–2** (1.1). Don't select it unless the account exposes it |

Discover all of this from the CLI rather than recalling it: `ck voices --providers` lists providers and
models, `ck voices --provider <name> --fields` prints exactly the keys and ranges one provider takes,
and `ck voices --provider <name> [--model m] [--language l] [--gender g]` lists the voices themselves
(Speechify needs `--language`).

Language coverage differs per provider: Cartesia, Azure and Eleven Labs are language-indexed (each
voice has a language/locale), while Sarvam voices are multilingual and not language-indexed — which
makes Sarvam the reliable secondary for a language only one provider covers.

Accounts have a **provider envelope**: the set of voice/transcriber providers and editable fields
allowed for that user. A config outside the envelope is one the user cannot see or undo in the UI.
Honour it, and never write a field the account has no control for.

---

## 10. Transcriber — `transcriber` / `secondary_transcriber`

| Provider | `transcriber_language` | `transcriber_model` | Extra fields / capabilities |
| --- | --- | --- | --- |
| **Deepgram** | **string**: `en hi kn mr ta te bn multi` | required. `nova-3` (best general), `nova-3-general`, `nova-3-medical`, `nova-2`, `nova-2-general`, en-only domain variants `nova-2-{meeting,phonecall,finance,conversationalai,voicemail,medical,drivethru,automotive}`, `nova-general`, `nova-phonecall`, `voicemail`, `flux-general`, `flux-general-multi` (hi+en) | `keywords[]`, `transcriber_language_detection`, domain-specific models |
| **Sarvam** | **string** BCP-47: `hi-IN en-IN bn-IN kn-IN ml-IN mr-IN od-IN pa-IN ta-IN te-IN gu-IN doi-IN as-IN ur-IN ne-IN kok-IN ks-IN sd-IN sa-IN sat-IN mni-IN brx-IN mai-IN`, or `unknown` for auto-detect | required. `saaras:v3` (default), `saaras:v4` | `transcriber_mode` (`transcribe` \| `translate` \| `verbatim` \| `translit` \| `codemix`), `transcriber_prompt` (context hint) |
| **Groq** | **string**: `en`, `hi` only | required. `whisper-large-v3-turbo`, `whisper-large-v3`, `distil-whisper-large-v3-en` | — |
| **Azure** | **array** of locales (`hi-IN en-IN en-US kn-IN mr-IN ta-IN te-IN bn-IN gu-IN ml-IN pa-IN as-IN or-IN ur-IN`) — never a plain string | **none** | simultaneous multi-language recognition, `keywords[]` |
| **Eleven Labs** | **string**: `hi en kn mr ta te bn gu ml multi` | required. `scribe_v2_realtime` (low latency — prefer for live calls), `scribe_v2` (higher accuracy) | code-mixing via `multi` |
| **Soniox** | **array** (40+ codes: all major Indic plus `es fr de it pt nl pl ru uk tr ar fa he id ms vi th ja ko zh cs da fi no sv el hu ro`) | **none** | `keywords[]`, `transcriber_general_context[{key,value}]`, `transcriber_translation_terms[{source,target}]` |
| **Smallest AI** | **string**: `en hi ta te kn bn mr gu ml multi` | required. `pulse` (only model). Use `multi` for auto-detection | — |
| **Cartesia** | **string**: `hi en kn mr ta te bn gu ml` (`ink-2` is `en` only) | required. `ink-whisper` (default), `ink-2` | — |
| **Gnani** | **string**: `en-IN,hi-IN` (Hinglish — one comma-joined string, *not* an array), `hi-IN en-IN bn-IN gu-IN kn-IN ml-IN mr-IN pa-IN ta-IN te-IN` | **none** | `transcriber_format` (`verbatim` default \| `transcribe`), `transcriber_itn_native_numerals` (bool, default false — renders numbers in the language's own numerals) |
| **Callkaro** (restricted / admin-gated) | **array** | **none** | same context / keyword / translation fields as Soniox |

Guidance:

- Soniox is the strongest default primary (realtime, multi-language, richest context support);
  Azure — or Sarvam when Azure lacks the locale — is the usual secondary. Always pick a **different
  provider** for the secondary.
- A provider whose language field is a *string* cannot cover several languages at once. For genuinely
  mixed-language calls use an array provider (Azure, Soniox) or a code-mixing model (Deepgram
  `multi`, Eleven Labs `multi`, Sarvam `codemix` mode).
- Copy `transcriber_language` from the resolved catalogue value **verbatim** — do not reformat
  `["en-IN"]` → `"en"`, or `"hi"` → `"hi-IN"`, and never wrap a string provider's value in an array.
- `keywords[]` boosts recognition of brand/product/domain words and lives **inside** the transcriber
  object, not at version level.
- Some accounts have the transcriber language **locked** — leave it unchanged there.
- `useMultiTranscribers` (agent doc) makes the secondary run alongside the primary rather than only
  on failure.
- Discover this from the CLI instead of recalling it: `ck transcribers` lists every provider/model with
  its language field and languages, and `ck transcribers --provider <name> --fields` prints the exact
  keys that provider takes.
