---
name: callkaro
description: >
  Design, build, test and operate CallKaro voice and chat AI agents with the ck
  CLI. Use for designing an agent, writing its prompt, functions and post-call
  analysis, QA and debugging, and for managing versions, numbers, batches,
  workflows, contacts, secrets, simulations, audits and analytics.
---
# CallKaro skill graph

Use `ck` to build and operate CallKaro voice and chat agents. Start with
[How to Work](skill/INSTRUCTIONS.md), then open only the nodes needed for the
task. Links between nodes are graph edges; follow them when their detail is
relevant. Inside ai-fde's harness, map every `ck` command through
[tools/harness.md](skill/tools/harness.md).

Keep these invariants: check authentication first, prefer JSON read commands,
discover IDs instead of inventing them, use `--versions` for version selection,
and obtain explicit confirmation before a command spends credits or starts real
calls/messages. Design before writing a prompt; write prompts as plain text;
end calls through `end_call_msg` rather than an `end` function; fix a bad call
at its root cause, never with another rule.

## Nodes

<!-- BEGIN AUTO-GENERATED SKILL GRAPH -->

Every linked file is a graph node. Follow links inside a node only when relevant.

### Core operations

- [Analytics](skill/analytics.md) — Account, agent and version performance (calls, connect and conversion rates, minutes, credits). Use to answer how an agent is doing or compare versions after an A/B test.
- [Audit Strategies (AI Auditor)](skill/audit-strategies.md) — AI Auditor strategies via ck: score sampled calls with an LLM, scoped by call filters. Use to create or update an audit strategy; creating one spends credits on live calls.
- [Auth & Account](skill/auth.md) — Signing in to the ck CLI (ck login, whoami, logout) and where the token lives. Use when ck reports not logged in or the wrong account.
- [Batch Calls](skill/batches.md) — Batch call campaigns from a CSV of leads: validate, create, schedule, monitor, retry. Creating one dials real people at once, so confirm row count and spend first.
- [Calls — placing, history, live queues](skill/calls.md) — Placing calls (test by default), call history, a call's transcript and raw log, live queues. Use to make a test call, read what happened on a call, or debug a failed call from its log.
- [Chat agents](skill/chat-agents.md) — WhatsApp and Instagram chat agents via ck chat-agents: create, version, publish, templates, predefined functions. Use for any chat-agent task; never send chat payloads to voice agents.
- [Contacts (CRM)](skill/contacts.md) — CRM contacts: attribute schema, create, upload, update, delete, assign to an agent or workflow. Use when managing leads or the fields a workflow or agent reads.
- [How to Work — operating instructions for AI agents using CallKaro](skill/INSTRUCTIONS.md) — How to work on any CallKaro task: the operating loop, design first, safety and money rules, and playbooks for PRD builds, new agents, fixing bad calls, batches and comparisons. Read first.
- [Phone Numbers](skill/numbers.md) — Phone numbers: list, buy, release, spam flags, inbound vs outbound assignment rules (inbound is one agent per number). Use before assigning a number; buying one spends credits.
- [Account Secrets](skill/secrets.md) — The account Secrets Vault: names-only discovery and the reference syntax for function code and webhook headers. Use whenever an integration needs an API key or token; never inline one.
- [Simulations & Test Cases](skill/simulations.md) — Simulation test cases and runs: an LLM caller talks to a version and a judge grades PASS/FAIL. Use to create test cases, run them, and read results before publishing.
- [Workflows + Contacts together](skill/workflows-and-contacts.md) — How contacts and workflows connect: enrolment, the data a workflow reads from the CRM, and writing results back. Use when a workflow must act on contact attributes or update them.
- [Workflows](skill/workflows.md) — Workflow graphs via ck: steps (call, wait, WhatsApp, branch, CRM update), validation, import and runs. Use to build, edit or inspect a workflow from the CLI.

### Agents

