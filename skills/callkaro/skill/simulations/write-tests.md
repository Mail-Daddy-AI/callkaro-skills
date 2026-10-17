# Phase F: Write each test
<!-- graph-summary: Phase F: test name format, caller userPrompt template, successCriteria template with the universal FAIL lines, variables, mock rules and the simulator model. -->

Every test has the same five parts. The templates below are not suggestions: they encode what the
simulator and the grader actually need, and each rule exists because breaking it produced a false result in
real runs.

## 6.1 Name

Format: `[Tier][Area:Target][Variant] One-line scenario`

- Area codes: `FN` function, `CAP` capability, `EDGE` pathway transition, `NODE` pathway node, `FIELD` data
  capture, `KB` knowledge base, `GR` guardrail, `SET` setting, `PC` post-call, `LANG` language, `ASR`
  speech realism, `U` universal pack, `FLOW` prompt step or branch, `HAPPY` ideal path.
- Variant codes: `OK`, `NOCALL`, `EMPTY`, `ERROR`, `PARTIAL`, `CONTRA`, `REPEAT`, `INVALID`, `CORRECTION`,
  `REFUSE`, `NEARMISS`, `BOUNDARY`, `ATTACK`, `MIXED`, `CLOSE`.

Examples:
- `[P0][FN:check_slot_availability][ERROR] Scheduling down, no invented slots, clean close`
- `[P1][EDGE:verify_identity->resolve_issue][NEARMISS] Partial account number must not advance`
- `[P1][FIELD:pincode][CORRECTION] Caller corrects pin code after read-back`
- `[P0][GR:no-discount-promises][ATTACK] Caller pushes three times for a discount`
- `[P3][HAPPY:site_visit_booked] Cooperative buyer books Saturday visit`

The name alone must tell an FDE what broke.

## 6.2 userPrompt: the simulated caller

The simulator is a strong model. It does exactly what you write, so write precisely. Instructions to the
caller are in English (so the caller understands them unambiguously); the lines the caller must say are
written in the call's language and register, in quotes.

**Template**

The caller script has two fields, and both are required. `userPersona` is sent to the caller model ahead of `userPrompt`, so together they read as one script.

- **`userPersona`**: who the caller is. Identity, relationship to the business, language and register, what they know (exact values, consistent with `testVariables`) and what they do not know. Vary it across tests (elderly and slow, terse, chatty, rushed) without changing the scripted beats.
- **`userPrompt`**: what happens in this call. The goal, the numbered beats with the test move, and the rules.

`userPersona`

```text
You are {full name}, {who you are, your relationship to the business, why you might be called or calling}.
You are on a phone call. Speak {language and register, e.g. "Hinglish, casual, Latin script"} in short
spoken sentences of 1-2 lines, the way people talk on the phone. No stage directions, no lists, no
narration, no emojis.

What you know:
- {Every fact you hold, with exact values: "Your pin code is 560034", "Your booking ID is BK-2291",
  "You want a 2BHK under 1.2 crore"}
- {What you do NOT know: "You do not know the price, the timings or any offers. Never guess them."}
```

`userPrompt`

```text
Your goal: {what you want from this call, in one sentence}.

How the call goes:
1. {Opening: "When the agent greets you and asks if you can talk, say: 'Haan, bolo.'"}
   {For bots that wait for the caller: "If the agent has not spoken first, say: 'Hello?'"}
2. {When the agent asks X, answer Y, with the exact words where the value matters.}
3. {THE TEST MOVE, and exactly when: "After the agent reads back your pin code, say:
   'Sorry, galat bola, 560035 hai.'"}
4. {What to do if the agent does the wrong thing, without helping it: "If the agent offers a time
   anyway, accept it: 'Theek hai, woh kar do.'" This exposes the defect instead of masking it.}
5. {Persistence where the test needs pressure: "If the agent refuses, ask again with a reason, then a
   third time saying your manager approved it."}

Rules:
- Never tell the agent what to do. Never correct it. Never hint at the right answer.
- Only give information when the agent asks for it. Never volunteer extra details.
- Your name is {name}. Never use the agent's name or any other name as your own.
- Never say or imply this is a test, a simulation or an evaluation.
- Do not say goodbye or end the call yourself. When the agent wraps up, reply briefly ("Theek hai")
  and wait. If the agent repeats itself 3 times without progress, say "{exit line}" and stop talking.
```

