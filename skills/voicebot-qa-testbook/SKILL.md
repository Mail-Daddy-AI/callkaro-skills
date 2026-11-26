---
name: voicebot-qa-testbook
description: Generates the CallKaro "Voice AI Bot QA Testing Framework" Excel workbook (Read Me, Summary Scorecard with 95% certification gate, four pillar sheets P1 Technical / P2 Call Flow / P3 Business / P4 Humanization, Scoring & Certification, Thresholds) pre-filled with test cases for a specific bot. Use this whenever the user wants test cases, a QA sheet, a test plan, a certification scorecard or a UAT checklist for a voice bot, call bot, agent JSON, SoW, PRD or BRD (CallKaro, Yes Madam, Urban Company, NBFC, hiring, collections or any client), even if they don't say "Excel" or "framework". Keeps the exact columns, colours, formulas, weights and gate logic of the original sample, so the user never has to supply the sample workbook again.
---

# Voice Bot QA Testbook

Produces one `.xlsx` per bot in the CallKaro QA framework format. The look, columns, dropdowns, colour rules, scoring formulas and certification gate live in a bundled template, so they are identical every time. Your job is the part that changes per bot: reading the bot's source and writing good test cases.

## Workflow

1. **Get the source.** Ask for (or locate) the agent JSON, SoW / PRD / BRD, call flow, or a plain description. If the conversation already has one, use it. For a PDF, extract the text (e.g. `pypdf`) rather than guessing.
2. **Extract the testable facts**: the ordered flow, branches, eligibility rules and boundaries, dispositions/tags, variables captured, scripted lines, FAQs and approved deflections, guardrails, transfer/callback logic, language, and any numeric constants (age range, cut-offs, time windows). Note every gap or contradiction in the source; these become `(TBD)` cases rather than invented rules.
3. **Read `references/framework.md`** for the pillars, columns, priority/weight rules and coverage checklist, and **`references/baseline_library.json`** for the 95 standard checks every bot gets (adapt their example inputs and pass criteria to this bot; keep their intent).
4. **Write the spec JSON** (format in `references/spec_format.md`; full worked example in `examples/sonia_spec.json`). Aim for depth where the bot's risk is: usually 30-45 Technical, 30-40 Call Flow, 45-60 Business, 20-25 Humanization for a multi-branch bot; fewer for a simple one. Eligibility rules, dispositions, and guardrails each deserve their own rows because each is a separate way to fail.
5. **Validate, then build**:
   ```bash
   python scripts/build_testbook.py my_spec.json --check-only   # fix ERRORs; read WARNs
   python scripts/build_testbook.py my_spec.json --out "<Bot>_QA_Test_Suite_v1.0.xlsx"
   ```
   Needs `openpyxl` (`pip install openpyxl`). Run from the skill folder, or use its absolute path.
6. **Deliver** the xlsx to the user, with a short summary: case counts per pillar, number of P0s, and the TBD / source-gap list that needs client confirmation.

## Rules that keep the output trustworthy

- **Only test what the source says**, plus the standard framework checks. If the source is silent, write the case with `(TBD: ...)` in the expected result instead of making up a rule. A made-up pass criterion gets certified against and later blamed on the bot.
- **Scripted lines are quoted exactly** in the expected result so a tester can compare word for word. When the source gives behaviour but not a line, say "BEHAVIOUR:" rather than inventing a script.
- **Priority drives the release gate**: P0 = wrong business decision, PII/compliance breach, hallucination, dead air, broken transfer, wrong disposition. Be honest about P0; over-using it makes the gate meaningless, under-using it lets real blockers through. See the framework reference.
- **Thresholds**: reference numbers by `[KEY]` in the expected text. The 20 framework keys already exist; add bot-specific constants (age limits, windows, counts) in `thresholds_extra` so they can be tuned in one place. The script fills the "Referenced by" column.
- **Results columns stay empty** (Actual, Status, Severity, Remarks). Never pre-fill statuses; testers do that, and the scorecard reads "NOT YET TESTED" until they do.
- **Language**: write example inputs in the language callers really use (Hinglish for Indian voice bots, in Roman script unless asked otherwise); the sheet text itself stays English.
- Flag sensitive source requirements instead of silently encoding them, e.g. a "never reveal it's an AI" rule: write the case per the source and add a note to confirm it meets applicable disclosure rules.

## Don't

- Don't edit the template workbook or hand-build sheets with openpyxl; always go through the script so formatting and formulas stay identical to the sample.
- Don't change weights (P0=3, P1=2, P2=1), the 95% gate, or column order unless the user explicitly asks; other teams compare scorecards across bots.
