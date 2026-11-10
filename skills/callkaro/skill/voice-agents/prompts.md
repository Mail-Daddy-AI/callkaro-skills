# Writing Agent Prompts
<!-- graph-summary: How to write a good prompt: the 8 sections, multi-prompt structure, the 5 snippets, rules that stop prompts breaking, Indian-language and persona conventions, closing lines and update rules. -->

The system prompt is the heart of the agent: who it is, its goal, how it
behaves, what it must never do, the call flow, and objection handling. This
file is HOW to write it well; field mechanics live in
[script-and-types.md](reference/script-and-types.md) §2–§5 and [capabilities-and-pathways.md](reference/capabilities-and-pathways.md) §4.

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
greeting, stronger for negotiation — temperature here is 0–1, not 0–10); and
`endpointing`, which controls turn completion for that phase. Its `min_delay`
reduces premature cutoffs, its `max_delay` limits the wait before ending a turn,
`fixed` applies configured timing consistently, and `dynamic` adapts within those
bounds to the caller's speech and conversation context.

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

(`gender_prompt_snippet` is a sixth, used only with `detect_gender: true`.) The default texts are in [snippets.md](snippets.md).

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
- After writing: **simulate** (../simulations/simulation-playbook.md) and fix every step where more
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

## Using memory of earlier calls

Call Memory ([call-memory-and-rotation.md](call-memory-and-rotation.md)) feeds functions, not the
prompt. To let the agent speak about a previous call, have a pre-call function put the facts into
metadata (for example `last_disposition`) and reference them with a fallback:
`If {{last_disposition}} is present, acknowledge it once ("Last time you asked for a callback") and
don't repeat questions already answered.` Never quote a transcript back at the caller.

## Closing lines, variables, updates

- `end_call_msg`: 2–3 natural closing lines in the agent's persona and language, for example
  `["ठीक है, आपका दिन शुभ हो!", "धन्यवाद, अलविदा!"]`. The call ends the moment the agent says one, so
  keep them to genuine final lines.
- Language codes: `en hi kn ta te mr gu bn ml`. Set `default_language` and `silence_language` to the
  language you actually wrote the script in.
- Placeholders: `{{name}}` is filled before the call from metadata, and `{name}` is captured or
  resolved during the call (full rules in [script-and-types.md](reference/script-and-types.md) §3).
- **Keep variables at the end (prompt caching).** The LLM caches the prompt only up to the first
  `{{name}}` / `{name}`, because everything after it differs per call. In the body write `<name>`
  (never substituted), and list every variable once as the last thing in the script:
  ```
  Greet the customer as <customer_name> and mention their loan of <loan_amount>.
  ...
  # Call variables
  Values for the <placeholders> used above:
  - <customer_name> = {{customer_name}}
  - <loan_amount> = {{loan_amount}}
  ```
  Type 0: end of `systemprompt`. Type 1: the last item of `rebuttals`. Types 2/3: end of each
  capability's `system_prompt` that uses variables. Pre-call/in-call `.replace("{name}", …)` code
  still works, since `{{name}}` in the list contains `{name}`. The dashboard shows a
  "% cacheable" badge and a "Make cacheable" button that does this rewrite.
- Updating an existing script: change only what was asked and keep its style, agent name and brand,
  and any custom placeholders. See [verify-and-review.md](verify-and-review.md).
