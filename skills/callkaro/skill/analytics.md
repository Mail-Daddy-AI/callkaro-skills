<!-- graph-summary: Account, agent and version performance (calls, connect and conversion rates, minutes, credits) through the call analytics tool. Use to answer how an agent is doing or compare versions after an A/B test. -->
# Analytics

`call_analytics` (`agentId`, `startDate`, `endDate`; load the `calls` tool
group first) returns three views, mirroring the dashboard. Default window when
no dates are given: the last ~6 days. Dates are `YYYY-MM-DD`.

| View | What you get |
|---|---|
| Overview (account) | Account totals: `total_calls`, `total_minutes`, `avg_minutes_per_call`, `total_credits`, `avg_credits_per_call`, `avg_credits_per_minute` (+ day-wise series and hangup-reason distribution). |
| Performance (per agent) | Per-agent rows: `total_calls`, `connected_calls`, `converted_calls`, `receipt_to_conversion_pct`, `connected_to_conversion_pct`. Keyed by agent id — join names via `list_agents`. Excludes test calls. |
| Version (with `agentId`) | Per-version totals + conversion % for one agent — **the A/B test scorecard**, with daily series, duration buckets, drop-off reasons, post-call variable counts. |

Finer overview filters (call type, voice provider, LLM model, connected,
batch) are on the CallKaro dashboard.

## Answering common questions

- *"How is my agent doing?"* → the performance view (find the agent's row),
  then `call_analytics` with `agentId` for the per-version story.
- *"Which A/B version wins?"* → `call_analytics` with `agentId`, compare
  `overall_connected_to_conversion_pct` between the version rows; if the test
  ran inside a batch, the batch's status is on the dashboard.
- *"What are calls costing?"* → the overview → credits totals/averages.
- *"Why are calls failing?"* → the overview → `hangup_reason_distribution`;
  drill in with `list_calls` → `read_call`, or `analyze_calls`.
