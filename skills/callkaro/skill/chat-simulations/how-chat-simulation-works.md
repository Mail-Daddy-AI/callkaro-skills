# How chat simulation works
<!-- graph-summary: What a chat simulation run does, the verified facts C1–C12 (user speaks first, default mocks, no contact record, nothing sent, 7/10 pass mark, grading failures), the test case fields, ck chat-sim commands and MCP tools. Mandatory first read for chat tests. -->

Read this before writing any chat test. It is the chat counterpart of
[How simulation actually works](../simulations/how-simulation-works.md); the
voice facts do not carry over unless they are repeated here.

## What a run is

- Chat simulation is available for **WhatsApp chat agents of type Basic
  (`agentMode: "ai"`) or Advanced (`agentMode: "advanced"`)**. Chat Center
  Workflows, widget flow agents and Instagram agents are not simulated.
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
| C4 | There is **no contact record**: the agent sees an empty contact, and test cases have no variables. | A prompt that depends on CRM attributes (name, lead stage) is tested against blanks. Put "has a filled contact" cases on the manual-QA list, or test them in the dashboard's Test Chat with a real number. |
| C5 | **Custom functions never run their real code.** A mocked function returns its `function_mocks[].response`; a plain string becomes `{"status":"success","message":"<string>"}`. | Mock every custom function the scenario touches, with the shape the agent expects. |
| C6 | An **unmocked custom function returns `{"status":"success","message":"Function executed successfully"}`**. | A missing mock gives fake success and the agent may invent data. Never leave a function the scenario calls unmocked. |
| C7 | A mock is **static**: one response per function, whatever the arguments. | Split "first lookup fails, retry succeeds" into separate tests. |
| C8 | The grader sees every message **and every function call with its arguments and result**. | Criteria can and should name the function that must (or must not) be called and the arguments it needs. |
| C9 | The grader returns `successRating` 0–10 plus `agentPerformance`, `userPerformance` and `successFlaws`. **7 or more passes.** | Write criteria so a partial success lands below 7: list each required outcome, and the FAIL conditions. |
| C10 | An **empty `post_simulation`** means the grader produced nothing: the run is neither PASS nor FAIL. | Classify it INVALID and rerun; never count it as a failure of the agent. |
| C11 | Results arrive one by one, written asynchronously. There is no run-status flag. | A run is complete only when the result count equals `number_of_runs`. A just-finished result can take a few seconds to appear. |
| C12 | Runs cost credits (agent, simulated user and grader tokens). Limits: 1–100 epochs, at most 500 runs per batch. | Confirm the run size with the user before starting a large batch. |

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
| `--mocks` / `functionMocks` | `function_mocks` | `[{ "name": "<custom function>", "response": <json> }]`. Built-in send functions need no mock. |

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
