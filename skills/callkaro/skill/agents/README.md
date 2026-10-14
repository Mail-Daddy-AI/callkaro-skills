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
(CLI workflows + starter JSON), [versions.md](versions.md) (publish/A/B),
[voice-and-transcriber.md](voice-and-transcriber.md) (voice + STT choices),
[functions.md](functions.md) (abilities incl. advanced code).

## Prompt types (`systempromptType`)

| Type | Name | Script fields |
|---|---|---|
| 0 | Basic | one `systemprompt` string — **start here unless told otherwise** |
| 1 | Advanced | structured: `role`, `goal`, `callFlow`, `instructions[]`, `guardrails[]`, `rebuttals[]` |
| 2 | Multi-prompt | base `systemprompt` + `capabilities[]` (named sub-prompts the call switches between) |
| 3 | Pathways | graph of `capabilities[]` nodes with `transitions[]`, `extract_variables[]`; type-1 fields must stay empty |

## Minimum viable agent

1. A script for its type (e.g. `systemprompt` for type 0)
2. `voice_configuration` + `transcriber`
3. An LLM `model` (types 0/1) or per-node `llms` (types 2/3)

Everything else has sane defaults.

## Commands

| Command | Does |
|---|---|
| `ck agents list [--json]` | all agents: name, id, status, numbers, published versions |
| `ck agents get <id> [--json]` | agent-level fields only (no version data) |
| `ck agents get <id> --versions <vid> --json` | ONE merged agent+version JSON — the full working config |
| `ck agents versions <id> [--json]` | version list: name, id, language, type, active |
| `ck agents create [json\|--file f.json]` | create from a single JSON object (`name` required; `versionName` defaults `v1`). **The new agent is immediately published.** |
| `ck agents clone-version <id> --versions <sourceVid> --name <name> --prompt-type <0-3> --language <code>` | clone a source into a sibling version under the same agent; see [versions.md](versions.md) |
| `ck agents update <id> --set '{json}' [--versions <vid>] [--commit "msg"]` | patch fields; see [create-update.md](create-update.md) for the level split |
| `ck agents export <id> [--versions <ids>] [--file out.json]` | sanitized JSON (ids/publish state stripped, `x_agent_id` added) — re-importable |
| `ck agents import file.json [--dry-run]` | object → one agent; array → one agent with several versions. Validates like the web importer first |
| `ck agents publish <id> --versions <vid>` | publish (per-language; replaces that language's published version) |
| `ck agents toggle-active <id> --versions <vid>` | activate/deactivate a version |
| `ck agents ab <id> --versions "v1=60,v2=40"` / `--disable` | A/B traffic split (≥2 versions, ratios sum to 100) |
| `ck agents ab-advanced <id> --rules @rules.json` / `--show` / `--disable` | **rule-based A/B**: if/elseif/else on call metadata → version or language (see [versions.md](versions.md)) |
| `ck agents set-inbound / set-outbound <id> --number <nId>` | phone assignment — see [../numbers.md](../numbers.md) |

## Rules the server enforces (expect these errors)

- Version-level fields in `update` without `--versions <vid>` → 400
  *"Version ID is required to update version-specific fields."*
- An inbound number already inbound on another agent → 409.
- A published or A/B version cannot be deactivated or deleted.
- Functions whose `type` starts with `whatsapp` are stripped on import unless
  the source agent belongs to the same owner.
- `userId` is always taken from the token — never send it.
