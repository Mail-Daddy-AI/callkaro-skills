# The standard CallKaro SoW (what every document contains)
<!-- graph-summary: What every CallKaro SoW contains: the fixed skeleton, the seven standard sections with their columns and how to fill each, a wording template for the Purpose paragraph, adapting to other bot types, and a content-quality checklist. -->

Reference: "Yes Madam – AI Voice Bot, Outbound Hiring Screening (Sonia)", v2.0, 13 pages (`examples/yes_madam_spec.json` reproduces it).

## Document skeleton (fixed by the renderer)
1. **Cover page**: "SCOPE OF WORK", client name (large blue), bot subtitle in the form "AI Voice Bot — <Use case> (<Bot name>)", "Prepared by CallKaro AI", "Confidential — For <Client> Use Only", date, "Version x.y".
2. **Table of Contents**: auto-built with dot leaders and page numbers.
3. **Purpose of this Document**: one paragraph + a Field/Detail table (Client, Prepared by, Date, Bot name, Language, Classification).
4. **Sections 1-7**, each starting on a new page, each with a one or two sentence intro then a table.

Every page carries the CallKaro logo header and the footer "Scope of Work · <Client> · Prepared by CallKaro AI · <Classification>" with "Page X of N".

## Purpose paragraph (template)
"This document defines the scope for the AI voice bot (“<Bot>”), built and operated by CallKaro AI for <Client>, to <what the calls do> to <who is called>. It sets out the call flow and the fields the bot must capture, the variables extracted and pushed to the reporting / CRM system, how each call is dispositioned, and the guardrails, rebuttals, and objection-handling behaviour the bot follows on every call. The engagement details below record the client, the bot’s name and operating language, and the date and classification of this document."
Details rows: Client · Prepared by · Date · Bot name · Language (Primary / Secondary) · Classification.

## Sections: purpose, columns, how to fill
| # | Title | Table columns | What goes in |
|---|---|---|---|
| 1 | Voice Bot Flow | # · Field · Script / Behaviour · Requirement | One row per step, in call order. Opening script quoted exactly. Branch rules as bullets (Female → …, Male → …, Fallback: …). Numeric limits stated (age 18–50, list of cities). Notes as "**Note:** …". Requirement = Necessary / Optional. Intro states what must be captured for the call to count as complete, and any rule that spans steps (e.g. gender-neutral language until a step). |
| 2 | Extracted Entities / Variables | # · Variable · Possible Values / Format · Requirement · Captured At (Stage) | Every variable pushed to CRM: type/format (Yes / No, Open text, enumerated values), Necessary / Optional (+ condition), and the flow stage it is captured at ("Stage 4 — Location", "Opportunistic (any stage)"). |
| 3 | Call Outcome / Disposition Variables | # · Variable · Possible Values / Format · Description | Summary, **Disposition** (numbered list, each label with its precise definition; exactly one per call), Call Back flag + date/time, Call Duration, Call Completion Status, Call Recording URL, plus any client-specific outcome fields. |
| 4 | Guardrails | # · Guardrail · Behaviour | Hard rules that apply on every call whatever the caller says: age/eligibility floors, abuse handling, calling window, no payment collection, no fabricated claims, no persuasion after refusal, single disposition, DNC permanence, persona/disclosure rule. |
| 5 | Rebuttals | # · Caller Pushback · Bot Rebuttal | Moments the caller resists or disputes (doesn't recognise the call, wrong person, busy, refuses, asks for human, wrong number, DNC, unclear answer, pause, out-of-area, someone else answers). Each says what the bot does and that it then resumes the pending question. |
| 6 | Objection Handling | # · Caller Question / Concern · Bot Response | Questions about the offer (what work, travel, earnings, commission, fees, training, insurance, payment, number source, what happens next, "are you AI?", unsupported details). Approved answer, or the standard deflection line. |
| 7 | FAQs | If the candidate asks… · Sonia's answer (no # column) | The closed list the bot may answer from. State "strictly from the list, no paraphrasing". Mark items that must never be quoted with [strict]. |

Rows in 5, 6 and 7 that the bot is not allowed to answer all use one standard deflection line the client approves (e.g. “Iske baare mein hamari team aapko sahi jankari de payegi.” — then returns back to the flow.). Reuse it verbatim.

## Adapting to other bot types
The seven sections are the standard for any outbound/inbound voice bot. Vocabulary shifts with the use case; the structure does not:
- Collections / reminders: flow rows = verification (RPC check), amount/due-date statement, payment options, PTP capture; dispositions = PTP, Paid, Refuses to pay, Dispute, Wrong number, Callback, DNC; guardrails add calling hours, no threats, no third-party disclosure.
- Lead qualification / booking: flow = interest, requirement, budget/location, slot booking; variables = slot, preference; dispositions = Booked, Callback, Not interested.
- Support / complaint: flow = identify customer, issue category, ticket creation, ETA, escalation; variables = ticket ID, category.
If the client's BRD contains requirements that fit none of the seven sections (integrations, SLAs, reporting), put them in an extra section appended after Section 7, using the same table style, and keep numbering consecutive.

## Content quality checklist (before building)
- Every Necessary field in Section 1 has a matching variable in Section 2 and a stage reference.
- Every outcome the flow can produce has a disposition in Section 3, and each disposition label is spelled identically everywhere.
- Guardrails don't contradict rebuttals (e.g. "never reveals AI" vs "explains it is an automated assistant").
- Numbers, lists and scripts are copied from the client source, not reworded.
- Anything the source doesn't settle is marked (TBC with client) and listed in your reply.
