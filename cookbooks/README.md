# Jers cookbooks

Runnable recipes against a Jers gateway. Each prints what it measured; nothing is hard-coded.

```bash
export JERS_API_KEY=jj_live_...            # your Jers key
export JERS_BASE_URL=https://api.getjers.com  # the default
python3 cookbooks/support_triage.py
```

Each script deletes and rewrites the memory of its own subjects under your key's tenant (`northwind`, `contoso`,
`fabrikam`, `mia`, `player-7`, `pump-12`, `pump-13`), and its requests are billed; use a tenant of its own.

| Script | Pattern | What it shows |
|---|---|---|
| `support_triage.py` | speculative fan-out | five questions per ticket in one request; code uses the ones the category makes relevant |
| `escalation_with_memory.py` | memory-first routing | the same complaint from a priority account and a control account, with and without memory |
| `forget_on_request.py` | forgetting | remember, decide, forget with a verified removal, decide again, delete |
| `rules_in_memory.py` | rules in memory | forbidden options left out in code, a stop-loss as a rule with `when`, and what memory wording can and cannot do, measured |
| `guardrails.py` | screening | nouls plus a severity score route messages to pass, review, block or support |
| `intent_routing.py` | confidence-gated routing | intent and complexity choose the handler: code, specialist, person |
| `composite_scoring.py` | composite scoring | one score per dimension, two weightings in code |
| `game_npc_memory.py` | a player as the subject | how characters treat a player, with and without what the player did |
| `device_alerts.py` | a machine as the subject | limits checked in code with `derive`, memory for what a technician knows |
| `lead_scoring.py` | lead scoring | an unsubscribe gate first, then fit, timing, budget and size combined in code |

`JERS_MODEL` picks the model (default `jers-english`). Their measured output is on https://getjers.com/docs/cookbooks.html.
