# Writing Agent Prompts

> **Writing a script right now?** Use the production writer prompts in
> [../authoring-pipeline/](../authoring-pipeline/README.md) —
> `script-writer-agent.md` (types 0/1) or `multi-prompt-script-writer-agent.md`
> (types 2/3), then critique with `reflect-agent.md`. This file is the
> background theory; those are the operating instructions.

The system prompt is the heart of the agent: who it is, its goal, how it
behaves, what it must never do, the call flow, and objection handling. This
file is HOW to write it well; field mechanics live in
[AGENT-VERSION-REFERENCE.md](AGENT-VERSION-REFERENCE.md) §2–§5.

## The 8 sections of a complete prompt

Every good prompt contains these, whatever the mode. In Basic (type 0) you
write all 8 in one box; in Advanced (type 1) they map onto the ready-made
fields; in Multi-prompt/Pathway (2/3) they distribute across base + capabilities.

1. **Role / Persona** — name, language, tone, personality. *"You are Arya, a
   friendly and confident sales assistant from CallKaro AI. You sound warm,
   human, and never robotic."* Declare `Persona gender: male|female` explicitly.
2. **Goal / Objective** — what the call must achieve, in order. *Confirm
   identity → explain the service → book a demo.*
3. **Call Flow** — the step-by-step roadmap, with IF/THEN branches in plain
   words. *"If the customer says they are busy, then ask for a callback time,
   then end the call."*
4. **Instructions** — operational do's and don'ts. *"Always wait for the
   customer to finish speaking. Never repeat the same line twice."*
5. **Behavioural Guidelines** — tone, response length, formality, filler style.
6. **Rebuttals** — ready replies for pushbacks (*"call me later", "why are you
   calling?"*) that keep the call moving.
7. **Objections** — deeper concern handling: pricing, timing, trust.
8. **Guardrails** — hard limits. *"Never promise a price without knowing the
   order volume."*

Advanced mode's 6 boxes = Role, Goal, Instructions, Call Flow, Guardrails,
Rebuttals (behavioural guidelines fold into Role/Instructions; objections into
Rebuttals).

## Multi-prompt thinking (types 2/3)

Basic/Advanced = the agent re-reads the whole booklet every turn. Multi-prompt
= sticky notes: the base prompt (identity, brand, standing rules — active all
call) plus one capability per phase (greeting, qualification, booking,
objection handling, closing). Result: faster replies, better focus, and per-phase
LLM/temperature/functions/post-call control. Structure a capability set as:

- **Base prompt**: persona, company info, tone, universal rules, objection
  handling. **No call flow here.**
- **Start capability**: greet, introduce, check availability to talk, decide
  the next step.
- One capability per phase after that. In type 2, switching is prose inside the
  prompts ("when X, move to qualification"); in type 3 it's data (`transitions`).

Per-capability toggles that matter while writing: `overwrite` ON = this prompt
must be fully self-contained (base is excluded); `stick_capability` ON = once
entered, never leaves; `use_filler`; per-capability `llms` (cheap model for
greeting, stronger for negotiation — temperature here is 0–1, not 0–10).

## The 5 prompt snippets

Specialised instruction blocks the LLM prioritises — use them for tricky
scenarios instead of bloating the main prompt. Omit a snippet to get the
platform default; set `""` to suppress it entirely.

| Snippet | Governs |
|---|---|
| `model_response_snippet` | how replies are shaped — no stage directions, how to speak emails/numbers aloud |
| `security_guardrails_snippet` | scope limits, refusals, prompt-injection & abuse handling |
| `function_calling_snippet` | when/how to invoke functions and verbalise results (never read raw JSON aloud) |
| `language_switch_snippet` | when/how to change language smoothly |
| `hold_call_snippet` | hold behaviour: go on hold, stay silent until the caller returns |

(`gender_prompt_snippet` is a sixth, used only with `detect_gender: true`.)

## Rules for prompts that don't break

- **Plan the structure first**, then write. Use numbered sections/subsections
  (A, A.1, A.2) so every rule has a fixed address; separate sections with lines.
- **Say each thing once.** The prompt is sent on every turn — duplication costs
  tokens and the copies drift apart and clash.
- **Never write two contradicting rules** — the model picks one; this is the #1
  cause of bugs.
- **Literal instructions**: "ask for the 6-digit pincode", not "handle location".
- **No arrow symbols** (`→`); write "then". **No math or logic to compute** —
  the agent reads the prompt as text and cannot calculate; precompute dates and
  values and hand them as ready facts (or via a pre-call function).
- **Cover every path**: interested, not interested, busy/callback, wrong
  person, and ending the call. **Explicitly say when the right action is to do
  nothing** — otherwise the agent invents something.
- Train it like a new human hire: walk the call step by step.
- After writing: **simulate** (../simulations.md) and fix every step where more
  than one action was possible.

## Language & persona conventions (Indian-language agents)

- Spoken lines in the target language; **all operational text (headings, step
  labels, conditions, tool guidance) in English**.
- Native script, never romanised. Mix in the English words real speakers use
  (`booking`, `slot`, `confirm`, `payment`). Everyday spoken register, not
  literary.
- ONE persona gender across every field and the voice: Hindi `बोल रही हूँ … कर
  सकती हूँ` **or** `बोल रहा हूँ … कर सकता हूँ`, never mixed.
- Never translate capability names, function names, or `{{placeholder}}` names.
- Every `{{metadata}}` reference needs a fallback so an empty value is never
  spoken.
