# Phase A: Profile the bot (the dossier)
<!-- graph-summary: Phase A: which inspect commands to run and the dossier template (use case, structure, rules, guardrails, functions, data, variables, post-call fields) whose numbered items become coverage items. -->

Do not write a single test until the dossier is complete. Read with `inspect_agent_version` on the exact
version under test. Use these commands:

| Command | Why |
|---|---|
| `summary` | Type, language, models, time limit, counts |
| `script` with `fullText: true` (and `includeCapabilityPrompts: true` for Multi Prompt / Pathway) | The full prompt: the source of most expected behaviour |
| `capabilities`, then `capability_details` per capability with `fullText: true` | Each capability's prompt, flags, scoped functions, post-call fields, model |
| `pathway_graph` (Pathway only) | Nodes, transitions, conditions, extract variables, global nodes |
| `list_functions`, then `function_details` per function with `includeSourceCode: true` | Every function's type, scope, trigger, parameters, response shape, side effects |
| `script_variables` | Every `{{variable}}` the prompts use |
| `postcall_variables` | Every post-call field, type, allowed values, default; conversion and disposition rules |
| `call_parameters` | Opening behaviour, end lines, silence, language, transfer, reschedule, KB, pronunciation, metadata exposure |
| `llms` | Which model runs where |

Read every prompt in full. Do not work from previews. Every line of a prompt is a potential test.

## 3.1 Dossier template

Write the dossier as a working document before planning tests. Every row must be filled; write "none" when
something is absent.

```markdown
BOT DOSSIER: <agent name> / <version name> (<versionId>)

1. Use case: <what the call is for, in one sentence>
   Direction: inbound | outbound | both
   Caller: <who is on the other end and their relationship to the business>
   Success outcome(s): <each distinct way the call can succeed, e.g. visit booked, callback set>
   Other end states: <not interested, wrong person, DND, transfer, error, …>
   conversion_reason: <text or none>

2. Persona and language
   Agent name / gender: <…>
   Default language: <code>; register: <e.g. Hinglish, formal Hindi>
   Language switching: on | off; allowed: <list>; switchableLanguages: <list or none>

3. Type: Basic | Advanced | Multi Prompt | Pathway

4. Structure
   Basic/Advanced: flow steps in order (S1, S2, …), each conditional branch (B1, B2, …)
   Multi Prompt: each capability (C1…) with: purpose, entry trigger, exit rule, flags
                 (is_starting, overwrite, stick_capability, switch message), scoped functions, model
   Pathway: each node (N1…) with type (normal/global), prompt purpose, extract variables (required?),
            each transition (E1…) as: from → to, condition type 0/1, condition text;
            each global node's when_to_jump

5. Prompt rules (one line each, numbered R1, R2, …)
   Every instruction, every "if…then", every rebuttal, every closing rule, every data-handling rule.

6. Guardrails and prohibitions (G1, G2, …)
   Every "never", "do not", "only", "must", compliance line, and data the bot must not reveal.

7. Functions (F1, F2, …)
   name | type | scope (global / capability / node) | trigger (from description and prompt) |
   inputs | response shape (from source code or API config) | side effect | expected behaviour on
   success / empty / error

8. Data the bot must capture (D1, D2, …)
   field | format and validation | where it is used (function argument, extract variable, post-call) |
   read-back required?

9. Variables (V1, V2, …)
   Every {{variable}} and every pre-call output field, with a realistic value and its meaning.

10. Knowledge base: attached? <ids>; facts the bot must answer (from owner): <list or "owner to supply">

11. Settings visible in text (S-settings)
    Opening (outbound speakfirst value + message; inbound speakfirst_inbound), end_call_msg lines,
    transfer targets and conditions, hold, auto_reschedule + prompts, followup, switchableAgents,
    preFormatVariables, insert_metadata_in_prompt, time_limit.

12. Post-call fields (P1, P2, …)
    name | type | allowed values | default | which scenario should produce each value
```

Everything numbered in the dossier (S, B, C, N, E, R, G, F, D, V, KB facts, settings, P) is a **coverage
item**. Each coverage item must map to at least one test ID in the coverage matrix (section [8.4](run-triage-report.md#84-report-format)).
