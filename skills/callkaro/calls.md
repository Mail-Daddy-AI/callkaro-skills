# Calls — placing, history, live queues

## Place a single call

```bash
ck calls make --agent <agentId> --to 9198XXXXXXXX [--test] \
  [--var name=Jatin --var city=Delhi] [--metadata '{"lead_id":"42"}'] \
  [--versions <versionId>] [--commit <commitId>]
```

- `--test` marks it a test call — **use this by default** while iterating; omit
  it only when the user explicitly wants a real production call.
- **A real call costs credits and phones a real human. Always confirm with the
  user before running without `--test`.**
- Metadata: repeatable `--var k=v` and/or `--metadata '{json}'` (merged; `--var`
  wins). These become in-call variables the agent's prompt can reference.
- The number format is with country code, `+` optional: `919812345678`.
- Common errors surfaced by the dialer: `VERIFICATION_REQUIRED` (the destination
  number must be OTP-verified first — user does this in the dashboard) and
  `DND_NUMBER` (destination is on Do-Not-Disturb). Relay these to the user.

## Call history

```bash
ck calls list [--limit 50] [--json] [filters…]
ck calls get <callId> [--json]        # one call; --json includes transcript + recording URL
ck calls export [filters…] [--file out.csv] [--email you@x.com] [--fields a,b] [--include-chat]
```

Filters (shared by `list` and `export`, all comma-separable):
`--type inbound,outbound,outbound-api,outbound-scheduled,outbound-test,agent-test`
· `--agent <ids>` · `--versions <ids>` · `--start YYYY-MM-DD` · `--end YYYY-MM-DD`
· `--batch true|false` · `--hangup <reasons>` · `--duration 0,1-10,11-30,31-60,>60`
· `--to <number>` · `--converted true|false` · `--lead <id>` · `--buylead <v>`

Export writes CSV locally; if the dataset is too large the server says so — re-run
with `--email` and it's mailed instead. There is **no call delete** — by design.

Useful JSON fields on a call: `name` (type), `from`, `to`, `agent.name`,
`versionId.versionName`, `call_duration` (s), `hangup_reason`,
`disposition_reason`, `conversion_status`, `total_credits`,
`recording.recordingUrl`, `recording.transcription`, `recording.chat_history`.

## Live queues (ongoing calls)

```bash
ck ongoing status [--json]        # queued call counts + paused state per agent
ck ongoing pause  [--agent <id>]  # pause dialing (whole account, or one agent)
ck ongoing resume [--agent <id>]
ck ongoing clear  [--agent <id>]  # DROP queued calls — destructive, confirm first
```

Use `pause` as the emergency brake when a batch is misbehaving; `clear` throws
the queue away permanently.
