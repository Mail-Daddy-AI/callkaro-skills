# Client Regression — branch coverage & verification discipline

Use when **building from a PRD/BRD** (this is the checklist that turns a spec
into a test suite), auditing a live client agent, fixing a reported
misbehaviour, or hardening an agent before it ships. The mechanics (export,
patch, simulate) are in [create-update.md](create-update.md),
[versions.md](versions.md) and [../simulations.md](../simulations.md) — this
file is **what to test** and **what each branch must do**.

## Branch library — every client agent needs these covered

Write one simulation test case per branch. A prompt is not "done" until each
branch behaves correctly *and* terminal branches actually terminate.

| Branch | Required behaviour |
|---|---|
| **Happy path** | Deliver the benefit line the BRD expects; walk the caller through **one step at a time**, waiting for confirmation before the next. |
| **Login / OTP** | One instruction at a time. **Never** ask the caller to read out or share an OTP, PIN, password, or screenshot. |
| **Wrong person / wrong number** | Apologise, end immediately. |
| **DND / do-not-call** | Acknowledge the request, end immediately. |
| **Human support / transfer** | Only refuse if the version has no `transfer` function; otherwise offer exactly the alternative the BRD permits. |
| **Missing context** | Trigger only on the literal missing-context cue. Generic "I can't retrieve that" text must not hijack other branches. |
| **Callback / item unavailable** | Echo the requested time; state plainly that scheduling is **not confirmed** unless a function result confirms it. |
| **Upload / submit error** | Give **one** recovery path. Never invent submission, callback, or transfer success. |
| **Already submitted / duplicate** | Say it's already done; do not walk them through it again. |
| **Final close** | Explicit, validated end-call behaviour. |

## The four rules that cause most regressions

1. **Exact phrases are exact.** If the BRD or a test requires a literal
   sentence, the prompt must contain that sentence verbatim — not a paraphrase.
2. **Never invent a backend outcome.** No claiming submission succeeded, a
   callback is booked, a transfer connected, or a reference number exists
   without a real function result to back it. (Separate from, and as important
   as, "never invent ids" in [../INSTRUCTIONS.md](../INSTRUCTIONS.md).)
3. **No cross-client leakage.** Don't copy another client's metadata rules,
   formatting, or phrasing unless that client's BRD says the same thing.
   Sibling agents are a reference, not a source of truth.
4. **One option at a time.** One recovery path, one instruction per turn —
   unless the BRD explicitly allows more.

## Verification: two passes, always

```bash
ck sim run <agentId> --tests <failingTestId> --versions <vid>   # 1. the exact failure
ck sim run <agentId> --tests <allTestIds>   --versions <vid>    # 2. the FULL set
```

**A single-case pass is not a pass.** Narrow fixes routinely break a
neighbouring branch (a missing-context tweak swallowing the wrong-number path
is the classic). Only the full regression suite is the gate.

If a test is genuinely contradictory (it demands behaviour the BRD forbids),
**fix the test criteria** — don't distort the agent into an impossible shape.

## Audit checklist for a live agent

Beyond the config sanity checks in [transcriber.md](transcriber.md) and
[voice.md](voice.md) (language ↔ voice ↔ transcriber must agree):

- [ ] Prompt language, voice language and register all match the BRD.
- [ ] Number-ish fields spoken correctly (`preFormatVariables`, e.g.
      `Number:DigitByDigit` for account/reference numbers).
- [ ] Named entities formatted the way the BRD expects.
- [ ] No conflict between happy-path instructions and terminal branches.
- [ ] Every terminal branch really ends the call (`end` function present and
      the closing line is in `end_call_msg`).
- [ ] Each fix committed with a reason (`--commit "…"`) so the change is
      auditable.
