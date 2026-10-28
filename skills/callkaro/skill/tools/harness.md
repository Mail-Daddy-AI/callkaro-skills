<!-- graph-summary: For ai-fde's own harness: which harness tool does what a ck command in these nodes does, and which tasks have no harness tool yet. Read before acting on any ck instruction inside the harness. -->
<!-- audience: harness -->

# Harness tool map

Inside ai-fde's harness you do not run `ck`. Wherever a node says to run a `ck` command, use the
harness tool in this table. The account is always the signed-in session's; never pass a user or
account id yourself. A task with no harness tool cannot be done from here: say so and tell the user
where it is done (dashboard or CLI).

Approvals are handled by the harness: publishing, A/B changes, phone-number changes and starting a
simulation batch always ask the user; saving a version and editing test cases show the change first.

| ck command | Harness tool |
|---|---|
| `ck agents list` | `list_agents` |
| `ck agents versions <id>` | `list_versions` |
| `ck agents get <id> --versions <v>` | `read_agent_state` (loads it into the draft) then `read_version` for sections |
| search across versions for a reference | `search_versions` |
| `ck agents create` | `create_agent_in_db`, then write the fields into the draft (`trigger_single_pipeline`) and `save_version_to_db` (the agent is created with its first version on save) |
| `ck agents update --versions <v>` | write the changed fields yourself and pass them as `draftPatch` to `trigger_single_pipeline`, then `save_version_to_db` |
| change one node, function or field of a large draft | `trigger_single_pipeline` with `edits` (addressed by capability and function name), not a resent array |
| `ck agents clone-version` + update | `save_version_to_db` with "save as new version" |
| several languages at once | write each language's fields as `lanePatches` for `trigger_parallel_pipeline`, then `read_parallel_drafts` |
| `ck agents publish` | `manage_version_publishing` (`publish_version`) |
| `ck agents ab`, `ck agents ab-advanced` | `read_ab_test_configuration`, `manage_ab_testing` |
| metadata keys for A/B rules | `discover_ab_test_metadata` |
| `ck numbers list` | `list_phone_numbers` (`voice` or `whatsapp`) |
| `ck agents set-inbound` / `set-outbound` / `set-whatsapp-outbound` | `assign_phone_number` |
| `ck whatsapp list`, WhatsApp setup checks, templates | `check_whatsapp_readiness` |
| `ck voices --providers`, `ck voices --provider <name> ...` | `list_voices` (no provider: providers and models; with provider: voices) |
| `ck sim tests <agentId>` | `list_simulation_test_cases` |
| `ck sim create` | `create_simulation_test_case` |
| update a test case | `update_simulation_test_case` |
| `ck sim run` | `start_simulation_batch` |
| `ck sim runs` | `list_simulation_batches` |
| `ck sim results` | `get_simulation_batch_status`, `analyze_simulation_batch` (pass rates and transcripts) |
| ask the user to approve a plan | `present_plan_and_questions` |
| web research | `web_search` |
| read a skill node or one section of it | `read_skill` |

No harness tool yet: placing calls (`ck calls make`), call history and logs (`ck calls list/get/logs`),
batches, analytics, contacts, workflows, secrets, the transcriber catalogue (use reference §10), buying or releasing
numbers, audit strategies, chat agents. For these, explain what to do and where; never pretend it was
done.
