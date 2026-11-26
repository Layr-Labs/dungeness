#!/usr/bin/env python3
"""Run and falsify the offline Runtime verification loop."""
from __future__ import annotations

import argparse
from contextlib import ExitStack, contextmanager
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dungeness.execution import environments

FIXTURE = ROOT / "script/verify"
OUTPUT = ROOT / ".verify"
ROUTES = {
    "anthropic", "claude-subscription", "google", "google-vertex",
    "openai", "openai-chatgpt", "openrouter", "xai",
}
EXPECTED_POLICY_SHA256 = "70fe147b1b6385c3b17f5521588396a4a1bb5ba62f4172384613be540f3e175e"
STOCK_COMMIT = "ac5b68b4268f94fd10d011e923526086d8973ef4"
STOCK_SHA256 = "f42b48c62bda371bed37af04f90e7846e85e2f628e9885c163557debd9d647e0"
CANARY = "dungeness-verify-synthetic-provider-key"
CANARY_BYTES = CANARY.encode()
SHARED_CREDENTIALS = Path("/dev/shm")
IMAGE_OWNER_LABEL = "dungeness.verify.owner"
ARTIFACT_LEAK = "VERIFY: synthetic credential reached a run artifact"
OUTPUT_LEAK = "VERIFY: synthetic credential reached scored command output"
SOURCE_URL = "https://example.invalid/source.git"
LINUX_X86 = platform.system() == "Linux" and platform.machine() == "x86_64"
LINUX_SKIP = "Requires Linux x86-64 with a local Docker bridge and host listener. On macOS the bridge is inside a Linux VM."


class VerificationError(Exception):
    pass


def need(condition, reason):
    if not condition:
        raise VerificationError(reason)


def require(condition, reason):
    if not condition:
        raise AssertionError(reason)


@contextmanager
def artifact_errors(label):
    try:
        yield
    except (AttributeError, KeyError, TypeError, ValueError, OSError) as error:
        raise VerificationError(f"{label}: {type(error).__name__}: {error}") from error


def sha256(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def redact(value):
    value = value.replace(CANARY, "[synthetic credential redacted]")
    return re.sub(r"synthetic-[a-z0-9_-]+-0123456789", "[synthetic credential redacted]", value)


def capture(*argv, cwd=ROOT, env=None):
    try:
        return subprocess.run(argv, cwd=cwd, env=env, check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60).stdout.strip()
    except subprocess.CalledProcessError as error:
        diagnostic = redact((error.stderr or "").strip())
        raise VerificationError(f"{argv[0]} exited {error.returncode}. {diagnostic}".rstrip()) from error
    except OSError as error:
        raise VerificationError(f"Cannot run {argv[0]}: {error}") from error


def interrupt(_signum, _frame):
    raise KeyboardInterrupt


def command(argv, cwd, env, output, stderr):
    with subprocess.Popen(argv, cwd=cwd, env=env, stdout=output, stderr=stderr,
                          start_new_session=True) as child:
        try:
            return child.wait(timeout=420)
        except (KeyboardInterrupt, subprocess.TimeoutExpired):
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                child.wait(timeout=30)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                child.wait()
            raise


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
    with artifact_errors("Cannot read the stock adapter"):
        need(sha256(stock) == STOCK_SHA256, "Stock adapter digest differs from the pinned source.")
    endpoint = env.get("DOCKER_HOST") or capture(
        "docker", "context", "inspect", "--format", "{{.Endpoints.docker.Host}}", env=env)
    need(endpoint.startswith("unix://"), "Use a local Docker Unix socket for verification.")
    template = "{{.Id}} {{.Os}}/{{.Architecture}}"
    architecture = {"aarch64": "arm64", "arm64": "arm64", "x86_64": "amd64"}.get(platform.machine())
    need(architecture is not None, f"Unsupported fixture architecture: {platform.machine()}.")
    need(capture("docker", "image", "inspect", "--format", template, base, env=env)
         == f"{base} linux/{architecture}", "The fixture image must match its full ID and local architecture.")
    env["UV_CACHE_DIR"] = str(uv_cache.resolve())
    return base, stock.resolve()


@contextmanager
def scratch(env, evidence):
    with artifact_errors("Cannot create the scratch checkout"):
        temporary = tempfile.TemporaryDirectory(prefix="runtime-", dir=OUTPUT)
    try:
        root = Path(temporary.name) / "repo"
        with artifact_errors("Cannot copy the scratch checkout"):
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
    finally:
        primary_error = sys.exc_info()[0]
        try:
            temporary.cleanup()
        except OSError as error:
            message = f"Cannot clean the scratch checkout: {error}"
            evidence["cleanup_errors"].append(redact(message))
            if primary_error is None:
                raise VerificationError(message) from error


def dockerfile(base, owner):
    return f"FROM {base}\nLABEL {IMAGE_OWNER_LABEL}={owner}\nUSER root\n"


def stage_gateway(root, base, env, owner, *, scoring=False):
    gateway = root / "services/gateway"
    path = gateway / "Dockerfile"
    original = path.read_text()
    need(original.startswith("FROM ") and len(re.findall(r"^FROM ", original, re.M)) == 1
         and re.search(r"^ADD ", original, re.M) is None, "Unsupported gateway build inputs.")
    install = "RUN pip install --no-cache-dir --requirement /app/requirements.txt"
    replace(gateway, "Dockerfile", f"{install}\n", "")
    replace(gateway, "Dockerfile", "WORKDIR /app\n",
            "RUN if [ -d /app ]; then find /app -mindepth 1 -delete; fi\nWORKDIR /app\n")
    account = "useradd --no-create-home --shell /usr/sbin/nologin --uid 10001 gateway"
    replace(gateway, "Dockerfile", account, f'{{ id gateway || {account}; }}')
    source = dockerfile(base, owner) + path.read_text().partition("\n")[2]
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
                "-keyout", "verify-key.pem", "-out", "verify-cert.pem", cwd=gateway, env=env)
        (gateway / "verify-key.pem").chmod(0o444)
        source += ('\nUSER root\nCOPY verify_provider.py verify-key.pem verify-cert.pem /app/\n'
                   'RUN cat verify-cert.pem >> "$(python -m certifi)"\n'
                   'USER gateway\nCMD ["python", "/app/verify_provider.py"]\n')
    path.write_text(source)


