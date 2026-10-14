# Auth & Account

State lives in `~/.config/callkaro/config.json` (a revocable `ck_…` token). The
user stays signed in until `ck logout`. Endpoints (backend/web/call URLs) are
baked into the CLI — nothing to configure.

## Commands

| Command | What it does | Notes for agents |
|---|---|---|
| `ck login` | Opens the user's **browser** to sign in (email or Google); the CLI waits and picks up the token. | You cannot complete this for the user — run it, tell them to finish sign-in in the browser, and wait for the success line. Times out after 10 min. |
| `ck login --password [--email <e>]` | Interactive email+password prompt in the terminal. | Only for headless/CI use. Prompts interactively — not usable non-interactively. |
| `ck register` | Interactive picker: **Continue with Google** (browser) or **Email + password** (OTP sent to email, 3 attempts). | Interactive; the OTP arrives in the user's email — you can't read it. |
| `ck register --google` | Skip the picker, browser sign-up directly. | |
| `ck logout` | Revokes the token server-side and clears local config. | |
| `ck whoami [--json]` | Account details: id, name, email, credits, plan. | **Use this as the auth check** before any workflow. |
| `ck config` | Shows backend/call/web URLs + session status. | Read-only. |

## Patterns

**Auth check gate** (start every workflow with this):
```bash
ck whoami --json || echo "NOT_LOGGED_IN"
```
If not logged in: run `ck login`, tell the user to complete sign-in in the
browser window that opens, and re-check.

**Credits**: `ck whoami --json` → `.currentCredits`. Calls, numbers, and batches
consume credits; warn the user if credits look low before a batch.
