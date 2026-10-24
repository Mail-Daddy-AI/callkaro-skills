# How chat simulation works
<!-- graph-summary: What a chat simulation run does, the verified facts C1–C12 (user speaks first, the 0000000000 test contact, mocks on by default and switchable off to run real code, nothing sent, 7/10 pass mark, grading failures), the Workflow-agent facts W1–W5 (code steps mocked by key, button taps, counters), the test case fields, ck chat-sim commands and MCP tools. Mandatory first read for chat tests. -->

Read this before writing any chat test. It is the chat counterpart of
[How simulation actually works](../simulations/how-simulation-works.md); the
voice facts do not carry over unless they are repeated here.

## What a run is

- Chat simulation is available for **WhatsApp chat agents of type Basic
  (`agentMode: "ai"`), Advanced (`agentMode: "advanced"`) or Workflow
  (`agentMode: "workflow"`)**. Widget flow agents and Instagram agents are not
  simulated. Workflows differ in a few ways: see
  [Workflow agents](#workflow-agents).
- A run is a **text WhatsApp conversation** between two LLMs:
  - the **agent**: the version's real prompt (or Advanced flow), functions and
    chat models, run in test mode;
  - the **simulated user**: driven by `user_persona` + `user_prompt`, played by
    `primary_user_model` (falling back to `secondary_user_model`).
- After the conversation an **LLM grader** — the agent's own chat model — rates
  the transcript against `success_criteria`.
- A run executes **every test case × every version × epochs**. The batch's
  `number_of_runs` is that product.

## Verified facts to design around

| # | Fact | What it means for you |
|---|---|---|
| C1 | The **simulated user sends the first message**; the chat starts empty. | Opening-message and greeting tests need the user's first line scripted. An agent that is meant to message first cannot be tested for that here. |
| C2 | A conversation ends when the agent ends it, the user ends it, the two start repeating each other, it reaches **20 user turns**, or **10 minutes** pass. | Keep each scenario reachable well inside 20 turns. Long multi-step flows belong in several tests. |
| C3 | **Nothing is sent.** Templates, media, contact cards and calls are produced in the transcript but never delivered. CRM writes from functions are dry runs. | Safe to run against production numbers. A function's side effect cannot be checked outside the transcript. |
| C4 | Every run talks as the account's **`0000000000` test contact**, created the first time a simulation needs it. The agent and its functions (`x_contact`, `x_context.contact`) see that contact's attributes; writes to it are dry runs. Test cases have no variables. | To test a prompt that depends on CRM attributes, set them on the `0000000000` lead in the CRM first; they apply to every chat test in the account. Cases that need different contacts per test stay on the manual-QA list. |
| C5 | A custom function **with its mock on** (the default) never runs its real code: it returns `function_mocks[].response`; a plain string becomes `{"status":"success","message":"<string>"}`. A mock with **`"enabled": false`** runs the **real function** instead: its real API calls, the account's real `x_secrets`, `x_contact` = the test contact, `x_context.is_test` = `true`. | Mock every custom function the scenario touches, with the shape the agent expects. Switch a mock off only for a function that is safe to call for real (a read-only lookup, a test endpoint) — its side effects really happen. |
| C6 | A custom function with **no `function_mocks` entry at all returns `{"status":"success","message":"Function executed successfully"}`**. | A missing mock gives fake success and the agent may invent data. Never leave a function the scenario calls without an entry. |
| C7 | A mock is **static**: one response per function, whatever the arguments. | Split "first lookup fails, retry succeeds" into separate tests. |
| C8 | The grader sees every message **and every custom function call with its arguments and result**. A send — template, media, contact card — reaches the grader as the message it produced, never as a call with arguments. | Criteria can and should name the custom function that must (or must not) be called and the arguments it needs. For a send, write the criterion against what the customer receives. |
| C13 | The grader **never sees a media link or a template's header file**. A media send reads `[document] <caption>`, a media header reads `[image]`. | A test can check that a file went out and what was said about it, never *which* file. Pin the link in the function's `sources` / `varSources` so the right file is guaranteed by configuration rather than left to the model and unverifiable here. |
| C9 | The grader returns `successRating` 0–10 plus `agentPerformance`, `userPerformance` and `successFlaws`. **7 or more passes.** | Write criteria so a partial success lands below 7: list each required outcome, and the FAIL conditions. |
| C10 | An **empty `post_simulation`** means the grader produced nothing: the run is neither PASS nor FAIL. | Classify it INVALID and rerun; never count it as a failure of the agent. |
| C11 | Results arrive one by one, written asynchronously. There is no run-status flag. | A run is complete only when the result count equals `number_of_runs`. A just-finished result can take a few seconds to appear. |
| C12 | Runs cost credits (agent, simulated user and grader tokens). Limits: 1–100 epochs, at most 500 runs per batch. | Confirm the run size with the user before starting a large batch. |

## Workflow agents

A Workflow agent ([Workflow chat agents](../chat-agents-workflow.md)) is
simulated the way it runs live: each simulated message walks the workflow, its
sends go into the transcript, and when it reaches an `assign_agent` step the
assigned Basic or Advanced agent replies in the same turn, at its published
version.

| # | Fact | What it means for you |
|---|---|---|
| W1 | **Code steps are mocked by key.** Each returns the `function_mocks[]` entry whose `name` is the step's `key`; with no entry, `{"status":"success","message":"Function executed successfully"}`. A mock with `"status": "error"` takes the failure exit. An entry with `"enabled": false` runs the step's real code, with `x_message`, `x_history`, `x_secrets` and `x_contact` (the test contact) as live. | Mock every code step the scenario reaches, with the fields later steps read as `{{key.path}}`. Test the failure branch with an error mock. Switch one off only when its code is safe to run for real (C5). |
| W2 | The assigned agent's custom functions use the **same `function_mocks`**, by function name. | Put the assigned agent's mocks in the workflow's test case too. |
| W3 | When the simulated user types a button's title from the last interactive message, it counts as a **tap**: `button_id` is that button's id. | Write user prompts that pick options by their exact title. |
| W4 | **Counters count the simulated chat** (the whole chat; `windowHours` is ignored). `last_reply` reads it too. | Counter limits such as "after 3 messages hand off" are testable. |
| W5 | Workflow sends show the **step name** in the transcript; Update contact steps are dry runs. | Criteria can name the step that should have sent a message. |

There is no post-call extraction in chat simulation, and `ended_by` is not
returned with the result — read the last messages to see who ended the chat.

## Test case fields

| Field (CLI / MCP) | Backend field | Purpose |
|---|---|---|
| `--name` / `testCaseName` | `test_case_name` | Scenario name. Required. |
| `--persona` / `userPersona` | `user_persona` | Who the user is: background, tone, what they know. |
| `--prompt` / `userPrompt` | `user_prompt` | What the user wants and how they behave. Instructions for the user, never for the agent. |
| `--criteria` / `successCriteria` | `success_criteria` | Numbered, checkable outcomes for the grader. |
| `--model` / `primaryUserModel` | `primary_user_model` | Model playing the user; a chat-agent model. Defaults to the account's chat-agent default. |
| `--secondary-model` / `secondaryUserModel` | `secondary_user_model` | Optional fallback; must differ from the primary. |
| `--mocks` / `functionMocks` | `function_mocks` | `[{ "name": "<custom function>", "response": <json>, "enabled": true }]`. `enabled` defaults to `true`; `false` runs the real function or code step (C5) and its `response` is kept but unused. Built-in send functions need no mock. |

## CLI

| Command | Use |
|---|---|
| `ck chat-agents list --json`, `ck chat-agents versions <chatAgentId> --json` | Agent and version IDs |
| `ck chat-agents models --json` | Models allowed for the simulated user |
| `ck chat-sim tests <chatAgentId> [--json]` | List test cases |
| `ck chat-sim create <chatAgentId> --name … --persona … --prompt … --criteria … [--model … --secondary-model … --mocks <json\|@file>]` | Create a test case |
| `ck chat-sim update <testCaseId> [same flags]` | Change only the passed fields |
| `ck chat-sim delete <testCaseId> [--yes]` | Delete a test case |
| `ck chat-sim run <chatAgentId> --tests <ids> --versions <ids> [--name … --epochs <n>]` | Start a run (async, spends credits) |
| `ck chat-sim runs <chatAgentId> [--json]` | List runs with `number_of_runs` and total cost |
| `ck chat-sim results <runId> [--json]` | PASS / FAIL / GRADING FAILED per run; `--json` includes transcripts |

## MCP tools

| Tool | Use |
|---|---|
| `list_chat_agents`, `list_chat_agent_versions` | Agent and version IDs |
| `list_llm_models` (category `chat-agent`) | Allowed user models |
| `list_chat_test_cases` | See existing tests before writing new ones |
| `create_chat_test_case`, `update_chat_test_case`, `delete_chat_test_case` | Manage tests |
| `create_chat_simulation_run` | `chatAgentId`, `batchName`, `epochs`, `testCaseIds[]`, `versionIds[]` |
| `list_chat_simulation_runs` | Find runs and `number_of_runs` |
| `get_chat_simulation_results` | Read results (`runId`): `chat_transcript` and `post_simulation[0]` |
