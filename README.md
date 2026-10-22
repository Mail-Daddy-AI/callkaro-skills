# CallKaro Skills for AI Agents

Teach Claude Code (or any AI coding agent) to build and operate
[CallKaro](https://callkaro.ai) voice AI agents: create agents, write call
scripts, pick voices and transcribers, run simulations, place calls, schedule
batch campaigns, build workflows, manage CRM contacts, and read analytics — all through the `ck` CLI.

## Prerequisite

The skills drive the CallKaro CLI, so install it and sign in first:

```bash
npm install --global @callkaro-official/cli
ck login
```

## Install the skills

**Option A — Claude Code plugin (recommended):** inside Claude Code run

```
/plugin marketplace add Mail-Daddy-AI/callkaro-skills
/plugin install callkaro@callkaro
```

**Option B — via the CLI** (skills also ship inside it):

```bash
ck skills install              # your account (~/.claude/skills) — all projects
ck skills install --project    # just this project — commit .claude/ to share
```

**Option C — manual:** copy `skills/callkaro/` into `~/.claude/skills/`.

Then just ask Claude anything CallKaro-related — *"build me a Hindi sales agent
and test it"* — and it will load the skill.

## What's inside

| File | Covers |
|---|---|
| `skills/callkaro/SKILL.md` | the single entry point and generated graph router |
| `skills/callkaro/skill/INSTRUCTIONS.md` | how to think: operating loop, playbooks, safety rules |
| `skills/callkaro/skill/secrets.md` | account secret commands, names-only discovery, and safe reference syntax |
| `skills/callkaro/skill/voice-agents/AGENT-VERSION-REFERENCE.md` | every agent/version field, its values, and the traps |
| `skills/callkaro/skill/voice-agents/` | prompts, voice/STT, functions, creation, versions, and regression testing |
| `skills/callkaro/skill/workflows.md` · `contacts.md` | workflow graphs and CRM contacts |
| `skills/callkaro/skill/chat-agents.md` · `chat-simulations/` | chat agents, and testing them with chat simulations (`ck chat-sim`) |
| `skills/callkaro/skill/auth.md` · `numbers.md` · `calls.md` · `batches.md` · `simulations/simulation-playbook.md` · `analytics.md` | the rest of the platform |

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

## Updating

Skills are versioned with this repo — `/plugin update callkaro` (marketplace
installs) or re-run `ck skills install` after upgrading the CLI.
