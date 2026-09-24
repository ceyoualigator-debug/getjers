---
name: jers
description: Use Jers, the decision API with memory, inside the software you write - typed choice/score/noul questions about a state, with a per-subject memory - instead of asking a chat model for JSON.
---

# Jers

Jers answers typed questions about a state in one request and never generates text. Use it in the
application you are building for routing, classification, scoring, yes/no checks, and any decision
that should take a subject's remembered facts into account. Do not use it to write code or chat.

## Call it

- `POST $JERS_BASE_URL/v1/systemone` (default `https://api.getjers.com`), `Authorization: Bearer $JERS_API_KEY`.
- Body: `state` (string, object or array of strings), `questions` (map of id to question), optional
  `model` (`jers-latest`, `jers-english`, `jers-multilingual`, `jers-typed-decisions`), optional `subject` (whatever the decision is about: a customer, a user, a player, a device) and `memory {use, compare, top_k, min_share, placebo}`, `robust`, `windows`, `derive` with `values`, `cache`.
- Question types: `{"type":"choice","instructions":...,"criteria":{name: description}}` (1 to 255 options; up to 20 are read in one pass, more in two rounds);
  `{"type":"score","instructions":...,"criteria":[low, ..., high]}` (2 to 10 levels);
  `{"type":"noul","instructions":...}` (yes/no). At most 400 engine questions per request.
- Answers: choice `{choice, probabilities, confidence}`, score `{score, probabilities, legend, confidence}`, noul `{noul, confidence}`; plus `warnings`, `reading` and a `decision_id`.
- Python: `pip install -e sdk/python`; `from jers import JersClient, Choice, Score, Noul`; `client.system_one(state, questions, subject=...)`,
  `client.remember(subject, text)`, `client.forget(subject, concept)`, `client.delete(subject)`, `client.rules_add(subject, when, text)`.
- TypeScript: `sdk/typescript`; `new JersClient()`, `jers.systemOne(state, questions, { subject })`.

## Write good questions

- One thing per question; combine answers in code with weights and thresholds you control.
- Choice for unordered categories (add `other`), Score for a spectrum described as situations, Noul for a statement phrased for yes.
- Send every question that might matter in one request; adding questions does not change the others.
- Gate actions on confidence. Start from a guess, such as acting alone above about 0.9, confirming between 0.6 and 0.9 and handing lower ones to a person, then set the thresholds from `GET /v1/quality`, which gives per question the probability where 90% accuracy is reached.
- The engine reads up to about 475 tokens of state on the English model (measured with a short yes/no question; long questions, many options and memory lines leave less); `usage.state_truncated` says when it read less, and `windows: true` reads the rest, billed per window.
- Keep the `decision_id`, send `POST /v1/feedback` when the right answer is known, and read `GET /v1/quality`.

## Use the memory well

- Write facts once with `remember`, as positive statements that use the names your states use; name the `subject` in decisions.
- Never name a forbidden option in memory (naming it makes it more likely); when an option must never be chosen, leave it out of the question's criteria in code.
- The engine does not compare numbers or times: put the number in `values` and add a rule with `when` (`POST /v1/memory/rules`, with `expires` or `ttl_seconds` when it should end), checked in code at every decision; or compute the fact with `derive`.
- Keep memories short; replace lines rather than append. Use `memory.compare` and `memory.placebo` in development to see what the memory changed.
- `forget` removes one concept and returns `verified_forgotten`; `delete` removes everything stored about a subject. Use them for data-protection requests; the billing ledger still keeps the subject id of each priced request.

## Errors

401 key, 402 no credit, 409 a limit (memory, rules, golden cases), 422 bad request (the message says why), 429 rate limit (`Retry-After`), 502 engine down (nothing charged). Both SDKs retry 429, 502 and 503.

The documentation index is `GET /llms.txt` on the gateway.
