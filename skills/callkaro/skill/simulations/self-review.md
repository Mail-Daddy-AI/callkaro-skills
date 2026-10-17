# Phase G: Self-review before creating anything
<!-- graph-summary: Phase G: the coverage, per-test and suite checklist to pass before creating any test. Mandatory. -->

Read your whole suite once more as a hostile reviewer. Fix everything that fails this checklist. Do not
create tests until it passes.

**Coverage**
- [ ] Every dossier item (S, B, C, N, E, R, G, F, D, V, KB, settings, P) has at least one test ID.
- [ ] Every in-call function has all its variants from 5.5.
- [ ] Every capability has entry, no-false-entry and exit tests; every pathway edge is taken once.
- [ ] Every guardrail has a P0 attack. The universal pack (U1–U12) is present.
- [ ] Every post-call field has an exact expected value somewhere, including defaults.
- [ ] Every not-testable item is on the manual-QA list.

**Each test**
- [ ] One primary target and one test move.
- [ ] `userPersona` and `userPrompt` are both filled: persona holds identity, style and knowledge; prompt holds goal, beats and rules.
- [ ] The caller script has every fact the bot will ask for, consistent with `testVariables`.
- [ ] The caller cannot "help" the bot or hint at the answer.
- [ ] The caller holds back from hanging up, unless the test is about leaving.
- [ ] No impossible behaviour (audio, silence, keypad, interruption mid-sentence).
- [ ] Every in-call function is mocked; target function has the right variant; others have sentinels.
- [ ] Every variable is supplied.
- [ ] Criteria are numbered, observable, cite prompt rules, include the close, include all universal FAIL
      lines and the expected post-call line.
- [ ] No criterion asks for behaviour the prompt does not require (except universal lines and safe defaults).
- [ ] No criterion asks the grader to count, compare or investigate.
- [ ] Name follows the format and says what breaks.

**Suite**
- [ ] No true duplicates.
- [ ] Tiers assigned; epoch preference asked (or given); total simulated calls stated for the chosen mode.
- [ ] Baseline variables and baseline mocks are consistent across tests.
