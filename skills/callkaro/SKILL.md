---
name: callkaro
description: >
  Operate CallKaro voice AI agents from the terminal via the `ck` CLI: create and
  manage voice agents and their versions, buy/assign phone numbers, place single
  or batch outbound calls, run simulations and test cases, and read call history
  and analytics. Use whenever the user wants to build, test, call with, or analyze
  a CallKaro voice agent.
---

# CallKaro CLI (`ck`)

CallKaro is a voice-AI platform: users build **voice agents** (LLM + voice +
transcriber + prompt) that make and receive phone calls. This skill lets you do
everything the CallKaro dashboard does, through the `ck` CLI.

## Ground rules (read first)

1. **Check auth before anything**: run `ck whoami`. If it fails, the user must
   sign in — run `ck login` (opens their browser; never ask for a password in
   the terminal). You cannot complete login for them; wait until it succeeds.
2. **Always prefer `--json`** on read commands — parse the output instead of
   scraping tables.
3. **IDs are Mongo ObjectIds** (24-hex). Get them from list commands; never
   invent them. Phone-number commands also accept the raw number (with/without `+`).
4. **Versions are selected with `--versions <id>`** on every command (never
   `--version`, which prints the CLI version).
5. **Money moves**: `ck numbers buy`, `ck calls make` (without `--test`), and
   `ck batches create` spend real credits / place real phone calls. Confirm with
   the user before running them. Prefer `ck calls make --test` and `ck sim run`
   for iteration.
6. **Exit codes**: non-zero = failure; the message on stderr says why.

## How this pack is organised — one fact, one home

Four layers. **Never look for the same thing in two of them** — each owns
something different, and where they overlap the owner below wins.

| Layer | Owns | Files |
|---|---|---|
| **Method** | how to think, plan, decide | `INSTRUCTIONS.md` (operating loop, playbooks, safety rules) |
| **Reference** | **every field, allowed value, enum, per-provider table** — the facts | `agents/AGENT-VERSION-REFERENCE.md` (the single source of truth for config) |
| **Craft** | how to make good choices in one area | `agents/prompts.md`, `voice-and-transcriber.md`, `functions.md`, `versions.md`, `regression.md` |
| **Production prompts** | the exact role + output contract ai-fde uses at each build stage | `authoring-pipeline/*` (verbatim; also owns the `source_code` protocols) |

So: **facts → Reference. Judgement → Craft. Stage roles → pipeline.** A Craft
file never restates a field table; it links to the Reference section.

## Entity map — which file to read

| You need to… | Read |
|---|---|
| **How to think, plan, and operate (read once per session)** | [INSTRUCTIONS.md](INSTRUCTIONS.md) |
| Sign in / account | [auth.md](auth.md) |
| **User handed you a PRD / BRD / PDF spec** ("build this bot") | [INSTRUCTIONS.md](INSTRUCTIONS.md) §5 first playbook — read doc → requirement sheet → pipeline → derive tests from the doc |
| **BUILDING or EDITING an agent** — run ai-fde's production pipeline (plan → script → reflect → functions → parameters) | **[authoring-pipeline/README.md](authoring-pipeline/README.md)** |
| **Any field's name, allowed values, defaults, or a provider table** | **[agents/AGENT-VERSION-REFERENCE.md](agents/AGENT-VERSION-REFERENCE.md)** — look here first, always |
| Agent concepts + the `ck agents` commands | [agents/README.md](agents/README.md) |
| Writing the system prompt / script (8 sections, modes, snippets) | [agents/prompts.md](agents/prompts.md) |
| Create / update workflows + starter JSON | [agents/create-update.md](agents/create-update.md) |
| Versions, publishing, A/B (incl. rule-based) | [agents/versions.md](agents/versions.md) |
| Picking a voice or transcriber (`ck voices`, pairing, language traps) | [agents/voice-and-transcriber.md](agents/voice-and-transcriber.md) |
| Which function to add, basic vs advanced, where to attach | [agents/functions.md](agents/functions.md) |
| Account secrets (list/set/rename/remove and safe agent references) | [secrets.md](secrets.md) |
| Phone numbers (list/buy/assign/spam/release) | [numbers.md](numbers.md) |
| Single calls, call history, exports, live queues | [calls.md](calls.md) |
| Batch calling + CSV format | [batches.md](batches.md) |
| Simulations & test cases | [simulations.md](simulations.md) |
| **Auditing/fixing a live agent** — branch coverage, exact phrases, full-suite gate | [agents/regression.md](agents/regression.md) |
| Analytics / performance | [analytics.md](analytics.md) |

## The golden path (creating a working agent end-to-end)

```bash
ck whoami                                   # 1. logged in?
ck voices --json                            # 2. pick a voice for the language
ck agents create --file agent.json          # 3. create (see agents/create-update.md)
ck sim create <agentId> --name "smoke" \
  --prompt "You are a customer asking about pricing" \
  --criteria "Agent explains pricing and offers a follow-up"
ck agents versions <agentId> --json         # get the version id
ck sim run <agentId> --tests <testId> --versions <versionId>
ck sim results <runId>                      # iterate on the prompt until PASS
ck agents publish <agentId> --versions <versionId>
ck numbers list --json                      # 4. pick/buy a number
ck agents set-outbound <agentId> --number <numberId>
ck calls make --agent <agentId> --to <phone> --test   # 5. test call
```
