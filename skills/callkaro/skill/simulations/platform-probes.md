# Appendix A: Platform probe tests
<!-- graph-summary: Appendix A: probe tests (KB retrieval, post-call functions, bot-ended calls, time limit, hand-offs, mocks) to run once per environment to settle the unverified platform behaviour. -->

Run these once per environment, and again after any simulation platform release. They test the platform,
not a bot, so use a small dedicated probe agent. Record results in the run report under "Platform
observations" and update section [1.3](how-simulation-works.md#13-not-yet-verified-use-the-safe-default-until-a-probe-confirms).

| Probe | Setup | What to look for |
|---|---|---|
| KB retrieval | Probe agent with a KB containing one invented fact ("The office cat is named Tofu") and a prompt that says to answer from the KB | Agent says "Tofu" when asked → KB works in simulation |
| Post-call function | `custom_post_call` posting to a harmless request-capture endpoint | Request arrives → post-call functions run against real systems in simulation |
| Bot-ended call | Caller script that never ends the call; prompt that ends after one exchange | Value of `ended_by` when the agent calls `end_call` |
| Turn limit | Caller script that never ends and an agent that keeps asking questions | Maximum `total_turns`, and how the run ends |
| time_limit | `time_limit` 30 seconds, long conversation | Whether the simulated call stops |
| speakfirst 0 | Outbound agent with `speakfirst.value` 0 | Who produces the first turn |
| Grader inputs | Criterion that can only be judged from a function result not spoken aloud, or from `post_call` | Whether the grader can see them |
| Capability/node visibility | Multi Prompt agent with a capability-scoped function | Whether results show the active capability per turn |
| Hand-offs | `switchableLanguages` or `switchableAgents` configured | Whether the hand-off happens inside simulation |
| Predefined mocks | Mock entries for `check_availability`, `book_a_meeting`, WhatsApp send | Whether mocks are used or real integrations are called |
| Mock argument sensitivity | Two calls with different arguments | Confirms [F3](how-simulation-works.md#12-verified-behaviour-you-must-design-around) still holds |
