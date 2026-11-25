"""Trusted route data drives endpoints and recipes without Python edits."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from access_config import CONFIG_PATH, load_access_routes
from model_access import MODEL_ACCESS, credential_requirements, validate_upstream_settings, upstream_model
from gateway_auth import authentication_headers


class AccessConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.path = self.root / "model-access.json"
        self.document = json.loads(CONFIG_PATH.read_text())

    def load(self, document):
        self.path.write_text(json.dumps(document))
        return load_access_routes(self.path)

    def test_endpoint_and_authentication_come_from_configuration(self):
        config = self.document["access_routes"]["openai"]
        config["upstream_default"] = "https://api.example.invalid/v2"
        config["authentication"]["sources"][0]["headers"] = {
            "x-api-key": {"env": "EXAMPLE_TOKEN"}}
        routes = self.load(self.document)
        with patch.dict(MODEL_ACCESS, routes, clear=True):
            self.assertEqual(credential_requirements(["openai"])["environment"],
                             {"EXAMPLE_TOKEN": "TESTBED_EXAMPLE_TOKEN"})
            validate_upstream_settings({"OPENAI_UPSTREAM_BASE_URL": "https://api.example.invalid/v2"})
            with self.assertRaises(ValueError):
                validate_upstream_settings({"OPENAI_UPSTREAM_BASE_URL": "https://api.openai.com/v1"})
        with patch.dict("os.environ", {"EXAMPLE_TOKEN": "synthetic-token"}, clear=True):
            self.assertEqual(authentication_headers(routes["openai"]["authentication"]),
                             {"x-api-key": "synthetic-token"})

    def test_invalid_configuration_fails_closed(self):
        changes = [
            ("upstream_default", "http://api.example.invalid/v1"),
            ("upstream_default", "https://private-sentinel@api.example.invalid/v1"),
            ("upstream_default", "https://api.example.invalid/v1?key=private-sentinel"),
            ("upstream_default", "https://api.example.invalid/v1#fragment"),
            ("routes", ["account/delete"]),
            ("routes", "responses"),
            ("usage_parser", "arbitrary-python-import"),
            ("billed", "false"),
            ("auth", "passthrough"),
            ("gateway_route", "chatgpt"),
            ("upstream_env", "ANTHROPIC_UPSTREAM_BASE_URL"),
            ("passthrough", ["host"]),
            ("authentication", {"sources": []}),
            ("authentication", {"sources": [{"headers": {
                "host": {"env": "EXAMPLE_TOKEN"}}}]}),
            ("authentication", {"sources": [{"headers": {
                "authorization": {"env": "EXAMPLE_TOKEN", "literal": "private-sentinel"}}}]}),
            ("models", {"alias": {"upstream": "../account", "catalog": "example/model"}}),
            ("models", {"alias": {"upstream": "model"}}),
            ("models", []),
            ("model_header", "host"),
            ("model_header", "openai-beta"),
        ]
        for key, value in changes:
            with self.subTest(key=key, value=value):
                document = copy.deepcopy(self.document)
                document["access_routes"]["openai"][key] = value
                with self.assertRaises(ValueError) as error:
                    self.load(document)
                self.assertNotIn("private-sentinel", str(error.exception))

    def test_model_mapping_and_alias_are_configuration(self):
        config = copy.deepcopy(self.document["access_routes"]["openai"])
        config.update(gateway_route="example", models={
            "public-name": {"upstream": "upstream-name", "catalog": "example/reference"}},
            model_header="x-selected-model")
        routes = self.load({"schema_version": 1, "access_routes": {"example-api": config}})
        self.assertEqual(upstream_model(routes["example-api"], "public-name"), "upstream-name")
        with self.assertRaises(ValueError):
            upstream_model(routes["example-api"], "unlisted-model")
        with patch.dict(MODEL_ACCESS, routes, clear=True):
            from model_access import gateway_base_url
            self.assertEqual(gateway_base_url("example-api", "openai-chat"),
                             "http://gateway:8080/model/example/v1")

    def test_alias_cannot_shadow_another_route_id(self):
        self.document["access_routes"]["openai"]["gateway_route"] = "other"
        self.document["access_routes"]["anthropic"]["gateway_route"] = "openai"
        with self.assertRaises(ValueError):
            self.load(self.document)

    def test_missing_or_unsupported_configuration_has_no_embedded_fallback(self):
        with self.assertRaises(FileNotFoundError):
            load_access_routes(self.path)
        for document in ({}, {**self.document, "schema_version": 2},
                         {**self.document, "extra": True}):
            with self.assertRaises(ValueError):
                self.load(document)
