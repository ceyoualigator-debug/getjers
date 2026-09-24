// One error class per answer the gateway can give, the same ones the Python SDK has.

export class JersError extends Error {
  status: number | undefined;
  kind: string | undefined;
  retryAfter: number | undefined;

  constructor(message: string, status?: number, kind?: string, retryAfter?: number) {
    super(message);
    this.name = new.target.name;
    this.status = status;
    this.kind = kind;
    this.retryAfter = retryAfter;
  }
}

export class AuthenticationError extends JersError {}      // 401
export class PaymentRequiredError extends JersError {}     // 402: no credit left
export class PermissionDeniedError extends JersError {}    // 403: e.g. sign-up is off, or an invite code is needed
export class NotFoundError extends JersError {}            // 404
export class ConflictError extends JersError {}            // 409: a limit such as the number of golden cases
export class BadRequestError extends JersError {}          // 413, 415, 422
export class RateLimitError extends JersError {}           // 429
export class ServerError extends JersError {}              // 500
export class EngineError extends JersError {}              // 502, 503: the engine or the product behind the gateway
export class ConnectionFailed extends JersError {}         // no HTTP answer at all

const BY_STATUS: Record<number, typeof JersError> = {
  401: AuthenticationError, 402: PaymentRequiredError, 403: PermissionDeniedError, 404: NotFoundError, 409: ConflictError,
  413: BadRequestError, 415: BadRequestError, 422: BadRequestError, 429: RateLimitError, 500: ServerError,
  502: EngineError, 503: EngineError,
};

export function errorFor(status: number, message: string, kind?: string, retryAfter?: number): JersError {
  const Cls = BY_STATUS[status] ?? JersError;
  return new Cls(message, status, kind, retryAfter);
}
