<!-- graph-summary: Batch call campaigns from a CSV of leads: validate, create, schedule, monitor, retry. Creating one dials real people at once, so confirm row count and spend first. -->
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
4. **An agent is required**: choose one agent for the whole batch, OR give each
   row its own `x_agent_id` column. Neither → the create is rejected.
5. Optional per-row columns: `x_agent_id` (route rows to different agents),
   `x_language` (per-row language override).
6. Max upload 50 MB.

## On the dashboard

The user creates, schedules, monitors and retries batches on the CallKaro
dashboard; there is no harness tool. What a batch can do:

- **Create** uploads the CSV and **starts dialing now**, optionally with a batch
  language, funnel(s) or a workflow attached. If the dialer didn't accept it, the
  batch still exists — fix the cause and send its untriggered rows.
- **Schedule** dials at a **future time** instead. A daily calling window limits
  hours; retries and gaps auto-redial unanswered numbers; rows may override the
  time with an `x_schedule_at` column; carry-over and priority are scheduling
  options too. Past datetimes are rejected — create to dial now.
- **Status** shows progress per try, the next try and the connected count.
- **Send untriggered** dials rows that never got a call (e.g. after a failed trigger).
- **Send next try** re-dials not-connected numbers (voicemail/unresponsive/rejected).
- **Download** saves row-level results: receipts, triggered, untriggered, not-connected.

A batch cannot be deleted (by design).

## Recommended agent workflow

1. Sanity-check the CSV: header row? first column phone numbers? columns match
   the variables the agent's prompt uses?
2. Verify the agent exists and is published (`list_agents`).
3. Tell the user: "<N> rows will be dialed by <agent>. Proceed?" — then the user
   creates the batch on the dashboard.
4. Monitor progress on the dashboard; pausing the live queue is the brake.
5. Afterwards, retrying the misses is more real calls — confirm with the user first.
