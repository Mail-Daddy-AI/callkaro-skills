# SoW spec JSON format
<!-- graph-summary: Spec JSON the SoW renderer reads: cover, purpose, sections, columns, cell blocks (bullets, numbered), inline markup and defaults. -->

```json
{
  "cover": {
    "client": "Yes Madam",
    "subtitle": "AI Voice Bot — Outbound Hiring Screening (Sonia)",
    "prepared_by": "CallKaro AI",
    "classification": "Confidential",
    "date": "4 November 2026",
    "version": "2.0",
    "confidential_line": "optional override of 'Confidential — For <client> Use Only'",
    "footer": "optional override of the footer text"
  },
  "purpose": {
    "text": "paragraph (or list of paragraphs)",
    "details": [["Client","Yes Madam"],["Prepared by","CallKaro AI"],["Date","4 November 2026"],["Bot name","Sonia"],["Language","Primary — Hindi/Hinglish; Secondary — English"],["Classification","Confidential"]]
  },
  "sections": [
    {
      "title": "Section 1 — Voice Bot Flow",
      "intro": ["paragraph", "**Note:** second paragraph"],
      "numbered": true,
      "num_width": 25,
      "columns": [
        {"name": "Field", "width": 90, "bold": true},
        {"name": "Script / Behaviour", "width": 280},
        {"name": "Requirement", "width": 75}
      ],
      "rows": [
        ["Opening / Consent", "“Namaste, …”", "Necessary"],
        ["Gender → Job type", [{"bullets": ["Female → …", "Male → …"]}], "Necessary"]
      ]
    }
  ]
}
```

## Rules
- `sections` render in order, each on a new page, and feed the Table of Contents automatically. `title` is used verbatim in the TOC and heading.
- **Columns**: `width` values are relative (they are scaled to the 470 pt table width; the `#` column takes `num_width`, default 25). `bold: true` makes a column bold (used for the first label column). `numbered: true` adds the auto `#` column (1, 2, 3…); leave it off for FAQs.
- **Cells** are a string or a list of blocks. A block is a paragraph string, `{"bullets": [...]}` (large round bullets, hanging indent) or `{"numbered": [...]}` (1. 2. 3. with hanging indent). Every row needs exactly one value per column.
- **Inline markup** in any text: `**bold**`, `*italic*`. Curly quotes and the characters ₹ → ← ≥ ≤ ✓ are handled (the renderer routes glyphs Carlito lacks to fallback fonts).
- `intro` and optional `outro` are lists of paragraphs before/after the table. A section may instead carry several tables via `"tables": [{"caption": "...", columns, rows, numbered}, ...]`.
- `purpose.details` defaults to Client / Prepared by / Date when omitted.
- Defaults: `prepared_by` "CallKaro AI", `classification` "Confidential", `version` "1.0".

## Output
`build_sow.py` runs up to three passes so the TOC page numbers and "Page X of N" are correct, then prints `saved <file> pages: N`. If any TOC entry shows `?`, rebuild.
