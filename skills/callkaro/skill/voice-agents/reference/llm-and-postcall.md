# Reference: LLM, Temperature, Caching & Post-call Analysis
<!-- graph-summary: Field reference for models, temperature, caching strategy, and post-call analysis: variables, strategy, dispositions, conversion rules. -->

Part of the [version reference](../AGENT-VERSION-REFERENCE.md) (which document a field belongs to, topic map). Field index: [field-index.md](field-index.md).

## 7. LLM, temperature, caching

| Field | Type | Default | Notes |
| --- | --- | --- | --- |
| `model` | string | `callkaro/arjuna-2.5` | Primary LLM driving new Basic and Advanced agents. |
| `secondary_model` | string | `gpt-5.4-nano` | Fallback LLM for new agents. |
| `temperature` | number | `3` | **Version-level scale is 0–10**. Capability `llms.temperature` is **0–1** (new-agent default 0.2). Never copy one into the other without ×10 / ÷10. |
| `caching_strategy` | `response` \| `sentence` \| `none` | `response` | `response` caches whole responses (fastest repeats), `sentence` caches per sentence (more reuse, finer grain), `none` disables it. |

Typical model families available: `gpt-4o`, `gpt-4o-mini`, `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`,
`gpt-5-mini`, `gpt-5-nano`, `gpt-5.1-chat`, `gpt-5.2-chat`, `gpt-5.4-mini`, `gpt-5.4-nano`,
`openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `gpt-4o-realtime-preview`,
`gpt-4o-mini-realtime-preview`, `gemini-2.5-flash`, `llama-3.1-8b-instant`,
`llama-3.3-70b-versatile`, `meta-llama/llama-4-scout-17b-16e-instruct`,
`moonshotai/kimi-k2-instruct`, `qwen/qwen3-32b`. Availability is account- and deployment-dependent —
query the platform's model list rather than hardcoding.

**Realtime models are special:** when `model` contains `realtime`, the voice provider must be
`Open AI` (and Open AI is not selectable for non-realtime models). Realtime agents also hide the
voice-speed control, so a realtime voice config carries only `voice_provider` and `voice_name`.

On type 3, version-level `model`/`secondary_model`/`temperature` do not drive routing — per-node
`llms` win — but keep sane values anyway.

---

## 8. Post-call analysis

| Field | Type | Default | Meaning |
| --- | --- | --- | --- |
| `postcall` | object[] | `[]` | Variables extracted from the transcript **after** the call. |
| `postcallmodel` | enum | `callkaro/krishna-2.5` | Legacy fallback used when `post_call_strategy` is absent or empty. Preserve existing values; use the strategy fields for new configurations. |
| `post_call_strategy` | object | four duration buckets use `callkaro/krishna-2.5`; `only_agent_turns` uses `DEFAULT_VALUES` | Primary model **per call-duration bucket** — keys `1-10`, `11-30`, `31-60`, `>60` (seconds) and `only_agent_turns`. `DEFAULT_VALUES` skips model extraction and uses configured field fallbacks. |
| `secondary_post_call_strategy` | object | four duration buckets use `gpt-5.4-nano`; `only_agent_turns` uses `DEFAULT_VALUES` | Secondary post-call fallback with the same five-key shape. |
| `post_call_analysis_prompt` | string | `""` | How to analyse the transcript. |
| `conversion_reason` | string | `""` | What counts as a conversion. |
| `default_disposition_reason` | string | `""` | Fallback disposition when none is extracted. |
| `useOthersDropOffReason` | bool | `false` | Allow a free-text "Others" drop-off reason instead of forcing a known bucket. |

`postcall[]` entry:

```json
{
  "type": "boolean",
  "name": "appointment_booked",
  "description": "Did the user book an appointment?",
  "defaultValue": false,
  "defaultValueConfig": { "source": "static_value", "key": "", "other": false }
}
```

- `type`: `text` \| `selector` \| `boolean` \| `number` (`selector` = pick one of a known set,
  enumerated in the `description`).
- `name`: `snake_case`; `description` **is** the extraction spec — write it as a question or a
  precise instruction.
- `defaultValue` matches the type (`""` / `0` / `false`) and is used when nothing is extracted.
- `defaultValueConfig.source`: `static_value` (use `defaultValue`) or `call_metadata` (fall back to
  the metadata `key`).

Capability-scoped variables go in `capabilities[i].postcall`; global ones at version level. Global
wins on a name collision when scopes are collapsed. Never restate a node's `extract_variables` here
— one is captured live and steers the call, the other is derived afterwards.
