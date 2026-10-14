#!/usr/bin/env python3
"""Use the run-scoped Dungeness knowledge-base sidecar."""

from __future__ import annotations

import argparse
import json
import os
import re
from typing import Any, Sequence
import urllib.error
import urllib.request


DEFAULT_URL = "http://knowledge-base:8078"
DEFAULT_OPERATIONS = (
    "status",
    "list",
    "search",
    "read",
    "neighbors",
    "inspire",
)
REQUEST_TIMEOUT_SECONDS = 35


class KnowledgeBaseError(ValueError):
    """A user-facing knowledge-base client error."""


def request_json(
    path: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    base = os.environ.get("DUNGENESS_KNOWLEDGE_BASE_URL", DEFAULT_URL).rstrip("/")
    data = None
    method = "GET"
    if payload is not None:
        data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        method = "POST"
    request = urllib.request.Request(
        base + path,
        data=data,
        headers={"content-type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:
            value = json.loads(response.read())
    except urllib.error.HTTPError as error:
        try:
            value = json.loads(error.read())
        except (json.JSONDecodeError, UnicodeError):
            value = {}
        message = value.get("error") if isinstance(value, dict) else None
        raise KnowledgeBaseError(
            str(message or f"sidecar returned HTTP {error.code}")
        ) from error
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as error:
        raise KnowledgeBaseError(f"sidecar request failed: {error}") from error
    if not isinstance(value, dict):
        raise KnowledgeBaseError("sidecar response must be an object")
    return value


def configured_operations() -> tuple[str, ...]:
    raw = os.environ.get("DUNGENESS_KNOWLEDGE_BASE_OPERATIONS")
    if raw is None:
        return DEFAULT_OPERATIONS
    operations = tuple(
        operation.strip()
        for operation in raw.split(",")
        if operation.strip()
    )
    if (
        not operations
        or len(set(operations)) != len(operations)
        or set(operations) - set(DEFAULT_OPERATIONS)
    ):
        raise KnowledgeBaseError(
            "invalid DUNGENESS_KNOWLEDGE_BASE_OPERATIONS"
        )
    return operations


def page_range(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"([1-9][0-9]*)-([1-9][0-9]*)", value)
    if match is None:
        raise argparse.ArgumentTypeError(
            "pages must use FIRST-LAST, for example 1-5"
        )
    first, last = (int(part) for part in match.groups())
    if last < first:
        raise argparse.ArgumentTypeError(
            "the last page must not precede the first page"
        )
    return first, last


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="knowledge-base",
        description="Use the run-scoped knowledge base.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    operations = set(configured_operations())

    if "status" in operations:
        status = commands.add_parser("status")
        status.add_argument("--json", action="store_true", dest="as_json")

    if "list" in operations:
        listing = commands.add_parser("list")
        listing.add_argument("--json", action="store_true", dest="as_json")

    if "search" in operations:
        search = commands.add_parser("search")
        search.add_argument("query", nargs="+")
        search.add_argument("--max-results", "--limit", type=int, default=8)
        search.add_argument("--context-lines", type=int, default=3)
        search.add_argument("--json", action="store_true", dest="as_json")

    if "read" in operations:
        read = commands.add_parser("read")
        read.add_argument("page")
        read.add_argument(
            "--pages",
            type=page_range,
            metavar="FIRST-LAST",
            help="Render only this inclusive PDF page window.",
        )
        read.add_argument("--json", action="store_true", dest="as_json")

    if "neighbors" in operations:
        neighbors = commands.add_parser("neighbors")
        neighbors.add_argument("node")
        neighbors.add_argument("--json", action="store_true", dest="as_json")

    if "inspire" in operations:
        inspire = commands.add_parser("inspire")
        inspire.add_argument("--search-id", required=True)
        inspire.add_argument(
            "--passage",
            action="append",
            required=True,
            help="Exact returned passage as relative/page.md:L10-L18; repeatable.",
        )
        inspire.add_argument("--takeaway", required=True)
        inspire.add_argument("--planned-change", required=True)
        inspire.add_argument("--json", action="store_true", dest="as_json")
    return parser


def render(args: argparse.Namespace, document: dict[str, Any]) -> None:
    if args.as_json:
        print(json.dumps(document, indent=2, sort_keys=True))
        return
    if args.command == "status":
        print(f"source: {document.get('source_ref') or 'unversioned'}")
        print(f"entrypoint: {document.get('entrypoint', 'index.md')}")
        print(f"pages: {document.get('pages', 0)}")
        feedback = document.get("behavior_feedback") or {}
        print(f"behavior feedback: {feedback.get('mode', 'off')}")
    elif args.command == "list":
        for page in document.get("pages", []):
            print(f"{page['path']}\t{page['title']}")
    elif args.command == "search":
        print(f"search id: {document.get('search_id', '')}")
        results = document.get("results", [])
        if not results:
            print("no matches")
        for result in results:
            marker = "" if result.get("qualifying_source", True) else " (orientation)"
            print(
                f"[KB: {result['source']}#L{result['line_start']}"
                f"-L{result['line_end']}]{marker}"
            )
            if result.get("heading"):
                print(result["heading"])
            print(result["text"])
            print()
    elif args.command == "read":
        print(document["content"], end="" if document["content"].endswith("\n") else "\n")
    elif args.command == "neighbors":
        print(f"page: {document['page']}")
        print("depends_on: " + ", ".join(document.get("depends_on", [])))
        print("required_by: " + ", ".join(document.get("required_by", [])))
        print("links: " + ", ".join(document.get("links", [])))
    elif args.command == "inspire":
        print(
            "lookup qualified"
            if document.get("qualifying")
            else "lookup did not qualify"
        )
        print(f"lookup id: {document.get('kb_lookup_id', '')}")
        if document.get("reason"):
            print(f"reason: {document['reason']}")
        sources = document.get("qualifying_sources") or []
        if not document.get("qualifying") and sources:
            print("qualifying sources: " + ", ".join(sources))


def parse_passage(value: str) -> dict[str, Any]:
    match = re.fullmatch(r"([^:\s]+\.md):L([1-9][0-9]*)-L([1-9][0-9]*)", value)
    if match is None:
        raise KnowledgeBaseError(
            "passage must use relative/page.md:L10-L18"
        )
    return {
        "source": match.group(1),
        "line_start": int(match.group(2)),
        "line_end": int(match.group(3)),
    }


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "status":
            document = request_json("/v1/status")
        elif args.command == "list":
            document = request_json("/v1/pages")
        elif args.command == "search":
            document = request_json(
                "/v1/search",
                {
                    "query": " ".join(args.query),
                    "max_results": args.max_results,
                    "context_lines": args.context_lines,
                },
            )
        elif args.command == "read":
            payload: dict[str, Any] = {"page": args.page}
            if args.pages is not None:
                payload["first_page"], payload["last_page"] = args.pages
            document = request_json("/v1/read", payload)
        elif args.command == "neighbors":
            document = request_json("/v1/neighbors", {"node": args.node})
        elif args.command == "inspire":
            document = request_json(
                "/v1/inspire",
                {
                    "search_id": args.search_id,
                    "passages": [
                        parse_passage(value) for value in args.passage
                    ],
                    "takeaway": args.takeaway,
                    "planned_change": args.planned_change,
                },
            )
        else:
            raise KnowledgeBaseError(f"unknown command: {args.command}")
        render(args, document)
    except (KnowledgeBaseError, KeyError, TypeError) as error:
        parser.exit(1, f"knowledge-base: {error}\n")


if __name__ == "__main__":
    main()