def stage_run(root, base, stock, env, owner):
    replace(root, "src/dungeness/compiler.py", '"build": {"context": "./gateway"},',
            '"build": {"context": "./gateway", "network": "none"},')
    shutil.copytree(root / "tests/fixtures/runtime", root, dirs_exist_ok=True)
    verifier = root / "verifiers/sample-problem/synthetic"
    replace(root, "tasks/projects/dungeness/sample-starter/task.yaml",
            "evaluation:\n  mode: full-benchmark\n\n"
            "resources:\n  agent:\n    memory_mb: 4096\n    cpus: 4\n"
            "  verifier:\n    memory_mb: 8192\n    cpus: 4\n"
            "    timeout_sec: 1200\n    build_timeout_sec: 1200\n",
            "resources:\n  agent: {cpus: 1, memory_mb: 512}\n"
            "  verifier: {cpus: 1, memory_mb: 512}\n")
    (verifier / "Dockerfile").write_text(dockerfile(base, owner) + "COPY . /tests/\n")
    for name in ("grade.py", "test.sh"):
        shutil.copy2(FIXTURE / name, verifier / name)
    agent = root / "agents/projects/dungeness/command"
    (agent / "Dockerfile").write_text(dockerfile(base, owner) + "COPY workspace/ /workspace/repo/\n")
    replace(agent, "agent.yaml",
            '  entrypoint: ["python3", "-c", "import os,json; '
            "print(json.load(open(os.environ['DUNGENESS_TASK']))['instruction'])\"]\n",
            '  entrypoint: ["python", "/workspace/repo/harness.py"]\n')

    source = root.parent / "fixture-source"
    source.mkdir()
    (source / "solution").mkdir()
    (source / "solution/value.txt").write_text("0\n")
    (source / "check.txt").write_text("42\n")
    shutil.copy2(FIXTURE / "harness.py", source / "harness.py")
    replace(source, "harness.py", "@CANARY_SHA256@", hashlib.sha256(CANARY_BYTES).hexdigest())
    replace(source, "harness.py", "@CANARY_BYTES@", str(len(CANARY_BYTES)))
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
    spec = Path("run-specs/projects/dungeness/sample-starter.yaml")
    replace(root, spec, "62ae3d00d1e01d7bc640b5163cfea8dabffd8392", commit)
    replace(root, spec, "provider: openai\n", "provider: anthropic\n")
    replace(root, spec, "upstream_id: openai/gpt-6-astra\n", "upstream_id: anthropic/claude-opus-5\n")
    replace(root, spec, "request_model: gpt-6-astra\n", "request_model: claude-opus-5\n")
    replace(root, spec, "api: openai-responses\n", "api: anthropic-messages\n")
    replace(root, spec, "max_usd: 1\n", "max_usd: 0.005\n")
    credentials = root / ".env"
    credentials.write_text(f"TESTBED_ANTHROPIC_API_KEY={CANARY}\n")
    credentials.chmod(0o600)
    return spec, commit


