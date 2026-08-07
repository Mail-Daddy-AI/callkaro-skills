# The ai-fde Authoring Pipeline — build agents the way our own AI does

These files are the **actual production prompts** of ai-fde, CallKaro's
agent-building AI. When you build or edit an agent, don't improvise: run this
pipeline, adopting each file's role at its stage. This is what makes the
difference between "an agent that works" and an ai-fde-grade agent.

## The pipeline (CREATE)

```
1. INTAKE      user-chatbot.md                 understand + interrogate the requirement
2. PLAN        planner-agent.md                (types 0/1)   — or —
               planner-agent-multiprompt.md    (types 2/3)
3. SCRIPT      script-writer-agent.md          (types 0/1)   — or —
               multi-prompt-script-writer-agent.md (types 2/3)
4. REFLECT     reflect-agent.md                critique the script; loop to 3 until clean
5. ANALYZE     script-analyzer-for-functions-agent.md   postcall vars, conversion, dispositions
6. FUNCTIONS   function-planner-agent.md       decide WHAT functions are needed
               predefined-agent.md             transfer/end/hold/booking/availability
               {pre|in|post}-call-basic-agent.md        fixed API calls
               advanced-{pre|in|post}-call-agent.md     Python/JS source_code
               function-critic-agent.md        review every generated function
7. PARAMETERS  call-params-planner-agent.md    decide WHICH parameter areas need touching
               voice-transcriber-agent.md      voice + STT (the big one — read fully)
               llm-caching-agent.md · call-init-term-agent.md ·
               agent-behavior-agent.md · call-settings-agent.md ·
               filler-pronunciation-agent.md · switchable-entities-agent.md ·
               pre-format-agent.md · call-flow-json-agent.md
8. ASSEMBLE    merge every stage's JSON into one agent.json → ck agents create
9. VERIFY      read back (ck agents get --versions … --json) + simulate (../simulations.md)
```

For an UPDATE, run only the stages the change touches — but ALWAYS re-run
**reflect** after a script change, and **function-critic** after a function change.

## Reading these prompts (they were written for ai-fde's internals)

Each file is a verbatim production system prompt. When you run that stage,
**adopt the role and follow its rules exactly**, translating its tooling:

| It says | You do |
|---|---|
| "draft" / "save to draft" / sub-tools that persist fields | edit your working `agent.json` (or the `--set` patch you're building) |
| `get-*-voices` / `get-*-transcriber` tools | `ck voices --json` + [../agents/voice-and-transcriber.md](../agents/voice-and-transcriber.md) |
| read-version / "existing script/config" context | `ck agents get <agentId> --versions <vid> --json` |
| "return JSON with exactly these keys" | produce that JSON object as the fields you write into the payload |

## What these files own (and don't)

They own the **role, judgement and output contract** of each stage — including
the exact `source_code` protocols for advanced functions. They do **not** own
field tables: for any field name, allowed value or provider table, use
[../agents/AGENT-VERSION-REFERENCE.md](../agents/AGENT-VERSION-REFERENCE.md).
Where a prompt restates a fact that the reference also covers, **the reference
wins** (it tracks the live schema).

## Rules of the pipeline

- **Each stage reads the previous one's output.** The script needs the plan;
  functions need the script's variables; the voice needs the persona gender
  from the script; pre-format needs the metadata variables. Don't jump ahead.
- **Stage outputs are JSON fragments** (each prompt defines its exact keys).
  Collect them; the union becomes your create payload / update patches.
- Field mechanics (what's legal where) stay governed by
  [../agents/AGENT-VERSION-REFERENCE.md](../agents/AGENT-VERSION-REFERENCE.md) —
  the pipeline tells you *what to write*, the reference tells you *where it goes*.
- Voice/transcriber tool calls in these prompts (`get-cartesia-voices`,
  `get-soniox-transcriber`, …) map to `ck voices --json` + the provider tables
  in [../agents/voice-and-transcriber.md](../agents/voice-and-transcriber.md) and
  [../agents/voice-and-transcriber.md](../agents/voice-and-transcriber.md).
- The reflect loop is not optional. ai-fde never ships a first draft; neither
  should you.
