# Flow Diagram — bot flow as PNG or HTML (extract and confirm)
<!-- graph-summary: Make a hand-drawn-style bot flow diagram (one PNG or one self-contained HTML) from an agent JSON, SoW/PRD/BRD, sample flow or prompt: when to use it, questions to ask, input modes and reading an agent JSON, then confirming the outline. Needs no ck login. -->

Standalone deliverable (no `ck` login needed). Continue with [House style, build and deliver](flow-diagram-style-and-render.md) once the outline is confirmed. Turns an agent JSON, SOW/PRD/BRD, a sample flow, or a plain prompt into a colourful, hand-drawn-style bot flow diagram on a plain white background. The output is exactly ONE file in the format the user picks: a PNG image or a self-contained HTML page. Do NOT share an .excalidraw file, a .md file, an SVG, a .json file, or any other file. Everything is generated and rendered inside the sandbox. Never open, upload to, or depend on excalidraw.com or any other external website, and never upload the user's documents anywhere.

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

If a sample PNG/flow is shared, follow its layout, node style, side-flow boxes, and colour meanings. If none is shared, use sample-flow.png in this skill (if present) and the [House Style](flow-diagram-style-and-render.md).

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