def record_command(evidence, name, argv, cwd, env, *, stdout_only=False, check_canary=False):
    start = time.monotonic()
    print(f"RUN {name}", flush=True)
    entry = {"leg": name, "command": list(map(str, argv)), "status": "failed"}
    evidence["commands"].append(entry)
    destination = OUTPUT / evidence["mode"] / f"{name}.log"
    try:
        with ExitStack() as files:
            output = files.enter_context(tempfile.TemporaryFile())
            stderr = files.enter_context(tempfile.TemporaryFile()) if stdout_only else None
            try:
                code = command(entry["command"], cwd, env, output, stderr or subprocess.STDOUT)
                entry["exit_code"] = code
            finally:
                primary_error = sys.exc_info()[0]
                try:
                    output.seek(0)
                    raw = output.read()
                    if stderr is not None:
                        stderr.seek(0)
                    raw_stderr = stderr.read() if stderr is not None else b""
                    leaked = check_canary and (CANARY_BYTES in raw or CANARY_BYTES in raw_stderr)
                    log = redact(raw.decode(errors="replace"))
                    diagnostic = redact(raw_stderr.decode(errors="replace"))
                    if leaked:
                        entry["assertion"] = OUTPUT_LEAK
                        diagnostic += f"\n{OUTPUT_LEAK}\n"
                    destination.write_text(log + ("\n" + diagnostic if diagnostic else ""))
                    entry["log"] = str(destination.relative_to(ROOT))
                except OSError as error:
                    message = f"Cannot write the {name} log: {error}"
                    if primary_error is None:
                        raise VerificationError(message) from error
                    entry["log_error"] = redact(message)
            if leaked:
                return 1, f"{log}\n{OUTPUT_LEAK}"
            entry["status"] = "passed" if code == 0 else "failed"
            return code, log
    except OSError as error:
        raise VerificationError(f"Cannot execute {name}: {error}") from error
    finally:
        entry["wall_seconds"] = round(time.monotonic() - start, 3)


def checked(evidence, name, argv, cwd, env, *, stdout_only=False):
    code, log = record_command(evidence, name, argv, cwd, env, stdout_only=stdout_only)
    need(code == 0, f"{name} exited {code}. See {evidence['commands'][-1]['log']}.")
    return log


@contextmanager
def fixture_images(root, env, evidence, owner):
    marker = f"{IMAGE_OWNER_LABEL}={owner}"
    before = image_inventory(root, env)
    try:
        yield
    finally:
        try:
            containers = capture("docker", "container", "ls", "--all", "--quiet", "--no-trunc",
                                 "--filter", f"label={marker}", cwd=root, env=env).splitlines()
            if containers:
                evidence["cleanup_errors"].append(f"Verification left fixture containers: {', '.join(containers)}")
                capture("docker", "container", "rm", "--force", *containers, cwd=root, env=env)
        except (VerificationError, subprocess.TimeoutExpired) as error:
            evidence["cleanup_errors"].append(redact(str(error)))
        try:
            owned = image_inventory(root, env, f"label={marker}")
            remove_images({image: owned[image] for image in owned.keys() - before.keys()},
                          root, env, evidence, marker)
        except (VerificationError, subprocess.TimeoutExpired) as error:
            evidence["cleanup_errors"].append(redact(str(error)))
        try:
            for image in sorted(image_inventory(root, env).keys() - before.keys()):
                history = image_history(image, root, env)
                if "verify_provider" in history or "dungeness-verify" in history:
                    evidence["cleanup_errors"].append(f"Verification left a fixture image: {image}")
        except (VerificationError, subprocess.TimeoutExpired) as error:
            evidence["cleanup_errors"].append(redact(str(error)))


def gateway_check(root, base, evidence, name, env, *, linux=False):
    temp = root.parent / "tmp"
    with artifact_errors("Cannot create the gateway probe directory"):
        temp.mkdir()
    env = dict(env, TMPDIR=str(temp))
    tag = "dungeness-verify-" + uuid.uuid4().hex
    cleanup_start = len(evidence["cleanup_errors"])
    with fixture_images(root, env, evidence, tag):
        with artifact_errors("Cannot stage the gateway fixture"):
            stage_gateway(root, base, env, tag)
        checked(evidence, name + "-build",
                ["docker", "build", "--network=none", "-q", "-t", tag, "services/gateway"], root, env)
        argv = ["make", "check-run-isolation", f"VERIFY_GATEWAY_IMAGE={tag}"] if linux else [
            "python3", "script/check-gateway-isolation.py", "--image", tag,
            "--bind-owner", evidence["docker_bind_owner"],
        ]
        code, log = record_command(evidence, name, argv, root, env)
    if code == 0 and len(evidence["cleanup_errors"]) > cleanup_start:
        return failed_assertion(evidence, log, evidence["cleanup_errors"][cleanup_start])
    return code, log


