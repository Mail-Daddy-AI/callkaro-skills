# Chat Simulations & Test Cases
<!-- graph-summary: Entry point for testing a WhatsApp chat agent with simulations: which voice phases to reuse and what changes for chat, the chat test templates, the run-and-read order, and the release gate. -->

Use this to build, run and read a simulation suite for a **chat agent**. The
method is the same as the voice suite in
[Simulations & Test Cases](../simulations/simulation-playbook.md); this page
lists what changes for chat. Read
[How chat simulation works](how-chat-simulation-works.md) first, every time.

## Before anything

1. Confirm the agent is a WhatsApp Basic, Advanced or Workflow agent
   (`ck chat-agents get <chatAgentId> --json`: `channel` and `agentMode`). If
   not, stop: it cannot be simulated. For a Workflow, read
   [Workflow agents](how-chat-simulation-works.md#workflow-agents) first: its
   code steps are mocked by key.
2. List existing tests (`ck chat-sim tests <chatAgentId>`) so you extend the
   suite rather than duplicate it.

## The phases, for chat

| Phase | Reuse | What changes for chat |
|---|---|---|
| A. Profile | [profile-the-bot.md](../simulations/profile-the-bot.md) | Read `chatAgentSystemPrompt` (Basic) or the persona and flow steps (Advanced), `functions`, `followUpFunctions` and models. There are no pre-call variables, transcriber or voice settings. |
| B. Lint | [lint-config-and-prompt.md](../simulations/lint-config-and-prompt.md) | Skip voice items (opening line, end-call, transfer, language switch by speech). Check every function description is a clear trigger, every `send_template` variable has a `varDescriptions` entry or is pinned in `varSources`, every media link is pinned or described, and the prompt says what to do when a function fails. |
| C. Classify | [plan-the-suite.md](../simulations/plan-the-suite.md) | Manual-QA list: agent-first messages (C1), a filled CRM contact other than the shared `0000000000` test contact (C4), real side effects of sends and functions (C3), scheduled follow-ups, media the user sends. |
| D–E. Derive, prioritise | [plan-the-suite.md](../simulations/plan-the-suite.md) | Same tiers and epoch question. Ask the user about epochs before running — runs cost credits (C12). |
| F. Write | below | The voice templates apply with the substitutions below. |
| G. Self-review | [self-review.md](../simulations/self-review.md) | Plus: every custom function the scenario touches has a mock entry (C6), and any mock switched off is safe to run for real (C5). |
| H. Run and read | below | Read results in the order below. |

## Writing a chat test

- **Name**: `[P0] <capability> - <scenario>` as in [6.1](../simulations/write-tests.md#61-name).
- **user_persona**: who is messaging and how they write on WhatsApp — short
  messages, typos, Hinglish, emojis — when the real users do.
- **user_prompt**: the user's goal, the beats in order, what they refuse or
  push back on, and when to stop. The user speaks first (C1), so give their
  opening line. Do not let the user end the chat before the agent has had
  the chance to close, unless the test is about leaving.
- **success_criteria**: numbered PASS lines, each observable in the
  transcript, then FAIL lines. Name functions explicitly: "calls
  `get_order_status` with the order id the user gave", "does not call
  `send_payment_link` before the user confirms". Always add:
  - FAIL if the agent states a fact that no function result or prompt line supports.
  - FAIL if the agent asks again for information the user already gave.
  - FAIL if the agent replies outside the language the user is writing in, unless told to.
  Write a send as what the customer receives — "sends the price list document
  with a one-line caption" — not as a call with arguments: a send never reaches
  the grader as one, and the file's link is never shown to it (C8, C13).
- **function_mocks**: one per custom function the scenario touches, shaped
  like the real response. To test a failure path, mock the failure
  (`{"status":"error","message":"Order not found"}`) in its own test (C7).
  Leave mocks on. Set `"enabled": false` only to exercise a function's real
  code end to end, and only when calling it for real is safe (a read-only
  lookup or a test endpoint): its API calls and side effects really happen
  (C5). Say so in the test name, e.g. `[P1] Order status - live lookup`.

Example:

```bash
ck chat-sim create <chatAgentId> \
  --name "[P0] Order status - order not found" \
  --persona "A customer who ordered shoes last week. Writes short Hinglish messages." \
  --prompt "Open with: 'mera order kahan hai?'. Give order id 48213 when asked. When told it is not found, ask what to do next. End once you have a next step." \
  --criteria "PASS if all hold: 1. Asks for the order id before looking anything up. 2. Calls get_order_status with 48213. 3. Says the order was not found without inventing a status. 4. Offers a concrete next step. FAIL if it states a delivery date or status." \
  --mocks '[{"name":"get_order_status","response":{"status":"error","message":"Order not found"}}]'
```

## Run and read

1. Smoke-run one P0 test with 1 epoch on the target version; check the
   transcript looks like a real chat before running the suite.
2. Run the suite: `ck chat-sim run <chatAgentId> --tests <ids> --versions <ids> --epochs <n>`.
   To compare versions, pass the published version and the candidate together.
3. Wait until the result count equals `number_of_runs` (C11).
4. Read in this order, for every run:
   1. **Validity**: GRADING FAILED (empty `post_simulation`) → INVALID, rerun (C10).
      User drifted off its script (`userPerformance`, or read it yourself) → fix the test.
   2. **Mechanics**: the expected functions were called with the right
      arguments, and none were left without a mock entry (C6). A function
      whose mock is off returned its real result (C5) — read it before
      blaming the agent.
   3. **Verdict**: `successRating` ≥ 7 is PASS; read `successFlaws` on every FAIL.
5. Triage each failure to one owner (prompt, function, test) as in
   [8.2](../simulations/run-triage-report.md#82-triage-every-failure-to-exactly-one-owner),
   fix in a **new version** ([Chat agents → Versions](../chat-agents.md#versions)),
   and rerun old and new side by side before publishing.

**Release gate**: every P0 passes on every epoch, P1 meets its pass rule, and
no run is left INVALID.
