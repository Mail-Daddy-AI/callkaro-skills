# Versions, Publishing & A/B Testing
<!-- graph-summary: Versions, commits and publishing, cloning a sibling version, ratio, rule-based and JavaScript-routed A/B tests, and the safe iteration recipe that avoids editing production in place. -->

## How versions work

- Each version is a full standalone config (prompt + LLM + voice + everything
  version-level) under one agent, identified by `versionName` + `default_language`.
- **Publishing is per-language**: `publishedVersionsByLanguage` holds one live
  version per language. Publishing a `hi` version replaces the previous `hi`
  entry and leaves `en` untouched. Calls use the published version for the
  call's language (agents `get` with no `--versions` also falls back to it).
- Every version save with `--commit` writes a snapshot. Browse, diff and revert
  them with `ck agents commits | commit | compare | revert` (see
  [History, compare and revert](#history-compare-and-revert)).
- `isVersionActive` soft-disables a version. A version must be **active** to be
  published or A/B'd; a **published or A/B version cannot be deactivated or
  deleted** (the server rejects it).

## Commands

```bash
ck agents versions <agentId> --json                 # name, id, language, type, active
ck agents clone-version <agentId> --versions <sourceVid> --name <name> \
  --prompt-type <0-3> --language <code>
ck agents publish <agentId> --versions <vid>        # per-language publish
ck agents toggle-active <agentId> --versions <vid>  # activate/deactivate
ck agents ab <agentId> --versions "<vid1>=60,<vid2>=40"   # start A/B
ck agents ab <agentId> --disable                    # stop A/B
ck agents commits <agentId> [--versions <vid>]      # saved snapshots, newest first
ck agents commit <commitId> --json                  # one snapshot, full saved state
ck agents compare <agentId> --a <vidA> --b <vidB>   # diff two live versions
ck agents compare <agentId> --commits --a <cA> --b <cB>   # diff two commits
ck agents revert <agentId> <commitId>               # restore a snapshot (asks first)
```

### History, compare and revert

- `commits` lists snapshots (id, version, message, author, time); filter to one
  version with `--versions`. `commit <id> --json` returns the full saved state.
- `compare` prints the changed fields; `--field <name>` shows one field A then B
  (prompts, instructions and similar text fields diff as text), `--json` gives
  everything. Without `--commits`, `--a/--b` are **version** ids and must belong
  to the same agent; with `--commits` they are **commit** ids.
- `revert` **overwrites the version's current settings** with the snapshot and
  records the revert as a new commit (so it can be undone the same way). It
  asks for confirmation; pass `--yes` only when the user has already approved.
  Never revert a **published or A/B** version without telling the user — calls
  use it immediately; use `compare` first to show what will change.
- Over MCP, history and compare are read-only tools (`list_agent_commits`,
  `get_agent_commit`, `compare_agent_versions`); there is no revert tool.

### Clone a sibling version

`clone-version` copies an existing version under the **same agent**. All four
inputs are mandatory: source `--versions`, target `--name`, target
`--prompt-type`, and target `--language`.

```bash
ck agents clone-version <agentId> \
  --versions <sourceVid> \
  --name "Hindi v1" \
  --prompt-type 1 \
  --language hi \
  --set '{"silence_language":"hi"}' \
  --json
```

Prompt types are `0` Basic, `1` Advanced, `2` Multi-prompt, and `3` Pathways.
Languages are `en hi kn ta te mr gu bn ml`. A changed prompt type is migrated
by the backend. Prompts, functions, models, capabilities, and other version
settings are inherited from the source.

`--set` is optional and accepts only `transcriber`, `secondary_transcriber`,
`voice_configuration`, `secondary_voice_configuration`, and
`silence_language`. It does not accept prompts, models, capabilities, or
`default_language`; use the mandatory `--language` option for the latter.

With `--json`, read the new id from `newVersion._id`. If the target language
already has a published version, the clone is not published automatically. If
none exists, the backend adds the clone to that language's published mapping.
Edit the clone afterward with:

```bash
ck agents update <agentId> --versions <newVid> --set @changes.json
ck agents get <agentId> --versions <newVid> --json
ck agents versions <agentId> --json
```

A/B rules (CLI validates before sending): **at least 2 versions**, ratios are
integers that **sum to exactly 100**, and each version must be active. Traffic
splits by ratio; score with `ck analytics version <agentId> --json`
(compare `overall_connected_to_conversion_pct`).

## Advanced (rule-based) A/B testing

Routes calls by **metadata conditions** instead of pure ratios: an ordered
if / elseif / else chain evaluated before the ratio A/B (and only when the call
does not pin an explicit version).

```bash
ck agents ab-advanced <agentId> --rules @rules.json   # enable / replace the chain
ck agents ab-advanced <agentId> --show [--json]       # inspect the current chain
ck agents ab-advanced <agentId> --disable             # turn it off
```

`rules.json` — an ARRAY of rule objects:

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
  ([expression grammar](reference/capabilities-and-pathways.md)): fully parenthesised,
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
`advancedAbTestRules`, and for JavaScript routing `advancedAbTestMode`,
`advancedAbTestJsCode`) — no `--versions` flag involved. `--rules` also sets
`advancedAbTestMode: "rules"`.

### Editing an existing rule chain (read → modify → write)

`--rules` REPLACES the whole chain — there is no per-rule patch. So:

```bash
# 1. dump the current chain to a file (the wrapper object is fine —
#    --rules accepts it as-is, no reshaping needed)
ck agents ab-advanced <agentId> --show --json > rules.json
# 2. edit rules.json: change a condition, add an elseif, adjust ratios…
# 3. apply the whole chain back
ck agents ab-advanced <agentId> --rules @rules.json
# 4. verify
ck agents ab-advanced <agentId> --show
```

To add/remove/reorder a rule: edit the array (order = evaluation order; keep
`if` first, `else` last). To change only one target ratio: edit that rule's
`targets` and keep the rule's ratios summing to 100.

## Advanced A/B with JavaScript routing

Instead of a rule chain, advanced A/B can run code: `advancedAbTestMode: "js"`
with `advancedAbTestJsCode`. Same place in resolution as the rules (before the
ratio A/B, only when the call does not pin a version); rules and code are
alternatives, and the other one stays saved.

```bash
ck agents ab-advanced <agentId> --test --js @route.js --metadata '{"city":"Mumbai"}'  # dry run, saves nothing
ck agents ab-advanced <agentId> --js @route.js     # save + enable JS routing
ck agents ab-advanced <agentId> --test --metadata @sample.json   # dry-run the SAVED code
ck agents ab-advanced <agentId> --mode rules       # back to the saved rule chain (--mode js to return)
ck agents ab-advanced <agentId> --show [--json]    # mode + rules or code
```

MCP: `update_agent` with `advancedAbTestEnabled: true, advancedAbTestMode: "js",
advancedAbTestJsCode`, and `test_ab_routing_js` (agentId, code, metadata) for the
dry run.

`route.js`:

```js
async function route(context) {
  if (context.metadata.city === 'Mumbai') return 'hi';      // a language
  if (Number(context.metadata.age) > 40) return context.versions[0];  // a version id
  // returning nothing → the ratio A/B / published version decides
}
```

- **Signature:** `async function route(context)` at the top level (helpers may sit
  beside it). The server refuses code without it, and `eval`, `Function(...)`,
  `process.env`, `require('fs' | 'child_process')`.
- **context:** `metadata` (the call's metadata; keys can be missing and numbers
  can arrive as text, so use `Number()`), `versions` (the agent's ACTIVE version
  ids), `languages` (languages with a published version or a ratio-A/B version).
  Inbound calls get the metadata of the caller's last call, or `{}`.
- **Return:** a version id from `context.versions` (that version runs the call),
  a language from `context.languages` (language override; resolution continues),
  or nothing (ratio A/B decides). Anything else is "invalid".
- **Available:** `axios`, `moment`, `_` (lodash), `console`, `x_secrets['name']`
  for saved secrets (never paste keys). No `require`, `process` or file access.
- **Never fails a call:** a throw, a return outside the lists, or more than **5 s**
  logs the error and falls back to the ratio A/B. The caller waits while it runs:
  give API calls `timeout: 3000`. Returning callers run it again, so their version
  can change between calls.
- `--test` prints `version` / `language` / `none` / `invalid` / `error` with the
  time taken. Test before saving.

## Safe iteration recipe (don't edit prod in place)

```bash
# 1. capture the current published version
ck agents get <agentId> --versions <publishedVid> --json > current.json
# 2. clone it into a sibling version under the same agent
ck agents clone-version <agentId> --versions <publishedVid> \
  --name "v2-discount-fix" --prompt-type <0-3> --language <code> --json
# 3. read newVid from newVersion._id, then edit only the clone as needed
ck agents update <agentId> --versions <newVid> --set @changes.json
# 4. test it with simulations (see ../simulations/simulation-playbook.md) until PASS
ck sim run <agentId> --tests <t1,t2> --versions <newVid>
# 5. either flip over…
ck agents publish <agentId> --versions <newVid>
# …or A/B it against the incumbent:
ck agents ab <agentId> --versions "<oldVid>=50,<newVid>=50"
# 6. after enough calls, read the scorecard and settle:
ck analytics version <agentId> --json
ck agents ab <agentId> --disable
ck agents publish <agentId> --versions <winnerVid>
```

## Multi-language agents

One agent can serve several languages: create one version per language
(`default_language: "hi"`, `"en"`, …) and publish each. The agent's
`default_agent_language` decides which published version answers when the call
doesn't specify a language.
