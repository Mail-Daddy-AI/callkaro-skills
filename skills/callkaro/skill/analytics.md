# Analytics

Three views, mirroring the dashboard. Default window when no dates are given:
the last ~6 days. Dates are `YYYY-MM-DD`.

| Command | What you get |
|---|---|
| `ck analytics overview [--json]` | Account totals: `total_calls`, `total_minutes`, `avg_minutes_per_call`, `total_credits`, `avg_credits_per_call`, `avg_credits_per_minute` (+ day-wise series and hangup-reason distribution in `--json`). |
| `ck analytics performance [--start] [--end] [--json]` | Per-agent rows: `total_calls`, `connected_calls`, `converted_calls`, `receipt_to_conversion_pct`, `connected_to_conversion_pct`. Keyed by agent id — join names via `ck agents list --json`. Excludes test calls. |
| `ck analytics version <agentId> [--versions <ids>] [--start] [--end] [--json]` | Per-version totals + conversion % for one agent — **the A/B test scorecard**. `--json` adds daily series, duration buckets, drop-off reasons, post-call variable counts. |

Overview filters: `--agent <ids>` · `--versions <ids>` · `--type <call types>` ·
`--voice-provider <p>` · `--llm-model <m>` · `--connected true|false` ·
`--batch true|false` · `--start` · `--end`.

## Answering common questions

- *"How is my agent doing?"* → `performance` (find the agent's row), then
  `version <agentId>` for the per-version story.
- *"Which A/B version wins?"* → `analytics version <agentId> --json`, compare
  `overall_connected_to_conversion_pct` between the version rows; also check
  `ck batches status` if the test ran inside a batch.
- *"What are calls costing?"* → `overview --json` → credits totals/averages.
- *"Why are calls failing?"* → `overview --json` → `hangup_reason_distribution`;
  drill in with `ck calls list --hangup <reason>`.