def json_lines(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def find_artifact_leak(result):
    def unreadable(error):
        raise error

    for folder, _, filenames in os.walk(result, onerror=unreadable):
        for filename in filenames:
            path = Path(folder) / filename
            if stat.S_ISREG(path.lstat().st_mode) and CANARY_BYTES in path.read_bytes():
                return f"{ARTIFACT_LEAK}: {path.relative_to(result)}"
    return None


def image_inventory(root, env, *filters):
    arguments = [argument for value in filters for argument in ("--filter", value)]
    listing = capture("docker", "image", "ls", "--all", "--no-trunc", *arguments,
                      "--format", "{{.ID}} {{.Repository}}:{{.Tag}}", cwd=root, env=env)
    images = {}
    for line in listing.splitlines():
        image, tag = line.split()
        refs = images.setdefault(image, set())
        if "<none>" not in tag:
            refs.add(tag)
    return images


def image_history(image, root, env):
    return capture("docker", "image", "history", "--no-trunc", "--format", "{{.CreatedBy}}",
                   image, cwd=root, env=env)


def remove_images(images, root, env, evidence, marker):
    if not images:
        return
    errors = evidence["cleanup_errors"]
    tags = sorted({tag for refs in images.values() for tag in refs})
    if tags:
        try:
            capture("docker", "image", "rm", "--no-prune", *tags, cwd=root, env=env)
        except (VerificationError, subprocess.TimeoutExpired) as error:
            errors.append(redact(str(error)))
    current = image_inventory(root, env)
    dangling = [image for image in images.keys() & current.keys() if not current[image]]
    # Every classic Dockerfile step adds a history entry, even for metadata-only steps.
    dangling.sort(key=lambda image: len(image_history(image, root, env).splitlines()), reverse=True)
    if dangling:
        try:
            capture("docker", "image", "rm", "--no-prune", *dangling, cwd=root, env=env)
        except (VerificationError, subprocess.TimeoutExpired) as error:
            errors.append(redact(str(error)))
    remaining = images.keys() & image_inventory(root, env).keys()
    evidence.setdefault("image_cleanup", []).append({"marker": marker, "removed": sorted(images.keys() - remaining)})
    if remaining:
        errors.append(f"Could not remove verification images for {marker}: {', '.join(sorted(remaining))}")


def project_images(project, root, env):
    # Harbor's classic Compose build can omit the project label from its images.
    images = image_inventory(root, env, f"label=com.docker.compose.project={project}")
    for image, tags in image_inventory(root, env, f"reference={project}-main:latest",
                                       f"reference={project}-gateway:latest").items():
        images.setdefault(image, set()).update(tags)
    return images


def project_resources(project, root, env):
    label = f"label=com.docker.compose.project={project}"
    resources = {}
    for kind, args in (("containers", ("container", "ls", "--all")),
                       ("networks", ("network", "ls"))):
        ids = capture("docker", *args, "--quiet", "--no-trunc", "--filter", label, cwd=root, env=env)
        if ids:
            resources[kind] = sorted(set(ids.splitlines()))
    if images := project_images(project, root, env):
        resources["images"] = sorted(tag for tags in images.values() for tag in tags)
        resources["images"].extend(sorted(image for image, tags in images.items() if not tags))
    return resources


def check_scored_cleanup(result, temp, root, env, evidence, *, failed, credentials_before=None):
    errors = evidence["cleanup_errors"]
    count_before = len(errors)
    try:
        staging = sorted(path.name for path in temp.iterdir()
                         if path.name.startswith(("dungeness-credentials-", f"dungeness-{result.name}-")))
        if staging:
            errors.append(f"Scored run left staging paths: {', '.join(staging)}")
    except OSError as error:
        errors.append(redact(f"Cannot check scored run staging: {error}"))
    if credentials_before is not None:
        for path in sorted(set(SHARED_CREDENTIALS.glob("dungeness-credentials-*")) - credentials_before):
            try:
                info = path.lstat()
                if stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid() and find_artifact_leak(path):
                    errors.append(f"Scored run left shared credential staging: {path.name}")
                    shutil.rmtree(path)
            except FileNotFoundError:
                continue
            except OSError as error:
                errors.append(redact(f"Cannot clean scored run credentials: {error}"))
    try:
        trials = environments.harbor_trials_for_run(result)
        projects = [f"{trial}{suffix}" for trial in trials for suffix in ("__env", "__verifier__trial")]
        completed = {path.parent.name.lower() for path in (result / "harbor").glob("*/*/result.json")}
        if completed.difference(trials):
            errors.append("Cannot identify both Docker projects for each recorded Harbor trial.")
        evidence.setdefault("scored_run", {})["docker_projects"] = projects
    except OSError as error:
        errors.append(redact(f"Cannot find scored run projects: {error}"))
        return

    for project in projects:
        try:
            remaining = project_resources(project, root, env)
            if remaining:
                errors.append(f"Scored run left Docker resources for {project}: {remaining}")
        except (VerificationError, subprocess.TimeoutExpired) as error:
            errors.append(redact(str(error)))
    if not failed and len(errors) == count_before:
        return
    for project in projects:
        try:
            capture("docker", "compose", "--project-name", project, "down", "--volumes", "--remove-orphans",
                    cwd=root, env=env)
        except (VerificationError, subprocess.TimeoutExpired) as error:
            errors.append(redact(f"Could not tear down scored run project {project}: {error}"))
        try:
            remove_images(project_images(project, root, env), root, env, evidence,
                          f"com.docker.compose.project={project}")
            remaining = project_resources(project, root, env)
            if remaining:
                errors.append(f"Could not remove scored run resources for {project}: {remaining}")
        except (VerificationError, subprocess.TimeoutExpired) as error:
            errors.append(redact(str(error)))


def failed_assertion(evidence, log, error):
    entry = evidence["commands"][-1]
    reason = redact(str(error))
    entry.update(status="failed", assertion=reason)
    try:
        with (ROOT / entry["log"]).open("a") as handle:
            handle.write(f"\n{reason}\n")
    except OSError as log_error:
        entry["log_error"] = redact(str(log_error))
    return 1, f"{log}\n{reason}"


def scored_run(root, base, stock, evidence, name, env):
    env = dict(env)
    scored = {}
    evidence["scored_run"] = scored
    invocation = uuid.uuid4().hex
    run_id = "runtime-verify-" + invocation[:12]
    image_owner = "dungeness-verify-" + invocation
    with artifact_errors("Cannot stage the scored fixture"):
        stage_gateway(root, base, env, image_owner, scoring=True)
        owner = evidence["docker_bind_owner"]
        if owner != f"{os.geteuid()}:{os.getegid()}":
            replace(root, "src/dungeness/compiler.py",
                    '                "user": f"{os.geteuid()}:{os.getegid()}",',
                    f'                "user": "{owner}",')
            scored["patched"] = {"gateway_user": owner}
        spec, fixture_commit = stage_run(root, base, stock, env, image_owner)
        temp = root.parent / "tmp"
        temp.mkdir()
        credentials_before = None
        if SHARED_CREDENTIALS.is_dir() and os.access(SHARED_CREDENTIALS, os.W_OK):
            credentials_before = set(SHARED_CREDENTIALS.glob("dungeness-credentials-*"))
    env["TMPDIR"] = str(temp)
    result = root / "runs/users/verify" / run_id
    argv = ["uv", "run", "--isolated", "--locked", "--python", "3.12", "python", "dungeness", "run", spec,
            "--namespace", "users/verify", "--run-id", run_id]
    code = 1
    log = ""
    cleanup_start = len(evidence["cleanup_errors"])
    with fixture_images(root, env, evidence, image_owner):
        try:
            code, log = record_command(evidence, name, argv, root, env, check_canary=True)
            with artifact_errors("Cannot read the scored run artifacts"):
                leak = find_artifact_leak(result) if result.exists() else None
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
                require(leak is None, leak)
                if code == 0:
                    scored.update(read_score(result, run_id, fixture_commit, evidence, trials, log))
        except AssertionError as error:
            code, log = failed_assertion(evidence, log, error)
        except VerificationError as error:
            if code == 0:
                failed_assertion(evidence, log, error)
            raise
        finally:
            check_scored_cleanup(result, temp, root, env, evidence,
                                 failed=code != 0 or sys.exc_info()[0] is not None,
                                 credentials_before=credentials_before)
    if code == 0 and len(evidence["cleanup_errors"]) > cleanup_start:
        return failed_assertion(evidence, log, evidence["cleanup_errors"][cleanup_start])
    return code, log


def read_score(result, run_id, fixture_commit, evidence, trials, log):
    data = json.loads((result / "record.json").read_text())["data"]
    require(data.get("status") == "completed", "The run record is not terminal and completed.")
    pins = data["configuration"]
    require(pins["repository"]["commit"] == evidence["commit"], "The run record has the wrong runtime pin.")
    launcher = pins["launcher"]
    expected_pins = evidence["pins"]
    require(launcher["harbor_version"] == expected_pins["harbor"]
         and launcher["litellm_version"] == expected_pins["litellm"],
         "The run record has the wrong launcher pins.")
    require(data["checkpoint"]["repository"]["commit"] == fixture_commit
         and data["task"]["evaluator"]["commit"] == fixture_commit,
         "The run record does not bind the staged checkpoint and evaluator.")

    require(len(trials) == 1, "Expected exactly one scored Harbor trial.")
    rewards = json.loads(trials[0].read_text())["verifier_result"]["rewards"]
    score = rewards["sample_score"]
    require(score == 42, f"Expected score 42, received {score}.")
    job = json.loads((result / "harbor" / run_id / "result.json").read_text())
    stats = job["stats"]
    require(job["n_total_trials"] == stats["n_completed_trials"] == 1 and
            all(stats[key] == 0 for key in (
                "n_errored_trials", "n_cancelled_trials", "n_running_trials", "n_pending_trials")),
            "Harbor did not report one successfully completed trial.")
    execution = data.get("execution", {})
    require(execution.get("stats") == stats and execution.get("n_total_trials") == job["n_total_trials"],
            "The run record does not match Harbor's outcome and score.")
    summary = json.loads((result / "usage/summary.json").read_text())
    usage = summary.get("usage")
    require(summary.get("run_id") == run_id and isinstance(usage, dict)
         and type(usage.get("model_requests")) is int and type(usage.get("model_tokens")) is int
         and type(usage.get("normalized_usd")) in (int, float),
         "Incompatible gateway usage summary.")
    require(data.get("usage") == usage, "The run record usage does not match the gateway usage summary.")
    require(usage.get("model_accounting_state") == "settled" and usage["model_requests"] == 2
         and usage["model_tokens"] == 2056
         and usage["normalized_usd"] == 0.01044, "Scored run usage did not settle at the fixture amounts.")
    provider = json_lines(result / "usage/fixture-provider.jsonl")
    require(len(provider) == 2 and provider[0] == provider[1],
         "Expected two identical upstream requests and no budget replay.")
    ledger = json_lines(result / "usage/events.jsonl")
    rejected = sum(entry["data"].get("code") == "model_budget_exhausted" for entry in ledger)
    requests = sum(entry["kind"] == "gateway.http_request_completed"
                   and entry["data"]["route"].startswith("/model/") for entry in ledger)
    require(rejected == 1, "Expected exactly one gateway budget rejection.")
    require(requests == len(provider) + rejected, "Gateway events did not account for every fixture request.")
    require("VERIFY: scaffold sent two attempts and one budget probe" in log,
         "The harness did not record its recovery checks.")
    return {
        "score": score, "checkpoint_and_evaluator": fixture_commit,
        "usage": usage, "upstream_requests": len(provider), "gateway_requests": requests,
        "budget_rejections": rejected,
    }


def route_check(root, evidence, name, env):
    code, log = record_command(evidence, name,
                               ["uv", "run", "--isolated", "--locked", "--python", "3.12",
                                "python", "dungeness", "providers", "--details"],
                               root, env, stdout_only=True)
    if code:
        return code, log
    try:
        with artifact_errors("Cannot parse the route report"):
            document = json.loads(log)
            actual = set(document["providers"])
            missing = sorted(ROUTES - actual)
            extra = sorted(actual - ROUTES)
            require(not missing, f"VERIFY: missing registered route {', '.join(missing)}")
            require(not extra, f"VERIFY: unexpected registered route {', '.join(extra)}")
            policy = document["access_policy"]
            require(policy.get("schema_version") == 1 and policy.get("sha256") == EXPECTED_POLICY_SHA256,
                    "VERIFY: public policy digest does not match the registry")
    except AssertionError as error:
        return failed_assertion(evidence, log, error)
    except VerificationError as error:
        failed_assertion(evidence, log, error)
        raise
    evidence["routes"] = sorted(actual)
    evidence["public_policy_sha256"] = policy["sha256"]
    return 0, log


def replace(root, relative, before, after):
    path = root / relative
    source = path.read_text()
    need(source.count(before) == 1, f"The verification substitution no longer matches {relative}.")
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
    elif name == "credential-in-artifact":
        replace(root, "src/dungeness/records.py",
                "    write_json(record_path, record)\n    return",
                "    write_json(record_path, record)\n"
                f"    (record_path.parent / 'credential-canary.bin').write_bytes({CANARY_BYTES!r})\n"
                "    return")
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
        for indent in (" " * 16, " " * 12):
            replace(root, "services/gateway/gateway_usage.py",
                    f'\n{indent}if self.model_accounting_incomplete:\n'
                    f'{indent}    raise BudgetExceeded("model accounting is incomplete",'
                    ' code="model_accounting_incomplete", action="check_accounting")',
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
    "credential-in-artifact": ARTIFACT_LEAK,
    "cut-stream-unsettled": "AssertionError: VERIFY: cut stream left accounting unsettled",
    "repeated-budget-rejection": "AssertionError: VERIFY: scaffold repeated a rejected request",
    "replay-after-cut": "AssertionError: VERIFY: replay after ambiguous dispatch reached inference",
    "wrong-policy-digest": "VERIFY: public policy digest does not match the registry",
    "failed-run-boundary": "AssertionError: Unexpected reachability: host",
}


def proof(evidence, base, stock, env, *, fault=None):
    cases = {fault: FAULTS[fault]} if fault else FAULTS
    for name, expected in cases.items():
        if name == "failed-run-boundary" and not LINUX_X86:
            evidence["faults"].append({"fault": name, "status": "skipped", "reason": LINUX_SKIP})
            continue
        case = dict(evidence, commands=[], cleanup_errors=[], image_cleanup=[])
        case.pop("scored_run", None)
        entry = {"fault": name, "expected": expected}
        detected = False
        try:
            with scratch(env, case) as root:
                with artifact_errors(f"Cannot seed {name}"):
                    seed(root, name)
                if name in {"missing-route", "wrong-policy-digest"}:
                    code, log = route_check(root, case, name, env)
                elif name in {"lost-retry-flag", "credential-in-harness", "credential-in-artifact",
                              "repeated-budget-rejection"}:
                    code, log = scored_run(root, base, stock, case, name, env)
                else:
                    code, log = gateway_check(root, base, case, name, env,
                                              linux=name == "failed-run-boundary")
        except (VerificationError, subprocess.TimeoutExpired) as error:
            code = 1
            entry["error"] = redact(str(error))
        else:
            detected = code != 0 and expected in log and not case["cleanup_errors"]
        finally:
            evidence["commands"].extend(case["commands"])
            evidence["cleanup_errors"].extend(case["cleanup_errors"])
            evidence.setdefault("image_cleanup", []).extend(case["image_cleanup"])
        if "scored_run" in case:
            entry["docker_projects"] = case["scored_run"].get("docker_projects", [])
        if patched := case.get("scored_run", {}).get("patched"):
            entry["patched"] = patched
        entry.update(status="detected" if detected else "failed", exit_code=code)
        evidence["faults"].append(entry)
        print(f"{name}: {entry['status']}", flush=True)
    require(all(item["status"] != "failed" for item in evidence["faults"]),
            "A fault survived or failed somewhere other than its expected assertion.")


def baseline(evidence, base, stock, env):
    log = checked(evidence, "check", ["make", "-j1", "check"], ROOT, env)
    suites = re.split(r"^Checking (.+)\n", log, flags=re.M)
    require(suites[1::2] == ["tests", "services/gateway/tests", "tools/transcripts", "Harbor adapter contract"],
            "A required unittest suite is missing or repeated. See the check log.")
    test_counts = [re.findall(r"^Ran (\d+) tests? in", result, re.M) for result in suites[2::2]]
    require(all(len(counts) == 1 and int(counts[0]) > 0 for counts in test_counts),
            "A unittest suite ran no tests or reported more than one result. See the check log.")
    evidence["counts"]["unittest"] = sum(int(counts[0]) for counts in test_counts)
    evidence["counts"]["unittest_skipped"] = sum(map(int, re.findall(r"^OK \(skipped=(\d+)\)", log, re.M)))
    code, _ = route_check(ROOT, evidence, "routes", env)
    require(code == 0, "Route discovery failed. See the routes log.")
    failures = []
    for leg in ("gateway-isolation", "run-isolation") if LINUX_X86 else ("gateway-isolation",):
        try:
            with scratch(env, evidence) as root:
                code, _ = gateway_check(root, base, evidence, leg, env, linux=leg == "run-isolation")
            if code:
                failures.append(f"{leg.replace('-', ' ').capitalize()} failed. See the {leg} log.")
        except (VerificationError, subprocess.TimeoutExpired) as error:
            failures.append(str(error))
    try:
        with scratch(env, evidence) as root:
            code, _ = scored_run(root, base, stock, evidence, "scored-run", env)
        if code:
            failures.append("Scored run failed. See the scored-run log.")
    except (VerificationError, subprocess.TimeoutExpired) as error:
        failures.append(str(error))
    if patched := evidence.get("scored_run", {}).get("patched"):
        host = f"{os.geteuid()}:{os.getegid()}"
        failures.append("Gateway cannot start unmodified on this Docker engine: "
                        f"bind owner {patched['gateway_user']} != host {host}; see skill Gotchas.")
    try:
        code, _ = record_command(evidence, "google-sdk", [
            "uv", "run", "--locked", "--offline", "--isolated", "--python", "3.12",
            "--group", "gateway", "--group", "google-sdk", "python", "-B", "-c",
            "import importlib.metadata as m, runpy, sys; "
            "assert sys.version_info[:2] == (3, 12); "
            "assert m.version('google-genai') == '3.6.1'; "
            "runpy.run_path('script/check-google-client.py', run_name='__main__')",
        ], ROOT, env)
        if code:
            failures.append("Google SDK failed. See the google-sdk log.")
    except (VerificationError, subprocess.TimeoutExpired) as error:
        failures.append(str(error))
    require(not failures, " ".join(failures))


def write_evidence(path, encoded):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(encoded)
        temporary.replace(path)
    finally:
        if temporary is not None:
            primary_error = sys.exc_info()[0]
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                if primary_error is None:
                    raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--prove", action="store_true")
    mode.add_argument("--doctor", action="store_true")
    mode.add_argument("--leg", choices=("scored-run", "gateway-isolation", "faults"))
    mode.add_argument("--fault", choices=tuple(FAULTS))
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, interrupt)
    start = time.monotonic()
    name = args.fault or args.leg or ("prove" if args.prove else "doctor" if args.doctor else "verify")
    full_run = name in {"verify", "prove"}
    evidence = {"status": "failed", "mode": name, "commands": [], "counts": {}, "faults": [],
                "cleanup_errors": [], "skipped": [], "platform": platform.platform()}
    if full_run and not LINUX_X86:
        evidence["skipped"].append({"leg": "run-isolation", "reason": LINUX_SKIP})
    env = offline_environment()
    try:
        with artifact_errors("Cannot prepare the evidence directory"):
            OUTPUT.mkdir(mode=0o700, exist_ok=True)
            (OUTPUT / name).mkdir(mode=0o700, exist_ok=True)
        evidence["commit"] = capture("git", "rev-parse", "HEAD", env=env)
        evidence["worktree_dirty"] = bool(capture("git", "status", "--porcelain", env=env))
        need(not full_run or not evidence["worktree_dirty"], "The worktree was dirty at startup.")
        base, stock = inputs(env)
        if evidence["skipped"]:
            print(f"SKIP run-isolation. {LINUX_SKIP}", flush=True)
        with artifact_errors("Cannot read verification pins"):
            evidence["pins"] = {
                "local_image": base, "stock_adapter_sha256": STOCK_SHA256, "stock_adapter_commit": STOCK_COMMIT,
                "google_genai": "3.6.1",
                "uv_lock_sha256": sha256(ROOT / "uv.lock"),
                "verification_script_sha256": sha256(Path(__file__)),
                "pricing_sha256": sha256(ROOT / "services/gateway/pricing.yaml"),
                "registry_sha256": sha256(ROOT / "services/gateway/model-access.json"),
                "fixture_sha256": {path.name: sha256(path) for path in sorted(FIXTURE.iterdir()) if path.is_file()},
            }
            harbor = (ROOT / "src/dungeness/execution/harbor.py").read_text()
            for key in ("harbor", "litellm"):
                match = re.search(fr'^{key.upper()}_VERSION = "([^"]+)"', harbor, re.M)
                need(match is not None, f"Cannot read the {key} version pin.")
                evidence["pins"][key] = match[1]
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
                "import shutil, sys\n"
                "from importlib.metadata import version\n"
                "from pathlib import Path\n"
                "assert sys.version_info[:2] == (3, 12), 'The fixture requires Python 3.12'\n"
                "assert shutil.which('bash'), 'The fixture requires bash'\n"
                "for line in Path('/verify-requirements').read_text().splitlines():\n"
                "    if line.strip() and not line.startswith('#'):\n"
                "        name, expected = line.split('==')\n"
                "        assert version(name) == expected, name\n"
                "owner = Path('/verify-requirements').stat()\n"
                "print(f'{owner.st_uid}:{owner.st_gid}')"], ROOT, env, stdout_only=True).strip()
        need(re.fullmatch(r"[0-9]+:[0-9]+", owner), "Docker did not report a bind-mount owner.")
        evidence["docker_bind_owner"] = owner
        if args.leg == "scored-run":
            with scratch(env, evidence) as root:
                code, _ = scored_run(root, base, stock, evidence, name, env)
            require(code == 0, evidence["commands"][-1].get("assertion", "Scored run failed. See the scored-run log."))
        elif args.leg == "gateway-isolation":
            with scratch(env, evidence) as root:
                code, _ = gateway_check(root, base, evidence, name, env)
            require(code == 0, "Gateway isolation failed. See the gateway-isolation log.")
        elif args.leg == "faults" or args.fault:
            proof(evidence, base, stock, env, fault=args.fault)
        elif not args.doctor:
            baseline(evidence, base, stock, env)
            if args.prove:
                proof(evidence, base, stock, env)
        need(not evidence["cleanup_errors"], "Verification cleanup failed. See cleanup_errors in the evidence.")
        evidence["worktree_dirty_at_end"] = bool(capture("git", "status", "--porcelain", env=env))
        if full_run:
            need(not evidence["worktree_dirty_at_end"], "The worktree was dirty at completion.")
            need(capture("git", "rev-parse", "HEAD", env=env) == evidence["commit"],
                 "The worktree commit changed during verification.")
        if args.doctor:
            evidence["status"] = "ready"
        elif evidence["faults"] and all(item["status"] == "skipped" for item in evidence["faults"]):
            evidence["status"] = "skipped"
        else:
            evidence["status"] = "passed"
    except (AssertionError, VerificationError, subprocess.TimeoutExpired, FileNotFoundError) as error:
        evidence["error"] = redact(str(error))
    except KeyboardInterrupt:
        evidence["error"] = "Interrupted."
    finally:
        evidence["wall_seconds"] = round(time.monotonic() - start, 3)
        evidence["counts"].update(
            commands_run=len(evidence["commands"]), legs_skipped=len(evidence["skipped"]),
            faults_detected=sum(item["status"] == "detected" for item in evidence["faults"]),
        )
        encoded = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
        try:
            write_evidence(OUTPUT / name / "evidence.json", encoded)
            if full_run:
                write_evidence(OUTPUT / "evidence.json", encoded)
        except OSError as error:
            evidence["status"] = "failed"
            evidence.setdefault("error", redact(f"Cannot write verification evidence: {error}"))
    if evidence["status"] == "failed":
        detail = " ".join(evidence["error"].splitlines())
        print(f"FAIL Runtime {name}. {detail}", file=sys.stderr)
        return 1
    if evidence["status"] == "skipped":
        print(f"SKIP Runtime {name}. {evidence['faults'][0]['reason']}", flush=True)
        return 0
    provenance = {key: evidence[key] for key in
                  ("commit", "pins", "tools", "worktree_dirty", "worktree_dirty_at_end")}
    provenance["skipped_legs"] = [item["leg"] for item in evidence["skipped"]]
    provenance["skipped_faults"] = [item["fault"] for item in evidence["faults"] if item["status"] == "skipped"]
    patched = evidence.get("scored_run", {}).get("patched") or next(
        (item["patched"] for item in evidence["faults"] if "patched" in item), None)
    if patched:
        provenance["patched"] = patched
    status = "READY" if args.doctor else "PASS"
    print(f"{status} Runtime {name} " + json.dumps(provenance, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
