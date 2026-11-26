---
name: conversational-flow-diagram
description: Builds colorful hand-drawn-style conversational/bot flow diagrams on a white background, delivered as either ONE PNG image or ONE self-contained HTML file (user's choice), from a voice-bot agent JSON (CallKaro export), SOW, PRD, BRD, sample flow, or a plain prompt with domain suggestions (BFSI/NBFC, auto, HR, etc.). Use when asked for a call flow, bot flow, process flow, or decision tree, or when the user shares an agent JSON and asks for its flow.
---

# Conversational Flow Diagram (PNG or HTML)

Turns an agent JSON, SOW/PRD/BRD, a sample flow, or a plain prompt into a colourful, hand-drawn-style bot flow diagram on a plain white background. The output is exactly ONE file in the format the user picks: a PNG image or a self-contained HTML page. Do NOT share an .excalidraw file, a .md file, an SVG, a .json file, or any other file. Everything is generated and rendered inside the sandbox. Never open, upload to, or depend on excalidraw.com or any other external website, and never upload the user's documents anywhere.

## When to trigger

Use this skill whenever the user asks for a flow diagram, call flow, bot flow, voice-bot flow, process flow, journey map, or decision tree, or says "make a flow from this SOW/PRD/BRD/JSON".

Also trigger when:
- The user shares a voice-bot agent JSON (e.g. a CallKaro export) and asks for the flow, call flow, or diagram of that bot.
- The user has NO document and only types a prompt, such as "make a collection bot flow" or "create a flow for an NBFC". In that case, build the flow from their prompt plus the suggestion prompts below.

## Step 1: Ask for references, output format, and choose the input mode

Always start by asking, in ONE message:

- **Reference document:** "Please share the agent JSON, SOW, PRD, or BRD for this bot."
- **Reference flow / sample PNG:** "Do you have a sample flow diagram (PNG, image, PDF, HTML, or .md) whose style or structure I should follow?"
- **Output format:** "Which format do you want the flow in?
  1. **PNG** – a single image, easy to paste into decks, emails, and test sheets.
  2. **HTML** – a single interactive page you open in a browser (zoom, pan, click a node to see its full script/rules, download as PNG)."
- If no document is available: "No problem. Describe the flow in your own words, or pick one of the suggestion prompts below."

If the user already named the format in their request ("give me a PNG", "make it HTML"), do not ask again. If they skip the question, default to PNG.

Then use one of these input modes:

- **JSON mode:** an agent config JSON (CallKaro export or similar) was shared. See "Reading an agent JSON" below. JSON mode takes priority when a JSON and an SOW are both shared; use the SOW to fill gaps and flag any mismatch between them.
- **Document mode:** an SOW, PRD, BRD, or sample flow was shared.
- **Prompt mode:** no document; the user describes the flow or picks a suggestion.

If a sample PNG/flow is shared, follow its layout, node style, side-flow boxes, and colour meanings. If none is shared, use sample-flow.png in this skill (if present) and the House Style below.

### Suggestion prompts (Prompt mode)

Show these 10 as a numbered list. The user can reply with a number, or with a number plus their own client name.

1. BFSI / NBFC – "Personal loan EMI pre-due reminder bot for [Client NBFC]: verify customer, share EMI amount & due date, send payment link, capture PTP date, handle dispute."
2. BFSI / Collections – "Credit card overdue collection bot for [Client Bank]: RPC check, outstanding amount, payment options, PTP / refuse-to-pay / already-paid branches."
3. Insurance – "Policy renewal reminder bot for [Client Insurer]: policy details, premium due, renewal link, objection handling, callback."
4. Automobile – "Car service reminder & booking bot for [Client Dealer]: due service, preferred date & slot, pickup/drop, dealer location, reschedule."
5. Two-Wheeler Sales – "Test-ride lead qualification bot for [Client Brand]: model interest, city, budget, finance need, test-ride slot booking."
6. Customer Care – "Complaint registration bot for [Client Telecom/DTH]: identify customer, issue category, ticket ID, resolution ETA, escalation, CSAT."
7. Human Resources – "Bulk hiring candidate screening bot for [Client Company]: interest check, experience, location, notice period, CTC expectation, interview slot."
8. Consumer Product Support – "Appliance support ticketing bot for [Client Brand]: product & serial, warranty check, guided troubleshooting, create ticket, technician visit."
9. FMCG – "Retailer reorder & scheme bot for [Client FMCG Distributor]: stock check, order quantity, scheme offer, delivery date, payment terms."
10. Healthcare – "Clinic appointment booking bot for [Client Hospital]: department/doctor, slot, report reminder, reschedule/cancel."

### Questions to ask (all modes, in the same first message)

- Client name (or keep it as [Client] if they don't want to share it). In JSON mode, take the client/agent name from the JSON and only ask if it is missing.
- Script language: English / Hindi (Devanagari) / Hinglish (Roman) / Other regional (Bengali, Tamil, Telugu, Marathi, Kannada, Gujarati, Odia, Punjabi, Malayalam...). Write regional scripts only when the user picks one. In JSON mode, default to the language of the scripts in the JSON.
- Script detail: full bot script lines in each node, or step labels only?
- Output format: PNG or HTML (see above).

## Step 2: Extract and confirm the flow

### Reading an agent JSON (JSON mode)

Read the whole JSON, not only the top-level prompt. Pull out:

- **Identity:** agent name, agent ID, version ID, client, language/voice settings. Put agent ID and version ID in the title block.
- **Opening:** first message / welcome message / greeting field.
- **Main prompt / system prompt:** split it into stages (opening, RPC check, verification, main message, questions, objections, closes). Each stage becomes a node.
- **States / nodes / steps (if the JSON has a state machine):** each state becomes a node; each transition, condition, or intent becomes a labelled edge. Keep the JSON's own state names as the node label next to the N-ID (e.g. "N3 · verify_dob").
- **Tools / functions / API or webhook calls:** each becomes a purple API/DB node with the tool name and the variables it reads and writes.
- **Variables:** dynamic variables (e.g. {customer_name}, {{emi_amount}}) exactly as written in the JSON.
- **End-call conditions / dispositions / tags / call outcomes:** each becomes a close or stop node with its tag.
- **Fallbacks and limits:** silence/no-input timeout, max retries, max call duration, interruption settings, transfer/handover number. Show them as inline RULE text or in side flows.
- **Guardrails:** calling hours, do-not-say rules, PII rules (no OTP/PIN), third-party disclosure rules found in the prompt.

Flag, as grey TBD notes, anything the JSON references but never defines (a tool with no description, a tag never reached by any branch, a branch with no close, a variable used in a script but never set) and any mismatch with a shared SOW.

### Reading SOW/PRD/BRD and prompts (Document and Prompt modes)

Read every shared document fully. Pull out: opening, repeat opening, RPC check (Yes / No / Family-relative / Don't know), verification (with max tries), main message, bot questions, branches by customer response, API/DB calls and variables, fallbacks (no-input, invalid, max re-prompts), objection/reason handling (death, health, low balance, job loss, other), callbacks and hold, closes with link/thank-you, stop/sensitive ends, and dispositions/tags.

### All modes

Also collect "from any node" side flows: handover/no response, invalid/no input, repeat, follow-up, hello, busy/call me later, wrong number, and guardrails (calling hours, max dials/day, no threats, no OTP/PIN, no third-party disclosure).

Show a numbered outline (N0, N1, N2...) with every branch label in chat, then ask: "Modify this here, or share your own idea / changes?" Apply edits, re-show, and draw only after they confirm.

Flag missing or contradictory items instead of guessing. Mark unknown business rules as a grey note: "TBD – confirm with client".

Keep variable names exactly as written in the source (e.g. (customer), (amt), (due date), {customer_name}, {{emi_amount}}).

## House Style (from the reference flow)

**Canvas:** plain solid white background (#ffffff) everywhere, in both PNG and HTML. No grid, no transparency, no dark mode (the HTML page must stay white even when the viewer's browser is in dark mode).

**Board sections, left to right:**

- Main flow: top-to-bottom, starting at the OPENING node.
- SIDE FLOWS — from any node: a light-blue box listing side-flow scripts (not connected by arrows).
- GUARDRAILS: a red box with compliance rules.
- COLOUR LEGEND: a box mapping every colour to its meaning.
- Title block (top-left): client, bot name, flow number/version, date, script language; in JSON mode also agent ID and version ID.

**Node rules:**

- Node IDs N0, N1, N2... in flow order; N0 is always the entry point.
- Each node shows the exact script line in quotes, then short inline rules (e.g. RULE: no loan details to third party · Max 2 tries, never hint · Wait max 30 sec · Callback only 9 AM–7 PM · Tag WRONG_NUMBER).
- Section headers inside nodes in caps: OPENING, VERIFICATION, MAIN REMINDER.
- Every arrow has a label (Yes / No / Pass / Fail / Input / intent name / condition like "Within 2 days").
- Loop-backs (e.g. hold → back to opening) use dashed arrows.
- Every end node is a close: thank-you, link, callback, stop, or human handover.

**Colour system:**

| Meaning | Fill | Stroke |
|---|---|---|
| Opening / repeat opening | #b2f2bb | #2f9e44 |
| Verification (must pass) | #a5d8ff | #1971c2 |
| Main message / reminder | #ffd43b | #f08c00 |
| Bot question | #fff3bf | #fab005 |
| Third-party (no disclosure) / callback | #ffd8a8 | #e8590c |
| Hold / move to opening / API-DB call / tool call | #d0bfff | #6741d9 |
| Close with link / thank you | #d3f9d8 | #37b24d |
| Stop / sensitive / fail end | #ffc9c9 | #e03131 |
| Side flow box | #e7f5ff | #1c7ed6 |
| Guardrail box | #ff8787 | #c92a2a |
| TBD note | #e9ecef | #868e96 (dashed) |

Arrows #343a40; dashed for loop-backs.

## Step 3: Build the diagram in the backend

### 3a. Working data

Save the flow as internal working data in flow.json (never shared with the user):

```json
{"title":"...","client":"...","agent_id":"...","version_id":"...","version":"v1","language":"Hindi","source":"json|document|prompt","output":"png|html",
 "nodes":[{"id":"N0","kind":"opening|verification|main|question|thirdparty|hold|close|stop|api|note","label":"...","state_name":"...","script":"...","rules":"..."}],
 "edges":[{"from":"N0","to":"N1","label":"Yes","dashed":false}],
 "side_flows":[{"name":"HANDOVER","script":"..."}],
 "guardrails":["Calls 9 AM–7 PM, max 3 dials/day","..."]}
```

`agent_id`, `version_id` and `state_name` are filled only in JSON mode. All later edits change this file and then re-render, which keeps IDs, colours, and layout stable. The same flow.json drives both PNG and HTML, so switching format later needs no re-extraction.

### 3b. Layout

- Main flow top-to-bottom; branches fan left/right by depth (layered layout).
- ~120 px vertical gap, ~80 px horizontal gap. No overlapping boxes, arrows crossing boxes, or text overflow.
- Wrap text at ~30 chars; grow boxes to fit long script lines.
- Side flows, guardrails, and legend boxes sit to the right of the main flow.
- Keep a ~60 px white margin around the whole board.

### 3c. Shapes

- Ellipse = opening, rectangle = most nodes, diamond = pure decision without a script, dashed rectangle = API/DB/tool call or TBD note.
- Text centred in each shape, ~16 px font, line height 1.25.
- Arrows with arrowheads, label text placed on or beside each arrow on a small white label background so it stays readable.

### 3d. Render (no network calls except npm/pip installs)

First, draw the board once as an SVG: Node + roughjs for the hand-drawn look, with a full-size white background rectangle as the first element. Then produce the format the user chose.

**If PNG:**

- Convert the SVG to PNG with Playwright/Chromium, rsvg-convert, or cairosvg.
- Export at 2x scale so text is sharp when zoomed.
- Make sure the PNG background is solid white (#ffffff), not transparent. If the converter produces transparency, flatten onto white (e.g. Pillow: paste onto a white RGB image).

**If HTML:**

- Build ONE self-contained .html file: the SVG inlined in the page, all CSS and JavaScript inline, fonts embedded as base64 @font-face (subset if large), no external scripts, stylesheets, images, or CDN links, so it opens offline.
- Page background and diagram background solid white (#ffffff). Do not add a dark-mode style; force `color-scheme: light`.
- Interactions (plain JavaScript, no libraries):
  - Zoom (mouse wheel, + / − buttons, "Fit to screen") and pan (drag).
  - Click a node to open a side panel showing its N-ID, state name (JSON mode), full script, rules, and incoming/outgoing branch labels.
  - Search box that highlights nodes by N-ID, state name, script text, or tag.
  - "Download PNG" button that draws the SVG onto a canvas at 2x with a white fill and saves it.
- Header bar with the title block details; legend, side flows, and guardrails stay visible on the board exactly as in the PNG.
- Keep the file under ~5 MB.

**Fonts (both formats):** hand-drawn fonts have no Indic glyphs. For Hindi/Bengali/Tamil etc., use the matching Noto font (Noto Sans Devanagari, Noto Sans Bengali, Noto Sans Tamil...). In HTML, embed that font too.

**Check before delivering:**

- PNG: open the rendered image and check white background, no broken-glyph boxes, no clipped text, no overlaps, legend and side-flow boxes visible.
- HTML: open it in headless Chromium, take a screenshot, and run the same checks; also confirm that zoom, click-to-open-panel, search, and Download PNG work, and that the browser console shows no errors and no network requests.

Fix and re-render if anything is off.

## Step 4: Deliver

- Send ONLY the one file in the chosen format: the PNG displayed directly in chat, or the single .html file. Do not send .excalidraw, .md, .svg, .json, or any other file, and do not mention them.
- One-line summary: number of nodes, branches, side flows, and gaps/TBDs found (in JSON mode, also tools/APIs and end-call tags covered).
- Offer one next step, e.g. "Want a test-case sheet generated from this flow?" or "Want this in the other format (PNG/HTML) too?"
- On change requests: edit flow.json, re-render, keep IDs, colours, and layout stable, and resend only the updated file in the same format (or the other format if the user asks to switch).

## Rules

- Output is always a single file with a white background: one PNG or one self-contained HTML, as the user chose. Nothing else.
- No external websites; no uploading user documents anywhere; the HTML file makes no network requests.
- Never invent business rules missing from the document or JSON — mark them TBD.
- Never reveal loan, amount, or account details on third-party branches unless the source explicitly allows it.
- Keep variable names and JSON state/tool names exactly as in the source.
- Script text must be in the language the user chose; keep variables untranslated.
- Use sample-flow.png in this skill (if present) as the visual style reference for layout, spacing, and colours; a sample shared by the user in chat takes priority.