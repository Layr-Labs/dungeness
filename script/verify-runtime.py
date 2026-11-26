#!/usr/bin/env python3
"""Run and falsify the offline Runtime verification loop."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "script/verify"
OUTPUT = ROOT / ".verify"
ROUTES = {
    "anthropic", "claude-subscription", "google", "google-vertex",
    "openai", "openai-chatgpt", "openrouter", "xai",
}
STOCK_COMMIT = "ac5b68b4268f94fd10d011e923526086d8973ef4"
STOCK_SHA256 = "f42b48c62bda371bed37af04f90e7846e85e2f628e9885c163557debd9d647e0"
CANARY = "dungeness-verify-synthetic-provider-key"
SOURCE_URL = "https://example.invalid/source.git"
LINUX_X86 = platform.system() == "Linux" and platform.machine() == "x86_64"
LINUX_SKIP = "Requires Linux x86-64 with a local Docker bridge and host listener. On macOS the bridge is inside a Linux VM."
GOOGLE_INPUT = "Set DUNGENESS_VERIFY_GOOGLE_PYTHON to a local Python 3.12 environment with google-genai 3.6.1."


class VerificationError(Exception):
    pass


def need(condition, reason):
    if not condition:
        raise VerificationError(reason)


def sha256(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def redact(value):
    value = value.replace(CANARY, "[synthetic credential redacted]")
    return re.sub(r"synthetic-[a-z0-9_-]+-0123456789", "[synthetic credential redacted]", value)


def capture(*argv, cwd=ROOT, env=None):
    return subprocess.run(argv, cwd=cwd, env=env, check=True, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60).stdout.strip()


def interrupt(_signum, _frame):
    raise KeyboardInterrupt


def command(argv, cwd, env):
    with tempfile.TemporaryFile(mode="w+b") as output:
        with subprocess.Popen(argv, cwd=cwd, env=env, stdout=output, stderr=subprocess.STDOUT,
                              start_new_session=True) as child:
            try:
                child.wait(timeout=420)
            except (KeyboardInterrupt, subprocess.TimeoutExpired):
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
                raise
        output.seek(0)
        return child.returncode, redact(output.read().decode(errors="replace"))


def offline_environment():
    keys = ("PATH", "HOME", "DOCKER_CONFIG", "DOCKER_CONTEXT", "DOCKER_HOST",
            "XDG_CACHE_HOME", "XDG_DATA_HOME", "SYSTEMROOT")
    env = {k: os.environ[k] for k in keys if k in os.environ}
    env.update(UV_OFFLINE="1", UV_PYTHON="3.12", UV_PYTHON_DOWNLOADS="never",
               GIT_ALLOW_PROTOCOL="file", GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               DOCKER_BUILDKIT="0", COMPOSE_BAKE="false", LITELLM_LOCAL_MODEL_COST_MAP="True",
               PYTHONNOUSERSITE="1", PYTHONUNBUFFERED="1")
    return env


def inputs(env):
    uv_cache = Path(os.environ.get("DUNGENESS_VERIFY_UV_CACHE", "")).expanduser()
    stock = Path(os.environ.get("DUNGENESS_VERIFY_STOCK_ADAPTER", "")).expanduser()
    base = os.environ.get("DUNGENESS_VERIFY_IMAGE", "")
    need(
        uv_cache != Path(".") and uv_cache.is_dir() and stock.is_file()
        and re.fullmatch(r"sha256:[a-f0-9]{64}", base) is not None,
        "Set DUNGENESS_VERIFY_UV_CACHE, DUNGENESS_VERIFY_STOCK_ADAPTER and DUNGENESS_VERIFY_IMAGE "
        "to the local inputs described in the verification skill.",
    )
    need(sha256(stock) == STOCK_SHA256, "Stock adapter digest differs from the pinned source.")
    endpoint = env.get("DOCKER_HOST") if not env.get("DOCKER_CONTEXT") else None
    if not endpoint:
        endpoint = capture("docker", "context", "inspect", "--format", "{{.Endpoints.docker.Host}}", env=env)
    need(endpoint.startswith("unix://"), "Use a local Docker Unix socket for verification.")
    template = "{{.Id}} {{.Os}}/{{.Architecture}}"
    architecture = {"aarch64": "arm64", "arm64": "arm64", "x86_64": "amd64"}[platform.machine()]
    need(capture("docker", "image", "inspect", "--format", template, base, env=env)
         == f"{base} linux/{architecture}", "The fixture image must match its full ID and local architecture.")
    env["UV_CACHE_DIR"] = str(uv_cache.resolve())
    return base, stock.resolve()


@contextmanager
def scratch(env):
    with tempfile.TemporaryDirectory(prefix="runtime-", dir=OUTPUT) as folder:
        root = Path(folder) / "repo"
        capture("git", "clone", "--quiet", "--shared", "--no-checkout", str(ROOT), str(root), env=env)
        capture("git", "reset", "--quiet", "--mixed", "HEAD", cwd=root, env=env)
        names = capture("git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", env=env)
        for name in dict.fromkeys(names.split("\0")):
            source = ROOT / name
            if name and source.is_file() and not source.is_symlink():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
        yield root


def dockerfile(base):
    return f"FROM {base}\nUSER root\n"


def stage_gateway(root, base, *, scoring=False):
    gateway = root / "services/gateway"
    source = (gateway / "Dockerfile").read_text()
    need(source.startswith("FROM ") and len(re.findall(r"^FROM ", source, re.M)) == 1
         and re.search(r"^ADD ", source, re.M) is None, "Unsupported gateway build inputs.")
    source = dockerfile(base) + source.partition("\n")[2]
    install = "RUN pip install --no-cache-dir --requirement /app/requirements.txt"
    need(source.count(install) == 1, "The gateway image dependency install changed.")
    source = source.replace(install, "")
    source = source.replace("WORKDIR /app", "RUN if [ -d /app ]; then find /app -mindepth 1 -delete; fi\nWORKDIR /app")
    account = "useradd --no-create-home --shell /usr/sbin/nologin --uid 10001 gateway"
    need(source.count(account) == 1, "The gateway account configuration changed.")
    source = source.replace(account, f'{{ id gateway || {account}; }}')
    if scoring:
        registry = gateway / "model-access.json"
        document = json.loads(registry.read_text())
        for route, config in document["access_routes"].items():
            config["upstream_default"] = f"https://127.0.0.1:8443/{route}/v1"
        registry.write_text(json.dumps(document))
        legacy = gateway / "providers.json"
        if legacy.exists():
            need(not json.loads(legacy.read_text())["providers"], "The scored fixture requires built-in routes.")
        shutil.copy2(FIXTURE / "provider.py", gateway / "verify_provider.py")
        capture("openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1",
                "-subj", "/CN=runtime-loop", "-addext", "subjectAltName=IP:127.0.0.1",
                "-keyout", "verify-key.pem", "-out", "verify-cert.pem", cwd=gateway)
        (gateway / "verify-key.pem").chmod(0o444)
        source += ('\nUSER root\nCOPY verify_provider.py verify-key.pem verify-cert.pem /app/\n'
                   'RUN cat verify-cert.pem >> "$(python -m certifi)"\n'
                   'USER gateway\nCMD ["python", "/app/verify_provider.py"]\n')
    (gateway / "Dockerfile").write_text(source)


def stage_run(root, base, stock, env):
    shutil.copytree(root / "tests/fixtures/runtime", root, dirs_exist_ok=True)
    verifier = root / "verifiers/sample-problem/synthetic"
    task = root / "tasks/projects/dungeness/sample-starter/task.yaml"
    task.write_text(task.read_text().split("evaluation:")[0] +
                    "resources:\n  agent: {cpus: 1, memory_mb: 512}\n"
                    "  verifier: {cpus: 1, memory_mb: 512}\n")
    (verifier / "Dockerfile").write_text(dockerfile(base) + "COPY . /tests/\n")
    for name in ("grade.py", "test.sh"):
        shutil.copy2(FIXTURE / name, verifier / name)
    agent = root / "agents/projects/dungeness/command"
    (agent / "Dockerfile").write_text(dockerfile(base) + "COPY workspace/ /workspace/repo/\n")
    descriptor = agent / "agent.yaml"
    descriptor.write_text(descriptor.read_text().split("execution:")[0] +
                          'execution:\n  interface: dungeness-command-v1\n'
                          '  entrypoint: ["python", "/workspace/repo/harness.py"]\n')

    source = root.parent / "fixture-source"
    source.mkdir()
    (source / "solution").mkdir()
    (source / "solution/value.txt").write_text("0\n")
    (source / "check.txt").write_text("42\n")
    (source / "harness.py").write_text((FIXTURE / "harness.py").read_text().replace(
        "@CANARY_SHA256@", hashlib.sha256(CANARY.encode()).hexdigest()))
    shutil.copy2(stock, source / "stock_adapter.py")
    capture("git", "init", "-q", cwd=source, env=env)
    capture("git", "add", ".", cwd=source, env=env)
    git_env = dict(env, GIT_AUTHOR_DATE="2025-01-01T00:00:00+00:00",
                   GIT_COMMITTER_DATE="2025-01-01T00:00:00+00:00")
    capture("git", "-c", "user.name=Runtime Fixture", "-c", "user.email=runtime@example.invalid",
            "commit", "-qm", "Scored runtime fixture", cwd=source, env=git_env)
    commit = capture("git", "rev-parse", "HEAD", cwd=source, env=env)
    cache = root.parent / "sources"
    cache.mkdir()
    key = hashlib.sha256(f"{SOURCE_URL}\n{commit}".encode()).hexdigest()
    (cache / key).symlink_to(source)
    env["DUNGENESS_REPOSITORY_CACHE"] = str(cache)

    checkpoint = root / "checkpoints/sample-challenge" / (commit + ".yaml")
    checkpoint.write_text(f"""schema_version: 1
