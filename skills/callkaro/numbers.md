# Phone Numbers

Numbers come from CallKaro's own pool (no bring-your-own). A number can be:
- **outbound** for MANY agents (caller ID for outgoing calls)
- **inbound** for exactly ONE agent (the server rejects a second inbound
  assignment with a 409 — surface that message to the user)

All commands accept **either the number's id or the phone number itself**
(with/without `+`, spaces, dashes): `ck numbers spam 918244464128` works.

## Commands

| Command | What it does |
|---|---|
| `ck numbers list [--json]` | Your numbers: number, id, purchase date, spam flag, active/released, which agent uses it inbound, which agents use it outbound. |
| `ck numbers catalog [--json]` | Buyable pool + `pricepernumber` (₹, deducted from credits). |
| `ck numbers buy <numberOrPhone> [--yes]` | Buy (allot) a pool number. **Spends credits** — confirm with the user first; `--yes` skips the CLI's own prompt. |
| `ck numbers spam <numberOrPhone> [--off]` | Mark as spam (`--off` unmarks). |
| `ck numbers unspam <numberOrPhone>` | Same as `spam --off`. |
| `ck numbers release <numberOrPhone> [--yes]` | Release (unrent) — the number is unassigned from ALL agents. Destructive; confirm first. |

## Assigning numbers to agents (lives under `ck agents`)

| Command | What it does |
|---|---|
| `ck agents set-outbound <agentId> --number <numberId>` | Set the agent's caller-ID number for outgoing calls. |
| `ck agents set-outbound <agentId> --clear` | Remove it. |
| `ck agents set-inbound <agentId> --number <numberId>` | Route this number's incoming calls to the agent. Fails with 409 if another agent already has it inbound. |
| `ck agents set-inbound <agentId> --number <numberId> --remove` | Unassign. |

## Typical flow: give an agent a number

```bash
ck numbers list --json                 # anything free?
# none free →
ck numbers catalog --json              # show user the options + price
ck numbers buy <id>                    # after user confirms the spend
ck agents set-outbound <agentId> --number <id>
ck agents set-inbound  <agentId> --number <id>   # only if it should answer calls
```

An agent needs an **outbound** number before `ck calls make` or a batch can
dial from it (test calls may use platform defaults).
