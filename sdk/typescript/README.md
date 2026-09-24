# jers-sdk (TypeScript)

TypeScript client for Jers, the decision API with memory. No dependencies: it uses the `fetch` built into
Node, Deno, Bun and browsers. The source is plain TypeScript that Node 22.18+ runs directly.

Install it from a clone of this repository (npm links the folder, and Node runs the TypeScript there):

```bash
git clone https://github.com/ceyoualigator-debug/getjers
npm install ./getjers/sdk/typescript      # then: import { JersClient } from "jers-sdk"
```

Node does not strip types from files copied into `node_modules`, so a packed copy (`npm pack`, or `--install-links`) fails with `ERR_UNSUPPORTED_NODE_MODULES_TYPE_STRIPPING`; import from the linked folder, or from the source path as below.

```ts
import { JersClient, choice, noul, score } from "jers-sdk";

const jers = new JersClient();                       // JERS_API_KEY, JERS_BASE_URL
const r = await jers.systemOne("We were charged twice for September again.", {
  route: choice("Which team should handle this?", { billing: "Charges and refunds", support: "Product problems", other: "None of these" }),
  refund: noul("Is the customer asking for money back?"),
  urgency: score("How urgent is this?", ["Can wait a week", "Should be handled today", "Blocking the customer now"]),
}, { subject: "acme", memory: { compare: true } });

r.answers.route.choice;          // typed "billing" | "support" | "other"
r.answers.refund.noul;           // probability of yes
r.memory?.without_memory;        // the same call without the memory
r.usage.answers_billed;          // what this call cost, in answers
```

`new JersClient({ apiKey, baseUrl, timeoutMs, maxRetries, backoffMs })`: the key falls back to `JERS_API_KEY`,
the gateway to `JERS_BASE_URL` and then `https://api.getjers.com`; by default 120 000 ms per call, 2 retries,
500 ms backoff.

Everything the API offers has a method: `remember`, `forget`, `delete`, `memory(subject, lines)`, `rulesAdd`,
`rules`, `rulesDelete`, `feedback`, `quality`, `calibrationFit`, `calibration`, `goldenAdd`, `golden`,
`goldenRun`, `goldenDelete` (`[]` deletes nothing; no argument, every case), `decisionsDelete`, `batchCreate`,
`batchUpload` (JSON Lines), `batch`, `batches`, `batchResults`, `batchWait`, `models`, `usage`,
`request(method, path, body)` for any route, and `signup(email, { inviteCode })`, which needs no key.

Options on `systemOne`: `model`, `subject`, `memory` (`use`, `top_k`, `min_share`, `compare`, `placebo`),
`robust` (`true` or `{ orders: 1-5 }`, choices of up to 20 options), `windows` (`true` or
`{ combine: { question_id: "max" | "mean" | "min" } }`), `derive`, `values`, `cache`.

Errors are typed per status: `AuthenticationError`, `PaymentRequiredError`, `PermissionDeniedError`,
`NotFoundError`, `ConflictError`, `BadRequestError`, `RateLimitError` (with `retryAfter`), `EngineError`,
`ServerError`, `ConnectionFailed`. The client retries 429, 502 and 503 with backoff and retries a
connection that failed before the request was sent; a request that was sent and then failed is sent
again only if it is a GET, so a decision is never billed twice.

`tsconfig.json` has the settings for type-checking the source with `tsc`.
