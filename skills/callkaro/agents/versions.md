# Versions, Publishing & A/B Testing

## How versions work

- Each version is a full standalone config (prompt + LLM + voice + everything
  version-level) under one agent, identified by `versionName` + `default_language`.
- **Publishing is per-language**: `publishedVersionsByLanguage` holds one live
  version per language. Publishing a `hi` version replaces the previous `hi`
  entry and leaves `en` untouched. Calls use the published version for the
  call's language (agents `get` with no `--versions` also falls back to it).
- Every version save with `--commit` writes a snapshot (commit history is
  browsable/revertable in the dashboard).
- `isVersionActive` soft-disables a version. A version must be **active** to be
  published or A/B'd; a **published or A/B version cannot be deactivated or
  deleted** (the server rejects it).

## Commands

```bash
ck agents versions <agentId> --json                 # name, id, language, type, active
ck agents publish <agentId> --versions <vid>        # per-language publish
ck agents toggle-active <agentId> --versions <vid>  # activate/deactivate
ck agents ab <agentId> --versions "<vid1>=60,<vid2>=40"   # start A/B
ck agents ab <agentId> --disable                    # stop A/B
```

A/B rules (CLI validates before sending): **at least 2 versions**, ratios are
integers that **sum to exactly 100**, and each version must be active. Traffic
splits by ratio; score with `ck analytics version <agentId> --json`
(compare `overall_connected_to_conversion_pct`).

## Safe iteration recipe (don't edit prod in place)

```bash
# 1. capture the current published version
ck agents get <agentId> --versions <publishedVid> --json > current.json
# 2. create a sibling version: export + import is the clean path, or update a
#    scratch version. Give it a clear versionName like "v2-discount-fix".
# 3. test it with simulations (see ../simulations.md) until PASS
ck sim run <agentId> --tests <t1,t2> --versions <newVid>
# 4. either flip over…
ck agents publish <agentId> --versions <newVid>
# …or A/B it against the incumbent:
ck agents ab <agentId> --versions "<oldVid>=50,<newVid>=50"
# 5. after enough calls, read the scorecard and settle:
ck analytics version <agentId> --json
ck agents ab <agentId> --disable
ck agents publish <agentId> --versions <winnerVid>
```

## Multi-language agents

One agent can serve several languages: create one version per language
(`default_language: "hi"`, `"en"`, …) and publish each. The agent's
`default_agent_language` decides which published version answers when the call
doesn't specify a language.
