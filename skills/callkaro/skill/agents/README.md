<!-- graph-summary: What a voice agent is (LLM, voice, transcriber, prompt, functions, post-call) and the harness tools that act on it. Use as the entry point for any voice-agent task. -->
# Voice Agents — the core entity

A CallKaro **agent** is a phone-calling AI: an LLM + voice (TTS) + transcriber
(STT) + a prompt/script, plus call behavior (turn-taking, silence handling,
functions/tools, post-call analysis). Configuration is split across two levels:

- **Agent** (one doc): name, language, phone-number assignments, publish
  pointers, A/B config, status.
- **Version** (many per agent): *everything else* — the prompt, LLM, voice,
  transcriber, functions, post-call config. You iterate by editing/creating
  versions and publishing the good one. See [versions.md](versions.md).

Read next: **[AGENT-VERSION-REFERENCE.md](AGENT-VERSION-REFERENCE.md) — the complete field reference (every
field, its values, per-provider voice/transcriber sets, functions, pathways,
traps). Load it before writing any agent/version payload.** Then
[prompts.md](prompts.md) (how to write the script), [create-update.md](create-update.md)
(create/edit workflow + starter JSON), [versions.md](versions.md) (publish/A/B),
[voice-and-transcriber.md](voice-and-transcriber.md) (voice + STT choices),
[functions.md](functions.md) (abilities incl. advanced code), [ivr.md](ivr.md) (DTMF menus before the LLM, Pathways only).

## Prompt types (`systempromptType`)

| Type | Name | Script fields |
|---|---|---|
| 0 | Basic | one `systemprompt` string — **start here unless told otherwise** |
| 1 | Advanced | structured: `role`, `goal`, `callFlow`, `instructions[]`, `guardrails[]`, `rebuttals[]` |
| 2 | Multi-prompt | base `systemprompt` + `capabilities[]` (named sub-prompts the call switches between) |
| 3 | Pathways | graph of `capabilities[]` nodes with `transitions[]`, `extract_variables[]`; type-1 fields must stay empty; may start with [IVR nodes](ivr.md) |

## Minimum viable agent

1. A script for its type (e.g. `systemprompt` for type 0)
2. `voice_configuration` + `transcriber`
3. An LLM `model` (types 0/1) or per-node `llms` (types 2/3)

Everything else has sane defaults.

## Tools

| Tool | Does |
|---|---|
| `list_agents` | all agents with each published version per language; pass `name` to find the one the user means |
| `list_versions` | all versions: id, name, language, prompt type, active/published state, A/B use |
| `read_agent_state` | loads one version (the published one when `versionId` is omitted) into the working draft — the full working config |
| `read_version` | selected sections of a saved version or the draft; start with the schema, fetch only what you need |
| `create_agent_in_db` → `trigger_single_pipeline` → `review_draft` → `save_version_to_db` | create an agent and its first version. **The first version is immediately published** for its language |
| `trigger_single_pipeline` (`draftPatch` or `edits`) or `edit_draft_script` → `review_draft` → `save_version_to_db` | change version fields; see [create-update.md](create-update.md) for the level split. A published base version is always saved as a new version, never overwritten |
| `manage_version_publishing` | `publish_version` (per-language; replaces that language's published version), `set_display_version`, `set_status` |
| `read_ab_test_configuration`, `discover_ab_test_metadata`, `manage_ab_testing` | A/B traffic split (≥2 versions, ratios sum to 100) and **rule-based A/B**: if/elseif/else on call metadata → version or language (see [versions.md](versions.md)). Load the ab_testing tools first |
| `list_phone_numbers` → `assign_phone_number` | phone assignment (load the numbers tools) — see [../numbers.md](../numbers.md) |

Export/import (sanitized JSON: ids and publish state stripped, `x_agent_id` added) and
activating/deactivating a version are done on the CallKaro dashboard.

## Rules the server enforces (expect these errors)

- Version-level fields written without a version id → 400
  *"Version ID is required to update version-specific fields."*
- An inbound number already inbound on another agent → 409.
- A published or A/B version cannot be deactivated or deleted.
- Functions whose `type` starts with `whatsapp` are stripped on import unless
  the source agent belongs to the same owner.
- `userId` is always taken from the token — never send it.
