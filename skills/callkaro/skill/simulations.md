<!-- graph-summary: Simulation test cases and runs: an LLM caller talks to a version and a judge grades PASS/FAIL. Use to create test cases, run them, and read results before publishing. -->
# Simulations & Test Cases

Simulations let you test an agent **without phone calls** (a batch still spends credits):
an LLM plays the customer (from a test case's `userPrompt`), talks to a chosen
agent **version**, and an LLM judge marks PASS/FAIL against `successCriteria`.
This is the core iteration loop — use it after every prompt change, before
publishing, and before any batch.

## Tools

Load the `simulation` tool group first.

| Tool | What it does |
|---|---|
| `list_simulation_test_cases` (`agentId`) | List the agent's test cases. |
| `create_simulation_test_case` (`agentId`, `testcaseName`, `userPrompt`, `successCriteria`, `testVariables`, `testFunctions`, `testLLMModel`) | Create a test case. `userPrompt` = the simulated customer's persona/goal. `successCriteria` = what the judge checks. Default model `gpt-4.1-mini`. Pauses for the user's approval. |
| `update_simulation_test_case` (`agentId`, `testCaseId`, `updates`) | Edit a test case (only the changed fields). Deleting one is done on the CallKaro dashboard. |
| `start_simulation_batch` (`agentId`, `versionIds`, `testIds`, `batchName`, `epoch`) | Run every test × every version, `epoch` times each (at most 50 runs). **Async** — returns a batch id immediately. Spends credits. |
| `list_simulation_batches` (`agentId`) | List past batches, newest first. |
| `get_simulation_batch_status` (`agentId`, `batchId`) | Progress and PASS/FAIL (`isTestSucceed`) per test×version; no transcripts. |
| `analyze_simulation_batch` / `analyze_simulations` | Pass rates with failing transcripts / why runs failed and the cause in the version. |

**What to write tests for:** [agents/regression.md](agents/regression.md) has
the branch library (happy path, OTP, wrong number, DND, transfer, missing
context, callback, upload error, duplicate, final close) — cover every branch,
and treat the **full suite**, not one case, as the pass/fail gate.

## Writing good test cases

- `userPrompt` is the **customer**, not the agent: *"You are a busy shop owner who
  is skeptical about pricing. You interrupt and push for discounts."*
- `successCriteria` must be judgeable from the transcript: *"The agent states the
  price, handles the discount objection without inventing discounts, and books a
  follow-up."*
- Create several personas: cooperative, skeptical, confused, wrong-number,
  abusive — one test case each.

## Iteration loop (the ai-fde way)

1. `list_versions` → the version id.
2. `start_simulation_batch` with the test ids and that version (confirm the spend).
3. `get_simulation_batch_status` until `isComplete` is true (results arrive
   per run as workers finish; trust `isComplete`).
4. On FAIL: read the judge summary and transcript (`analyze_simulation_batch`
   or `analyze_simulations`), fix the draft (`trigger_single_pipeline`),
   `review_draft`, `save_version_to_db` once the user approves.
5. Re-run the cases, but treat a PASS as a hint, not proof. Simulations run a different model from production
   (which one changes over time), fill `{{metadata}}` from test variables but never run pre-call code (so a
   `{BLOCK}` a pre-call injects is empty), and their judge is unreliable. Confirm the fix on a real test call
   before publishing with `manage_version_publishing`.
