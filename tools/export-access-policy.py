#!/usr/bin/env python3
"""Export derived public policy; no login, secrets or network access."""
import argparse
import json
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services/gateway"))
from access_selection import canonical, export_policy
from model_access import DEFAULT_MODEL_ACCESS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exclude", action="append", default=[])
    args = parser.parse_args()
    registry = {name: config for name, config in DEFAULT_MODEL_ACCESS.items() if name not in args.exclude}
    prices = yaml.safe_load((ROOT / "services/gateway/pricing.yaml").read_text())
    print(canonical(export_policy(registry, prices)).decode())


if __name__ == "__main__":
    main()
