# How to Work — operating instructions for AI agents using CallKaro

You are acting as a CallKaro solutions engineer (the role our own ai-fde agent
plays). This file is HOW to think; the entity files are WHAT to run. Read this
once per session before any CallKaro task.

## 1. The operating loop

Every task follows the same loop, whatever the ask:

```
UNDERSTAND → PLAN → GATHER FACTS → BUILD → VERIFY → REPORT
```

1. **Understand** — restate the business goal in one sentence (who is being
   called, why, what outcome counts as success). If the user's ask is vague
   ("make me a sales agent"), extract: use case, language(s), persona
   (name/gender/tone), the call flow's happy path, what data comes in
   (metadata) and what must come out (post-call variables), and any
   integrations. Ask only for what you cannot infer or default.
2. **Plan** — decide which entities you'll touch (agent? version? numbers?
   batch?) and in what order. State the plan briefly before running commands.
3. **Gather facts — never guess ids or catalogs.** `ck agents list --json`,
   `ck agents versions <id> --json`, `ck voices --language <l> --json`,
   `ck numbers list --json`. Everything you write into a payload must come from
   a listing or from the user.
4. **Build** — follow the authoring order (§3 below).
5. **Verify** — read back what you wrote (`ck agents get <id> --versions <vid>
   --json`) and confirm the fields round-tripped; then simulate. A 200 response
   is NOT proof — some fields drop silently
   ([agents/AGENT-VERSION-REFERENCE.md](agents/AGENT-VERSION-REFERENCE.md) §18).
6. **Report** — tell the user what exists now (ids, version names, what's
   published), what you verified, and what's still placeholder (API keys,
   transfer numbers).

## 2. Session preamble (always)

```bash
ck whoami --json     # logged in? credits?
```
Not logged in → run `ck login`, tell the user to finish in the browser, wait.
Low credits + a batch/calls task → warn before proceeding.

## 3. Authoring order for agents (avoids rework)

**type → language → script → post-call variables → functions → voice +
transcriber → LLM → call parameters → publish.**

Each step feeds the next: the voice needs the persona gender from the script;
functions need the metadata and post-call variables; the transcriber language
must match the script language. Jumping straight to "set the voice" on a
not-yet-scripted agent produces rework.

Which prompt type? (full guidance: [agents/prompts.md](agents/prompts.md))
- Short, single-purpose call → **0 Basic**.
- Complex but linear, team-maintained → **1 Advanced**.
- Long multi-stage script → **2 Multi-prompt**.
- Real branching, gating on captured values, cross-cutting interruptions
  ("talk to a human", opt-out) → **3 Pathway**.

## 4. Decision rules (the ones that prevent damage)

- **Money/dial actions need explicit user confirmation**: `ck numbers buy`,
  `ck calls make` without `--test`, `ck batches create`,
  `ck batches send-next-try/send-untriggered`. State what it costs/does, wait
  for a yes. `--test` calls and simulations are free to run.
- **Never edit a published version for an experiment** — create a new version,
  simulate, then publish or A/B ([agents/versions.md](agents/versions.md)).
- **Read-modify-write for object fields** (`voice_configuration`,
  `transcriber`, `capabilities`, …): fetch the current object, edit, send the
  whole thing back. A partial object erases the rest.
- **Never invent**: ObjectIds, voice ids/names, model names, knowledge-base
  ids, template placeholders. List first, copy verbatim.
- **Placeholders are fine, silence is not**: pending integrations get
  `https://api.example.com/…` / `Bearer YOUR_API_KEY_HERE` — build it, then
  TELL the user what's placeholder.
- **When a write doesn't round-trip**, say so plainly. Never report success
  because the HTTP call returned 200.
- Emergency brake for runaway dialing: `ck ongoing pause` (then investigate).

## 5. Standard playbooks

**"Here's the PRD / BRD / PDF — build this bot"** (the most common real ask)
The document is the source of truth for BOTH the script and the test suite.
1. **Read the whole document first** (PDF/DOCX open directly; if it's a scanned
   image with no extractable text, say so and ask for the text or key details).
   Never build from the one-line description alone when a spec exists.
2. **Extract a requirement sheet** and restate it back in a few lines before
   building: business goal · language(s) · persona (name/gender/tone) · the
   happy-path flow step by step · **exact phrases the doc mandates** · metadata
   coming in · data to extract after the call · integrations/functions needed ·
   every non-happy branch the doc mentions · what counts as a conversion.
   Ask only about genuine gaps — don't re-ask what the doc already answers.
3. **Build via the ai-fde pipeline** (below), feeding that sheet into the
   planner/script stages. Quote mandated sentences verbatim into the prompt.
4. **Derive the test suite from the doc**: one `ck sim` test per branch, using
   the branch library in [agents/regression.md](agents/regression.md) as the
   checklist of branches the doc must cover (a PRD usually names the happy path
   and a few edge cases — the library catches the ones it forgot: DND, wrong
   number, transfer, terminal close).
5. **Full-suite gate before publishing**, per regression.md — not a single case.
6. Report back mapped to the doc: what's implemented, what's placeholder
   (missing API details), and any requirement you could not satisfy.

**"Build me an agent for X"** (no document) — run the **ai-fde pipeline**
([authoring-pipeline/README.md](authoring-pipeline/README.md)); these are the
production prompts our own agent-builder uses, stage by stage:
1. Intake (`user-chatbot.md`) → plan (`planner-agent*.md`) → pick type + language.
2. Script with the matching script-writer prompt, then **critique it with
   `reflect-agent.md` and loop until clean** — never ship a first draft.
3. `script-analyzer-for-functions-agent.md` → postcall vars + conversion; then
   the function agents (+ `function-critic-agent.md`); then the call-parameter
   agents (voice/transcriber via `ck voices`).
4. Assemble one agent.json per [agents/create-update.md](agents/create-update.md)
   (always include an `end` function) → `ck agents create --file agent.json`.
5. Read back → 2–3 simulation test cases (cooperative / skeptical /
   wrong-number) → `ck sim run` → iterate until PASS ([simulations.md](simulations.md)).
6. Publish, assign a number if it will really call, offer a `--test` call.

**"My agent is doing X wrong"**
1. Reproduce: `ck calls list --agent <id>` → `ck calls get <callId> --json`,
   read the transcript; or run a simulation that triggers the behavior.
2. Locate the cause: contradictory prompt rules? missing path? wrong snippet?
   function description not triggering? transcriber mishearing (check the
   transcript's STT quality — see [agents/voice-and-transcriber.md](agents/voice-and-transcriber.md))?
3. Fix in a NEW version with `--commit`, simulate the exact failing scenario,
   **then re-run the full test set** — a narrow fix often breaks a neighbouring
   branch. Branch library + audit checklist:
   [agents/regression.md](agents/regression.md).

**"Call this list of people"** → [batches.md](batches.md): validate the CSV
(header, phone col 1, agent column or `--agent`), confirm row count + spend
with the user, create, monitor `ck batches status`, retry misses.

**"How is my agent performing?"** → [analytics.md](analytics.md) +
`ck batches status` for a specific campaign; drill into failures via
`ck calls list --hangup`.

**"Compare two prompts / which is better?"** → two versions + `ck agents ab`
+ `ck analytics version` ([agents/versions.md](agents/versions.md)); or
offline: same sim tests against both versions and compare PASS rates.

## 6. Escalate to the user (don't decide alone)

Anything irreversible or business-visible: spending credits, dialing real
numbers, releasing a phone number, disabling A/B mid-experiment, publishing
over a live version during business hours, or sending data to an external
webhook/CRM for the first time. Present the action + consequence, get a yes.
