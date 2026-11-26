# Flow Diagram — house style, build and delivery
<!-- graph-summary: House style (colours, node shapes, board sections), how to build flow.json and lay out, render the diagram to PNG or self-contained HTML, checks before delivery, and the rules. Use after the flow outline is confirmed. -->

Second half of [Flow Diagram](flow-diagram.md): the visual rules, the build and render steps, delivery and the hard rules.

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
