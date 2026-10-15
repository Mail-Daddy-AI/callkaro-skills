# Phase B: Lint the configuration and the prompt
<!-- graph-summary: Phase B: configuration lint checklist (opening, end lines, functions vs prompt, transfer, capabilities, pathway, language, post-call) and prompt gap analysis, run before any test. -->

Before testing behaviour, look for defects that exist on paper. Report them as findings with severity.
They are often the cheapest bugs to fix and some will make tests fail for reasons unrelated to the prompt.

## 4.1 Configuration lint checklist

- **Opening:** outbound `speakfirst.value` is 0 (wait) while a `customMsg` greeting is written → the greeting
  never plays and the outbound bot waits in silence. `speakfirst.value` 2 with an empty message.
- **Auto hang-up lines:** `end_call_msg` lines that the agent might also say mid-call (generic thank-yous,
  phrases shared with other prompt lines). The call ends the moment the agent says one, on any turn.
- **Functions vs prompt:** a function the prompt tells the bot to call is not attached (or attached to a
  different capability); an attached function is never mentioned in any prompt or has a vague description;
  a function description contradicts the prompt about when to call it.
- **Transfer:** transfer function with no destination; warm transfer on with no briefing prompt; prompt
  promises a human but no transfer exists.
- **Capabilities:** zero or several `is_starting`; a capability with no way to be entered; `overwrite: true`
  on a capability whose prompt relies on base-prompt rules; switch message static but empty.
- **Pathway:** unreachable nodes, nodes with no exit, cycles without a stop condition, transitions pointing
  at names that do not exist, required extract variables never asked for in the node prompt, expression
  conditions on metadata keys that are not supplied.
- **Variables:** `{{variables}}` used in prompts that no caller of this agent will supply; variables used in
  the opening line that could be empty (the bot would say "Hello  ji").
- **Language:** prompt says to switch languages but switching is off; allowed list excludes a language the
  prompt mentions; persona gender in prompt differs from the voice.
- **Reschedule:** `auto_reschedule` on but the prompt never handles "call me later"; or the prompt promises
  callbacks while auto-reschedule is off and no function schedules them.
- **Post-call:** selector values no scenario can produce; boolean fields whose description is ambiguous;
  `conversion_reason` that does not match the prompt's success outcome; fields duplicated across scopes.
- **Metadata exposure:** `insert_metadata_in_prompt` on while metadata holds data the bot must not speak.
- **Pre-call side effects:** any pre-call function that writes to an external system (hazard under [F5](how-simulation-works.md#12-verified-behaviour-you-must-design-around)).
- **Time limit:** `time_limit` shorter than a realistic happy path for this flow.

## 4.2 Prompt gap analysis

For each scenario in section [5.5](plan-the-suite.md#55-derive-tests-from-features-phase-d) and the universal pack (section [5.6](plan-the-suite.md#56-universal-negative-pack-every-bot)), ask: "Does the prompt say what the bot
should do here?" If not, record a **prompt gap** (e.g. "No wrong-party rule", "No instruction for when the
slot API fails"). You still test these scenarios, using the safe-default expectation from section [6.4](write-tests.md#64-when-the-prompt-is-silent-safe-default-expectations), and
the gap appears in your report so the FDE can decide the intended behaviour.

Also flag **contradictions** inside the prompt (two rules that cannot both hold) and **untestable promises**
(the prompt promises an SMS or email but no function sends one).
