# Reference: Minimal Payloads
<!-- graph-summary: Minimal working create/update payloads for each prompt type (basic, multi-prompt, pathway), to copy from. -->

Part of the [version reference](../AGENT-VERSION-REFERENCE.md) (which document a field belongs to, topic map). Field index: [field-index.md](field-index.md).

## 20. Minimal payloads

**Type 0 (Basic) — new agent + first version**

```json
{
  "name": "Riya – Service Reminder",
  "default_agent_language": "hi",
  "agentStatus": "in-progress",

  "versionName": "v1",
  "systempromptType": 0,
  "default_language": "hi",
  "silence_language": "hi",
  "systemprompt": "Role\nPersona gender: female\n... full script ...",
  "role": "", "goal": "", "callFlow": "",
  "instructions": [], "guardrails": [], "rebuttals": [],
  "end_call_msg": ["आपका दिन शुभ हो!", "धन्यवाद, आपसे बात करके अच्छा लगा।"],
  "model": "callkaro/arjuna-2.5",
  "secondary_model": "gpt-5.4-nano",
  "temperature": 3,
  "caching_strategy": "response",
  "voice_configuration": { "voice_provider": "Eleven Labs", "...": "resolved from the catalogue" },
  "secondary_voice_configuration": { "voice_provider": "Sarvam", "...": "different provider" },
  "transcriber": { "transcriber_provider": "Soniox", "transcriber_language": ["hi"], "keywords": [] },
  "secondary_transcriber": { "transcriber_provider": "Azure", "transcriber_language": ["hi-IN"] },
  "speakfirst": { "value": 1, "message_interruption": false },
  "speakfirst_inbound": { "value": 0, "message_interruption": false },
  "initial_pause_outbound": 1,
  "functions": [{ "type": "end", "name": "end_call", "description": "End the call when done" }],
  "postcall": [
    { "type": "boolean", "name": "reminder_acknowledged",
      "description": "Did the customer acknowledge the service reminder?",
      "defaultValue": false,
      "defaultValueConfig": { "source": "static_value", "key": "", "other": false } }
  ],
  "time_limit": 300,
  "agentMemory": { "enabled_for_call": true, "call_filters": { "maxCalls": 5, "onlyConnected": true, "maxDays": 30, "additionalAgents": { "mode": "self", "agentIds": [] }, "includeTranscript": false } }
}
```

(`agentMemory` is optional — include it only when the agent should remember earlier calls; see [§14b](variables-memory-whatsapp.md).)

**Type 2 (Multiprompt) — capability block**

```json
{
  "systemprompt": "<shared persona, brand, standing rules, Persona gender: … — no call flow>",
  "capabilities": [
    {
      "capability": "greeting",
      "is_starting": true,
      "system_prompt": "<what to do/say in this phase; prose may say when to move on>",
      "overwrite": false,
      "stick_capability": false,
      "msg_while_switching_type": "silent",
      "msg_while_switching": "",
      "endpointing": { "mode": "fixed", "min_delay": 0.5, "max_delay": 3 },
      "llms": { "primary_model": "callkaro/arjuna-2.5", "secondary_model": "gpt-5.4-nano", "temperature": 0.2 },
      "functions": [],
      "postcall": []
    }
  ]
}
```

**Type 3 (Pathway) — node block with a global node**

```json
{
  "systemprompt": "<shared persona, brand, standing rules, Persona gender: … — no call flow>",
  "capabilities": [
    {
      "capability": "qualify_intent",
      "is_starting": true,
      "node_type": "normal",
      "system_prompt": "<what to do/say here — NO 'if X then go to Y'>",
      "overwrite": false,
      "extract_variables": [
        { "type": "boolean", "name": "buy_intent",
          "description": "True if the caller expresses intent to buy", "is_required": true }
      ],
      "transitions": [
        { "condition_type": 1, "condition": "(buy_intent==True)", "next_capability": "pitch_offer" },
        { "condition_type": 0, "condition": "The caller is not interested and wants to end the call",
          "next_capability": "soft_close" }
      ],
      "when_to_jump": "",
      "msg_while_switching_type": "silent",
      "msg_while_switching": "",
      "endpointing": { "mode": "fixed", "min_delay": 0.5, "max_delay": 3 },
      "llms": { "primary_model": "callkaro/arjuna-2.5", "secondary_model": "gpt-5.4-nano", "temperature": 0.2 },
      "functions": [],
      "postcall": []
    },
    {
      "capability": "talk_to_human",
      "is_starting": false,
      "node_type": "global",
      "when_to_jump": "The caller asks to speak to a human or becomes frustrated",
      "system_prompt": "<acknowledge, then execute the transfer>",
      "overwrite": false,
      "transitions": [],
      "extract_variables": [],
      "msg_while_switching_type": "dynamic",
      "msg_while_switching": "Say a short bridging line before connecting a human",
      "endpointing": { "mode": "fixed", "min_delay": 0.5, "max_delay": 3 },
      "functions": [
        {
          "type": "transfer", "name": "transfer_to_agent",
          "description": "Transfer to a human agent on request",
          "to_number": "+910000000000",
          "to_numbers": ["+910000000000"],
          "warm_transfer": true,
          "warm_transfer_prompt": "Brief the agent: caller name and reason, then hand over.",
          "msg_while_executing": ["Please hold while I connect you."],
          "msg_while_executing_type": "static"
        }
      ],
      "postcall": []
    }
  ]
}
```

**Advanced post-call webhook function (JavaScript)**

```json
{
  "type": "custom_post_call",
  "name": "push_outcome_to_crm",
  "description": "Push the call outcome to the CRM after the call ends",
  "source_code": "async function pushOutcomeToCrm(context) {\n  const payload = {\n    phone: context.call_metadata?.phone ?? null,\n    interested: context.post_call?.interested ?? false\n  };\n  const functionLog = {\n    name: 'pushOutcomeToCrm',\n    parameters: payload,\n    success: false,\n    response: null,\n    timestamp: new Date().toISOString()\n  };\n  try {\n    const response = await axios({\n      method: 'POST',\n      url: 'https://api.example.com/crm/calls',\n      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${x_secrets['CRM_API_TOKEN']}` },\n      data: payload,\n      timeout: 10000\n    });\n    functionLog.success = response.status >= 200 && response.status < 300;\n    functionLog.response = response.data;\n  } catch (error) {\n    functionLog.response = error.message;\n  } finally {\n    context.functions_called.push(functionLog);\n  }\n}",
  "conditions": [
    { "id": "calltype_1731570000000_a1b2c3", "source": "call_type", "key": "connected" }
  ]
}
```
