<!-- graph-summary: Every harness tool by job (find, read, edit, save, publish, test, calls, numbers, chat agents, research), the tool groups to load, and what only the dashboard can do. Read to pick the tool for a task. -->
<!-- audience: harness -->

# Harness tool map

You act only through these tools. The account is always the signed-in session's; never pass a user or account
id yourself. A task with no tool cannot be done from here: say so and tell the user it is done on the CallKaro
dashboard; never pretend it was done.

Tools in a group are not available until you load the group with `load_tools`: `simulation`, `ab_testing`,
`numbers`, `voices`, `calls`, `research`, `languages`, `chat_agents`, `skills` (this library and `read_skill`).

Approvals are handled by the harness: saving a version, creating an agent's first version, publishing, A/B
changes, phone-number changes, simulation test cases and starting a batch all show the change and wait for the
user.

## Find and read a voice agent

| Job | Tool |
|---|---|
| Find the agent the user means | `list_agents` (pass `name` as they said it; several matches: ask) |
| Its versions, published state, A/B use | `list_versions` |
| Load a version into the working draft | `read_agent_state` (no `versionId` = the published one; `useAsTemplate` for another agent used only as a pattern) |
| Read sections of a saved version or the draft | `read_version` (start with `schema`, then only the sections you need) |
| Reference versions across the account | `search_versions` (research group) |
| A question that needs many reads | `investigate` |

## Build and edit the draft

| Job | Tool |
|---|---|
| New agent | `create_agent_in_db`, then write its fields into the draft |
| Write or change fields | `trigger_single_pipeline` (`draftPatch` for fields you wrote; `edits` for one node, function or snippet) |
| The same change in many places | `edit_draft_script` (Python, jq or sed over /draft/version.json) |
| Several languages at once | `trigger_parallel_pipeline` (`lanePatches`), then `read_parallel_drafts` (languages group) |
| Build from a BRD | `extract_requirements`, `write_unit`, `write_units`, `update_requirements`: [BRD build](../harness/brd-build.md) |
| Check the draft before saving | `review_draft` |
| Save | `save_version_to_db`: a published base is always saved as a new version, never overwritten ([editing drafts](../harness/editing-drafts.md)) |

## Plan, decide, look up

| Job | Tool |
|---|---|
| Get a plan approved or ask questions | `present_plan_and_questions` |
| Remember a user decision | `record_decision` |
| Search large results, the draft, the skills | `query_context`; page through one result with `read_context_handle` ([large results](../harness/large-results.md)) |
| Read a skill node or section | `read_skill` |
| Facts about the client's business | `web_search` (research group) |

## Go live

| Job | Tool |
|---|---|
| Publish a version, set status or display version | `manage_version_publishing` (only when the user asks) |
| A/B tests | `read_ab_test_configuration`, `discover_ab_test_metadata`, `manage_ab_testing` (ab_testing group) |
| Phone numbers | `list_phone_numbers`, then `assign_phone_number` (numbers group) |
| WhatsApp readiness and templates | `check_whatsapp_readiness` (numbers group) |
| Voices | `list_voices` (voices group) |

## Test and debug

| Job | Tool |
|---|---|
| Test cases | `list_simulation_test_cases`, `create_simulation_test_case`, `update_simulation_test_case` (simulation group) |
| Run and follow a batch | `start_simulation_batch` (spends credits), `list_simulation_batches`, `get_simulation_batch_status` |
| Why runs failed | `analyze_simulation_batch` (evidence), `analyze_simulations` (causes and fixes) |
| Real calls | `list_calls`, `read_call`, `call_analytics`, `analyze_calls` (calls group): [call debugging](../harness/call-debugging.md) |

## Chat agents (WhatsApp bots)

`list_chat_agents`, `get_chat_agent`, `list_chat_agent_versions`, `list_chat_agent_models`, `create_chat_agent`,
`create_chat_agent_version`, `update_chat_agent`, `publish_chat_agent_version` (chat_agents group). Experiment in a
version made with `create_chat_agent_version`, never on the live one. See [chat agents](../chat-agents.md).

## Only on the dashboard

Placing calls, raw call logs and exports, live-call controls, batches, contacts, workflows, secrets, audit
strategies, buying or releasing numbers, WhatsApp inbound assignment, creating or managing WhatsApp templates
(reading approved ones is `check_whatsapp_readiness`), agent export and import, activating or deactivating a
version, renaming an agent and its other agent-level fields, chat-agent simulations, talking to an agent in text,
and the transcriber catalogue (use [AGENT-VERSION-REFERENCE](../agents/AGENT-VERSION-REFERENCE.md) §10). Explain
what the user should do there. Never reach another account's data through internal admin or impersonation routes.
