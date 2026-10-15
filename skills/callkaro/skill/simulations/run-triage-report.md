# Phase H: Create, run, read, gate, report
<!-- graph-summary: Phase H: run the smoke test then the suite, read results in order (validity, mechanics, post-call, verdict), triage each failure to an owner, the release gate, and the report format. -->

## 8.1 Run and read

1. **Check existing tests** (`list_test_cases`). Do not duplicate them; update or replace weak ones and
   say which.
2. **Create** the tests. Record each test ID against its name and tier.
   Then ask the epoch preference with its cost estimate ([5.3](plan-the-suite.md#53-epoch-preference-always-ask-before-running)), unless the user already gave it.
3. **Run the smoke test first**: one P3 test, 1 epoch. If it fails, stop and report: the bot's base flow is
   broken and the rest of the suite would be noise.
4. **Run with the chosen epoch mode** ([5.3](plan-the-suite.md#53-epoch-preference-always-ask-before-running)). Fixed number: one run with every test at that number of
   epochs. AI decides: one run per tier (P0 at 5, P1 at 3, P2 at 3, P3 at 2). Name runs `<agent short name> <version> <tier> <date>`.
5. **Wait for completion**: results count = `totalRuns` ([F14](how-simulation-works.md#12-verified-behaviour-you-must-design-around)). An empty or partial list means still running.
6. **Read every result in this order**, not just the flag:
   1. **Validity.** INVALID if the summary says "Failed to run LLM analysis" ([F9](how-simulation-works.md#12-verified-behaviour-you-must-design-around)), or if the caller left its
      script (took another name, volunteered facts, ignored a scripted beat, hung up early contrary to
      its rules) whatever `isPerformedLikeUser` says ([F11](how-simulation-works.md#12-verified-behaviour-you-must-design-around)). Rerun invalid results once; if the caller
      drifts again, fix the caller script.
   2. **Mechanics.** Function calls in the transcript match the criteria: names, arguments, order, count.
      No sentinel values leaked. The last agent turn closes and calls `end_call` where expected.
   3. **Post-call.** Each `post_call` value equals the expected value in the criteria.
   4. **Verdict.** Only now read `isTestSucceed` and the summary. A PASS that contradicts steps 2–3 is a
      **FAIL with loose criteria**: count it as FAIL and tighten the test.
7. **Aggregate per test across the epochs that ran** and apply the tier pass rule ([5.2](plan-the-suite.md#52-tiers-recommended-epochs-and-pass-rules-phase-e)): with a fixed
   number, a test passes only if it passed in every epoch.

## 8.2 Triage every failure to exactly one owner

| Cause | Typical evidence | Owner and fix |
|---|---|---|
| **Bot defect: prompt** | Bot invents data, breaks a rule, wrong branch, re-asks data | FDE: fix the prompt or capability prompt |
| **Bot defect: integration** | Wrong function arguments, function never called, wrong scope | FDE: fix function description, scope or prompt instruction |
| **Bot defect: config** | Lint finding reproduced (opening silent, end line mid-call) | FDE: fix the setting |
| **Prompt gap** | Bot did something reasonable that the prompt never specified, and the safe default was breached | FDE + owner: decide the intended behaviour and write it into the prompt |
| **Test defect** | Criterion demands something the prompt never asked; mock shaped wrong; caller script contradicts variables | You: fix the test, and say so |
| **Platform defect** | Grader crash, pre-call mock ignored, mock not returned | Simulation engineering; mark the test BLOCKED, not FAIL |

Never "fix" a failing test by loosening its criteria unless triage proved it is a test defect.

## 8.3 Release gate

The version is **ready to ship** only when all of these hold:
- every P0, P1 and P3 test meets its pass rule;
- every P2 failure has been reviewed and signed off by name;
- no INVALID or BLOCKED result is hiding an untested P0 or P1 item;
- every config-lint finding of high severity is fixed or explicitly accepted;
- the manual-QA list has been handed to QA and signed off separately.

## 8.4 Report format

Produce this report at the end of every suite run. Keep it factual; numbers before adjectives.

```markdown
SIMULATION REPORT: <agent> / <version> / <date>

VERDICT: READY | NOT READY | BLOCKED
<one line why>

Suite: <N> tests (P0 <n>, P1 <n>, P2 <n>, P3 <n>); <total> simulated calls
Epoch mode: fixed <n> | AI decides; tiers run below recommended epochs: <list or none>

Results by tier
| Tier | Tests | Passed rule | Failed | Invalid/blocked |

Failures (most severe first)
| Test | Tier | Pass rate | What happened (turn reference) | Owner | Suggested fix |

Config lint findings
| Severity | Finding | Setting / prompt line | Fix |

Prompt gaps
| Scenario | What the bot did | Decision needed |

Hazards
- <pre-call or post-call functions that touched real systems during simulation>

Manual-QA list (not covered by simulation)
- <item>: <why not testable>

Coverage matrix
| Dossier item | Test IDs |
(every item listed; uncovered items marked UNCOVERED with reason)

Platform observations
- <any probe result or platform behaviour that differs from section 1 of the skill>
```
