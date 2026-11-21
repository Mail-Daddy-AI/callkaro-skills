<!-- graph-summary: Versions, new versions from an existing one, publishing per language and A/B testing (normal and advanced rules). Use when making a new version, publishing, or splitting traffic between versions. -->
# Versions, Publishing & A/B Testing

## How versions work

- Each version is a full standalone config (prompt + LLM + voice + everything
  version-level) under one agent, identified by `versionName` + `default_language`.
- **Publishing is per-language**: `publishedVersionsByLanguage` holds one live
  version per language. Publishing a `hi` version replaces the previous `hi`
  entry and leaves `en` untouched. Calls use the published version for the
  call's language (`read_agent_state` without a `versionId` also loads it).
- Every version save writes a commit snapshot (commit history is
  browsable/revertable in the dashboard).
- `isVersionActive` soft-disables a version (activating/deactivating is done on
  the CallKaro dashboard). A version must be **active** to be
  published or A/B'd; a **published or A/B version cannot be deactivated or
  deleted** (the server rejects it).

## Tools

- `list_versions`: name, id, language, prompt type, active/published state, A/B use.
- `save_version_to_db` (`versionName`): saves the working draft; a published base
  is always saved as a new version.
- `manage_version_publishing` with `publish_version`: per-language publish.
- `manage_ab_testing` with `configure_normal` (`abTestVersions`) starts A/B,
  `disable_normal` stops it (load the ab_testing tools first).

### New version from an existing one

A new version is a copy of an existing version under the **same agent**: load
the source with `read_agent_state`, change what is needed in the draft
(`trigger_single_pipeline` or `edit_draft_script`), run `review_draft`, then
`save_version_to_db` with the new name (e.g. "Hindi v1"). A published base is
never overwritten; it is always saved as a new version. Prompts, functions,
models, capabilities, and other version settings are inherited from the source.

Prompt types are `0` Basic, `1` Advanced, `2` Multi-prompt, and `3` Pathways; to
change it, pass `systempromptType` to `trigger_single_pipeline`. Languages are
`en hi kn ta te mr gu bn ml`; for another language change `default_language`
together with `silence_language`, `voice_configuration` and `transcriber`.

A new version is not published automatically. Check with `list_versions` which
version is live for each language, and publish with `manage_version_publishing`
only when the user asks.

A/B rules (`manage_ab_testing` `configure_normal`): **at least 2 versions**,
ratios are integers that **sum to exactly 100** per configured language, and each
version must be active. Traffic splits by ratio; score with `call_analytics`
with the `agentId` (per-version; compare `overall_connected_to_conversion_pct`).

## Advanced (rule-based) A/B testing

Routes calls by **metadata conditions** instead of pure ratios: an ordered
if / elseif / else chain evaluated before the ratio A/B (and only when the call
does not pin an explicit version).

`manage_ab_testing` with `configure_advanced` (`advancedAbTestRules`) enables or
replaces the chain; `read_ab_test_configuration` shows the current chain;
`disable_advanced` turns it off. Never invent metadata keys: take them from the
user or `discover_ab_test_metadata`.

`advancedAbTestRules` — an ARRAY of rule objects:

```json
[
  { "kind": "if",     "condition": "(metadata.age > 24)", "returnType": "version",
    "targets": [ { "versionId": "<vid1>", "ratio": 50 }, { "versionId": "<vid2>", "ratio": 50 } ] },
  { "kind": "elseif", "condition": "(metadata.age < 24)", "returnType": "language",
    "targets": [ { "language": "ta", "ratio": 100 } ] },
  { "kind": "else",   "condition": "", "returnType": "version",
    "targets": [ { "versionId": "<vid1>", "ratio": 100 } ] }
]
```

Server-enforced rules (violations return a precise 400):
- Exactly ONE `if`, and it must be **first**; at most one `else`, and it must be
  **last**; middles are `elseif`.
- `condition` uses the pathway expression grammar
  (AGENT-VERSION-REFERENCE §"Expression grammar"): fully parenthesised,
  `metadata.<key>` operands, `== != >= <= > <`, UPPERCASE `AND`/`OR`.
  `else` has an empty condition.
- `returnType: "version"` → each target needs a `versionId` **belonging to this
  agent** (no duplicates). **This short-circuits resolution** — that version
  runs the call.
- `returnType: "language"` → each target needs a `language` from
  `en hi kn ta te mr gu bn ml` (no duplicates). This only overrides the
  language; normal resolution (ratio A/B → published-by-language → default)
  continues.
- Multiple targets in one rule = a weighted split: integer ratios 1–100 summing
  to exactly **100**. A single target is auto-set to 100.

The fields live on the AGENT document (`advancedAbTestEnabled`,
`advancedAbTestRules`) — no version is involved.

### Editing an existing rule chain (read → modify → write)

`configure_advanced` REPLACES the whole chain — there is no per-rule patch. So:
read the current chain with `read_ab_test_configuration`, edit it (change a
condition, add an elseif, adjust ratios…), send the whole chain back with
`configure_advanced`, then verify with `read_ab_test_configuration`.

To add/remove/reorder a rule: edit the array (order = evaluation order; keep
`if` first, `else` last). To change only one target ratio: edit that rule's
`targets` and keep the rule's ratios summing to 100.

## Safe iteration recipe (don't edit prod in place)

1. Load the current published version with `read_agent_state`.
2. Edit only what is needed in the draft, run `review_draft`, and save it with
   `save_version_to_db` under a new name (e.g. "v2-discount-fix"); the published
   base stays untouched.
3. Test the new version with simulations (see [../simulations.md](../simulations.md);
   load the simulation tools: `start_simulation_batch`, then
   `get_simulation_batch_status` and `analyze_simulation_batch`). A PASS is a hint, not proof: confirm on a real test call.
4. Either flip over with `manage_version_publishing` (`publish_version`), or A/B
   it against the incumbent with `manage_ab_testing` (`configure_normal`, 50/50).
5. After enough calls, read the scorecard with `call_analytics`, stop the A/B
   (`disable_normal`) and publish the winner.

## Multi-language agents

One agent can serve several languages: create one version per language
(`default_language: "hi"`, `"en"`, …) and publish each. The agent's
`default_agent_language` decides which published version answers when the call
doesn't specify a language.
