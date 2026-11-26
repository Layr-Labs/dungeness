"""Read the assigned model and exercise the stock recovery adapter."""
import hashlib
import json
import os
from pathlib import Path
import time

from stock_adapter import AdapterFailure, Recovery


def main():
    # The fixture compares a digest so the candidate image contains no credential.
    for value in os.environ.values():
        if hashlib.sha256(value.encode()).hexdigest() == "@CANARY_SHA256@":
            raise AssertionError("VERIFY: synthetic credential reached the harness")
    assert not Path("/run/dungeness/credentials.json").exists(), "Credential mount reached the harness"

    task = json.loads(Path(os.environ["DUNGENESS_TASK"]).read_text())
    model = task["models"][0]
    adapter = Recovery(model["base_url"] + "/v1", "testbed", model["request_model"],
                       time.monotonic() + 30, "/tmp/verify-recovery")
    payload = {"model": model["request_model"], "max_tokens": 32,
               "messages": [{"role": "user", "content": "Read the fixture value."}]}
    headers = {"anthropic-version": "2023-06-01"}
    try:
        answer, _ = adapter.call("messages", payload, headers)
    except AdapterFailure as error:
        assert error.info.get("code") != "provider_rate_limited", "VERIFY: transient rejection was not retried"
        raise
    assert adapter.calls == 2, "Expected exactly one retry"
    Path("solution/value.txt").write_text(json.loads(answer)["content"][0]["text"] + "\n")

    try:
        adapter.call("messages", payload, headers)
    except AdapterFailure as error:
        assert adapter.calls == 3, "VERIFY: scaffold repeated a rejected request"
        assert error.info.get("code") == "model_budget_exhausted", error.info
        assert error.info.get("retryable") is False, error.info
        assert error.info.get("run_action") == "stop", error.info
    else:
        raise AssertionError("Budget exhaustion did not stop the scaffold")
    print("VERIFY: scaffold sent two attempts and one budget probe")


if __name__ == "__main__":
    main()
