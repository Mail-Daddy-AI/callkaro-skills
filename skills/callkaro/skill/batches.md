# Batch Calls

A batch = a CSV of leads dialed by an agent. Creating one **starts real calls
immediately** — always show the user the row count and get confirmation first.

## CSV format (critical — validate before creating)

```csv
phone,name,city,x_agent_id
919812345678,Jatin,Delhi,
919811111111,Asha,Mumbai,
```

Rules the server enforces:
1. **Row 1 must be a header.**
2. **Column 1 must be the phone number** (country code included, `+` optional).
3. Every other column becomes per-call **metadata** — the agent's prompt can
   reference these as variables (`name`, `city`, …). Match the variable names
   the agent's prompt actually uses.
4. **An agent is required**: pass `--agent <agentId>`, OR give each row its own
   `x_agent_id` column. Neither → the create is rejected.
5. Optional per-row columns: `x_agent_id` (route rows to different agents),
   `x_language` (per-row language override).
6. Max upload 50 MB.

## Commands

| Command | What it does |
|---|---|
| `ck batches create --file leads.csv --name "Q3 outreach" [--agent <id>] [--language <lang>] [--funnel a,b] [--workflow <id>]` | Upload CSV → create batch → **start dialing**. If the response says the dialer didn't accept it, the batch still exists — fix and use `send-untriggered`. |
| `ck batches schedule --file leads.csv --name X --at "2026-08-05T10:00:00+05:30" [--agent <id>] [--window 10:00-19:00] [--retries 2] [--gaps 30,60] [--carry-over] [--priority n]` | Schedule the batch for a **future time** instead of dialing now. `--window` limits daily calling hours; `--retries`/`--gaps` auto-redial unanswered numbers; rows may override the time with an `x_schedule_at` column. Past datetimes are rejected — use `create` to dial now. |
| `ck batches list [--limit n] [--json]` | Batches with triggered/connected/converted counts and tries. |
| `ck batches get <batchId> [--json]` | One batch summary. |
| `ck batches status <batchId> [--json]` | Progress/distribution (per-try stats, next try, connected count). |
| `ck batches send-untriggered <batchId>` | Dial rows that never got a call (e.g. after a failed trigger). |
| `ck batches send-next-try <batchId> [--max-try n]` | Re-dial not-connected numbers (voicemail/unresponsive/rejected). Defaults `--max-try` to the batch's current tries. |
| `ck batches download <batchId> --type receipts\|triggered\|untriggered\|not-connected [--file out.json]` | Save row-level results. |

No `batches delete` (by design).

## Recommended agent workflow

```bash
# 1. sanity-check the CSV yourself: header row? first column phone numbers?
head -3 leads.csv
# 2. verify the agent exists and is published
ck agents get <agentId> --json
# 3. tell the user: "<N> rows will be dialed by <agent>. Proceed?"
ck batches create --file leads.csv --name "..." --agent <agentId>
# 4. monitor
ck batches status <batchId> --json
ck ongoing status            # live queue; `ck ongoing pause` is the brake
# 5. afterwards
ck batches download <batchId> --type not-connected
ck batches send-next-try <batchId>        # retry the misses (confirm first — more real calls)
```
