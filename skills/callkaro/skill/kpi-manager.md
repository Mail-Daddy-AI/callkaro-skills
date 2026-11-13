# KPI Manager
<!-- graph-summary: KPI Manager per voice agent: data sources, KPI metrics with targets, the RCA prompt and model, Auto RCA, the scheduled KPI report (recipients, IST window, gap), RCA preview and on-demand runs, metric history, report preview, PDF export and delivery log; the ck kpi commands and the rules for safe edits. -->

KPI Manager tracks business numbers for one voice agent. **Data sources**
supply values, **KPI metrics** compare a value with a target, and when a metric
misses its target an **RCA** (root-cause analysis) explains why. A separate
**KPI report** can be emailed on a schedule. Everything is configured per
agent, keyed by the voice agent id (`ck agents list`). Chat agents have no KPI
Manager.

## Commands

| Command | What it does |
|---|---|
| `ck kpi list [--json]` | Agents that already have KPI Manager set up. |
| `ck kpi get <agentId> [--json] [--file cfg.json]` | Whole config: data sources, metrics, RCA prompt/model, Auto RCA, Auto Report, report schedule. `--file` saves JSON you can edit and send back. |
| `ck kpi update <agentId> [--set <json\|@file>] [flags]` | Change the config. Only the fields you pass change. |
| `ck kpi delete <agentId> [--yes]` | Delete the agent's whole KPI Manager config. Cannot be undone. |
| `ck kpi history <agentId,agentId…> [--start] [--end] [--json]` | Daily actual % vs target % per metric (default: last 30 days). |
| `ck kpi rca-preview <agentId> [--prompt <text>] [--model <name>] [--lookback-days <n>]` | What the RCA prompt compiles to and how many calls it matches. Read-only. |
| `ck kpi rca-run <agentId> --start <date> [--end <date>] [filters] [--yes]` | Run RCA now. **Uses credits** — confirm with the user first. Results land in RCA History on the dashboard. |
| `ck kpi report preview <agentId> [--start] [--end] [--report <idOrName>] [--set <json>] [--json]` | Compute a report's values for a window. Sends nothing. |
| `ck kpi report export <agentId> [--start] [--end] [--report] [--set] [--file out.pdf]` | Save the report as a PDF. |
| `ck kpi report deliveries <agentId> [--json]` | Last 30 scheduled sends: slot, window, status, attempts, recipients, error. |
| `ck kpi report check-expression <agentId> '<expr>' [--unique] [--start] [--end] [--post-call a,b] [--metadata k1,k2]` | Test a custom-variable expression against real calls. |

`ck kpi-manager` is an alias of `ck kpi`. All dates are `YYYY-MM-DD` in IST.

MCP has the same through `get_kpi_manager_info`, `update_kpi_manager`,
`delete_kpi_manager`, `preview_kpi_rca_prompt`, `run_kpi_rca`,
`preview_kpi_report` and `check_kpi_expression` (no PDF export; use the CLI
or the dashboard).

## `update`: flags and `--set`

Scalar flags:

| Flag | Field |
|---|---|
| `--rca-prompt <text>` | `rca_prompt` (max 10,000 chars; `""` clears it, so RCA covers all calls and metrics) |
| `--rca-model <name>` | `rca_model` + `rca_llms` (provider is worked out from the name; `""` uses the default) |
| `--auto-rca on\|off` | `nightly_rca_enabled` — nightly RCA email when a metric misses its target |
| `--auto-report on\|off` | `report_enabled` — scheduled KPI report email. Turning it on needs at least one recipient |
| `--recipients a@x.com,b@x.com` | `report_config.recipients` (max 10) |
| `--report-window 08:00-20:00` | `report_config.min_trigger_time` / `max_trigger_time` (IST) |
| `--report-every <hours>` | `report_config.interval_hours`. Under 24: sends at min, min+gap … up to max, every day. 24 or more: whole days only, sends once at the min time and the max time is ignored |

RCA models: `gpt-5.6-luna` (default), `gpt-5.6-sol`, `callkaro/krishna-2.5`,
and the two Claude Bedrock ARNs the dashboard lists. Copy a model name from
`ck kpi get <agentId> --json` or from the dashboard; never invent one.

`--set` takes the structured fields: `api_endpoints`, `python_data_sources`,
`expression_data_sources`, `kpi_metrics`, `rca_prompt`, `rca_model`,
`rca_llms`, `nightly_rca_enabled`, `report_enabled`, `report_config`. Unknown
keys are refused (`agentId` is ignored, so `get --json` output can be sent
back).