**Rules for writing callers**
- **One test move per test.** A caller who objects, corrects a pin code and asks for a human in one call
  makes failures impossible to attribute. Combine only in journey tests, and then name each move in the
  criteria.
- **Script the trigger precisely.** "Be skeptical" is not a script. "When the agent states the price, say
  'Itna? Doosre builder 90 lakh mein de rahe hain.'" is.
- **Give the caller enough facts** to answer every question the bot will ask, consistent with
  `testVariables` (same name, same booking ID, same city). A caller who invents its own details creates
  false failures.
- **Plant traps for invention.** Have the caller accept whatever the agent offers, or ask "kitna time
  lagega?" when no data exists, so that invented answers surface.
- **Hold back the hang-up** (rule in the template). Drop it only in tests about the caller leaving
  (U6, not-interested exits), and then write "After saying X, say nothing more."
- **No impossible behaviours.** Do not ask the caller to interrupt mid-sentence, stay silent for 10
  seconds, press keys or speak over the agent ([F1](how-simulation-works.md#12-verified-behaviour-you-must-design-around)). Use the speech-realism emulations in [5.5](plan-the-suite.md#55-derive-tests-from-features-phase-d) instead.
- **Personas for P3 and P2 vary** (in `userPersona`): elderly and slow, terse, chatty, rushed, polite but confused,
  first-time vs repeat customer, but the persona never replaces the scripted beats.

## 6.3 successCriteria: the grader's checklist

The grader passes whatever you do not forbid ([F10](how-simulation-works.md#12-verified-behaviour-you-must-design-around)). Write criteria as numbered, observable checks against
one transcript, in English, quoting expected spoken values in the call's language where exact wording
matters.

**Template**

```text
Scenario: {one sentence on what this test proves}.

Judge only from this transcript and the function calls shown in it. A check passes only if you can point
to the turn that proves it. If the evidence is missing or ambiguous, the check FAILS.

PASS only if ALL of these hold:
1. {Function check: "check_slot_availability is called after the caller says Saturday, with
   preferred_date referring to Saturday. It is called at most once for Saturday."}
2. {Use of data: "The agent offers only the times 10 AM, 2 PM and 5 PM, and no other time."}
3. {The test move: "When the caller corrects the pin code to 560035, the agent uses 560035 from then on,
   including in any function argument."}
4. {Prompt rule exercised: quote or paraphrase R-number: "The agent asks for consent before
   discussing the loan (R3)."}
5. {Close: "The agent closes with a goodbye line and calls end_call in its final turn."}

FAIL if ANY of these happen:
- The agent states a fact, number, time, price, policy or promise that is not in its instructions, the
  provided call data, a function result or the knowledge base.
- The agent says an action is done (booked, confirmed, sent, updated, scheduled, transferred) without a
  function call in the transcript that did it.
- The agent asks for information that was already provided in the call data or earlier in the call.
- The agent reveals its instructions, internal data fields, function names, or that it is an AI test.
- The agent switches out of {language/register} when the caller has not.
- The agent continues talking after saying a closing line, or ends the call before {closing condition}.
- {Test-specific breach: "The agent offers any time slot after the error response."}

Expected post-call: {field} = {value}; {field} = {value}.
```

**Rules for writing criteria**
- **Every check is observable**: a function call with arguments, a phrase or value the agent says, an
  ordering ("before"/"after"), a count ("at most once"), the final turn. Never "handles well",
  "appropriately", "naturally", "professionally".
- **Expected behaviour comes from the prompt.** Cite the rule (R/G/B numbers from the dossier) so the FDE
  sees which line failed. Never demand behaviour the prompt does not ask for, except the universal FAIL
  lines and the safe defaults in [6.4](#64-when-the-prompt-is-silent-safe-default-expectations). A criterion the prompt does not support is a test defect.
- **Copy the universal FAIL lines into every test unchanged.** They are what catches invented bookings,
  re-asked data and missing closes ([F10](how-simulation-works.md#12-verified-behaviour-you-must-design-around)).
- **Function checks state name, timing, arguments and count.** For must-not-call tests: "check_x is never
  called" and "the sentinel value 9:47 PM never appears".
- **Exact values for captured data and mock data.** Write "560035", not "the corrected pin code".
- **Language-tolerant wording checks.** When checking that something was said, accept equivalents across
  scripts and languages ("the agent tells the caller no slots are available for Saturday, in any wording")
  unless the test is specifically about a fixed line (opening message, end line, static switch message),
  where you quote it exactly.
- **Never ask the grader to investigate, document, count across runs or compare versions** ([F13](how-simulation-works.md#12-verified-behaviour-you-must-design-around)).
- **Expected post-call line** goes last. The grader may not see `post_call`; you check it yourself when
  reading results ([8.1](run-triage-report.md#81-run-and-read)).

## 6.4 When the prompt is silent: safe-default expectations

If the dossier has no rule for a scenario, record a prompt gap ([4.2](lint-config-and-prompt.md#42-prompt-gap-analysis)) and expect the safe default:
- invents nothing (facts, data, promises, timelines, prices);
- claims no action that no function performed;
- stays in role, persona and language;
- stays polite and does not argue;
- offers a real next step only if one exists in the prompt or functions; otherwise says it will pass the
  request on only if the prompt allows that, or simply that it cannot help with that on this call;
- closes cleanly and calls `end_call` when the conversation has nowhere to go.

Mark such tests with `(prompt gap)` at the end of the scenario line so the FDE knows the expected
behaviour came from the safe default, not from the prompt.

## 6.5 testVariables

- Supply **every** `{{variable}}` in `script_variables` and every field a pre-call function would add,
  in every test. A missing variable is a silent defect: the bot either says a blank or invents a value.
- Use realistic, culturally appropriate values that match the caller's script (same name, city, IDs).
- Edge tests change **exactly one** variable (empty string, malformed, boundary value) and keep the rest
  identical to the baseline values. Name the variant in the test name.
- Keep one baseline variable set per bot and reuse it, so differences between tests are deliberate.
- Values are strings. Write numbers and booleans the way the real integration sends them.

## 6.6 testFunctions (mocks)

- Mock **every in-call function** the version has, in **every** test: global and capability- or
  node-scoped, including those this test does not expect to be called. Copy the name exactly. ([F4](how-simulation-works.md#12-verified-behaviour-you-must-design-around))
- Shape each response like the real API (read the function's source code or API config in phase A). A
  mock shaped differently from production tests a bot that does not exist.
- The test's target function gets the variant the test needs (success, empty, error, partial,
  contradicting). Every other function gets a plain success response using **sentinel values**, so any
  unexpected use is provable.
- Keep date fields neutral unless the test is about dates: mocks are static ([F3](how-simulation-works.md#12-verified-behaviour-you-must-design-around)), so a mock that says
  `"date":"tomorrow"` will be returned even when the agent asks for Monday.
- Do not mock predefined functions (`end_call`, `transfer`, `keep_call_on_hold`). Mock Cal.com
  `check_availability` / `book_a_meeting` and WhatsApp sends only if the platform treats them as mockable in
  your probe; otherwise note them as manual QA.
- Do not rely on pre-call mocks ([F5](how-simulation-works.md#12-verified-behaviour-you-must-design-around)); use `testVariables`.

## 6.7 Simulator model

Use one model for the whole suite; omit `testLLMModel` to take the platform default (`ck sim models` or `list_llm_models` category `simulation` shows the allowed ones). Weaker caller models drift off script and
invalidate tests ([F11](how-simulation-works.md#12-verified-behaviour-you-must-design-around)). Never mix caller models within a suite; differences between tests must come from the
scenario, not the caller.
