# Audit Strategies (AI Auditor)

An audit strategy scores calls with an LLM against free-text instructions
(`--strategy`), scoped to a subset of an agent's calls via structured filters
(call type, hangup reason, drop-off reason, call duration, boolean postcall
variables). It runs on a schedule, sampling a percentage of eligible calls
each hour.

## Commands

| Command | What it does |
|---|---|
| `ck audit-strategies list <agentId> [--json]` | List existing strategies (name, id, active). Check before creating, to avoid duplicates. |
| `ck audit-strategies get <agentId> <strategyId> [--json]` | Show one strategy in full. |
| `ck audit-strategies filter-options <agentId> [--json]` | Drop-off reasons and boolean postcall filters configured on the agent's versions, plus the platform-wide hangup reason codes. |
| `ck audit-strategies models [--json]` | Audit models this account is allowed to use for `llms`. |
| `ck audit-strategies create <agentId> --strategy <text> [flags] [--set <json>]` | Create a strategy. `--strategy` (or `--set audit_strategy`) is required. |
| `ck audit-strategies update <agentId> <strategyId> [flags] [--set <json>]` | Update a strategy. Only the fields you pass change — the CLI fetches the existing strategy first and merges `audit_filters` onto it, so unrelated filter keys survive. |

Scalar flags on `create`/`update`: `--name`, `--active`, `--model
<provider/name>`, `--pct-per-hour <n>`, `--max-per-hour <n>`,
`--retranscribe`.

There is no `delete` command — intentionally out of scope.

## `--set` carries the structured fields

`audit_filters`, `postcall_filters`, `extra_variables`, and `llms` (if not
using `--model`) are JSON-shaped, not flag-shaped — pass them via `--set
'<json>'` or `--set @file.json` (same convention as `ck agents update --set`).

Create, with structured filters and a boolean postcall filter:
```bash
ck audit-strategies create <agentId> \
  --strategy "Flag calls where the agent quoted a price outside the approved rate card" \
  --set '{
    "audit_filters": { "call_duration": "30-60", "drop_off_reasons": "hung_up_early" },
    "postcall_filters": [{ "name": "asked_pricing", "value": "true" }]
  }'
```

Partial update — changes only `call_duration`, every other `audit_filters` key
(e.g. `name`, `hangup_reasons`) is left as-is:
```bash
ck audit-strategies update <agentId> <strategyId> \
  --set '{ "audit_filters": { "call_duration": "0-10" } }'
```

## Never invent a filter, model, or version value

Always run `ck audit-strategies filter-options <agentId>` and
`ck audit-strategies models` first, and only use values they return —
`drop_off_reasons`, `postcall_filters` names, and `llms` must come from
those, never guessed. `version_ids` (inside `audit_filters`) come from
`ck agents versions <agentId> --json`.