type: checkpoint
id: {commit}
namespace: public/github/layr-labs/sample-challenge
data:
  repository: {{url: {SOURCE_URL}, commit: {commit}}}
  history: {{anchor: {commit}, distance_from_anchor: 0, counting_method: git-rev-list-ancestry-path-count}}
  web_cutoff: "2024-12-31T23:59:59.999Z"
  interface: sample-directory-v1
""")
    spec = root / "run-specs/projects/dungeness/sample-starter.yaml"
    spec.write_text(spec.read_text().replace("62ae3d00d1e01d7bc640b5163cfea8dabffd8392", commit)
                    .replace("provider: openai", "provider: anthropic")
                    .replace("openai/gpt-6-astra", "anthropic/claude-opus-5")
                    .replace("gpt-6-astra", "claude-opus-5")
                    .replace("api: openai-responses", "api: anthropic-messages")
                    .replace("max_usd: 1", "max_usd: 0.005"))
    credentials = root / ".env"
    credentials.write_text(f"TESTBED_ANTHROPIC_API_KEY={CANARY}\n")
    credentials.chmod(0o600)
    return spec.relative_to(root), commit


def record_command(evidence, name, argv, cwd, env):
    start = time.monotonic()
    print(f"RUN {name}", flush=True)
    entry = {"leg": name, "command": list(map(str, argv)), "status": "failed"}
    evidence["commands"].append(entry)
    try:
        code, log = command(list(map(str, argv)), cwd, env)
        entry.update(exit_code=code, status="passed" if code == 0 else "failed")
        destination = OUTPUT / evidence["mode"] / f"{name}.log"
        destination.write_text(log)
        entry["log"] = str(destination.relative_to(ROOT))
        return code, log
    finally:
        entry["wall_seconds"] = round(time.monotonic() - start, 3)


def checked(evidence, name, argv, cwd, env):
    code, log = record_command(evidence, name, argv, cwd, env)
    need(code == 0, f"{name} exited {code}. See {evidence['commands'][-1]['log']}.")
    return log


@contextmanager
def gateway_image(root, base, evidence, name, env):
    stage_gateway(root, base)
    tag = "dungeness-verify-" + uuid.uuid4().hex[:12]
    try:
        checked(evidence, name + "-build",
                ["docker", "build", "--network=none", "-q", "-t", tag, "services/gateway"], root, env)
        yield tag
    finally:
        try:
            if subprocess.run(["docker", "image", "inspect", tag], env=env, cwd=root,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30).returncode == 0:
                capture("docker", "image", "rm", "--no-prune", tag, cwd=root, env=env)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
            evidence["cleanup_errors"].append(str(error))


def gateway_check(root, base, evidence, name, env, *, linux=False):
    temp = root.parent / "tmp"
    temp.mkdir()
    env = dict(env, TMPDIR=str(temp))
    with gateway_image(root, base, evidence, name, env) as tag:
        argv = ["make", "check-run-isolation", f"VERIFY_GATEWAY_IMAGE={tag}"] if linux else [
            "python3", "script/check-gateway-isolation.py", "--image", tag,
            "--bind-owner", evidence["docker_bind_owner"],
        ]
        return record_command(evidence, name, argv, root, env)


def json_lines(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def scored_run(root, base, stock, evidence, name, env):
    env = dict(env)
    stage_gateway(root, base, scoring=True)
    owner = evidence["docker_bind_owner"]
    if owner != f"{os.geteuid()}:{os.getegid()}":
        replace(root, "src/dungeness/compiler.py",
                '                "user": f"{os.geteuid()}:{os.getegid()}",',
                f'                "user": "{owner}",')
    spec, fixture_commit = stage_run(root, base, stock, env)
    temp = root.parent / "tmp"
    temp.mkdir()
    env["TMPDIR"] = str(temp)
    run_id = "runtime-verify-" + uuid.uuid4().hex[:12]
    result = root / "runs/users/verify" / run_id
    argv = ["uv", "run", "--locked", "python", "dungeness", "run", spec,
            "--namespace", "users/verify", "--run-id", run_id]
    code, log = record_command(evidence, name, argv, root, env)
    trials = list((result / "harbor").glob("*/*/result.json"))
    if code:
        for trial in trials:
            exception = json.loads(trial.read_text()).get("exception_info")
            if exception:
                log += "\n" + redact(json.dumps(exception, indent=2))
    for pattern in ("*/*/agent/harness-output-*.txt", "*/*/verifier/test-std*.txt"):
        for artifact in (result / "harbor").glob(pattern):
            log += "\n" + redact(artifact.read_text(errors="replace"))
    (OUTPUT / evidence["mode"] / f"{name}.log").write_text(log)

    if code:
        return code, log

    data = json.loads((result / "record.json").read_text())["data"]
    need(data["status"] == "completed", "The run record is not terminal and completed.")
    pins = data["configuration"]
    need(pins["repository"]["commit"] == evidence["commit"], "The run record has the wrong runtime pin.")
    launcher = pins["launcher"]
    expected_pins = evidence["pins"]
    need(launcher["harbor_version"] == expected_pins["harbor"]
         and launcher["litellm_version"] == expected_pins["litellm"],
         "The run record has the wrong launcher pins.")
    need(data["checkpoint"]["repository"]["commit"] == fixture_commit
         and data["task"]["evaluator"]["commit"] == fixture_commit,
         "The run record does not bind the staged checkpoint and evaluator.")

    need(len(trials) == 1, "Expected exactly one scored Harbor trial.")
    rewards = json.loads(trials[0].read_text())["verifier_result"]["rewards"]
    score = rewards["sample_score"]
    need(score == 42, f"Expected score 42, received {score}.")
    summary = json.loads((result / "usage/summary.json").read_text())
    usage = summary.get("usage")
    need(summary.get("run_id") == run_id and isinstance(usage, dict)
         and type(usage.get("model_requests")) is int and type(usage.get("model_tokens")) is int
         and type(usage.get("normalized_usd")) in (int, float),
         "Incompatible gateway usage summary.")
    need(usage.get("model_accounting_state") == "settled" and usage["model_requests"] == 2
         and usage["model_tokens"] == 2056
         and usage["normalized_usd"] == 0.01044, "Scored run usage did not settle at the fixture amounts.")
    provider = json_lines(result / "usage/fixture-provider.jsonl")
    need(len(provider) == 2 and provider[0] == provider[1],
         "Expected two identical upstream requests and no budget replay.")
    ledger = json_lines(result / "usage/events.jsonl")
    rejected = [entry for entry in ledger if entry["data"].get("code") == "model_budget_exhausted"]
    need(len(rejected) == 1, "Expected exactly one gateway budget rejection.")
    need("VERIFY: scaffold sent two attempts and one budget probe" in log,
         "The harness did not record its recovery checks.")
    evidence["scored_run"] = {
        "score": score, "checkpoint_and_evaluator": fixture_commit,
        "usage": usage, "upstream_requests": len(provider), "gateway_requests": 3,
        "budget_rejections": len(rejected), "model_spend_usd": 0,
    }
    return code, log


def route_check(root, evidence, name, env):
    code, log = record_command(evidence, name,
                               ["uv", "--quiet", "run", "--locked", "python", "dungeness", "providers", "--details"],
                               root, env)
    if code:
        return code, log
    document = json.loads(log)
    actual = set(document["providers"])
    missing = sorted(ROUTES - actual)
    registry = json.loads((root / "services/gateway/model-access.json").read_text())["access_routes"]
    normalized = {name: {**route, "routes": sorted(route["routes"])} for name, route in registry.items()}
    expected_digest = hashlib.sha256(json.dumps(
        normalized, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()
    policy = document["access_policy"]
    reason = None
    if missing:
        reason = f"VERIFY: missing registered route {', '.join(missing)}"
    elif policy["schema_version"] != 1 or policy["sha256"] != expected_digest:
        reason = "VERIFY: public policy digest does not match the registry"
    if reason:
        entry = evidence["commands"][-1]
        entry.update(assertion=reason, status="failed")
        (ROOT / entry["log"]).write_text(log + "\n" + reason + "\n")
        return 1, reason
    evidence["routes"] = sorted(actual)
    evidence["public_policy_sha256"] = policy["sha256"]
    return 0, log


def replace(root, relative, before, after):
    path = root / relative
    source = path.read_text()
    need(source.count(before) == 1, f"The proof mutation no longer matches {relative}.")
    path.write_text(source.replace(before, after))


def seed(root, name):
    if name == "missing-route":
        path = root / "services/gateway/model-access.json"
        registry = json.loads(path.read_text())
        need("xai" in registry["access_routes"], "The route to remove is absent before mutation.")
        del registry["access_routes"]["xai"]
        path.write_text(json.dumps(registry))
    elif name == "lost-retry-flag":
        replace(root, "services/gateway/gateway_security.py",
                '        **details,\n    }}, status_code=status',
                '        **{key: value for key, value in details.items() if key != "retryable"},\n    }}, status_code=status')
    elif name == "credential-in-harness":
        replace(root, "src/dungeness/compiler.py",
                '        main_environment["OPENAI_API_KEY"] = "testbed"',
                f'        main_environment["OPENAI_API_KEY"] = {CANARY!r}')
    elif name == "cut-stream-unsettled":
        replace(root, "services/gateway/gateway_runtime.py",
                "                                await finalize(bytes(response_body), content_type)",
                "                                if status != 'stream_interrupted':\n"
                "                                    await finalize(bytes(response_body), content_type)")
    elif name == "repeated-budget-rejection":
        replace(root, "services/gateway/gateway.py",
                '    permanent = not error.details["retryable"]',
                '    if error.code == "model_budget_exhausted":\n'
                '        error.details.update(retryable=True, run_action="continue")\n'
                '    permanent = not error.details["retryable"]')
    elif name == "replay-after-cut":
        replace(root, "services/gateway/gateway_usage.py",
                '                if self.model_accounting_incomplete:\n'
                '                    raise BudgetExceeded("model accounting is incomplete",'
                ' code="model_accounting_incomplete", action="check_accounting")\n',
                '')
    elif name == "wrong-policy-digest":
        replace(root, "src/dungeness/contracts.py", '"sha256": policy_digest(registry)', '"sha256": "0" * 64')
    elif name == "failed-run-boundary":
        replace(root, "src/dungeness/compiler.py",
                '    return {"driver": "bridge", "internal": True, "driver_opts": {\n'
                '        "com.docker.network.bridge.gateway_mode_ipv4": "isolated",\n'
                '        "com.docker.network.bridge.gateway_mode_ipv6": "isolated",\n'
                '    }}',
                '    return {"driver": "bridge", "internal": True}')
    else:
        raise ValueError(name)


FAULTS = {
    "missing-route": "VERIFY: missing registered route xai",
    "lost-retry-flag": "AssertionError: VERIFY: transient rejection was not retried",
    "credential-in-harness": "AssertionError: VERIFY: synthetic credential reached the harness",
    "cut-stream-unsettled": "AssertionError: VERIFY: cut stream left accounting unsettled",
    "repeated-budget-rejection": "AssertionError: VERIFY: scaffold repeated a rejected request",
    "replay-after-cut": "AssertionError: VERIFY: replay after ambiguous dispatch reached inference",
    "wrong-policy-digest": "VERIFY: public policy digest does not match the registry",
    "failed-run-boundary": "AssertionError: Unexpected reachability: host",
}


def proof(evidence, base, stock, env):
    for name, expected in FAULTS.items():
        if name == "failed-run-boundary" and not LINUX_X86:
            evidence["faults"].append({"fault": name, "status": "skipped", "reason": LINUX_SKIP})
            continue
        with scratch(env) as root:
            seed(root, name)
            if name in {"missing-route", "wrong-policy-digest"}:
                code, log = route_check(root, evidence, name, env)
            elif name in {"lost-retry-flag", "credential-in-harness", "repeated-budget-rejection"}:
                code, log = scored_run(root, base, stock, evidence, name, env)
            else:
                code, log = gateway_check(root, base, evidence, name, env,
                                          linux=name == "failed-run-boundary")
            detected = code != 0 and expected in log
            evidence["faults"].append({
                "fault": name, "status": "detected" if detected else "failed",
                "exit_code": code, "expected": expected,
            })
            print(f"{name}: {'detected' if detected else 'failed'}", flush=True)
    need(all(item["status"] != "failed" for item in evidence["faults"]),
         "A fault survived or failed somewhere other than its expected assertion.")


def baseline(evidence, base, stock, env):
    log = checked(evidence, "check", ["make", "-j1", "check"], ROOT, env)
    evidence["counts"]["unittest"] = sum(map(int, re.findall(r"^Ran (\d+) tests? in", log, re.M)))
    evidence["counts"]["unittest_skipped"] = sum(map(int, re.findall(r"^OK \(skipped=(\d+)\)", log, re.M)))
    code, reason = route_check(ROOT, evidence, "routes", env)
    need(code == 0, reason)
    failures = []
    with scratch(env) as root:
        code, _ = gateway_check(root, base, evidence, "gateway-isolation", env)
    if code:
        failures.append("Gateway isolation failed. See the gateway-isolation log.")
    if LINUX_X86:
        with scratch(env) as root:
            code, _ = gateway_check(root, base, evidence, "run-isolation", env, linux=True)
        if code:
            failures.append("Run isolation failed. See the run-isolation log.")
    try:
        with scratch(env) as root:
            code, _ = scored_run(root, base, stock, evidence, "scored-run", env)
        need(code == 0, "Scored run failed. See the scored-run log.")
    except VerificationError as error:
        failures.append(str(error))
    python = google_python()
    if python:
        code, _ = record_command(evidence, "google-sdk", [python, "-B", "-c",
                "import importlib.metadata as m, runpy, sys; "
                "assert sys.version_info[:2] == (3, 12); "
                "assert m.version('google-genai') == '3.6.1'; "
                "runpy.run_path('script/check-google-client.py', run_name='__main__')"], ROOT, env)
        if code:
            failures.append("Google SDK failed. See the google-sdk log.")
    else:
        evidence["blocked"] = [{"leg": "google-sdk", "reason": GOOGLE_INPUT}]
        failures.append(GOOGLE_INPUT)
    need(not failures, " ".join(failures))


def google_python():
    value = os.environ.get("DUNGENESS_VERIFY_GOOGLE_PYTHON")
    if value:
        path = Path(value).expanduser().absolute()
        if path.is_file() and os.access(path, os.X_OK):
            return path
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--prove", action="store_true")
    mode.add_argument("--doctor", action="store_true")
    mode.add_argument("--leg", choices=("scored-run", "gateway-isolation", "faults"))
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, interrupt)
    start = time.monotonic()
    name = args.leg or ("prove" if args.prove else "doctor" if args.doctor else "verify")
    OUTPUT.mkdir(mode=0o700, exist_ok=True)
    (OUTPUT / name).mkdir(mode=0o700, exist_ok=True)
    evidence = {"status": "failed", "mode": name, "commands": [], "counts": {}, "faults": [],
                "cleanup_errors": [], "skipped": [], "platform": platform.platform()}
    if not LINUX_X86:
        evidence["skipped"].append({"leg": "run-isolation", "reason": LINUX_SKIP})
        print(f"SKIP run-isolation. {LINUX_SKIP}", flush=True)
    env = offline_environment()
    try:
        evidence["commit"] = capture("git", "rev-parse", "HEAD", env=env)
        base, stock = inputs(env)
        if args.prove and google_python() is None:
            evidence["blocked"] = [{"leg": "google-sdk", "reason": GOOGLE_INPUT}]
            raise VerificationError(GOOGLE_INPUT)
        evidence["pins"] = {
            "local_image": base, "stock_adapter_sha256": STOCK_SHA256, "stock_adapter_commit": STOCK_COMMIT,
            "google_genai": "3.6.1",
            "uv_lock_sha256": sha256(ROOT / "uv.lock"),
            "pricing_sha256": sha256(ROOT / "services/gateway/pricing.yaml"),
            "registry_sha256": sha256(ROOT / "services/gateway/model-access.json"),
            "fixture_sha256": {path.name: sha256(path) for path in sorted(FIXTURE.iterdir()) if path.is_file()},
        }
        harbor = (ROOT / "src/dungeness/execution/harbor.py").read_text()
        for key in ("harbor", "litellm"):
            evidence["pins"][key] = re.search(fr'^{key.upper()}_VERSION = "([^"]+)"', harbor, re.M)[1]
        evidence["tools"] = {
            "uv": capture("uv", "--version", env=env),
            "python": capture(capture("uv", "python", "find", "3.12", env=env), "--version", env=env),
            "docker": capture("docker", "version", "--format", "{{.Client.Version}}/{{.Server.Version}}", env=env),
            "compose": capture("docker", "compose", "version", "--short", env=env),
        }
        owner = checked(evidence, "image-dependencies", ["docker", "run", "--rm",
                "--pull=never", "--network=none", "--user=0:0",
                "--mount", f"type=bind,src={ROOT / 'services/gateway/requirements.txt'},dst=/verify-requirements,readonly",
                base, "python", "-c",
                "from importlib.metadata import version\n"
                "from pathlib import Path\n"
                "for line in Path('/verify-requirements').read_text().splitlines():\n"
                "    if line.strip() and not line.startswith('#'):\n"
                "        name, expected = line.split('==')\n"
                "        assert version(name) == expected, name\n"
                "owner = Path('/verify-requirements').stat()\n"
                "print(f'{owner.st_uid}:{owner.st_gid}')"], ROOT, env).strip()
        need(re.fullmatch(r"[0-9]+:[0-9]+", owner), "Docker did not report a bind-mount owner.")
        evidence["docker_bind_owner"] = owner
        if args.leg == "scored-run":
            with scratch(env) as root:
                code, _ = scored_run(root, base, stock, evidence, name, env)
            need(code == 0, "Scored run failed. See the scored-run log.")
        elif args.leg == "gateway-isolation":
            with scratch(env) as root:
                code, _ = gateway_check(root, base, evidence, name, env)
            need(code == 0, "Gateway isolation failed. See the gateway-isolation log.")
        elif args.leg == "faults":
            proof(evidence, base, stock, env)
        elif not args.doctor:
            baseline(evidence, base, stock, env)
            if args.prove:
                proof(evidence, base, stock, env)
        need(not evidence["cleanup_errors"], "Failed to remove a verification image.")
        evidence["status"] = "passed"
        print(f"PASS Runtime {name} " + json.dumps({
            "commit": evidence["commit"], "pins": evidence["pins"], "tools": evidence["tools"],
        }, sort_keys=True), flush=True)
    except (VerificationError, subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as error:
        evidence["error"] = redact(str(error))
        print(f"FAIL Runtime {name}. {evidence['error']}", file=sys.stderr)
    except KeyboardInterrupt:
        evidence["error"] = "Interrupted."
    finally:
        evidence["wall_seconds"] = round(time.monotonic() - start, 3)
        evidence["counts"].update(
            commands_run=len(evidence["commands"]), legs_skipped=len(evidence["skipped"]),
            faults_detected=sum(item["status"] == "detected" for item in evidence["faults"]),
        )
        encoded = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
        (OUTPUT / name / "evidence.json").write_text(encoded)
        with tempfile.NamedTemporaryFile(mode="w", dir=OUTPUT, delete=False) as handle:
            handle.write(encoded)
        Path(handle.name).replace(OUTPUT / "evidence.json")
    return 0 if evidence["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
