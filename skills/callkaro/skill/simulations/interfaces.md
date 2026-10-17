# Interfaces
<!-- graph-summary: Test case fields, the MCP tools and ck sim commands, including `userPersona`, mocks, variables, epochs and the default caller model. -->

You can work through the CallKaro MCP tools or the `ck` CLI. The fields matter more than the interface.

## 2.1 Test case fields

| Field | Purpose | Required by this skill |
|---|---|---|
| `testcaseName` | Name in the fixed format ([6.1](write-tests.md#61-name)) | Yes |
| `userPersona` | Who the caller is: identity, background, language and tone, what they know and do not know. Joined ahead of `userPrompt` | Yes |
| `userPrompt` | Instructions to the simulated caller | Yes |
| `successCriteria` | Numbered checks for the grader | Yes |
| `testVariables` | Values for every `{{variable}}` and every pre-call output field | Yes, whenever the version uses any variable |
| `testFunctions` | Mocks: `[{ "name": "<exact function name>", "response": <object> }]` | Yes, whenever the version has any in-call function |
| `testLLMModel` | Model that plays the caller. Omit for the platform default; list allowed ones with `list_llm_models` (category `simulation`) or `ck sim models` | Use one model for the whole suite; the platform default is fine |

## 2.2 MCP tools

| Tool | Use |
|---|---|
| `inspect_agent_version` | Profile the version (phase A) |
| `list_agent_versions`, `get_agent` | Find version IDs |
| `list_test_cases` | See existing tests before writing new ones |
| `create_test_case`, `update_test_case`, `delete_test_case` | Manage tests |
| `create_simulation_run` | `agentId`, `batchName`, `epoch`, `testIds[]`, `versionIds[]` |
| `list_simulation_runs` | Find runs and `totalRuns` |
| `get_simulation_results` | Read results (`batchId` = run ID) |
| `generate_simulation_reply` | Get one agent reply for a given chat history and metadata. Useful for quickly checking a single risky turn while debugging; not a substitute for a test. |

## 2.3 CLI

| Command | Use |
|---|---|
| `ck agents versions <agentId> --json` | Version IDs |
| `ck sim tests <agentId> [--json]` | List tests |
| `ck sim create <agentId> --name … --prompt … --criteria … [--persona … --model … --variables <json\|@file> --functions <json\|@file>]` | Create a test (mocks and variables supported) |
| `ck sim update <testCaseId> [same flags]` | Change only the passed fields |
| `ck sim models` | Allowed caller models and the default |
| `ck sim delete <testCaseId> [--yes]` | Delete a test |
| `ck sim run <agentId> --tests <ids> --versions <ids> [--name … --epoch <n>]` | Start a run (async) |
| `ck sim runs <agentId> [--json]` | List runs |
| `ck sim results <runId> --json` | Read results with transcripts |

The CLI can send `testVariables`, `testFunctions` and epochs, so it is as capable as MCP for building and running tests.
