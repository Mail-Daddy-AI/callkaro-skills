# How simulation actually works
<!-- graph-summary: What a run is and does, the verified platform facts F1–F14 (static mocks, pre-call functions ignoring mocks, caller hang-ups, grader crashes), and what is still unverified. Mandatory first read. -->

Read this section before writing anything. Many rules later in this file exist only because of these facts.
They were verified against real runs; anything not verified is listed separately with a safe default.

## 1.1 What happens in a run

- A simulation is a **text conversation** between two LLMs:
  - the **agent**: the version's real prompt, capabilities or nodes, functions and models (per-capability
    models are honoured);
  - the **simulated caller**: driven by the test's `userPrompt`, played by `testLLMModel`.
- After the conversation, **post-call extraction** runs with the version's post-call fields, and an **LLM
  grader** judges the transcript against `successCriteria`.
- Every result contains:
  - `transcript`: each turn, with the function calls made on that turn (name, arguments, result, `is_mock`);
  - `ended_by` (e.g. `user_hangup`), `total_turns`, `duration_seconds`;
  - `post_call`: each extracted field with a value and the extractor's comment;
  - `analysisStatus` (`ok` or `failed`), `isTestSucceed` and `testResultSummary` from the grader;
  - `isPerformedLikeUser`: the grader's view of whether the simulated caller followed its script;
  - costs (agent, simulator, analysis) and `logfile_url`.
- A run executes **every test × every version × epochs**. `totalRuns` on the run equals that product.

## 1.2 Verified behaviour you must design around

| # | Fact | What it means for you |
|---|---|---|
| F1 | No audio. No STT, TTS, VAD, noise, interruptions, silence timers, voicemail or DTMF. | Never write a test that depends on them. Put them on the manual-QA list. You can emulate the *text effects* of speech (see [5.5](plan-the-suite.md#55-derive-tests-from-features-phase-d), speech realism). |
| F2 | In-call function mocks work: the mock is returned verbatim to the agent. | Mock every in-call function, in every test. |
| F3 | A mock is **static**: one fixed response per function, whatever arguments the agent sends. | You cannot script "first call empty, second call has slots" in one test. Split sequences into separate tests, and never write criteria that expect the mock to change with arguments. |
| F4 | An in-call function with **no mock** does not hit the real API. The platform returns a generic `{"status":"ok","result":"Mock result for <name>"}`. | A missing mock produces fake success and the agent invents data. This silently invalidates the test. Never leave an in-call function unmocked. |
| F5 | **Pre-call functions ignore mocks and call the real API**. When that fails, the agent receives nothing and may invent the enriched values. | Supply every field a pre-call function would add as `testVariables`. Treat any pre-call function with side effects (writes, SMS, CRM updates) as a production hazard and report it before running. |
| F6 | `on_connected` functions leave no trace in results. | Not observable. Manual-QA list. |
| F7 | Post-call extraction runs and its values are returned. | Every post-call field can and must be asserted with an expected value. |
| F8 | The simulated caller usually ends the call (`ended_by: user_hangup`). Across 15+ runs, an agent with `end_call` never called it, and no grader noticed. | Unless a test is about the caller leaving, the caller script must NOT hang up first, so the agent's own closing and `end_call` get tested. Criteria must check the close explicitly. |
| F9 | Grader failure is reported as `analysisStatus: "failed"`, with `isTestSucceed: false` and summary "Failed to run LLM analysis on simulation results." Records saved before `analysisStatus` existed carry only the summary text. | `isTestSucceed` means nothing when `analysisStatus` is `failed`. Classify the run INVALID, not FAIL, and rerun. For older records, match the summary text. |
| F10 | The grader passes whatever the criteria do not forbid. A real run passed a bot that "confirmed" a booking with no booking function, re-asked for known details and never ended the call. | Criteria must be exhaustive, evidence-based, and include the universal FAIL lines (section [6.3](write-tests.md#63-successcriteria-the-graders-checklist)). |
| F11 | The simulated caller can drift: one took the agent's own name, yet `isPerformedLikeUser` came back true. | Caller scripts must pin identity and behaviour tightly. Read transcripts for drift yourself; do not trust `isPerformedLikeUser` alone. |
| F12 | Behaviour varies between epochs: 1 of 5 identical runs invented a wait estimate and a "priority booking". | Several epochs catch this, but simulation costs money, so the user chooses the epoch mode (section [5.3](plan-the-suite.md#53-epoch-preference-always-ask-before-running)). |
| F13 | The grader judges one transcript at a time. | Never write criteria that count across epochs, compare runs, or ask the grader to "document" or "investigate". Criteria are pass/fail checks, not research questions. |
| F14 | Results arrive one by one. There is no run-status flag. | A run is complete only when the result count equals `totalRuns`. |

## 1.3 Not yet verified: use the safe default until a probe confirms

| Unknown | Safe default until probed |
|---|---|
| Does simulation retrieve from an attached knowledge base? | Write KB tests, but run the KB probe ([Appendix A](platform-probes.md#appendix-a-platform-probe-tests)) first. If retrieval does not happen, mark KB tests BLOCKED and add KB to manual QA. |
| Do custom post-call functions run, and against real systems? | Do not rely on them. Report any post-call function with real side effects as a hazard. |
| Which capability or node was active per turn? | Infer from behaviour and from which scoped functions are called. Design tests so the active capability is provable from the transcript. |
| Does `time_limit` stop a simulated call? | Do not test time limits. Manual QA. |
| Do `switchableAgents` / `switchableLanguages` hand-offs happen in simulation? | Test that the hand-off message and condition are honoured in text; treat the actual hand-off as manual QA. |
| Does the grader see function results and `post_call`, or only spoken turns? | Write function checks against the function calls shown in the transcript, and check `post_call` yourself when reading results (phase H). |
| What does `ended_by` show when the agent calls `end_call`? | Check for the `end_call` function call in the last agent turn instead of relying on `ended_by`. |
| With `speakfirst` value 0 (agent waits), who opens the simulated call? | Caller scripts for such bots start with: "If the agent has not spoken yet, say 'Hello?'". |

If you run a probe and learn the answer, state it in your run report so the team can update this table.