- [Account survey reference (301 agents, Sept 2026)](skill/agents/account-survey.md) — What 301 production agents actually configure (types, voices, transcribers, models, time limits, silence). Use to sanity-check a config against real practice, not as rules.
- [CallKaro Agents & Versions — Complete Reference](skill/agents/AGENT-VERSION-REFERENCE.md) — Every agent and version field: where it lives, allowed values, traps, minimal payloads. Use to check a field before any create or update; read it by section, it is long.
- [Creating & Updating Agents](skill/agents/create-update.md) — Creating an agent in one JSON (agent and version fields together) and updating it with --versions. Use when assembling agent.json or patching an existing version.
- [CallKaro Voice Agents](skill/agents/field-notes.md) — Production traps: default snippet texts, the systempromptType trap, endpointing, fields that silently drop, speech hygiene, A/B rule chains. Use with the field reference before a write.
- [Functions — giving the agent abilities](skill/agents/functions.md) — Which function type to use (transfer, hold, booking, custom pre/in/post-call), basic or advanced, and where to attach it. Read first when adding a function; then function-authoring.
- [Post-Call Variables and Outcomes](skill/agents/post-call.md) — Post-call variables, analysis prompt, conversionreason, dispositions and per-duration models. Use when defining outputs or when extracted values are wrong, empty or guessed.
- [Writing Agent Prompts](skill/agents/prompts.md) — The sections of a complete agent prompt and how to choose the prompt type (0 to 3). Use as background when writing or restructuring a prompt; house rules point to the writing nodes.
- [Voice Agents — the core entity](skill/agents/README.md) — What a voice agent is (LLM, voice, transcriber, prompt, functions, post-call) and the ck agent commands. Use as the entry point for any voice-agent task.
- [Client Regression — branch coverage & verification discipline](skill/agents/regression.md) — Branch library and verification checklist that turns a PRD into a test suite. Use when building from a spec, auditing a live agent, or checking a fix did not break another branch.
- [Versions, Publishing & A/B Testing](skill/agents/versions.md) — Versions, cloning, publishing per language and A/B testing (normal and advanced rules). Use when making a new version, publishing, or splitting traffic between versions.
- [Voice (TTS) & Transcriber (STT) — choosing them](skill/agents/voice-and-transcriber.md) — Choosing the voice (TTS) and transcriber (STT) for a language and persona, and fixing mishearing. Use when setting or changing voice or transcriber; field tables are in the reference.

### Authoring Pipeline

