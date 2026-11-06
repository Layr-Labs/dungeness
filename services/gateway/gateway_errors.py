"""Safe recovery contract. A failed request need not end the research run."""
ERROR_SCHEMA_VERSION = 1

# Only these conditions require stopping inference. All other rejected requests
# leave the run open, but retrying an unchanged request needs separate evidence.
STOP_CODES = frozenset({
    "request_budget_exhausted", "model_token_budget_exhausted", "model_budget_exhausted",
    "model_budget_rejected", "model_accounting_incomplete", "gateway_cancelled",
    "provider_credentials_unavailable", "provider_configuration_invalid",
    "provider_authentication_failed", "provider_access_denied",
    "provider_accounting_incomplete",
})


def recovery(code, *, retryable=False, action=None):
    stop = code in STOP_CODES
    category = "run_stopping" if stop else "retryable" if retryable else "correctable"
    actions = {"retryable": "retry_with_backoff", "correctable": "correct_request",
               "run_stopping": "stop_and_report"}
    return {"error_schema_version": ERROR_SCHEMA_VERSION, "category": category,
            "run_action": "stop" if stop else "continue",
            "action": action or actions[category], "retryable": retryable and not stop}


class GatewayPolicyError(ValueError):
    """Only fixed, non-secret messages may be supplied."""
    def __init__(self, code, message):
        super().__init__(message)
        self.diagnostic = {"code": code, **recovery(code)}
