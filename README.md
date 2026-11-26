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

**Option C — manual:** copy the folders you want from `skills/` (e.g. `skills/callkaro/`) into `~/.claude/skills/`.

> The extra skills below are installed by the plugin (Option A). They reach `ck skills install` (Option B) once the CLI release that bundles them ships.

Then just ask Claude anything CallKaro-related — *"build me a Hindi sales agent
and test it"* — and it will load the skill.

## Extra skills (no `ck` CLI needed)

The plugin also ships three standalone skills for the work around building a bot.
Claude loads them automatically when you ask for the matching thing.

| Skill | What it does | Needs |
|---|---|---|
| `callkaro-sow-generator` | Turns a client BRD / PRD / script / description into the standard CallKaro Scope of Work **PDF** (cover, contents, Purpose, then Flow, Variables, Dispositions, Guardrails, Rebuttals, Objection Handling, FAQs). | `pip install reportlab` |
| `voicebot-qa-testbook` | Builds the Voice AI Bot QA Testing Framework **Excel workbook** (four pillar sheets, scorecard with the 95% certification gate, scoring, thresholds) pre-filled with test cases for a bot, from its SoW, agent JSON or description. | `pip install openpyxl` |
| `conversational-flow-diagram` | Draws a hand-drawn-style bot flow diagram (PNG or self-contained HTML) from an agent JSON, SoW/PRD/BRD or a prompt. | Node.js |

Typical chain: client BRD → `callkaro-sow-generator` → `conversational-flow-diagram` and
`voicebot-qa-testbook` from that SoW.

## What's inside

| File | Covers |
|---|---|
| `skills/callkaro/SKILL.md` | the single entry point and generated graph router |
| `skills/callkaro/skill/INSTRUCTIONS.md` | how to think: operating loop, playbooks, safety rules |
| `skills/callkaro/skill/secrets.md` | account secret commands, names-only discovery, and safe reference syntax |
| `skills/callkaro/skill/voice-agents/AGENT-VERSION-REFERENCE.md` + `reference/` | router for every agent/version field (which document it lives on), then one topic node per area (script, capabilities, functions, LLM and post-call, voice, call settings, variables and memory, versioning, payloads, field index) |
| `skills/callkaro/skill/voice-agents/` | prompts, voice/STT, functions, creation, versions, call memory and voice rotation (`ck agents memory`, `ck agents voice-rotation`), and regression testing |
| `skills/callkaro/skill/workflows.md` · `contacts.md` | workflow graphs and CRM contacts |
| `skills/callkaro/skill/chat-agents.md` · `chat-agents-advanced.md` · `chat-agents-workflow.md` · `chat-simulations/` | chat agents (Basic, Advanced and Workflow types), and testing them with chat simulations (`ck chat-sim`) |
| `skills/callkaro/skill/auth.md` · `numbers.md` · `outbound-strategies.md` · `calls.md` · `batches.md` · `simulations/simulation-playbook.md` · `analytics.md` | the rest of the platform |

## Maintaining the skill graph

There is only one discoverable `SKILL.md`. Every `.md` file below
`skills/callkaro/skill/` is a graph node, and relative Markdown links between
files are directed edges. Keep each node under about 12 KB (long reference material is split into topic nodes under `voice-agents/reference/` so an agent loads only what the task needs). Add a new node anywhere below that directory, give it
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
