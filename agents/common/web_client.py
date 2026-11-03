#!/usr/bin/env python3
"""Command-line client for gateway-mediated web search and page retrieval."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def main() -> None:
    # This agent-side client contains no provider key or policy logic. Docker DNS
    # resolves the fixed gateway service on the run's internal-only network.
    parser = argparse.ArgumentParser(prog="web")
    subparsers = parser.add_subparsers(dest="operation", required=True)
    for operation, argument in (("search", "query"), ("fetch", "url")):
        command = subparsers.add_parser(operation)
        command.add_argument(argument)
    args = parser.parse_args()

    field = "query" if args.operation == "search" else "url"
    payload = json.dumps({field: getattr(args, field)}).encode()
    base_url = os.environ.get("TESTBED_GATEWAY_URL", "http://gateway:8080")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/web/{args.operation}",
        data=payload,
        headers={"content-type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            sys.stdout.buffer.write(response.read())
            sys.stdout.write("\n")
    except urllib.error.HTTPError as error:
        sys.stderr.buffer.write(error.read())
        sys.stderr.write("\n")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
