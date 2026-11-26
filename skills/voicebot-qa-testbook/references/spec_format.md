# Spec JSON format

```json
{
  "bot": {
    "name": "CallKaro – Client · Bot (what it does)",       // Summary > Bot / Project name
    "short_name": "Client · Bot",                              // Read Me title, default filename
    "version": "v1.0",
    "use_case": "Campaign / use case",
    "tested_by": "QA team",
    "blurb": "Bot under test: ... (2-4 sentences: who it calls, in what language, the flow in one line, what a good outcome is)",
    "source_doc": "Scope of Work v2.0",                        // named in the Read Me "derived from" sentence
    "blocker_examples": "a wrong eligibility decision, a wrong disposition, ...",   // Scoring sheet closing note
    "business_constants_note": "age 18–50, 15 cities"          // optional; shown on Read Me when thresholds_extra exists
  },
  "cases": {
    "P1 Technical":    [ {case}, ... ],
    "P2 Call Flow":    [ ... ],
    "P3 Business":     [ ... ],
    "P4 Humanization": [ ... ]
  },
  "thresholds_extra": [
    {"key": "[AGE_MIN]", "controls": "Minimum eligible age", "recommended": "18", "unit": "years"}
  ]
}
```

Each `{case}` (all eight fields required; IDs are generated in order):
```json
{"category": "Business Rules",
 "parameter": "Age - lower boundary",
 "verifies": "18 qualifies, 17 does not",
 "method": "Log",
 "example_input": "Ages 17, 18, 19 across three calls.",
 "expected": "Below [AGE_MIN] (17) -> Not Eligible (screening stops); [AGE_MIN] (18) and 19 continue.",
 "type": "Positive",          // Positive | Negative | Edge
 "priority": "P0"}           // P0 | P1 | P2
```

Notes
- Row order is output order; group by category (the sheet filter handles the rest).
- `[KEYS]` in `expected` / `example_input` must exist in the 20 framework thresholds (see `baseline_library.json` -> `_thresholds`) or in `thresholds_extra`; the validator warns otherwise.
- Put unknown business rules as `(TBD: ...)` inside `expected`.
- Starting point for a brand-new bot: copy the sheets from `baseline_library.json` (90 standard cases), then adapt example inputs/criteria and add bot-specific rows. `examples/sonia_spec.json` shows a deeply customised result (161 cases).
- A sheet needs at least one case; the validator rejects missing/invalid fields and warns on uncovered baseline categories, duplicate parameters and undefined thresholds.
