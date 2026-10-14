#!/usr/bin/env python3
"""Serve one immutable, run-scoped Dungeness knowledge base."""

from __future__ import annotations

from datetime import datetime, timezone
import fcntl
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import threading
from typing import Any
import urllib.error
import urllib.request
import uuid

import yaml


PORT = 8078
DEFAULT_ROOT = "/app/content"
RUNTIME_METADATA = ".dungeness-knowledge-base.json"
MAX_QUERY_LENGTH = 4096
MAX_PAGE_BYTES = 256 * 1024
MAX_PDF_BYTES = 16 * 1024 * 1024
MAX_RENDERED_BYTES = 2 * 1024 * 1024
MAX_PDF_PAGE_WINDOW = 20
MAX_BODY_BYTES = 1024 * 1024
MAX_QUERY_TERMS = 20
DEFAULT_MAX_RESULTS = 8
DEFAULT_CONTEXT_LINES = 3
DEFAULT_MAX_PASSAGE_CHARACTERS = 1600
DEFAULT_MAX_TOTAL_RESULT_CHARACTERS = 8000
EVENT_SCHEMA_VERSION = 1
EVENT_TOKEN_FILENAME = ".event-token"
DEFAULT_EVENT_URL = "http://gateway:8080/internal/events"
DEFAULT_OPERATIONS = (
    "status",
    "list",
    "search",
    "read",
    "neighbors",
    "inspire",
)
READABLE_SUFFIXES = frozenset(
    {
        ".bbl",
        ".bib",
        ".json",
        ".md",
        ".pdf",
        ".tex",
        ".txt",
        ".yaml",
        ".yml",
    }
)
TEXT_SUFFIXES = READABLE_SUFFIXES - {".pdf"}


class KnowledgeBaseError(ValueError):
    """A bounded, user-facing request error."""


