# Interfaces
<!-- graph-summary: Test case fields, the MCP tools and ck sim commands, and the check that the CLI can send mocks, variables and epochs before you use it. -->

You can work through the CallKaro MCP tools or the `ck` CLI. The fields matter more than the interface.

## 2.1 Test case fields

| Field | Purpose | Required by this skill |
|---|---|---|
| `testcaseName` | Name in the fixed format ([6.1](write-tests.md#61-name)) | Yes |
| `userPrompt` | Instructions to the simulated caller | Yes |
| `successCriteria` | Numbered checks for the grader | Yes |
| `testVariables` | Values for every `{{variable}}` and every pre-call output field | Yes, whenever the version uses any variable |
| `testFunctions` | Mocks: `[{ "name": "<exact function name>", "response": <object> }]` | Yes, whenever the version has any in-call function |
| `testLLMModel` | Model that plays the caller | Yes: use one strong model (at least `gpt-4.1`) for the whole suite |

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
| `ck sim create <agentId> --name … --prompt … --criteria … [--model …]` | Create a test |
| `ck sim delete <testCaseId> [--yes]` | Delete a test |
| `ck sim run <agentId> --tests <ids> --versions <ids> [--name …]` | Start a run (async) |
| `ck sim runs <agentId> [--json]` | List runs |
| `ck sim results <runId> --json` | Read results with transcripts |

Before creating tests with the CLI, run `ck sim create --help` and `ck sim run --help` and check that you
can pass `testVariables`, `testFunctions` and epochs. **If the CLI cannot send mocks or variables, do not
create tests that need them through the CLI.** Use the MCP `create_test_case` tool instead, or stop and report
the gap. A test without its mocks is worse than no test, because it passes or fails for the wrong reason ([F4](how-simulation-works.md#12-verified-behaviour-you-must-design-around)).
If the CLI cannot set epochs, use the MCP `create_simulation_run` tool for gated runs.
