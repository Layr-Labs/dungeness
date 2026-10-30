"""No Docker or paid model calls: command/compiler/ledger boundary contracts."""
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


compiler = load("command_compiler", "src/dungeness/compiler.py")
CONFIGURED_FIXTURES = json.loads((ROOT / "tests/fixtures/provider-registry.json").read_text())["providers"]
usage = load("command_usage", "services/gateway/gateway_usage.py")
models = load("command_models", "services/gateway/gateway_models.py")
MODEL = {"provider": "openai-chatgpt", "request_model": "gpt-6-astra",
         "upstream_id": "openai/gpt-6-astra", "api": "openai-responses", "name_format": "request"}


class CommandHarnessTests(unittest.TestCase):
    def test_command_child_receives_real_deadline(self):
        with tempfile.TemporaryDirectory() as tmp:
            task = Path(tmp)/'task.json'
            task.write_text(json.dumps({'workspace': tmp, 'remaining_seconds': 45,
                'execution': {'entrypoint': [sys.executable, '-c',
                "import os,time; remaining=float(os.environ['DUNGENESS_AGENT_DEADLINE_EPOCH'])-time.time(); assert 40<remaining<=45; assert os.environ['DUNGENESS_AGENT_TIMEOUT_SEC']=='45'"]}}))
            result = subprocess.run([sys.executable, str(ROOT/'adapters/harbor/command_runner.py'), str(task)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_provider_discovery_does_not_import_execution_only_dependencies(self):
        code = ("import runpy,sys; sys.modules['dotenv']=None; "
                "sys.argv=[sys.argv[1],'providers']; runpy.run_path(sys.argv[0],run_name='__main__')")
        result = subprocess.run([sys.executable, "-c", code, str(ROOT / "dungeness")],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("anthropic", result.stdout)

    def test_retired_native_providers_cannot_compile(self):
        for provider in ("kimi-code", "moonshot"):
            with self.subTest(provider=provider), self.assertRaisesRegex(ValueError, "unsupported model provider"):
                compiler.command_models({"model": {**MODEL, "provider": provider}})

    def test_native_launchers_fail_before_model_selection(self):
        for name in ("codex", "claude-code", "pi", "prime-agent"):
            with self.subTest(name=name), patch.object(compiler, "command_models") as models:
                with self.assertRaisesRegex(ValueError, "Bundled agents are retired"):
                    compiler.build_harbor_job("retired", {"harbor": {"agent": name}}, ROOT)
                models.assert_not_called()

    def test_command_rejects_native_credentials_and_host_overrides(self):
        execution = {"interface": "dungeness-command-v1", "entrypoint": ["solver"]}
        for field, value in (
            ("authentication", {"mode": "chatgpt-subscription"}),
            ("environment", {"OPENAI_API_KEY": "synthetic-secret"}),
            ("adapter", "adapter:system/dungeness/custom"),
            ("harbor", {"import_path": "solver:HostCode"}),
        ):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "cannot select"):
                compiler.command_execution({"execution": execution, field: value})

    def test_chatgpt_without_command_policy_cannot_mount_credentials_in_agent(self):
        with self.assertRaisesRegex(ValueError, "requires command model_access"):
            compiler.build_compose("legacy", {"historical_cutoff": {}}, {}, provider="openai-chatgpt")

    def test_only_generic_command_example_and_adapters_are_bundled(self):
        descriptors = list((ROOT / "agents/projects/dungeness").glob("*/agent.yaml"))
        self.assertEqual([path.parent.name for path in descriptors], ["command"])
        for path in descriptors:
            compiler.command_execution(yaml.safe_load(path.read_text()))
        for path in ("adapters/harbor/codex_gateway.py", "adapters/harbor/codex_subscription.py",
                     "adapters/harbor/prime_agent.py", "adapters/harbor/pi_prebaked.py",
                     "services/codex-subscription-proxy"):
            self.assertFalse((ROOT / path).exists(), path)

    def test_control_plane_accepts_only_the_trusted_command_adapter(self):
        from test_record_model import cli
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "job.yaml"
            entry = {"import_path": "command_agent:CommandAgent", "env": {}}
            path.write_text(yaml.safe_dump({"agents": [entry]}))
            cli.validate_command_job(path)
            for override in ({"import_path": "solver:Host"}, {"name": "codex"},
                             {"env": {"OPENAI_API_KEY": "synthetic-secret"}}):
                path.write_text(yaml.safe_dump({"agents": [{**entry, **override}]}))
                with self.assertRaisesRegex(RuntimeError, "Only dungeness-command-v1"):
                    cli.validate_command_job(path)

    def test_host_provider_environment_scrubbing_is_preserved(self):
        from test_record_model import cli
        environment, scrubbed = cli.harbor_launch_environment({
            "PATH": "/usr/bin", "ANTHROPIC_API_KEY": "synthetic-secret",
            "AWS_BEARER_TOKEN_BEDROCK": "synthetic-secret", "CLAUDE_CODE_USE_BEDROCK": "1",
            "TESTBED_OPENAI_API_KEY": "gateway-only",
        }, {})
        self.assertEqual(environment, {"PATH": "/usr/bin", "TESTBED_OPENAI_API_KEY": "gateway-only"})
        self.assertEqual(set(scrubbed), {"ANTHROPIC_API_KEY", "AWS_BEARER_TOKEN_BEDROCK",
                                        "CLAUDE_CODE_USE_BEDROCK"})

    def test_configured_account_metadata_is_exposed_only_to_authorized_gateway(self):
        profile = {**CONFIGURED_FIXTURES["example-api"],
                   "credential_headers": {"account-id": "EXAMPLE_API_KEY_ACCOUNT"}}
        with patch.dict(compiler.CONFIGURED_PROVIDERS, {"example-api": profile}):
            for selected in ("example-api", "openai"):
                with self.subTest(selected=selected):
                    compose = yaml.safe_load(compiler.build_compose(
                        "configured-account",
                        {"historical_cutoff": {"end_published_date": "2026-05-28T23:59:59Z"},
                         "search": {"max_results": 25}},
                        {"web": {"searches": 0, "fetches": 0},
                         "model": {"requests": 10, "total_tokens": 10000}},
                        provider="example-api", max_usd=1,
                        command_policy={"models": [{
                            **MODEL, "provider": selected, "request_model": "example",
                            "base_url": f"http://gateway:8080/model/{selected}/v1",
                        }]}))
                    env = compose["services"]["gateway"]["environment"]
                    if selected == "example-api":
                        self.assertEqual(compose["services"]["gateway"]["x-dungeness-credential-env"]["EXAMPLE_API_KEY_ACCOUNT"],
                                         "TESTBED_EXAMPLE_API_KEY_ACCOUNT")
                        self.assertNotIn("EXAMPLE_API_KEY_ACCOUNT", env)
                    else:
                        self.assertNotIn("EXAMPLE_API_KEY_ACCOUNT", env)
                    self.assertNotIn("EXAMPLE_API_KEY_ACCOUNT", json.dumps(compose["services"]["main"]))

    def test_command_topology_needs_only_gateway_and_verifier(self):
        compose = yaml.safe_load(compiler.build_compose(
            "generic-run",
            {"historical_cutoff": {"end_published_date": "2026-05-28T23:59:59Z"},
             "search": {"max_results": 25}},
            {"web": {"searches": 0, "fetches": 0},
             "model": {"requests": 10, "total_tokens": 10000}},
            dev_scorer={"submissions": 10, "port": 8081, "context": "verifier"},
            provider="openai", max_usd=1,
        ))
        self.assertEqual(set(compose["services"]), {"main", "gateway", "dev-scorer"})
        self.assertTrue(compose["networks"]["agent_internal"]["internal"])
        self.assertEqual(compose["services"]["main"]["networks"], ["agent_internal"])

        self.assertEqual(compose["services"]["gateway"]["environment"]["MAX_MODEL_USD"], "1")
        self.assertEqual(compose["services"]["gateway"]["environment"]["DUNGENESS_OPENROUTER_INFERENCE_ONLY"],
                         "${TESTBED_OPENROUTER_INFERENCE_ONLY:-}")
        self.assertNotIn("DUNGENESS_OPENROUTER_INFERENCE_ONLY", compose["services"]["main"]["environment"])
        self.assertEqual(compose["services"]["dev-scorer"]["environment"]["MAX_SUBMISSIONS"], "10")
        self.assertNotIn("DUNGENESS_RESEARCH_STATE_URL", json.dumps(compose))

    def test_bounded_admission_is_owned_by_gateway(self):
        compose = yaml.safe_load(compiler.build_compose(
            "guarded-run", {"historical_cutoff": {}, "search": {"max_results": 25}},
            {"web": {"searches": 0, "fetches": 0}, "model": {"requests": 10, "total_tokens": 10000}},
            provider="openai", max_usd=1,
            command_policy={"models": [{**MODEL, "provider": "openai", "base_url": "http://gateway:8080/model/openai/v1"}],
                            "bounded_requests": True, "max_output_tokens": 65536}))
        env = compose["services"]["gateway"]["environment"]
        self.assertEqual(env["DUNGENESS_BOUNDED_REQUESTS"], "1")
        self.assertEqual(env["DUNGENESS_MAX_OUTPUT_TOKENS"], "65536")
        self.assertNotIn("DUNGENESS_BOUNDED_REQUESTS", compose["services"]["main"]["environment"])

    def test_run_networks_cannot_supply_a_host_bridge_or_packet_bypass(self):
        compose = yaml.safe_load(compiler.build_compose(
            "network-boundary", {}, {"model": {"requests": 5}},
            problem_service={"context": "problem", "sha256": "a" * 64}))
        for name in ("agent_internal", "problem_internal"):
            network = compose["networks"][name]
            self.assertTrue(network["internal"])
            self.assertNotIn("name", network)
            self.assertNotIn("external", network)
            for family in ("ipv4", "ipv6"):
                self.assertEqual(network["driver_opts"][
                    f"com.docker.network.bridge.gateway_mode_{family}"], "isolated")
        main = compose["services"]["main"]
        self.assertIn("NET_RAW", main["cap_drop"])
        self.assertIn("NET_ADMIN", main["cap_drop"])
        self.assertIn("no-new-privileges:true", main["security_opt"])
        gateway = compose["services"]["gateway"]
        self.assertEqual(gateway["sysctls"]["net.ipv4.ip_forward"], "0")
        self.assertEqual(gateway["sysctls"]["net.ipv6.conf.all.forwarding"], "0")
        self.assertIn("external_egress", gateway["networks"])
        for name, service in compose["services"].items():
            self.assertNotIn("ports", service)
            if name != "gateway":
                self.assertNotIn("external_egress", service["networks"])

    def test_claude_subscription_mounts_only_token_and_expiry_in_gateway(self):
        compose = yaml.safe_load(compiler.build_compose(
            "claude-session", {"historical_cutoff": {"end_published_date": "2026-05-28T23:59:59Z"},
                "search": {"max_results": 25}},
            {"web": {"searches": 0, "fetches": 0}, "model": {"requests": 10}},
            provider="claude-subscription", command_policy={"models": [{
                "provider":"claude-subscription", "request_model":"claude-test",
                "base_url":"http://gateway:8080/model/claude-subscription"}]}, max_usd=1))
        gateway = compose["services"]["gateway"]
        self.assertEqual(set(gateway["x-dungeness-credential-env"]),
                         {"CLAUDE_ACCESS_TOKEN", "CLAUDE_ACCESS_TOKEN_EXPIRES_AT"})
        for key in gateway["x-dungeness-credential-env"]:
            self.assertNotIn(key, gateway["environment"])
        main = compose["services"]["main"]
        self.assertNotIn("credentials.json", json.dumps(main))
        self.assertNotIn("ANTHROPIC_API_KEY", main["environment"])
        self.assertEqual(main["environment"]["ANTHROPIC_AUTH_TOKEN"], "testbed")
        self.assertEqual(main["environment"]["ANTHROPIC_BASE_URL"],
                         "http://gateway:8080/model/claude-subscription")

    def test_all_api_credentials_use_gateway_only_readonly_mount(self):
        providers = ("openai", "anthropic", "openrouter")
        compose = yaml.safe_load(compiler.build_compose(
            "credential-boundary",
            {"historical_cutoff": {"end_published_date": "2026-05-28T23:59:59Z"},
             "search": {"max_results": 25}},
            {"web": {"searches": 1, "fetches": 1}, "model": {"requests": 10}},
            provider="openai", command_policy={"models": [
                {"provider": p, "request_model": "fixture", "base_url": f"http://gateway:8080/model/{p}/v1"}
                for p in providers]}, max_usd=1))
        gateway = compose["services"]["gateway"]
        for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "OPENROUTER_API_KEY"):
            self.assertNotIn(key, gateway["environment"])
            self.assertIn(key, gateway["x-dungeness-credential-env"])
        mounts = [m for m in gateway["volumes"] if isinstance(m, dict)]
        self.assertEqual(len(mounts), 1)
        self.assertTrue(mounts[0]["read_only"])
        self.assertFalse(mounts[0]["bind"]["create_host_path"])
        main = compose["services"]["main"]
        self.assertEqual(main["environment"]["OPENAI_API_KEY"], "testbed")
        self.assertEqual(main["environment"]["ANTHROPIC_API_KEY"], "testbed")
        self.assertNotIn("credentials.json", json.dumps(main))
        self.assertNotIn("DUNGENESS_CREDENTIALS_FILE", json.dumps(main))
        self.assertNotIn("DUNGENESS_KNOWLEDGE_BASE", json.dumps(compose))

    def test_chatgpt_gateway_can_read_private_host_credentials(self):
        with patch.object(compiler.os, "geteuid", return_value=1234), patch.object(
                compiler.os, "getegid", return_value=5678):
            compose = yaml.safe_load(compiler.build_compose(
                "private-chatgpt",
                {"historical_cutoff": {"end_published_date": "2026-05-28T23:59:59Z"},
                 "search": {"max_results": 25}},
                {"web": {"searches": 0, "fetches": 0},
                 "model": {"requests": 10, "total_tokens": 10000}},
                provider="openai", max_usd=1,
                command_policy={"models": [{**MODEL,
                    "base_url": "http://gateway:8080/model/chatgpt/v1"}]}))
        gateway_service = compose["services"]["gateway"]
        self.assertTrue(gateway_service["read_only"])
        self.assertEqual(gateway_service["cap_drop"], ["ALL"])
        self.assertIn("no-new-privileges:true", gateway_service["security_opt"])
        self.assertEqual(gateway_service["mem_limit"], "1g")
        self.assertEqual(gateway_service["pids_limit"], 128)
        self.assertTrue(any(mount.startswith("/tmp:") for mount in gateway_service["tmpfs"]))
        self.assertEqual(gateway_service["environment"]["DUNGENESS_REQUIRE_MODEL_ALLOWLIST"], "1")
        self.assertNotIn("read_only", compose["services"]["main"])
        self.assertEqual(gateway_service["user"], "1234:5678")
        self.assertIn("${DUNGENESS_CODEX_AUTH_FILE:?ChatGPT access required}:"
                      "/run/dungeness/auth.json:ro", gateway_service["volumes"])
        self.assertNotIn("auth.json", json.dumps(compose["services"]["main"]))
        self.assertEqual(compose["services"]["main"]["networks"], ["agent_internal"])


    def test_adapter_uses_real_harbor_exec_result_contract(self):
        import asyncio
        from unittest.mock import AsyncMock
        try:
            from harbor.environments.base import ExecResult
        except ImportError:
            self.skipTest("Harbor is required for the adapter API contract test.")
        adapter = load("command_agent_contract", "adapters/harbor/command_agent.py")
        with tempfile.TemporaryDirectory() as temp:
            agent = adapter.CommandAgent(
                logs_dir=Path(temp), model_name="test-model",
                execution={"entrypoint": ["python3", "agent.py"]})
            environment = AsyncMock()
            with patch.object(agent, "exec_as_agent", new=AsyncMock(
                    return_value=ExecResult(return_code=0, stdout="ok"))):
                asyncio.run(agent.install(environment))
                asyncio.run(agent.run("test task", environment, None))
            self.assertEqual((Path(temp) / "harness-output-0.txt").read_text(), "ok\n")
            with patch.object(agent, "exec_as_agent", new=AsyncMock(
                    return_value=ExecResult(return_code=2, stderr="bad command"))):
                with self.assertRaisesRegex(RuntimeError, "status 2"):
                    asyncio.run(agent.run("test task", environment, None))

    def test_generic_job_has_no_codex_identity_and_cannot_import_solver_host_code(self):
        agent = {"execution": {"interface": "dungeness-command-v1", "entrypoint": ["python3", "harness.py"]},
                 "model": MODEL, "model_access": {"models": [MODEL]}}
        job = yaml.safe_load(compiler.build_harbor_job("sample", agent, ROOT))
        self.assertEqual(job["agents"][0]["import_path"], "command_agent:CommandAgent")
        self.assertEqual(job["agents"][0]["env"], {})
        self.assertNotIn("name", job["agents"][0])
        with self.assertRaises(ValueError):
            compiler.build_harbor_job("sample", {**agent, "harbor": {"import_path": "evil:Host"}}, ROOT)
        with self.assertRaises(ValueError):
            compiler.build_harbor_job("sample", agent, ROOT, continuation={"max_resumes": 1})

    def test_child_processes_run_inside_command_lifecycle(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            # Two independent subprocess workers write separate candidates.
            script = root / "harness.py"
            script.write_text(
                "import subprocess,sys\n"
                "workers=[subprocess.Popen([sys.executable,'-c',"
                "'from pathlib import Path; import sys; Path(sys.argv[1]).write_text(sys.argv[2])',"
                "f'candidate-{i}',str(i)]) for i in range(2)]"
                "\nfor worker in workers: assert worker.wait()==0\n")
            task = root / "task.json"
            task.write_text(json.dumps({"workspace": temp, "execution": {
                "entrypoint": [sys.executable, str(script)]}}))
            subprocess.run([sys.executable, str(ROOT / "adapters/harbor/command_runner.py"), str(task)],
                           check=True, timeout=10)
            self.assertEqual((root / "candidate-0").read_text(), "0")
            self.assertEqual((root / "candidate-1").read_text(), "1")

    def test_provider_protocol_controls_base_url_not_harness_name(self):
        anthropic = {"provider": "anthropic", "request_model": "claude-opus-5",
                     "upstream_id": "anthropic/claude-opus-5",
                     "api": "anthropic-messages", "name_format": "request"}
        resolved = compiler.command_models({"model": MODEL, "model_access": {"models": [MODEL, anthropic]}})
        self.assertEqual(resolved[0]["base_url"], "http://gateway:8080/model/chatgpt/v1")
        self.assertEqual(resolved[1]["base_url"], "http://gateway:8080/model/anthropic")

    def test_concurrent_admission_reserves_one_shared_budget(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {
            "MAX_SEARCHES": "0", "MAX_FETCHES": "0", "MAX_MODEL_REQUESTS": "20",
            "MAX_MODEL_TOKENS": "10000", "MAX_MODEL_USD": "1",
            "DUNGENESS_MAX_PARALLEL_REQUESTS": "8", "DUNGENESS_REQUEST_RESERVATION_USD": ".5",
        }):
            ledger = usage.UsageLedger("test", Path(temp))
            barrier = threading.Barrier(8)
            def start(i):
                barrier.wait()
                try:
                    ledger.admit_model(str(i))
                    return str(i)
                except usage.BudgetExceeded:
                    return None
            with ThreadPoolExecutor(8) as pool:
                accepted = [x for x in pool.map(start, range(8)) if x is not None]
            self.assertEqual(len(accepted), 2)
            self.assertEqual(ledger.counts["model_requests"], 2)
            ledger.add_model_usage(billed_tokens=10, normalized_usd=.25)
            ledger.finish_model(accepted[0], accounted=True)
            ledger.admit_model("next")
            self.assertEqual(ledger.model_inflight["next"], .25)
            ledger.finish_model("next", accounted=False)
            with self.assertRaises(usage.BudgetExceeded):
                ledger.admit_model("after-missing-usage")

    def test_normal_exit_cleans_background_workers_and_resume_selects_hook(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            script = root / "harness.py"
            # The background process inherits stdout. Without process-group
            # cleanup, communicate() cannot see EOF and hits the timeout.
            script.write_text("import subprocess,sys\n"
                              "subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'])\n")
            task = root / "task.json"
            execution = {"entrypoint": [sys.executable, str(script)],
                         "resume_entrypoint": [sys.executable, "-c", "print('resumed')"]}
            task.write_text(json.dumps({"workspace": temp, "execution": execution}))
            subprocess.run([sys.executable, str(ROOT / "adapters/harbor/command_runner.py"), str(task)],
                           check=True, capture_output=True, timeout=5)
            task.write_text(json.dumps({"workspace": temp, "execution": execution, "resume": True}))
            result = subprocess.run(
                [sys.executable, str(ROOT / "adapters/harbor/command_runner.py"), str(task)],
                check=True, capture_output=True, text=True, timeout=5)
            self.assertEqual(result.stdout.strip(), "resumed")

    def test_gateway_reads_chatgpt_auth_from_trusted_file(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "auth.json"
            path.write_text(json.dumps({"tokens": {
                "access_token": "synthetic-private-token", "account_id": "synthetic-account"}}))
            with patch.dict(os.environ, {"DUNGENESS_CHATGPT_AUTH_FILE": str(path)}):
                headers = models.provider_auth_headers("openai-chatgpt")
            self.assertEqual(headers, {"authorization": "Bearer synthetic-private-token",
                                      "chatgpt-account-id": "synthetic-account"})


if __name__ == "__main__":
    unittest.main()

class ConfiguredProviderCompilerTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.dict(compiler.CONFIGURED_PROVIDERS, CONFIGURED_FIXTURES))

    def test_installed_subscription_credentials_are_gateway_only(self):
        for name in ('grok-subscription', 'minimax-subscription'):
            profile = compiler.CONFIGURED_PROVIDERS[name]
            model = {'provider': name, 'request_model': next(iter(profile['models'])),
                     'base_url': f'http://gateway:8080/model/{name}/v1'}
            compose = yaml.safe_load(compiler.build_compose(
                'local-plan', {'historical_cutoff': {}},
                {'web': {'searches': 0, 'fetches': 0}, 'model': {'requests': 10, 'total_tokens': 10000}},
                provider=name, max_usd=3, command_policy={'models': [model]}))
            gateway = compose['services']['gateway']
            key = profile['credential_env']
            self.assertEqual(gateway['x-dungeness-credential-env'][key], 'TESTBED_' + key)
            self.assertNotIn(key, gateway['environment'])
            self.assertNotIn(key, json.dumps(compose['services']['main']))
            self.assertTrue(gateway['read_only'])

    def test_configured_credentials_only_reach_gateway(self):
        model = {'provider': 'example-session', 'request_model': 'example-model',
                 'base_url': 'http://gateway:8080/model/example-session/v1'}
        compose = yaml.safe_load(compiler.build_compose(
            'configured-run', {'historical_cutoff': {'end_published_date': '2026-05-28T23:59:59Z'},
                         'search': {'max_results': 25}},
            {'web': {'searches': 0, 'fetches': 0}, 'model': {'requests': 10, 'total_tokens': 10000}},
            provider='example-session', max_usd=3, command_policy={'models': [model]}))
        env = compose['services']['gateway']['environment']
        sources = compose['services']['gateway']['x-dungeness-credential-env']
        self.assertEqual(sources, {
            'EXAMPLE_SESSION_TOKEN': 'TESTBED_EXAMPLE_SESSION_TOKEN',
            'EXAMPLE_SESSION_TOKEN_EXPIRES_AT': 'TESTBED_EXAMPLE_SESSION_TOKEN_EXPIRES_AT'})
        self.assertNotIn('EXAMPLE_SESSION_TOKEN', env)
        self.assertNotIn('EXAMPLE_SESSION_TOKEN_EXPIRES_AT', env)
        self.assertNotIn('EXAMPLE_API_KEY', env)
        self.assertNotIn('OPENAI_API_KEY', env)
        main = json.dumps(compose['services']['main'])
        self.assertNotIn('EXAMPLE_SESSION_TOKEN', main)
        self.assertIn('testbed', main)
