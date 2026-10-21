"""Synthetic operator profiles, installed only for the duration of a test."""
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from provider_profiles import PROFILES, load_profiles

FIXTURES = load_profiles(Path(__file__).resolve().parents[3] / "tests/fixtures/provider-registry.json")


@contextmanager
def configured_profiles():
    from gateway_models import MODEL_PROVIDERS, configured_provider_config
    configurations = {name: configured_provider_config(name, profile) for name, profile in FIXTURES.items()}
    with patch.dict(PROFILES, FIXTURES), patch.dict(MODEL_PROVIDERS, configurations):
        yield
