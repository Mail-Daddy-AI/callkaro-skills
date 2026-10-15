# Anti-patterns seen in real suites (never do these)
<!-- graph-summary: Twelve test and criteria mistakes seen in real suites and why each gives false results; check when a test feels loose. -->

| Anti-pattern | Why it fails |
|---|---|
| Criteria like "Document exactly what happened" or "Count how many runs…" | The grader judges one transcript and returns pass/fail; it cannot investigate or count ([F13](how-simulation-works.md#12-verified-behaviour-you-must-design-around)) |
| "This is the most important test — it reveals what happens in production" with no mocks | An unmocked in-call function returns a generic success and the bot invents data ([F4](how-simulation-works.md#12-verified-behaviour-you-must-design-around)); it reveals nothing about production |
| Mocking a pre-call function and expecting the bot to use it | Pre-call mocks are ignored ([F5](how-simulation-works.md#12-verified-behaviour-you-must-design-around)) |
| Criteria that do not mention the close | Bots that never call `end_call` pass ([F8](how-simulation-works.md#12-verified-behaviour-you-must-design-around)) |
| "The agent handles the objection well" | Not observable; anything passes |
| Caller script "be a skeptical customer" with no scripted beats | The caller improvises, the scenario is not exercised, results vary for the wrong reason |
| Caller told to "say bye after 3-4 turns" | The caller ends the call and the bot's closing is never tested |
| Running everything once | Misses the defect that appears in 1 of 5 calls ([F12](how-simulation-works.md#12-verified-behaviour-you-must-design-around)) |
| Reading only `isTestSucceed` | Misses grader crashes ([F9](how-simulation-works.md#12-verified-behaviour-you-must-design-around)), false passes ([F10](how-simulation-works.md#12-verified-behaviour-you-must-design-around)) and caller drift ([F11](how-simulation-works.md#12-verified-behaviour-you-must-design-around)) |
| Rerunning one failed test until it passes, then publishing | Overfits one transcript and hides regressions elsewhere |
| A generic branch list (OTP, DND, upload error…) copied onto every bot | Tests behaviour the bot does not have and misses the behaviour it does |
| Testing language switching before functions, capabilities and guardrails work | Lowest-risk behaviour gets the attention; integration bugs ship |
