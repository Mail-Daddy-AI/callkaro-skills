# CallKaro Skills for AI Agents

Teach Claude Code (or any AI coding agent) to build and operate
[CallKaro](https://callkaro.ai) voice AI agents: create agents, write call
scripts, pick voices and transcribers, run simulations, place calls, schedule
batch campaigns, and read analytics — all through the `ck` CLI.

## Prerequisite

The skills drive the CallKaro CLI, so install it and sign in first:

```bash
npm install -g @callkaro/cli   # or the tarball your team provides
ck login                       # opens your browser to sign in
```

## Install the skills

**Option A — Claude Code plugin (recommended):** inside Claude Code run

```
/plugin marketplace add Mail-Daddy-AI/callkaro-skills
/plugin install callkaro@callkaro
```

**Option B — via the CLI** (skills also ship inside it):

```bash
ck skills install              # your account (~/.claude/skills) — all projects
ck skills install --project    # just this project — commit .claude/ to share
```

**Option C — manual:** copy `skills/callkaro/` into `~/.claude/skills/`.

Then just ask Claude anything CallKaro-related — *"build me a Hindi sales agent
and test it"* — and it will load the skill.

## What's inside

| File | Covers |
|---|---|
| `skills/callkaro/SKILL.md` | entry point: ground rules + where to look |
| `INSTRUCTIONS.md` | how to think: operating loop, playbooks, safety rules |
| `agents/AGENT-VERSION-REFERENCE.md` | every agent/version field, its values, and the traps |
| `agents/prompts.md` · `voice.md` · `transcriber.md` · `functions.md` | script writing, TTS, STT, abilities (incl. advanced Python/JS) |
| `agents/create-update.md` · `versions.md` | workflows, publishing, A/B testing |
| `auth.md` · `numbers.md` · `calls.md` · `batches.md` · `simulations.md` · `analytics.md` | the rest of the platform |

## Updating

Skills are versioned with this repo — `/plugin update callkaro` (marketplace
installs) or re-run `ck skills install` after upgrading the CLI.
