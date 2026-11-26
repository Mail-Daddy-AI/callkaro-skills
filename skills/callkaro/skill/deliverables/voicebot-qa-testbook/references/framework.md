# QA Framework reference (what the template encodes)
<!-- graph-summary: The QA workbook framework: sheet structure, pillar columns, the four pillars and their categories, P0/P1/P2 weights, scoring, the 95% certification gate and a per-pillar coverage checklist. -->

## Workbook structure (fixed by the template)
| Sheet | Purpose |
|---|---|
| Read Me | What the framework is, 4 pillars, how to run a cycle, the 95% gate, golden rules |
| Summary Scorecard | Run details (yellow), gate settings (yellow), headline results, per-pillar table + chart, gate checklist, failure focus. All formulas read the four pillar sheets |
| P1 Technical / P2 Call Flow / P3 Business / P4 Humanization | The execution sheets (rows 5-154 are wired into formulas, dropdowns and colour rules) |
| Scoring & Certification | Scoring logic + worked example |
| Thresholds | Numeric benchmarks referenced as `[KEY]` in pass criteria |

## Pillar sheet columns (A-N, header on row 4)
A Test ID (auto: TEC-/FLW-/BIZ-/HUM-NN) · B Category · C Test Parameter / Scenario · D What It Verifies · E How to Test (Method) · F Example Input / Stimulus · G Expected Result / Pass Criteria · H Test Type (Positive/Negative/Edge) · I Priority (P0/P1/P2) · J Weight (formula) · **K Actual Result · L Status (Pass/Fail/Partial/Blocked/N/A) · M Severity (Critical/Major/Minor) · N Remarks** (K-N yellow, filled by testers).

Spec fields map to B-I: `category, parameter, verifies, method, example_input, expected, type, priority`.

Method vocabulary used in the sample: Audio, Audio + Log, Log, Live, Live + Log, LLM judge, LLM judge + Log, Human, Human + LLM judge, Audio + Human, Mock API, Mock API + Log.

## The four pillars and their categories
- **P1 Technical**: Speech Recognition (STT) · Speech Synthesis (TTS) · Latency & Responsiveness · Telephony & Call Control · LLM & Integration Reliability.
- **P2 Call Flow**: Happy Path · Branch Coverage · Negative Flow · Edge Cases · State & Context · Recovery.
- **P3 Business**: Objective & Logic · Business Rules · Information Accuracy · Decisioning & Data · Compliance & Guardrails.
- **P4 Humanization**: Tone & Warmth · Pacing & Delivery · Language & Verbosity · Conversational Intelligence.

Keep these category names (the validator warns when a baseline category goes uncovered). Add bot-specific categories only if none fits.

## Priority and weight
- **P0** weight 3, release-blocking, must pass 100%: wrong eligibility/business decision, PII leak, hallucination, dead air, dropped/failed transfer, wrong disposition, DNC/compliance breach, fee/payment promises, exact-capture of business-critical values.
- **P1** weight 2: core behaviours; gate on P1 pass-rate >= 95%.
- **P2** weight 1: polish; tracked, not individually blocking.
P0 tests are Pass/Fail only (no Partial).

## Scoring
Status scores: Pass 1.0, Partial 0.5, Fail 0.0; Blocked and N/A are excluded. Pillar score = sum(weight x score) / sum(weight of executed tests). Overall pools all four pillars.

## Certification gate (editable yellow cells on the Summary)
CERTIFIED only if: overall weighted >= 95%, every pillar >= 90%, zero P0 failures (Fail or Partial), P1 pass rate >= 95%. Otherwise BLOCKED / NOT CERTIFIED. With no results logged it reads NOT YET TESTED.

## Coverage checklist when authoring a bot's cases
**Technical**: clean + noisy audio, accents, speech rate, code-mixing, exact capture of every business-critical value (numbers, dates, names, cities, amounts) with boundary phrasings, yes/no variants, self-correction, hesitation, language switching, gender/DTMF detection if used, TTS completeness/pronunciation/voice consistency/artifacts, latency p50/p95 + breakdown + dead air + latency masking, answer detection, AMD + false positives, barge-in, transfer happy path + context + failure modes, hangup + hard timer, network degradation, recording, hallucination, KB/FAQ accuracy, unknown-question fallback, API success/error/idempotency.
**Call flow**: golden path per persona/branch, every decision branch, question order, conditional steps, decline at each gate, refusal of required info, DNC, wrong number/third party, callback from any node, asks-for-human, drop-off, hard-stop rules (e.g. under-age), ambiguity, multiple values, out-of-order info, mid-flow question, repeat, pause, silence, context retention, corrections, intent change, retry limits, loop prevention.
**Business**: call objective, logical correctness, consistency; EVERY eligibility rule at both sides of its boundary; mandatory-step enforcement; each disposition/tag as its own case + single-disposition rule; every captured variable; call-back/transfer flags; each FAQ/objection answer exactly; restricted-info deflection; no over-promising; fees/payments; out-of-scope deflection; summary faithfulness; each guardrail from the source; PII; third-party privacy; abuse; jailbreak; calling window; DNC permanence.
**Humanization**: warmth, register/politeness form, emotional fit, persona consistency, pacing, pauses, prosody, number reading, conciseness, natural phrasing + code-mix, gendered grammar if relevant, verbal tics, fillers, vocabulary level, acknowledgement, turn-taking, frustration, confusion, sensitive topics, graceful closes, transfer hand-off, cultural fit, blind human-likeness.

## Golden rules (from the framework)
Never quietly delete standard checks; every P0 is release-blocking; any bot change means re-run the whole suite; refresh adversarial corpora quarterly; keep one filled workbook per bot per cycle as the audit trail.