- [Advanced In-Call Function Agent](skill/authoring-pipeline/advanced-in-call-agent.md) — Pipeline stage 6: writes Python source for custom in-call functions the LLM calls mid-call. Use when an in-call function needs logic or several requests.
- [Advanced Post-Call Function Agent](skill/authoring-pipeline/advanced-post-call-agent.md) — Pipeline stage 6: writes JavaScript source for custom post-call functions. Use when results need transforming or routing to several systems after the call.
- [Advanced Pre-Call Function Agent](skill/authoring-pipeline/advanced-pre-call-agent.md) — Pipeline stage 6: writes Python source for custom pre-call functions (P0 data loading and prompt rewriting). Use when a pre-call function needs code, not a fixed request.
- [Agent Behavior Agent](skill/authoring-pipeline/agent-behavior-agent.md) — Pipeline stage 7: silence handling, language switching, gender detection and turn-taking (VAD). Use when a request changes how the agent behaves between turns.
- [Call Flow JSON Agent](skill/authoring-pipeline/call-flow-json-agent.md) — Pipeline stage 7: converts a text call flow into the node graph JSON for the visual call-flow editor. Use when the call flow needs its diagram view.
- [Call Initiation & Termination Agent](skill/authoring-pipeline/call-init-term-agent.md) — Pipeline stage 7: who speaks first, opening pauses, voicemail and how the call ends (endcallmsg, time limit). Use when a request changes how calls start or end.
- [Call Parameters Planner](skill/authoring-pipeline/call-params-planner-agent.md) — Pipeline stage 7: decides which call-parameter areas a request touches (voice, LLM, behaviour, settings, fillers, languages, formatting, call flow). Use before changing any call parameter.
- [Call Settings Agent](skill/authoring-pipeline/call-settings-agent.md) — Pipeline stage 7: background noise, noise cancellation, DTMF and other call settings. Use when a request changes the call's audio or input settings.
- [Filler & Pronunciation Agent](skill/authoring-pipeline/filler-pronunciation-agent.md) — Pipeline stage 7: filler sounds while the agent thinks and custom pronunciations. Use when a request changes fillers or how a word is spoken.
- [Function Critic Agent](skill/authoring-pipeline/function-critic-agent.md) — Pipeline stage 6 check: verifies every planned function operation was carried out correctly and returns a verdict. Run after each function change.
- [Function Planner Agent](skill/authoring-pipeline/function-planner-agent.md) — Pipeline stage 6: decides which functions to create, update or delete for the agent. Use before generating any function.
- [In-Call Basic Function Agent](skill/authoring-pipeline/in-call-basic-agent.md) — Pipeline stage 6: generates a declarative in-call API function the LLM can call mid-call. Use when the plan needs a live lookup or action through a plain API call.
- [LLM & Caching Agent](skill/authoring-pipeline/llm-caching-agent.md) — Pipeline stage 7: sets the LLM, fallback model, temperature and caching. Use when a request changes the model or response caching.
- [Multi-Prompt Script Writer](skill/authoring-pipeline/multi-prompt-script-writer-agent.md) — Pipeline stage 3 for types 2 and 3: the script writer prompt for the base prompt and each capability or node, with the plain-text house rules. Use to write a multi-prompt or pathway script.
- [Planner (Multi-Prompt)](skill/authoring-pipeline/planner-agent-multiprompt.md) — Pipeline stage 2 for types 2 and 3: the planner prompt for multi-prompt capabilities and pathway nodes. Use before writing a multi-prompt or pathway agent.
- [Planner](skill/authoring-pipeline/planner-agent.md) — Pipeline stage 2 for types 0 and 1: the planner prompt that turns the requirement into an execution plan. Use before writing a basic or advanced agent's script.
- [Post-Call Basic Function Agent](skill/authoring-pipeline/post-call-basic-agent.md) — Pipeline stage 6: generates a declarative post-call API function (send results after the call). Use when the plan needs a plain webhook or API write after the call.
- [Pre-Call Basic Function Agent](skill/authoring-pipeline/pre-call-basic-agent.md) — Pipeline stage 6: generates a declarative pre-call API function (fixed request, no code). Use when the plan needs data fetched before the call by a plain API call.
- [Pre-Format Variables Agent](skill/authoring-pipeline/pre-format-agent.md) — Pipeline stage 7: how raw {{variables}} are formatted before the prompt (dates, numbers, currency). Use when metadata values must be spoken in a specific format.
- [Predefined Functions Agent](skill/authoring-pipeline/predefined-agent.md) — Pipeline stage 6: generates no-code functions (transfer, hold, availability, booking, end). Prefer endcallmsg over an end function. Use when the plan calls for a predefined function.
- [The ai-fde Authoring Pipeline — build agents the way our own AI does](skill/authoring-pipeline/README.md) — The ai-fde build pipeline: which production prompt runs at each stage (intake, plan, script, reflect, analyze, functions, parameters) and how outputs combine. Use to build an agent end to end.
- [Reflect Agent](skill/authoring-pipeline/reflect-agent.md) — Pipeline stage 4: the reviewer prompt that critiques a script in the 7-layer order and flags markdown, missing endcallmsg lines and patch rules. Loop with the writer until clean.
- [Script Analyzer for Functions](skill/authoring-pipeline/script-analyzer-for-functions-agent.md) — Pipeline stage 5: designs post-call variables, conversion reason and dispositions from the finished script. Use after the script is final, before functions.
- [Script Writer](skill/authoring-pipeline/script-writer-agent.md) — Pipeline stage 3 for types 0 and 1: the script writer prompt (systemprompt, or role/goal/callFlow fields), with the plain-text house rules. Use to write a basic or advanced script.
- [Switchable Entities Agent](skill/authoring-pipeline/switchable-entities-agent.md) — Pipeline stage 7: mid-call language switching targets and agent transfers (switchableLanguages, switchableAgents). Use when the agent must switch language or hand off to another agent.
- [Chatbot Supervisor](skill/authoring-pipeline/user-chatbot.md) — Pipeline stage 1, intake: the orchestrator prompt that turns a user request into the requirement and calls stages in order. Use when starting a build or update from a conversation.
- [Voice & Transcriber Agent](skill/authoring-pipeline/voice-transcriber-agent.md) — Pipeline stage 7: chooses and configures voice and transcriber for the language and persona. Use when a build or request touches voice or speech recognition.

