# Call Memory & Voice Rotation
<!-- graph-summary: Give an agent memory of earlier calls with the same contact (x_call_history in functions) and switch to a different voice on retries; fields, ck agents memory / voice-rotation commands, usage patterns and traps. -->

Both settings live in the version's `agentMemory` object. Field rules and defaults:
[variables-memory-whatsapp.md](reference/variables-memory-whatsapp.md) §14b. Function-code usage:
[function-code.md](function-code.md). Prompt wording: [prompts.md](prompts.md).

## Call memory — "remember the last call"

When `agentMemory.enabled_for_call` is `true`, in-call, pre-call and post-call **functions** get a
read-only global `x_call_history`: earlier calls with the same contact on the same account, newest
first. It is **off by default**, and it feeds functions only. The prompt does not see it unless a
pre-call function copies something into metadata (`update_call_data`) or a function returns it.

Use it for: follow-ups ("last time you asked for a callback"), retry logic ("skip the pitch if they
already agreed"), not repeating a question already answered, and post-call write-back that needs the
previous disposition.

```bash
ck agents memory <agentId> --versions <vid>                       # show current settings
ck agents memory <agentId> --versions <vid> --enable --max-calls 5 --days 30
ck agents memory <agentId> --versions <vid> --agents all          # also read calls made by the account's other agents
ck agents memory <agentId> --versions <vid> --with-transcript     # only if a function truly needs the words
```

| Flag | Field | Notes |
|---|---|---|
| `--enable` / `--disable` | `enabled_for_call` | Default off. |
| `--max-calls n` | `call_filters.maxCalls` | Default 10. `-1` = all (the backend stops at 200); `0` = none. |
| `--days n` | `call_filters.maxDays` | Default 30 in new agents; `0` = no age limit. |
| `--only-connected` / `--all-calls` | `call_filters.onlyConnected` | Default connected only. `--all-calls` also lists calls nobody answered. |
| `--with-transcript` / `--without-transcript` | `call_filters.includeTranscript` | Default off. Transcripts make every item large; keep off unless needed. |
| `--agents self\|all\|id,id` | `call_filters.additionalAgents` | `self` (default) = this agent only; `all` = every agent on the account; ids = a chosen set (max 50). |

Each item in `x_call_history`: `call_sid, agent_id, version_id, name, direction, from, to, time,
created_at, call_duration, hangup_reason, connected, conversion_status, disposition_reason,
post_call, call_metadata, functions_called, language, batch_id, workflow_id`, plus `transcript` when
enabled. The newest earlier call is `x_call_history[0]`; the list is empty on a first call.

Traps:
- **Test calls get no history.** A dashboard test call has no real contact. Verify with a real call
  to a number that has a previous call, or with a simulation-free manual check of the function code.
- **An empty list is normal.** Always handle `[]`; never index `[0]` without checking.
- **The current call is excluded.** Do not expect the call in progress.
- **Personal data.** Never send the whole list (or any transcript) to an external service; send only
  the fields the API needs. The platform rejects function code that posts it whole.
- `agentMemory` is replaced whole on update — see "Safe editing" below.

## Voice rotation — "retry with a different voice"

When the **previous call to the same contact on the same version** matches a trigger, the next call
speaks with the next voice from `voice_rotation_config.voices` instead of the version's primary
voice. Nothing is stored per contact; the step is derived from the previous call, so it works for
batches, retries and manual calls alike. A match moves one step on; no match returns to the primary
voice.

```bash
ck agents voice-rotation <agentId> --versions <vid>                                   # show
ck agents voice-rotation <agentId> --versions <vid> --enable --voices @voices.json    # default trigger
ck agents voice-rotation <agentId> --versions <vid> --trigger custom --status not_connected \
    --condition hangup_reason:equals:no-answer --on-exhausted cycle
```

`voices.json` is a JSON array of up to **5** complete voice configurations, built the same way as
the primary voice ([voice-and-transcriber.md](voice-and-transcriber.md): resolve real voices with
`ck voices`, never invent ids). Copy each voice's `configuration` object from `ck voices --json`
unchanged. The CLI checks provider and model against the live voice catalogue before saving; the backend
does **not**, so through other paths (raw `--set` on `agentMemory`, MCP) a made-up model is saved silently and
only fails on the retry call. A retry voice is used as is, not merged over the primary; only the call
language carries over when the voice does not set its own.

| Flag | Field | Notes |
|---|---|---|
| `--enable` / `--disable` | `enabled` | Enabling needs at least one voice. |
| `--trigger instant_hangup\|custom` | `trigger.mode` | Default `instant_hangup`: the previous call connected but the contact never spoke (only agent turns). Use it for "they hung up as soon as they heard the voice". |
| `--status connected\|not_connected` | `trigger.previous_call_status` | `custom` only; default `connected`. |
| `--condition source[.field]:op[:value]` | `trigger.conditions[]` | `custom` only; repeat the flag for more (all must match; max 20). Passing any replaces the list. |
| `--clear-conditions` | | Empty the list (custom then matches on status alone). |
| `--voices @file.json` | `voices` | Replaces the list. |
| `--on-exhausted last\|primary\|cycle` | `on_exhausted` | After the last voice: `last` stays on it (default), `primary` goes back to the primary voice, `cycle` restarts from the first retry voice. |

Condition sources: `hangup_reason`, `call_duration` (seconds), `conversion_status` (true/false),
`post_call_variable.<name>`. Operators: `equals`, `not_equals`, `empty`, `not_empty`, `eq`, `gt`,
`gte`, `lt`, `lte` (the last four compare numbers). Examples:
`call_duration:lt:10`, `conversion_status:equals:false`, `post_call_variable.interested:equals:false`,
`post_call_variable.reason:not_empty`.

Traps:
- Rotation follows the **same version**: calls on another version of the agent do not count as the
  previous call.
- `instant_hangup` only matches calls placed after the flag existed; older calls never match.
- Only the voice changes: language, transcriber and script stay the same. Pick retry voices in the
  agent's language and keep the persona gender.

## Safe editing

The backend replaces `agentMemory` whole, so sending `{call_filters: …}` alone **erases**
`voice_rotation_config`, and the reverse. `ck agents memory` and `ck agents voice-rotation` read the
current object, change only the flags you passed and send it all back, so use them. If you must use
`ck agents update --set`, read the version first and send the complete `agentMemory`:

```bash
ck agents get <agentId> --versions <vid> --json   # copy agentMemory, edit, send it all
ck agents update <agentId> --versions <vid> --set '{"agentMemory":{"enabled_for_call":true,"call_filters":{"maxCalls":5,"onlyConnected":true,"maxDays":30,"additionalAgents":{"mode":"self","agentIds":[]},"includeTranscript":false},"voice_rotation_config":{"enabled":false}}}'
```

After any change, run the checks in [verify-and-review.md](verify-and-review.md), and publish the
version when it should go live ([versions.md](versions.md)).
