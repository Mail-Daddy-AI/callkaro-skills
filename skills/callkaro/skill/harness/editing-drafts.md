<!-- graph-summary: Change a voice agent in the harness: load a version into the draft, edit it (a patch, targeted edits or a script), review, save as a new version or commit, publish only when asked. The write rules that bite. Use for any change to an existing agent. -->
<!-- audience: harness -->

# Editing and saving a voice agent

Every change goes through one working draft per conversation: load a version into it, change it, review it,
save it. Nothing reaches the backend until `save_version_to_db` and the user's approval.

## 1. Load

1. `list_agents` with the name as the user said it; if several match, ask which.
2. `list_versions` to see versions, which one is published per language, and A/B use.
3. `read_agent_state` with the `versionId` to change (omit it for the published one). This loads the version
   into the draft; the version it came from is the base.
4. Read only what you need: `read_version` (`schema` first, then sections), or `query_context` over
   `/draft/version.json`.

## 2. Edit

| Change | Use |
|---|---|
| Fields you wrote (a prompt, `end_call_msg`, a setting) | `trigger_single_pipeline` with `draftPatch` (`workflowMode: UPDATE`) |
| One node, one function, a snippet in long text | `trigger_single_pipeline` with `edits` (by capability and function name; `replace` for find/replace) |
| The same change in many places | `edit_draft_script` (one script over /draft/version.json) |
| Several languages | `trigger_parallel_pipeline` with `lanePatches` |

Every edit is validated; fix what validation reports. The rules that bite:

- **Arrays are replaced whole.** A `draftPatch` with one function deletes every other function. Change one
  function or node with `edits` instead.
- **Objects in a `draftPatch` are merged key by key** (`voice_configuration`, `transcriber`, `secondary_*`,
  `preFormatVariables`, `customPronunciations`, `callFlow_json`, `variableSource`). So a key cannot be removed that
  way: to drop one, read the object and write it whole with an `edits` `set`. On the saved version these objects
  are stored whole, so read the current value before you change it.
- **A `draftPatch` key is a top-level field name**, never a path such as `capabilities[3].transitions`.
- **Database fields are never written**: `_id`, `__v`, `createdAt`, `updatedAt`, `userId`, `agentId`.
- **Agent-level fields are not saved from the draft**: `name`, `folderId`, `useMultiTranscribers`,
  `default_agent_language`, phone numbers, A/B settings and status. Status goes through `manage_version_publishing`
  (`set_status`), A/B through `manage_ab_testing`, numbers through `assign_phone_number`; renaming the agent and the
  other agent fields are done on the dashboard.

## 3. Review

Before saving a change to prompts, nodes or functions, run `review_draft`. Fix every blocker and major issue;
a "decision" is the user's to make: ask with `present_plan_and_questions`. A single setting needs no review.

## 4. Save

`save_version_to_db` with a `versionName` that says what changed. It shows the user the diff and waits:

- **The base is published (live):** the only choice is **save as a new version**. The harness copies the base
  into a new version under the same agent and applies your changes to the copy; the live version is untouched.
  This is how you "create a new version" or "clone a version" of a voice agent. There is no separate clone tool.
- **The base is unpublished:** the user may also **commit to the current version**.
- Only the fields that differ from the base are sent, so untouched fields are never re-validated.

Write a change as a new version; never change a live version in place for an experiment. After saving, say what
exists (agent, version name and id, what is published) only from the tool's result, then read back the fields
that matter with `read_version`: a success message is not proof that every field round-tripped.

## 5. Go live (only when asked)

Test first ([simulations](../simulations.md)). Publishing replaces that language's live version:
`manage_version_publishing` with `publish_version`, after the user asks. To split traffic instead, A/B
([versions](../agents/versions.md)). Activating or deactivating a version is done on the dashboard.

Exporting and importing an agent are dashboard tasks. An export often fails to import because it leaves out
fields import requires (commonly `language_switching_instructions`, `silence_instructions`, `language_lockin_time`,
`allowed_languages`, `language_switch_min_words`): add each one it names, with the real value from `read_version`.