### Design

- [Designing a CallKaro Agent](skill/design/agent-design.md) — Design an agent before any prompt: intake, type 0-3 choice, stage map, what pre-call functions compute, function inventory. Use for a new agent, a big change, or a prompt full of if/else.

### Functions

- [Function authoring rules](skill/functions/function-authoring.md) — Field-level authoring rules per function variant plus a review checklist. Read before writing, updating or reviewing any custom function's JSON or sourcecode.
- [CallKaro Functions](skill/functions/function-rules.md) — Function contracts, execution order, global vs capability scope, P0 and placeholder rules, failure patterns. Use when writing any function or when one crashes a call or fights another.
- [CallKaro function runtime: what custom function code can see and use](skill/functions/runtime.md) — What custom function code can see at runtime (globals, utils, ctx.session, language-switching internals), measured on real calls. Read before writing a function that needs more than its arguments.
- [Function skeletons](skill/functions/templates.md) — Skeleton code for P0 and prompt-rewriting pre-call, onconnected, in-call and post-call functions. Fill from the design; delete what the agent does not need.

### Integrations

- [CallKaro Calls API](skill/integrations/calls-api.md) — Trigger CallKaro calls and campaigns over REST. Use when placing outbound calls, scheduling, retries, creating v1 or v2 campaigns, deleting scheduled calls, reading call history, handling errors.
- [CallKaro MCP](skill/integrations/mcp.md) — The remote CallKaro MCP server: which tool to use, the account-mismatch trap, safe edits, MCP vs ck. Use when CallKaro MCP tools are available or being set up.
- [CallKaro Webhooks](skill/integrations/webhooks.md) — Receive CallKaro realtime events. Use when setting up webhook destinations, handling callended, messagereceived, messagesent, templatesent, messagestatusupdated payloads.
- [CallKaro WhatsApp](skill/integrations/whatsapp.md) — Run WhatsApp on CallKaro. Use when connecting numbers, managing templates, sending via API, building campaign CSVs, reading inbox history, handling delivery status.
- [CallKaro Widget and Integrations](skill/integrations/widget-integrations.md) — Website widget install and CRM links (HubSpot, LeadSquared, Heltar, AI Sensy), number verification and DND. Use when embedding the widget or connecting a CRM.

### Platform

