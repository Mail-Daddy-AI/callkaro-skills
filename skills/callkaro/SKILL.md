---
name: callkaro
description: >
  Operate CallKaro voice and chat AI agents with the ck CLI. Use for creating,
  testing, calling with, or analyzing agents; managing versions, numbers,
  batches, workflows, contacts, secrets, simulations, and analytics.
---
# CallKaro skill graph

Use `ck` to build and operate CallKaro voice and chat agents. Start with
[How to Work](skill/INSTRUCTIONS.md), then open only the nodes needed for the
task. Links between nodes are graph edges; follow them when their detail is
relevant.

Keep these invariants: check authentication first, prefer JSON read commands,
discover IDs instead of inventing them, use `--versions` for version selection,
and obtain explicit confirmation before a command spends credits or starts real
calls/messages.

## Nodes

<!-- BEGIN AUTO-GENERATED SKILL GRAPH -->

Every linked file is a graph node. Follow links inside a node only when relevant.

### Core operations

- [Analytics](skill/analytics.md) — ck analytics overview / performance / version commands, their filters and output fields, and which one answers: agent health, A/B winner, cost, why calls fail.
- [Audit Strategies (AI Auditor)](skill/audit-strategies.md) — Create and manage AI-auditor strategies that score a sampled share of an agent's calls against free-text instructions; commands, filters, models, and the rule not to invent filter values.
- [Auth & Account](skill/auth.md) — Sign-in, register, logout, whoami and config; whoami is the auth gate before any workflow, and it shows the credits balance.
- [Batch Calls](skill/batches.md) — Create or schedule batch calls from a CSV (format rules, row-count confirmation), monitor status, re-dial unreached rows, download results. Creating a batch starts real calls immediately.
- [Calls — placing, history, live queues](skill/calls.md) — Place a single call (use --test while iterating), list, get and export call history with filters, read raw call logs, and inspect live call queues.
- [Chat agents](skill/chat-agents.md) — Chat agents are a separate entity from voice agents: ck chat-agents commands, WhatsApp number assignment, safe creation, prompt/model setup, functions and versions.
- [Contacts (CRM)](skill/contacts.md) — CRM contacts and their attributes: define attributes first, import and export CSV, assign contacts to a workflow or an agent, and the protection of hand-set values from workflows.
- [How to Work — operating instructions for AI agents using CallKaro](skill/INSTRUCTIONS.md) — Start here. The operating loop, session preamble, agent authoring order, decision rules that prevent damage, standard playbooks (build from a doc, build from scratch, debug a bad agent) and when to ask the user.
- [Phone Numbers](skill/numbers.md) — Phone numbers: list, browse the buyable catalog, buy, release and spam-flag; assigning a number to an agent (outbound caller ID, inbound); the WhatsApp number pool, which has no buy.
- [Account Secrets](skill/secrets.md) — The account secrets vault: list names, set, rename and remove secrets, and the xsecrets reference syntax used in function headers and code. Never put a credential in an agent payload.
- [Workflows + Contacts together](skill/workflows-and-contacts.md) — End-to-end recipe for using workflows with contacts: define attributes, gather ids, build the graph, load contacts, test on one number, verify, then scale.
- [Workflows](skill/workflows.md) — Build and run workflow graphs per contact: node types, the rules that bite, commands, generating a graph from a request using real ids, editing, and reading results.

### Voice Agents

