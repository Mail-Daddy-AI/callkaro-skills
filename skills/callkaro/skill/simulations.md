# Simulations & Test Cases

Simulations let you test an agent **without phone calls or credits-per-minute**:
an LLM plays the customer (from a test case's `userPrompt`), talks to a chosen
agent **version**, and an LLM judge marks PASS/FAIL against `successCriteria`.
This is the core iteration loop — use it after every prompt change, before
publishing, and before any batch.

## Commands

| Command | What it does |
|---|---|
| `ck sim tests <agentId> [--json]` | List the agent's test cases. |
| `ck sim create <agentId> --name <n> --prompt <p> --criteria <c> [--model <m>]` | Create a test case. `--prompt` = the simulated customer's persona/goal. `--criteria` = what the judge checks. Default model `gpt-4.1-mini`. |
| `ck sim delete <testCaseId> [--yes]` | Delete a test case. |
| `ck sim run <agentId> --tests <id,id> --versions <id,id> [--name <runName>]` | Run every test × every version. **Async** — returns a run id immediately. |
| `ck sim runs <agentId> [--json]` | List past runs. |
| `ck sim results <runId> [--json]` | Results: PASS/FAIL (`isTestSucceed`) + judge summary per test×version. `--json` includes the full `transcript`. |

**What to write tests for:** [agents/regression.md](agents/regression.md) has
the branch library (happy path, OTP, wrong number, DND, transfer, missing
context, callback, upload error, duplicate, final close) — cover every branch,
and treat the **full suite**, not one case, as the pass/fail gate.

## Writing good test cases

- `--prompt` is the **customer**, not the agent: *"You are a busy shop owner who
  is skeptical about pricing. You interrupt and push for discounts."*
- `--criteria` must be judgeable from the transcript: *"The agent states the
  price, handles the discount objection without inventing discounts, and books a
  follow-up."*
- Create several personas: cooperative, skeptical, confused, wrong-number,
  abusive — one test case each.

## Iteration loop (the ai-fde way)

```bash
ck agents versions <agentId> --json                    # version id
ck sim run <agentId> --tests <t1,t2,t3> --versions <v>
# results arrive asynchronously — poll:
ck sim results <runId> --json          # empty list = still running; re-check in ~30s
# on FAIL: read the judge summary + transcript, fix the prompt:
ck agents update <agentId> --set '{"systemprompt":"..."}' --versions <v> --commit "fix objection handling"
ck sim run ...                          # re-run until PASS
ck agents publish <agentId> --versions <v>
```

Results appear per-simulation as Python workers finish; there is no run-status
flag — an empty `results` list simply means nothing has completed yet.
