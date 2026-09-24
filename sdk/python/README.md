# jers-sdk

Python client for Jers, the decision API with memory. No dependencies beyond the standard library;
Pydantic models work when Pydantic is installed.

```python
from jers import JersClient, Choice, Noul, Score

with JersClient() as client:                      # reads JERS_API_KEY and JERS_BASE_URL
    r = client.system_one(
        state={"message": "We were charged twice for September again."},
        questions={
            "route": Choice("Which team should handle this?", {"billing": "Charges and refunds", "support": "Product problems",
                                                                "other": "None of these"}),
            "refund": Noul("Is the customer asking for money back?"),
            "urgency": Score("How urgent is this?", ["Can wait a week", "Should be handled today", "Blocking the customer now"]),
        },
        subject="acme",                            # whatever the decision is about; leave out for a stateless call
        memory={"compare": True},
    )
    print(r.answers["route"].choice, r.answers["refund"].noul, r.answers["urgency"].score)
    print(r.memory.lines_used, r.memory.lines_seen, r.memory.changes, r.usage.cost)
    for w in r.warnings:                           # known traps, for example a state longer than the engine reads
        print(w.code, w.message)
```

Install from GitHub: `pip install "git+https://github.com/ceyoualigator-debug/getjers#subdirectory=sdk/python"`. `JersClient(api_key=None, base_url=None, timeout=120.0, max_retries=2, backoff_seconds=0.5)`: the key falls back to `JERS_API_KEY`, the gateway to `JERS_BASE_URL` and then `https://api.getjers.com`.

## Pydantic models as questions

A `Literal` or an `Enum` field is a choice, a `bool` field a yes/no question, and an `int` or `float` field
marked with `Levels(...)` a score. The field's description is the question. The answers come back as the model:
an `int` score field gets the most likely level, a `float` the probability-weighted level, and a `bool` is true
when the probability of yes is at least 0.5.

```python
from typing import Annotated, Literal
from pydantic import BaseModel, Field
from jers import JersClient, Levels, Options

class Ticket(BaseModel):
    team: Annotated[Literal["billing", "support", "other"],
                    Options({"billing": "Charges and refunds", "support": "Product problems", "other": "None of these"})] = Field(
        description="Which team should handle this?")
    refund: bool = Field(description="Is the customer asking for money back?")
    urgency: Annotated[int, Levels("Can wait a week", "Should be handled today", "Blocking the customer now")] = Field(
        description="How urgent is this?")

r = JersClient().system_one("We were charged twice and need the money back today.", Ticket)
print(r.parsed.team, r.parsed.refund, r.parsed.urgency)
```

## Request options

| Option | What it does |
|---|---|
| `robust=True` | asks each choice in 3 option orders (2 for a two-option choice; `{"orders": n}` for 1 to 5) and averages; `agreement` is the share of those orders that picked the answer. A choice of more than 20 options is answered in two rounds instead |
| `windows=True` | reads a state longer than the engine reads in up to 16 overlapping windows; `{"combine": {"question_id": "max" \| "mean" \| "min"}}` sets how answers are combined |
| `derive={...}` | computes facts in code (`"reading.t > 75"`) and shows them to the model as computed by the system |
| `values={...}` | numbers and strings that `derive` and memory rules can use |
| `cache=True` | an identical request that does not use a subject's memory returns the stored answers without new engine work |
| `memory={"placebo": True}` | also asks with neutral lines, to show whether the memory worked by its content |

Robust orders, windows and the placebo pass are billed as answers; the `compare` pass is not, and a cache hit is billed like the first call. `usage.answers_billed` says how many.

## Everything else

```python
client.remember("mia", "Mia plays on Fridays.")
client.memory("mia", lines=True).lines                  # every stored line, word for word
client.forget("mia", "Fridays")["verified_forgotten"]; client.delete("mia")
client.rules_add("mia", "session_result <= -30", "Mia's stop-loss is reached: she stops now.")
client.system_one(state, questions, subject="mia", values={"session_result": -32})
client.rules("mia"); client.rules_delete("mia", rule_id)

client.feedback(r.decision_id, "route", "billing")      # the right answer, when you learn it
client.quality()                                        # accuracy, calibration error, how much can be automated
client.calibration_fit()                                # a temperature per question, kept only if it helps

client.golden_add([{"id": "c1", "state": "...", "questions": {...}, "expected": {"route": "billing"}}])
client.golden_run("jers-english")                       # accuracy, and what changed since the last run

job = client.batch_upload("requests.jsonl")             # or client.batch_create([...])
client.batch_wait(job["id"]); client.batch_results(job["id"])

client.models(); client.usage(); client.request("GET", "/v1/usage")   # any route

from jers import signup
signup("you@example.com", invite_code="...")            # on a gateway with sign-up on; needs no key
```

The client keeps one connection open per thread, retries 429, 502 and 503 with backoff (honouring
`Retry-After` up to 30 seconds) and retries a
connection that failed before the request was sent. A request that was sent and then failed is sent
again only if it is a GET, so a decision is never billed twice. Errors are typed per status:
`AuthenticationError`, `PaymentRequiredError`, `PermissionDeniedError`, `NotFoundError`, `ConflictError`,
`BadRequestError`, `RateLimitError`, `EngineError`, `ServerError`, `ConnectionFailed`.
`AsyncJersClient` has every method as a coroutine.