- [Voice Agents — the core entity](skill/voice-agents/agent-overview.md) — The agent versus version split, the four prompt types (basic, advanced, multi-prompt, pathway), the minimum viable agent, core commands, and the errors the server enforces.
- [CallKaro Agents & Versions — Complete Reference](skill/voice-agents/AGENT-VERSION-REFERENCE.md) — The complete field reference for agent and version documents: which doc a key belongs to, script and capability/pathway fields, functions, LLM, post-call, voice, transcriber, call settings, WhatsApp, versioning, a pre-flight checklist and minimal payloads. Load before writing any payload.
- [Creating & Updating Agents](skill/voice-agents/create-update.md) — Create, update, export and import agents with the ck CLI: the validation contract, a safe type-0 starter template, version-level versus agent-level patches, and cloning.
- [Writing Advanced Function Code](skill/voice-agents/function-code.md) — Rules for advanced function code: in-call Python (typed scalar parameters, status-dict returns, helpers) and post-call JavaScript (context fields, mandatory functionscalled log, forbidden APIs).
- [Functions — giving the agent abilities](skill/voice-agents/functions.md) — Choosing function types (end, transfer, hold, booking, in-call, pre/post-call, WhatsApp), basic versus advanced, secrets in functions, where to attach a function, and writing its description as a trigger.
- [Writing Agent Prompts](skill/voice-agents/prompts.md) — How to write a good prompt: the 8 sections, multi-prompt structure, the 5 snippets, rules that stop prompts breaking, Indian-language and persona conventions, closing lines and update rules.
- [Client Regression — branch coverage & verification discipline](skill/voice-agents/regression.md) — Branch library to cover when building from a PRD (happy path, wrong number, DND, transfer, callback, upload error and more), the four rules behind most regressions, two-pass verification and an audit checklist for live agents.
- [Behaviour Snippets — default texts](skill/voice-agents/snippets.md) — The verbatim default text of the five behaviour snippets (response style, security, function calling, language switch, hold). Open when you need to edit one.
- [Verifying a Built or Updated Agent](skill/voice-agents/verify-and-review.md) — Check a built or updated agent before publishing: does it deliver the request, update-without-damage rules, and function review (duplicates, scope, credentials, transfer fields, fix in place or redo).
- [Versions, Publishing & A/B Testing](skill/voice-agents/versions.md) — Versions, commits and publishing, cloning a sibling version, ratio and rule-based A/B tests, and the safe iteration recipe that avoids editing production in place.
- [Voice (TTS) & Transcriber (STT) — choosing them](skill/voice-agents/voice-and-transcriber.md) — How to choose a voice and transcriber: find real voices with ck voices, pick by language and gender, the two traps, and verifying after writing.

### Simulations

- [Anti-patterns seen in real suites (never do these)](skill/simulations/anti-patterns.md) — Twelve test and criteria mistakes seen in real suites and why each gives false results; check when a test feels loose.
- [Fixing and regression](skill/simulations/fixing-and-regression.md) — After a failure: clone the version, fix the right field for the agent type, run old and new side by side, re-run all P0 and P1, and turn incidents into tests.
- [How simulation actually works](skill/simulations/how-simulation-works.md) — What a run is and does, the verified platform facts F1–F14 (static mocks, pre-call functions ignoring mocks, caller hang-ups, grader crashes), and what is still unverified. Mandatory first read.
- [Interfaces](skill/simulations/interfaces.md) — Test case fields, the MCP tools and ck sim commands, including userPersona, mocks, variables, epochs and the default caller model.
- [Phase B: Lint the configuration and the prompt](skill/simulations/lint-config-and-prompt.md) — Phase B: configuration lint checklist (opening, end lines, functions vs prompt, transfer, capabilities, pathway, language, post-call) and prompt gap analysis, run before any test.
- [Phases C–E: classify, derive, prioritise](skill/simulations/plan-the-suite.md) — Phases C–E: what simulation can't observe, tiers P0–P3 with epochs and pass rules, the epoch-cost question, tests to derive by bot type and feature, the universal negative pack U1–U12, and suite sizing.
- [Appendix A: Platform probe tests](skill/simulations/platform-probes.md) — Appendix A: probe tests (KB retrieval, post-call functions, bot-ended calls, time limit, hand-offs, mocks) to run once per environment to settle the unverified platform behaviour.
- [Phase A: Profile the bot (the dossier)](skill/simulations/profile-the-bot.md) — Phase A: which inspect commands to run and the dossier template (use case, structure, rules, guardrails, functions, data, variables, post-call fields) whose numbered items become coverage items.
- [Phase H: Create, run, read, gate, report](skill/simulations/run-triage-report.md) — Phase H: run the smoke test then the suite, read results in order (validity, mechanics, post-call, verdict), triage each failure to an owner, the release gate, and the report format.
- [Phase G: Self-review before creating anything](skill/simulations/self-review.md) — Phase G: the coverage, per-test and suite checklist to pass before creating any test. Mandatory.
- [Simulations & Test Cases](skill/simulations/simulation-playbook.md) — Entry point for building, running and reading a simulation suite as a release gate: the phases A–H, the read order for the files below, and what is mandatory before any test is written.
- [Worked examples](skill/simulations/worked-examples.md) — Five worked tests to copy the shape of: a function-error test, a capability test, a guardrail attack, a pathway boundary test and a sizing example.
- [Phase F: Write each test](skill/simulations/write-tests.md) — Phase F: test name format, caller userPrompt template, successCriteria template with the universal FAIL lines, variables, mock rules and the simulator model.

<!-- END AUTO-GENERATED SKILL GRAPH -->
