# CallKaro Skills for the ai-fde harness

Teach ai-fde's harness to build and operate [CallKaro](https://callkaro.ai) voice and chat AI agents: design
agents, write call scripts, build from a client's BRD, pick voices, run simulations, debug real calls and read
analytics. The harness acts only through its own tools; `skills/callkaro/skill/tools/harness.md` maps every job
to a tool and lists what only the CallKaro dashboard can do. The harness loads this folder from
`AIFDE_PY_SKILLS_DIR` (optionally pinned by `AIFDE_PY_SKILLS_SHA256`).

## What's inside

| File | Covers |
|---|---|
| `skills/callkaro/SKILL.md` | the single entry point and generated graph router |
| `skills/callkaro/skill/INSTRUCTIONS.md` | how to think: operating loop, playbooks, safety rules |
| `skills/callkaro/skill/tools/harness.md` | every harness tool by job, and the dashboard-only tasks |
| `skills/callkaro/skill/harness/` | BRD builds, editing and saving drafts, call debugging, large results |
| `skills/callkaro/skill/agents/AGENT-VERSION-REFERENCE.md` | every agent/version field, its values, and the traps |
| `skills/callkaro/skill/agents/` | prompts, voice/STT, functions, creation, versions, and regression testing |
| `skills/callkaro/skill/writing/` · `design/` · `quality/` · `functions/` | prompt style, agent design, QA and debugging, function authoring |
| `skills/callkaro/skill/authoring-pipeline/` | production authoring stages linked as a subgraph (not served to the supervisor) |
| `skills/callkaro/skill/numbers.md` · `calls.md` · `simulations.md` · `analytics.md` · `chat-agents.md` | the platform the harness can act on |
| `skills/callkaro/skill/batches.md` · `contacts.md` · `workflows.md` · `secrets.md` · `integrations/` | product reference for what the user does on the dashboard or over the API |

## Maintaining the skill graph

There is only one discoverable `SKILL.md`. Every `.md` file below
`skills/callkaro/skill/` is a graph node, and relative Markdown links between
files are directed edges. Add a new node anywhere below that directory, give it
an H1 title and a short first paragraph, then run:

```bash
python3 scripts/sync_skill_graph.py
```

The command updates only the generated node catalog in `SKILL.md` and validates
local graph links. Use an optional `<!-- graph-summary: Short routing text. -->`
in a node to override its inferred catalog summary. CI can enforce a clean graph
without rewriting files:

```bash
python3 scripts/sync_skill_graph.py --check
```