- [CallKaro AI Auditor](skill/platform/ai-auditor.md) — AI Auditor: writing audit strategies, filters, sampling, extra variables, reading strategy and batch reports, turning findings into fixes. Use to set up or read call audits.
- [CallKaro Chat Agents](skill/platform/chat-agents-design.md) — Build CallKaro chat agents for WhatsApp and Instagram. Use when creating chat agents, writing system prompts, configuring follow-ups, functions, channels, testing and monitoring.
- [CallKaro KPI Manager](skill/platform/kpi-manager.md) — KPI Manager: data sources, metrics and targets, the RCA prompt and reports, the Pending Tasks board. Use to set up KPI tracking or read why a metric missed its target.
- [CallKaro QA and Ops](skill/platform/operations.md) — Operate and debug CallKaro day to day. Use when monitoring calls, auditing, reading RCA, managing feedback, batch tables, scheduled queues, analytics, onboarding, pricing, AI FDE help.
- [CallKaro Workflows](skill/platform/workflows-build-and-debug.md) — Turn a follow-up plan into a workflow: step types, Conditions, importable JSON, enrolment, reading a run's path. Use to design a workflow or find why a run took the wrong branch.
- [CallKaro workflows](skill/platform/workflows-official-spec.md) — Verbatim official workflow spec (docs.callkaro.ai, fetched 2026-10-13): the importable workflow JSON, step types and Conditions. Source of truth when it disagrees with other nodes.

### Quality

- [Case library](skill/quality/qa-case-library.md) — Branch patterns to turn into QA cases from the Agent Brief: who answers, availability, slot attacks, objections, functions, endings. Critical cases are marked C.
- [CallKaro Agent QA Framework](skill/quality/qa-framework.md) — The standard QA method: Agent Brief, branch enumeration, simulation and manual cases, scoring (pass at 85, critical cases 5 of 5). Use to plan, run or score QA on a version.
- [CallKaro QA Grader](skill/quality/qa-grader.md) — Grade CallKaro QA test calls from history. Use when reviewing tester transcripts, scoring prompt vs function vs config faults, checking dispositions, or writing QA findings back to the team.
- [Workbook spec](skill/quality/qa-workbook.md) — Layout of the QA workbook (Agent Brief, review scores, simulation and manual cases, summary) as JSON.
- [Reviewing and Debugging an Agent](skill/quality/review-debug.md) — 7-layer agent review and root-cause debugging: evidence, frequency, layer, smallest fix, verify, never another NEVER line. Use to audit a version or when a call went wrong.

### Tools

- [The ck CLI](skill/tools/ck.md) — The ck CLI: rules that bite on every write (whole objects, whole function arrays, changed fields only), raw call logs, export/import, and what ck cannot do. Use for terminal work.
- [Harness tool map](skill/tools/harness.md) — For ai-fde's own harness: which harness tool does what a ck command in these nodes does, and which tasks have no harness tool yet. Read before acting on any ck instruction inside the harness.

### Writing

- [Conversational Agents: Writing the Call Flow](skill/writing/conversational-agents.md) — Write the prompt body: SAY vs composed lines, the prompt skeleton, call-flow steps, objections, endings, lines in each Indian language. Use when writing or fixing a semi-scripted prompt.
- [Conversational Voice: Sounding Human on CallKaro](skill/writing/conversational-voice.md) — Make the agent sound human: short turns, goals over scripts, example exchanges, rationed fillers, prompt size vs latency, Hinglish. Use when calls sound robotic, long or repetitive.
- [Language Switching: Implicit, Silent, Testable](skill/writing/language-switching.md) — Implicit language switching for multilingual agents: Section 0A, matching config (min words, allowed languages, transcriber), a 12-utterance test. Use when the agent must follow the caller's language.
- [CallKaro Prompt Style](skill/writing/prompt-style.md) — Plain-text house style for prompts: no markdown, banner sections, SSML pauses, the begin message, placeholder-safe rewrites. Use when writing, converting or shrinking any prompt.
- [Template A: Section 0A (implicit language switching)](skill/writing/template-a-language.md) — Paste-in Section 0A for multilingual agents with implicit language switching; its word threshold must equal languageswitchminwords. Fill every [[FILL]] first.
- [Template B: Section 0B (conversational agent)](skill/writing/template-b-conversational.md) — Paste-in Section 0B for semi-scripted agents: how the model reads SAY lines vs composed GOAL / MUST CONTAIN / NEVER blocks, turn length and how it sounds. Fill every [[FILL]] first.

<!-- END AUTO-GENERATED SKILL GRAPH -->
