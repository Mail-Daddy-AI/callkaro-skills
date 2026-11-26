---
name: callkaro-sow-generator
description: Turns a client's BRD, PRD, requirement doc, call script, agent JSON, email thread or plain description into CallKaro AI's standard Scope of Work (SoW) PDF for a voice bot - cover page, table of contents, Purpose page, then Voice Bot Flow, Extracted Entities/Variables, Call Outcome/Disposition Variables, Guardrails, Rebuttals, Objection Handling and FAQs, in the exact house layout (navy-header striped tables, Carlito type, CallKaro logo, page X of N footer). Use this whenever someone wants a SoW, scope document, requirement sign-off doc or "standardised doc" for a voice or chat bot from any client input, says "make the SoW", "convert this BRD into our format", or uploads a client requirement document for a CallKaro bot, even if they never say "PDF" or "SoW".
---

# CallKaro SoW Generator

Converts whatever the client sent (BRD, PRD, call scripts, sample conversations, emails, spreadsheets, agent JSON, or just a description) into one standardised Scope of Work PDF. The layout, colours, fonts, logo and page furniture are fixed in a bundled renderer, so every client gets an identical-looking document. Your job is the part that changes per client: reading their material and writing precise, testable content for the standard sections.

## Workflow

1. **Collect inputs.** Read every file the user attached or pointed to (extract PDF/DOCX/XLSX text properly rather than skimming). If nothing is attached, ask for the client document or a short description. Ask only for what you cannot infer: client name, bot name, language(s), and who the bot calls.
2. **Extract the bot's behaviour** into the SoW's structure (see `references/sow_standard.md` for what belongs in each section and the style of wording):
   - Flow: ordered fields/steps, exact scripts, branches, requirement level (Necessary/Optional), eligibility rules and numeric limits, transfer or close logic.
   - Variables the bot captures, and call-outcome/disposition values with precise definitions.
   - Guardrails (what it must never do), rebuttals (caller pushback), objection handling (caller questions), approved FAQ answers.
3. **Never invent client rules.** If the client document is silent or ambiguous, write the closest defensible wording from what they did say and mark it `(TBC with client)` in the cell, then list every TBC in your chat reply. A SoW is signed by the client; an invented rule becomes a contractual commitment. Scripts must be quoted exactly as given; where only behaviour is given, describe the behaviour rather than writing a script.
4. **Write the spec JSON** (format in `references/spec_format.md`; complete worked example in `examples/yes_madam_spec.json`). Keep sections numbered "Section N — Title" in the standard order; add or drop a section only if the source genuinely demands it (e.g. no FAQs provided: say so and ask, rather than silently omitting).
5. **Build the PDF**:
   ```bash
   python scripts/build_sow.py my_spec.json --out "<Client>_SoW_V<version>.pdf"
   ```
   Needs `reportlab` (`pip install reportlab`). Run from the skill folder or use its absolute path.
6. **Check the result**: open the PDF (render pages to images if you can), confirm no clipped text, sensible page breaks, TOC page numbers match, special characters (₹ → ≥) render, and the cover reads correctly. Fix the spec and rebuild if not.
7. **Deliver** the PDF, plus a short note: the section list, any TBC items needing client confirmation, and the assumptions you made. Offer the natural next steps: a flow diagram (`conversational-flow-diagram`) or a QA test workbook (`voicebot-qa-testbook`) built from this SoW.

## Writing rules that keep SoWs usable

- **Testable wording.** Each behaviour should be something a QA person can pass or fail ("asks once", "never quotes the fee", "age range 18–50"). Vague phrases like "handles objections well" belong nowhere in a SoW.
- **Consistency across sections.** The same fact (a number, a disposition name, a variable) must read identically everywhere it appears. Disposition names in Section 3 are the exact labels referenced in Sections 1, 4 and 5.
- **Voice of the document**: neutral, third person about the bot (Sonia asks..., the bot never...), short sentences, same terms as the client's own vocabulary. Quote scripts in curly quotes “…” in the language the bot speaks (Hinglish stays Roman script unless the client wants Devanagari).
- **Sensitive requirements** (e.g. never disclosing it is an AI, collecting payments, regulated disclosures): record them as the client states them, and flag in your reply that the client should confirm they meet applicable rules.
- **Cover facts**: date in "4 November 2026" style, version like "2.0" (use 1.0 for a first issue), classification "Confidential" unless told otherwise.

## Don't

- Don't hand-build the PDF or tweak colours/fonts; always render through `scripts/build_sow.py` so every SoW matches the reference.
- Don't paste the client's raw BRD text into cells; restructure it into the standard sections and tables.
- Don't leave `?` in the TOC or "Page ? of ?" in footers: if you see them, the page-number pass failed; rebuild.
