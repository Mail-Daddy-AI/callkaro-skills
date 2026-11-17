<!-- graph-summary: Work with large data in the harness without filling context: offloaded tool results, stored documents, the draft and the skills, searched or paged with the context tools. Use when a result says it was offloaded or a draft or document is long. -->
<!-- audience: harness -->

# Large results, documents and drafts

A large tool result is offloaded: you get an outline and a handle instead of the data. Long documents (a BRD) are
stored the same way as `doc_` handles. Search them; do not read them whole.

`query_context` runs a sandboxed bash script and returns only its output. Files:

| Path | Holds |
|---|---|
| `/ctx/<handle>.json` (`.txt` for text) | an offloaded result or stored document |
| `/draft/version.json` | the working draft |
| `/draft/base.json` | the version the draft started from |
| `/draft/agent.json` | the agent |
| `/draft/requirements.json` | the BRD checklist |
| `/skills/<node>` | this skill library |

Typical scripts: `jq '.capabilities[].capability' /draft/version.json`;
`sed -n '120,180p' /ctx/doc_<id>.txt`; `grep -rn -i 'end_call_msg' /skills | head`;
`diff <(jq -S . /draft/base.json) <(jq -S . /draft/version.json)`. `ck-validate` checks an edited copy of the
draft the way validation does. Nothing written in the sandbox persists and there is no network; change the draft
with `trigger_single_pipeline` or `edit_draft_script`.

`read_context_handle` reads one handle in bounded slices: pass `offset` and continue from `nextOffset`. Use it to
read a long text in order; use `query_context` to find something.