class KnowledgeBaseAccessError(KnowledgeBaseError):
    """The active manifest does not expose the requested operation."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def append_jsonl_locked(path: Path, record: dict[str, Any]) -> None:
    encoded = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    with path.open("a+", encoding="utf-8") as output:
        try:
            path.chmod(0o666)
        except OSError:
            pass
        fcntl.flock(output.fileno(), fcntl.LOCK_EX)
        try:
            event_id = record.get("event_id")
            if event_id:
                event_needle = (
                    '"event_id":'
                    + json.dumps(event_id, ensure_ascii=False)
                )
                source_needle = (
                    '"source":'
                    + json.dumps(record.get("source"), ensure_ascii=False)
                )
                output.seek(0)
                for line in output:
                    if event_needle in line and source_needle in line:
                        return
            output.seek(0, os.SEEK_END)
            output.write(encoded + "\n")
            output.flush()
        finally:
            fcntl.flock(output.fileno(), fcntl.LOCK_UN)


def page_title(text: str, fallback: str) -> str:
    if text.startswith("---\n"):
        closing = text.find("\n---\n", 4)
        if closing != -1:
            for line in text[4:closing].splitlines():
                match = re.fullmatch(r"title:\s*(.+?)\s*", line)
                if match:
                    return match.group(1).strip("'\"")
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback.replace("-", " ").title()


def normalize_page(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise KnowledgeBaseError("source must be a relative document path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise KnowledgeBaseError("source must be a safe relative document path")
    if len(value) > 240:
        raise KnowledgeBaseError("source path is too long")
    if path.suffix.lower() not in READABLE_SUFFIXES:
        raise KnowledgeBaseError(
            "source must use a supported readable document format"
        )
    return path.as_posix()


def normalize_pdf_page_window(
    first_page: Any,
    last_page: Any,
) -> tuple[int, int] | None:
    if first_page is None and last_page is None:
        return None
    if (
        not isinstance(first_page, int)
        or isinstance(first_page, bool)
        or not isinstance(last_page, int)
        or isinstance(last_page, bool)
        or first_page < 1
        or last_page < first_page
    ):
        raise KnowledgeBaseError(
            "PDF page window must use positive first_page and last_page "
            "integers in ascending order"
        )
    if last_page - first_page + 1 > MAX_PDF_PAGE_WINDOW:
        raise KnowledgeBaseError(
            f"PDF page window must contain at most {MAX_PDF_PAGE_WINDOW} pages"
        )
    return first_page, last_page


def query_terms(value: str) -> list[str]:
    """Split a query into literal, whitespace-separated search terms."""
    return value.split()[:MAX_QUERY_TERMS]


def heading_before(lines: list[str], line_index: int) -> str | None:
    for index in range(line_index, -1, -1):
        line = lines[index].strip()
        if line.startswith("#"):
            return line.lstrip("#").strip() or None
    return None


class KnowledgeBaseService:
    """Immutable corpus plus run-scoped, score-attributed inspiration."""

    def __init__(
        self,
        root: Path,
        usage_dir: Path,
        run_id: str,
        research_state_url: str | None = None,
        behavior_feedback_config: dict[str, Any] | None = None,
    ):
        self.root = root.resolve()
        if not self.root.is_dir():
            raise KnowledgeBaseError(f"knowledge-base root does not exist: {root}")
        self.usage_dir = usage_dir
        self.usage_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id
        self.research_state_url = (
            research_state_url.rstrip("/") if research_state_url else None
        )
        self.lock = threading.RLock()
        self.metadata = self._load_metadata()
        self.manifest = self._load_manifest()
        self.interface = self._load_interface()
        self.pages = self._load_pages()
        self.behavior_feedback = self._parse_behavior_feedback_config(
            behavior_feedback_config or {}
        )
        self.search_log: list[dict[str, Any]] = []
        self.qualified_passages: set[tuple[str, int, int]] = set()

    def _load_metadata(self) -> dict[str, Any]:
        path = self.root / RUNTIME_METADATA
        if not path.is_file():
            return {}
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise KnowledgeBaseError("runtime metadata must be an object")
        return value

    def _load_manifest(self) -> dict[str, Any]:
        path = self.root / "knowledge-base.yaml"
        if not path.is_file():
            return {}
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise KnowledgeBaseError("knowledge-base manifest must be an object")
        return value

    def _load_interface(self) -> dict[str, Any]:
        value = self.manifest.get("interface", {})
        if not isinstance(value, dict):
            raise KnowledgeBaseError("knowledge-base interface must be an object")
        unknown = sorted(set(value) - {"mode", "operations"})
        if unknown:
            raise KnowledgeBaseError(
                "unknown knowledge-base interface fields: "
                + ", ".join(unknown)
            )
        mode = value.get("mode", "curated-corpus")
        operations = value.get("operations", list(DEFAULT_OPERATIONS))
        if not isinstance(mode, str) or not mode:
            raise KnowledgeBaseError(
                "knowledge-base interface mode must be non-empty text"
            )
        if (
            not isinstance(operations, list)
            or not operations
            or not all(isinstance(operation, str) for operation in operations)
            or len(set(operations)) != len(operations)
        ):
            raise KnowledgeBaseError(
                "knowledge-base interface operations must be a non-empty "
                "list of unique names"
            )
        unsupported = sorted(set(operations) - set(DEFAULT_OPERATIONS))
        if unsupported:
            raise KnowledgeBaseError(
                "unsupported knowledge-base operations: "
                + ", ".join(unsupported)
            )
        return {
            "mode": mode,
            "operations": tuple(operations),
        }

    def _require_operation(self, operation: str) -> None:
        if operation not in self.interface["operations"]:
            raise KnowledgeBaseAccessError(
                f"knowledge-base operation is disabled: {operation}"
            )

    def _parse_behavior_feedback_config(
        self, value: dict[str, Any]
    ) -> dict[str, Any]:
        defaults = self.manifest.get("behavior_feedback")
        if not isinstance(defaults, dict):
            defaults = {}
        retrieval = {
            "max_results_per_search": DEFAULT_MAX_RESULTS,
            "context_lines": DEFAULT_CONTEXT_LINES,
            "max_passage_characters": DEFAULT_MAX_PASSAGE_CHARACTERS,
            "max_total_result_characters": DEFAULT_MAX_TOTAL_RESULT_CHARACTERS,
        }
        if isinstance(defaults.get("retrieval"), dict):
            retrieval.update(defaults["retrieval"])
        if isinstance(value.get("retrieval"), dict):
            retrieval.update(value["retrieval"])
        qualifying_sources = defaults.get("qualifying_sources", {})
        if not isinstance(qualifying_sources, dict):
            raise KnowledgeBaseError(
                "behavior_feedback.qualifying_sources must be an object"
            )
        prefixes = qualifying_sources.get("prefixes", [])
        pages = qualifying_sources.get("pages", [])
        if (
            not isinstance(prefixes, list)
            or not all(isinstance(item, str) and item for item in prefixes)
            or not isinstance(pages, list)
            or not all(isinstance(item, str) and item for item in pages)
        ):
            raise KnowledgeBaseError(
                "qualifying source prefixes and pages must be string lists"
            )
        mode = str(value.get("mode", defaults.get("mode", "shadow")))
        if mode not in {"off", "shadow", "visible"}:
            raise KnowledgeBaseError(
                "behavior feedback mode must be off, shadow, or visible"
            )
        return {
            "enabled": bool(value.get("enabled", defaults.get("enabled", True))),
            "mode": mode,
            "retrieval": retrieval,
            "qualifying_source_prefixes": tuple(prefixes),
            "qualifying_source_pages": frozenset(pages),
        }

    def _path(self, page: str) -> Path:
        relative = normalize_page(page)
        if relative not in self.pages:
            raise KnowledgeBaseError(
                f"knowledge-base document does not exist: {relative}"
            )
        path = self.root.joinpath(*PurePosixPath(relative).parts)
        if path.is_symlink() or not path.is_file():
            raise KnowledgeBaseError(
                f"knowledge-base document does not exist: {relative}"
            )
        resolved = path.resolve()
        if not resolved.is_relative_to(self.root):
            raise KnowledgeBaseError(
                f"knowledge-base document escapes root: {relative}"
            )
        return resolved

    def _load_pages(self) -> dict[str, dict[str, Any]]:
        pages: dict[str, dict[str, Any]] = {}
        for path in sorted(self.root.rglob("*")):
            if path.is_symlink() or not path.is_file():
                continue
            resolved = path.resolve()
            if not resolved.is_relative_to(self.root):
                continue
            relative = resolved.relative_to(self.root).as_posix()
            if (
                relative in {"knowledge-base.yaml", RUNTIME_METADATA}
                or resolved.suffix.lower() not in READABLE_SUFFIXES
            ):
                continue
            raw = resolved.read_bytes()
            if resolved.suffix.lower() in TEXT_SUFFIXES:
                text = raw.decode("utf-8")
                title = page_title(text, resolved.stem)
            else:
                title = (
                    str(self.manifest.get("title"))
                    if relative == self.manifest.get("entrypoint")
                    and isinstance(self.manifest.get("title"), str)
                    else resolved.stem.replace("-", " ").title()
                )
            pages[relative] = {
                "path": relative,
                "title": title,
                "format": resolved.suffix.lower().removeprefix("."),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
            }
        if not pages:
            raise KnowledgeBaseError(
                "knowledge base contains no readable documents"
            )
        return pages

    def _emit_usage_event(
        self,
        kind: str,
        data: dict[str, Any],
        *,
        event_id: str,
        observed_at: str | None = None,
    ) -> None:
        observed = observed_at or utc_now()
        document = {
            "run_id": self.run_id,
            "source": "knowledge-base",
            "kind": kind,
            "observed_at": observed,
            "event_id": event_id,
            "data": data,
        }
        try:
            token = (
                self.usage_dir / EVENT_TOKEN_FILENAME
            ).read_text(encoding="utf-8").strip()
            if not token:
                raise OSError("empty gateway event token")
            request = urllib.request.Request(
                os.environ.get("DUNGENESS_EVENT_URL", DEFAULT_EVENT_URL),
                data=json.dumps(document, separators=(",", ":")).encode("utf-8"),
                headers={
                    "content-type": "application/json",
                    "x-dungeness-event-token": token,
                },
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=2):
                return
        except (OSError, urllib.error.URLError, TypeError, ValueError):
            pass

        record: dict[str, Any] = {
            "schema_version": EVENT_SCHEMA_VERSION,
            "run_id": self.run_id,
            "sequence": None,
            "source": "knowledge-base",
            "kind": kind,
            "observed_at": observed,
            "recorded_at": utc_now(),
            "event_id": event_id,
            "data": data,
        }
        try:
            append_jsonl_locked(self.usage_dir / "events.jsonl", record)
        except OSError:
            pass

    def _append_event(self, action: str, **fields: Any) -> str:
        event_id = f"knowledge-base:{uuid.uuid4().hex}"
        self._emit_usage_event(
            "knowledge_base.request",
            {"action": action, **fields},
            event_id=event_id,
        )
        return event_id

    def _post_json(
        self,
        base: str | None,
        path: str,
        document: dict[str, Any],
        timeout: int = 5,
    ) -> dict[str, Any] | None:
        if base is None:
            return None
        request = urllib.request.Request(
            base + path,
            data=json.dumps(document, separators=(",", ":")).encode("utf-8"),
            headers={"content-type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                value = json.loads(response.read())
        except (OSError, urllib.error.URLError, json.JSONDecodeError):
            return None
        return value if isinstance(value, dict) else None

    def status(self) -> dict[str, Any]:
        self._require_operation("status")
        with self.lock:
            event_id = self._append_event("status", matches=len(self.pages))
        endpoints = {
            "status": "GET /v1/status",
            "list": "GET /v1/pages",
            "search": "POST /v1/search",
            "read": "POST /v1/read",
            "neighbors": "POST /v1/neighbors",
            "inspire": "POST /v1/inspire",
        }
        return {
            "schema_version": 3,
            "event_id": event_id,
            "available": True,
            "source_ref": self.metadata.get("source_ref"),
            "entrypoint": self.metadata.get("entrypoint", "index.md"),
            "selected_layers": self.metadata.get("selected_layers", []),
            "source_sha256": self.metadata.get("source_sha256"),
            "content_sha256": self.metadata.get("injected_sha256"),
            "pages": len(self.pages),
            "behavior_feedback": {
                "enabled": self.behavior_feedback["enabled"],
                "mode": self.behavior_feedback["mode"],
            },
            "interface": {
                "transport": "HTTP JSON",
                "mode": self.interface["mode"],
                "operations": list(self.interface["operations"]),
                "endpoints": {
                    operation: endpoint
                    for operation, endpoint in endpoints.items()
                    if operation in self.interface["operations"]
                },
            },
        }

    def list_pages(self) -> dict[str, Any]:
        self._require_operation("list")
        with self.lock:
            event_id = self._append_event("list", matches=len(self.pages))
        return {"event_id": event_id, "pages": list(self.pages.values())}

    def _rg_candidates(self, terms: list[str]) -> dict[str, set[int]]:
        command = [
            "rg", "--json", "--line-number", "--ignore-case",
            "--fixed-strings", "--glob", "*.md",
        ]
        for term in terms:
            command.extend(["-e", term])
        command.extend(["--", str(self.root)])
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        if result.returncode not in {0, 1}:
            raise KnowledgeBaseError(
                (result.stderr.strip() or "ripgrep search failed")[:500]
            )
        candidates: dict[str, set[int]] = {}
        for raw_line in result.stdout.splitlines():
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            if record.get("type") != "match":
                continue
            data = record.get("data")
            if not isinstance(data, dict):
                continue
            absolute = (data.get("path") or {}).get("text")
            line_number = data.get("line_number")
            if not isinstance(absolute, str) or not isinstance(line_number, int):
                continue
            path = Path(absolute).resolve()
            if not path.is_relative_to(self.root):
                continue
            relative = path.relative_to(self.root).as_posix()
            candidates.setdefault(relative, set()).add(line_number)
        return candidates

    def _qualifying_source(self, source: str) -> bool:
        """Can a passage from this page carry a qualifying inspiration lookup?"""

        prefixes = self.behavior_feedback["qualifying_source_prefixes"]
        pages = self.behavior_feedback["qualifying_source_pages"]
        if not prefixes and not pages:
            return True
        return source in pages or any(
            source.startswith(prefix) for prefix in prefixes
        )

    def search(
        self,
        query: Any,
        max_results: Any = DEFAULT_MAX_RESULTS,
        context_lines: Any = DEFAULT_CONTEXT_LINES,
    ) -> dict[str, Any]:
        """Case-insensitive literal term search: any term matches, best first.

        Deliberately dumb. Every term is a literal substring, terms are OR'd,
        and ranking is "how many distinct terms this passage contains", with
        qualifying sources breaking ties ahead of orientation pages. A query
        that names several things still finds the pages that name some of them,
        which is what a corpus reader actually wants.
        """

        self._require_operation("search")
        if not isinstance(query, str) or not 1 <= len(query.strip()) <= MAX_QUERY_LENGTH:
            raise KnowledgeBaseError(
                f"query must contain 1 to {MAX_QUERY_LENGTH} characters"
            )
        if (
            not isinstance(max_results, int)
            or isinstance(max_results, bool)
            or not 1 <= max_results <= 100
        ):
            raise KnowledgeBaseError("max_results must be between 1 and 100")
        if (
            not isinstance(context_lines, int)
            or isinstance(context_lines, bool)
            or not 0 <= context_lines <= 20
        ):
            raise KnowledgeBaseError("context_lines must be between 0 and 20")
        terms = query_terms(query)
        if not terms:
            raise KnowledgeBaseError("query must contain at least one term")
        folded_terms = [term.casefold() for term in terms]
        retrieval = self.behavior_feedback["retrieval"]
        passage_limit = int(retrieval["max_passage_characters"])
        ranked: list[dict[str, Any]] = []
        for source, line_numbers in self._rg_candidates(terms).items():
            lines = self._path(source).read_text(encoding="utf-8").splitlines()
            windows: list[list[int]] = []
            for line_number in sorted(line_numbers):
                start = max(1, line_number - context_lines)
                end = min(len(lines), line_number + context_lines)
                if windows and start <= windows[-1][1] + 1:
                    windows[-1][1] = max(end, windows[-1][1])
                else:
                    windows.append([start, end])
            for start, end in windows:
                text = "\n".join(lines[start - 1 : end]).strip()
                lowered = text.casefold()
                ranked.append(
                    {
                        "source": source,
                        "line_start": start,
                        "line_end": end,
                        "heading": heading_before(lines, start - 1),
                        "text": text[:passage_limit],
                        "match_terms": sorted(
                            {
                                term
                                for term, folded in zip(terms, folded_terms)
                                if folded in lowered
                            }
                        ),
                        # Say outright whether this passage can carry a
                        # qualifying lookup, instead of making the agent guess.
                        "qualifying_source": self._qualifying_source(source),
                    }
                )
        # Equally good matches are ordered so the pages that can actually earn a
        # qualifying lookup are not crowded out by orientation pages that repeat
        # the same vocabulary.
        ranked.sort(
            key=lambda item: (
                -len(item["match_terms"]),
                not item["qualifying_source"],
                item["source"],
                item["line_start"],
            )
        )
        results: list[dict[str, Any]] = []
        total_characters = 0
        total_limit = int(retrieval["max_total_result_characters"])
        for item in ranked:
            if total_characters + len(item["text"]) > total_limit:
                break
            results.append(item)
            total_characters += len(item["text"])
            if len(results) >= max_results:
                break
        search_id = f"kb-search:{uuid.uuid4().hex}"
        query_sha256 = hashlib.sha256(query.encode("utf-8")).hexdigest()
        status = "matches" if results else "no_matches"
        with self.lock:
            self.search_log.append(
                {
                    "search_id": search_id,
                    "query": query.strip(),
                    "query_sha256": query_sha256,
                    "status": status,
                    "results": results,
                }
            )
            event_id = self._append_event(
                "search",
                search_id=search_id,
                query_sha256=query_sha256,
                query_length=len(query),
                terms=len(terms),
                matches=len(results),
            )
        return {
            "event_id": event_id,
            "search_id": search_id,
            "query": query.strip(),
            "query_sha256": query_sha256,
            "status": status,
            "results": results,
        }

    def record_inspiration(
        self,
        search_id: Any,
        passages: Any,
        takeaway: Any,
        planned_change: Any,
    ) -> dict[str, Any]:
        self._require_operation("inspire")
        if not isinstance(search_id, str) or not search_id:
            raise KnowledgeBaseError("search_id must be non-empty text")
        if not isinstance(takeaway, str) or not 1 <= len(takeaway.strip()) <= 1000:
            raise KnowledgeBaseError("takeaway must contain 1 to 1000 characters")
        if (
            not isinstance(planned_change, str)
            or not 1 <= len(planned_change.strip()) <= 1000
        ):
            raise KnowledgeBaseError(
                "planned_change must contain 1 to 1000 characters"
            )
        if (
            not isinstance(passages, list)
            or not 1 <= len(passages) <= 8
            or not all(isinstance(item, dict) for item in passages)
        ):
            raise KnowledgeBaseError("passages must contain 1 to 8 ranges")
        with self.lock:
            search = next(
                (
                    record
                    for record in self.search_log
                    if record["search_id"] == search_id
                ),
                None,
            )
            if search is None:
                raise KnowledgeBaseError("search_id was not produced in this run")
            available = {
                (
                    result["source"],
                    result["line_start"],
                    result["line_end"],
                )
                for result in search["results"]
            }
            selected: list[tuple[str, int, int]] = []
            for item in passages:
                source = normalize_page(item.get("source"))
                line_start = item.get("line_start")
                line_end = item.get("line_end")
                if (
                    not isinstance(line_start, int)
                    or isinstance(line_start, bool)
                    or not isinstance(line_end, int)
                    or isinstance(line_end, bool)
                ):
                    raise KnowledgeBaseError("passage line ranges must be integers")
                key = (source, line_start, line_end)
                if key not in available:
                    raise KnowledgeBaseError(
                        "every inspiration passage must exactly match a search result"
                    )
                selected.append(key)
            selected = list(dict.fromkeys(selected))
            new_passages = [
                key for key in selected if key not in self.qualified_passages
            ]
            implementation_passages = [
                key for key in new_passages if self._qualifying_source(key[0])
            ]
            qualifying_sources = sorted(
                [
                    *self.behavior_feedback["qualifying_source_prefixes"],
                    *self.behavior_feedback["qualifying_source_pages"],
                ]
            )
            qualifying = bool(search["results"] and implementation_passages)
            if qualifying:
                reason = "new_implementation_passage_with_takeaway"
            elif not new_passages:
                reason = "duplicate_passages_only"
            else:
                reason = "no_implementation_detail_passage"
            lookup_id = f"kb-lookup:{uuid.uuid4().hex}"
            if qualifying:
                self.qualified_passages.update(implementation_passages)
            event_id = f"knowledge-base:{uuid.uuid4().hex}"
            event = {
                "event_id": event_id,
                "event": "kb_lookup_completed",
                "kb_lookup_id": lookup_id,
                "query": search["query"],
                "query_sha256": search["query_sha256"],
                "result_count": len(search["results"]),
                "new_passage_count": len(new_passages),
                "implementation_passage_count": len(
                    implementation_passages
                ),
                "qualifying": qualifying,
                "takeaway": takeaway.strip(),
                "planned_change": planned_change.strip(),
                "passages": [
                    {
                        "source": source,
                        "line_start": line_start,
                        "line_end": line_end,
                    }
                    for source, line_start, line_end in selected
                ],
                "reason": reason,
                # Tell a rejected lookup which sources would have qualified,
                # so the agent can retry instead of abandoning the corpus.
                "qualifying_sources": qualifying_sources,
            }
            self._emit_usage_event(
                "knowledge_base.inspiration",
                {
                    key: value
                    for key, value in event.items()
                    if key != "event_id"
                },
                event_id=event_id,
            )
        self._post_json(
            self.research_state_url,
            "/events/knowledge-base-inspiration",
            event,
        )
        return event

    def read(
        self,
        page: Any,
        first_page: Any = None,
        last_page: Any = None,
    ) -> dict[str, Any]:
        self._require_operation("read")
        relative = normalize_page(page)
        path = self._path(relative)
        source_bytes = path.stat().st_size
        suffix = path.suffix.lower()
        page_window = normalize_pdf_page_window(first_page, last_page)
        if suffix == ".pdf":
            if source_bytes > MAX_PDF_BYTES:
                raise KnowledgeBaseError(
                    f"PDF exceeds the {MAX_PDF_BYTES}-byte read limit: "
                    f"{relative}"
                )
            command = [
                "pdftotext",
                "-layout",
                "-nopgbrk",
                "-enc",
                "UTF-8",
            ]
            if page_window is not None:
                command.extend(
                    [
                        "-f",
                        str(page_window[0]),
                        "-l",
                        str(page_window[1]),
                    ]
                )
            command.extend([str(path), "-"])
            try:
                rendered = subprocess.run(
                    command,
                    capture_output=True,
                    check=False,
                    timeout=30,
                )
            except FileNotFoundError as error:
                raise KnowledgeBaseError(
                    "PDF reading is unavailable in this sidecar"
                ) from error
            except subprocess.TimeoutExpired as error:
                raise KnowledgeBaseError("PDF reading timed out") from error
            if rendered.returncode != 0:
                detail = rendered.stderr.decode(
                    "utf-8", errors="replace"
                ).strip()
                raise KnowledgeBaseError(
                    (detail or "PDF text extraction failed")[:500]
                )
            if len(rendered.stdout) > MAX_RENDERED_BYTES:
                raise KnowledgeBaseError(
                    "rendered PDF text exceeds the read response limit"
                )
            content = rendered.stdout.decode("utf-8")
            renderer = "pdftotext-layout"
        else:
            if page_window is not None:
                raise KnowledgeBaseError(
                    "page windows are supported only for PDF documents"
                )
            if source_bytes > MAX_PAGE_BYTES:
                raise KnowledgeBaseError(
                    f"document exceeds the {MAX_PAGE_BYTES}-byte read limit: "
                    f"{relative}"
                )
            content = path.read_text(encoding="utf-8")
            renderer = "utf-8"
        content_bytes = len(content.encode("utf-8"))
        content_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        with self.lock:
            event_id = self._append_event(
                "read",
                page=relative,
                page_sha256=self.pages[relative]["sha256"],
                bytes=content_bytes,
                source_sha256=self.pages[relative]["sha256"],
                source_bytes=source_bytes,
                content_sha256=content_sha256,
                content_bytes=content_bytes,
                page_window=(
                    {
                        "first": page_window[0],
                        "last": page_window[1],
                    }
                    if page_window is not None
                    else None
                ),
                renderer=renderer,
            )
        return {
            "event_id": event_id,
            "page": relative,
            "title": self.pages[relative]["title"],
            "sha256": self.pages[relative]["sha256"],
            "content_sha256": content_sha256,
            "format": self.pages[relative]["format"],
            "renderer": renderer,
            "page_window": (
                {
                    "first": page_window[0],
                    "last": page_window[1],
                }
                if page_window is not None
                else None
            ),
            "content": content,
        }

    def neighbors(self, node: Any) -> dict[str, Any]:
        self._require_operation("neighbors")
        if not isinstance(node, str) or not node.strip():
            raise KnowledgeBaseError("node must be a page path or node id")
        candidate = node.strip()
        if not candidate.endswith(".md"):
            candidate = f"nodes/{candidate}.md"
        relative = normalize_page(candidate)
        text = self._path(relative).read_text(encoding="utf-8")
        node_id = Path(relative).stem
        depends_on: list[str] = []
        if text.startswith("---\n"):
            closing = text.find("\n---\n", 4)
            if closing != -1:
                match = re.search(
                    r"(?m)^depends_on:\s*\[([^\]]*)\]\s*$", text[4:closing]
                )
                if match:
                    depends_on = [
                        value.strip().strip("'\"")
                        for value in match.group(1).split(",")
                        if value.strip()
                    ]
                id_match = re.search(
                    r"(?m)^id:\s*([a-z0-9._-]+)\s*$", text[4:closing]
                )
                if id_match:
                    node_id = id_match.group(1)
        required_by: list[str] = []
        for page in self.pages:
            if not page.startswith("nodes/") or page == relative:
                continue
            other = self._path(page).read_text(encoding="utf-8")
            if re.search(
                rf"(?m)^depends_on:\s*\[[^\]]*\b{re.escape(node_id)}\b[^\]]*\]",
                other,
            ):
                required_by.append(Path(page).stem)
        links = sorted(
            {
                target.split("#", 1)[0]
                for target in re.findall(
                    r"\[[^\]]*\]\(([^)]+\.md(?:#[^)]+)?)\)", text
                )
                if not target.startswith(("http://", "https://"))
            }
        )
        with self.lock:
            event_id = self._append_event("neighbors", page=relative)
        return {
            "event_id": event_id,
            "page": relative,
            "node_id": node_id,
            "depends_on": depends_on,
            "required_by": sorted(required_by),
            "links": links,
        }

def load_service() -> KnowledgeBaseService:
    raw_config = os.environ.get(
        "KNOWLEDGE_BASE_BEHAVIOR_FEEDBACK_CONFIG_JSON", "{}"
    )
    config = json.loads(raw_config)
    if not isinstance(config, dict):
        raise KnowledgeBaseError(
            "KNOWLEDGE_BASE_BEHAVIOR_FEEDBACK_CONFIG_JSON must be an object"
        )
    return KnowledgeBaseService(
        Path(os.environ.get("DUNGENESS_KNOWLEDGE_BASE_ROOT", DEFAULT_ROOT)),
        Path(os.environ.get("TESTBED_USAGE_DIR", "/var/lib/testbed/usage")),
        os.environ.get("TESTBED_RUN_ID", "unknown"),
        os.environ.get("DUNGENESS_RESEARCH_STATE_URL"),
        config,
    )


STATE: KnowledgeBaseService | None = None


def current_state() -> KnowledgeBaseService:
    global STATE
    if STATE is None:
        STATE = load_service()
    return STATE


class Handler(BaseHTTPRequestHandler):
    """Small, fixed REST surface for the sandbox client."""

    server_version = "DungenessKnowledgeBase/3"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _write(self, status: int, document: dict[str, Any]) -> None:
        body = json.dumps(
            document, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict[str, Any]:
        try:
            length = int(self.headers.get("content-length", "0"))
        except ValueError as error:
            raise KnowledgeBaseError("invalid content length") from error
        if length < 0 or length > MAX_BODY_BYTES:
            raise KnowledgeBaseError("request body is too large")
        try:
            value = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError as error:
            raise KnowledgeBaseError("request body must be JSON") from error
        if not isinstance(value, dict):
            raise KnowledgeBaseError("request body must be an object")
        return value

    def do_GET(self) -> None:
        try:
            if self.path == "/healthz":
                self._write(200, {"ok": True})
            elif self.path == "/v1/status":
                self._write(200, current_state().status())
            elif self.path == "/v1/pages":
                self._write(200, current_state().list_pages())
            else:
                self._write(404, {"error": "not found"})
        except KnowledgeBaseAccessError as error:
            self._write(403, {"error": str(error)})
        except (KnowledgeBaseError, OSError, UnicodeError) as error:
            self._write(400, {"error": str(error)})

    def do_POST(self) -> None:
        try:
            body = self._body()
            service = current_state()
            if self.path == "/v1/search":
                result = service.search(
                    body.get("query"),
                    body.get("max_results", body.get("limit", DEFAULT_MAX_RESULTS)),
                    body.get("context_lines", DEFAULT_CONTEXT_LINES),
                )
            elif self.path == "/v1/read":
                result = service.read(
                    body.get("page"),
                    body.get("first_page"),
                    body.get("last_page"),
                )
            elif self.path == "/v1/neighbors":
                result = service.neighbors(body.get("node"))
            elif self.path == "/v1/inspire":
                result = service.record_inspiration(
                    body.get("search_id"),
                    body.get("passages"),
                    body.get("takeaway"),
                    body.get("planned_change"),
                )
            else:
                self._write(404, {"error": "not found"})
                return
            self._write(200, result)
        except KnowledgeBaseAccessError as error:
            self._write(403, {"error": str(error)})
        except (KnowledgeBaseError, OSError, UnicodeError) as error:
            self._write(400, {"error": str(error)})


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