**Each list replaces the saved list.** Sending `kpi_metrics` with one metric
deletes the others. To add or change one item, fetch, edit, send the whole list:

```bash
ck kpi get <agentId> --file kpi.json
# edit kpi.json — keep every existing item you are not removing
ck kpi update <agentId> --set @kpi.json
```

`report_config` is different: the CLI merges the keys you send onto the saved
`report_config`, so `--set '{"report_config":{"recipients":["a@x.com"]}}'`
leaves the report layouts alone.

## Data sources

API Endpoint, Python Code and Expression source names share one namespace and
must be unique.

**API endpoint** (`api_endpoints[]`) — called once per batch of calls with the
phone numbers involved. Response must be `{ "data": { … } }`.

```json
{ "name": "crm", "url": "https://example.com/kpi", "method": "POST",
  "headers": [{ "key_name": "X-Api-Key", "value": "<ask the user>" }],
  "parameters": [{ "key_name": "phone_number", "value": "user_phone_number" }] }
```

Keep the `phone_number` parameter first. Headers are sent exactly as saved:
the account-secret references used in agent functions
([Account Secrets](secrets.md)) are **not** resolved here. Never ask for a
credential in chat or echo one back; have the user add the header value in
the dashboard, or write it into the `--set @file` themselves.

**Python code** (`python_data_sources[]`) — `{ name, parameters, source_code }`.
The code must be `async def generate_kpi_data(payload: list) -> dict:`;
`payload` is one entry per lead, the return is one flat dict, `httpx` is
available without importing. A CLI save does not run the dashboard's code
review. The code runs in a restricted sandbox (no `import`, limited builtins,
CPU, memory and time limits), so a mistake only shows up when the nightly run
fails. Keep the code within those rules and never hard-code a credential.

**Expression source** (`expression_data_sources[]`) — counts calls that pass a
test: `{ name, mode: "expression", expression, equals: true, consider_for:
"all" }` (`consider_for`: `all`, `connected`, `converted`, `unique`,
`unique_connected`). Test the expression with `check-expression` first.

## KPI metrics

`kpi_metrics[]` items are `{ "name", "source", "value" }`: a descriptive name
(the RCA reasons about it), where the value is read from, and the target %.

| Source type | Returns | `source` |
|---|---|---|
| API endpoint `crm` | `{ data: { conversion_rate: 85 } }` | `crm.data.conversion_rate` |
| Python source `budget` | `{ l2s: 5.4 }` | `budget.l2s` |

`connected_to_conversion_percentage` is built in (connected calls that
converted). Keep it in the list with `name` and `source` both set to that
name; only change its `value`.

## RCA

Before saving a new RCA prompt, run `ck kpi rca-preview <agentId> --prompt
"…"`. Read `scope`, `dropped` (parts that could not be applied) and
`matching_calls`. Zero matches or a dropped filter means the nightly RCA would
analyse nothing useful — reword before saving.

`rca-run` filters: `--type` (inbound, outbound, outbound-api,
outbound-scheduled), `--hangup-reasons`, `--versions`, `--batch true|false`,
`--duration 1-10,31-60`, `--converted true|false`, `--lead-id`; boolean
post-call filters go in `--set '{"postcall_<name>":"true"}'`. Take hangup
reasons and post-call names from `ck audit-strategies filter-options
<agentId>` and versions from `ck agents versions <agentId> --json`
([Audit Strategies](audit-strategies.md)).

## KPI report

| Auto RCA | Auto Report | Emailed |
|---|---|---|
| off | off | nothing |
| on | off | RCA email only, when a metric misses |
| off | on | KPI report on its schedule, to the report recipients |
| on | on | both; RCA emails also carry that day's KPI report PDF |

- Build and lay out reports (charts, tables, text, custom variables) in the
  dashboard's report builder. From the CLI, change the schedule and
  recipients, turn Auto Report on or off, and preview or export what is saved.
- Without `--start`, preview/export use the latest scheduled window. `--report`
  picks a saved report other than the primary (scheduled) one.
- Turning Auto Report on, or changing the schedule, never sends a report for
  a time already past.
- There is no CLI test-send. Use `report preview` / `report export` to check
  the content.

## Rules

- Run `ck kpi get <agentId> --json` before any update, and send whole lists.
- Confirm with the user before `rca-run` (credits), `delete`, and turning
  `--auto-report on` (emails real recipients).
- Never invent emails, model names, field names or filter values.
- `history` is empty until a nightly evaluation has run for that agent.
