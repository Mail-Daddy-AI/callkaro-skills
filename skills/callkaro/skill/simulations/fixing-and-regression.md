# Fixing and regression
<!-- graph-summary: After a failure: clone the version, fix the right field for the agent type, run old and new side by side, re-run all P0 and P1, and turn incidents into tests. -->

- **Never edit the version under test in place.** Clone it (`clone_agent_version`), change the clone,
  then run the old and new versions side by side in the same run on the full affected tiers. A fix that
  breaks another behaviour shows up immediately.
- **Fix the bot in the right field for its type.** Basic: `systemprompt`. Advanced: `role`, `goal`,
  `instructions`, `callFlow`, `guardrails`, `rebuttals`. Multi Prompt: the capability's `system_prompt`,
  flags or scoped functions; `systemprompt` is shared context only. Pathway: the node prompt, its
  transitions or extract variables. Function and capability arrays are full replacements, so read the
  current version first and send complete arrays.
- **Re-run the full P0 and P1 tiers** after any fix, not just the test that failed.
- **Every production incident becomes a test** before its fix ships.
- **Rebuild the dossier on every structural change** (new capability, node, function, guardrail, variable,
  post-call field), then add the tests its rules require. Delete tests whose target no longer exists and
  say so in the report.
