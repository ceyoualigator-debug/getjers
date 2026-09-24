"""One error class per answer the gateway can give, so code can catch what it can handle."""
from __future__ import annotations


class JersError(Exception):
    """Base class. `status` is the HTTP status, `kind` the gateway's error type, `retry_after` seconds when given."""

    def __init__(self, message: str, status: int | None = None, kind: str | None = None, retry_after: float | None = None):
        super().__init__(message)
        self.status, self.kind, self.retry_after = status, kind, retry_after


class AuthenticationError(JersError):     # 401
    pass


class PaymentRequiredError(JersError):    # 402: no credit left
    pass


class PermissionDeniedError(JersError):   # 403: for example sign-up is off, or an invite code is needed
    pass


class NotFoundError(JersError):           # 404
    pass


class ConflictError(JersError):           # 409: a limit such as the number of golden cases
    pass


class BadRequestError(JersError):         # 413, 415, 422
    pass


class RateLimitError(JersError):          # 429
    pass


class ServerError(JersError):             # 500
    pass


class EngineError(JersError):             # 502, 503: the engine or the product behind the gateway
    pass


class ConnectionFailed(JersError):        # no HTTP answer at all
    pass


BY_STATUS = {401: AuthenticationError, 402: PaymentRequiredError, 403: PermissionDeniedError, 404: NotFoundError, 409: ConflictError, 413: BadRequestError, 415: BadRequestError,
             422: BadRequestError, 429: RateLimitError, 500: ServerError, 502: EngineError, 503: EngineError}


def error_for(status: int, message: str, kind: str | None = None, retry_after: float | None = None) -> JersError:
    return BY_STATUS.get(status, JersError)(message, status=status, kind=kind, retry_after=retry_after)
