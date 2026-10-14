"""Historical web-search policy and Exa request validation."""

from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any
from urllib.parse import urlparse


SEARCH_TYPES = {"auto", "fast", "instant"}
FULL_GIT_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
ARXIV_ID_RE = re.compile(
    r"^/(?:abs|html|pdf)/(\d{2})(\d{2})\.\d+(?:v\d+)?(?:\.pdf)?$"
)
WAYBACK_SNAPSHOT_RE = re.compile(r"^/web/(\d{14})(?:id_)?/")
CONTENT_BEARING_RESULT_FIELDS = {
    "context",
    "entities",
    "extras",
    "highlights",
    "summary",
    "text",
}

# Exa documents that these specialized categories do not honor
# crawl/publication date filters.
DATELESS_CATEGORIES = {"company", "people"}


def parse_utc(value: str) -> datetime:
    """Parse Exa's date-only metadata and full ISO timestamps as UTC."""

    if len(value) == 10:
        return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def mutable_url_reason(value: Any) -> str | None:
    """Return why a URL cannot identify stable historical content."""

    if not isinstance(value, str) or not value:
        return "missing_url"
    try:
        parsed = urlparse(value)
    except ValueError:
        return "invalid_url"
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return "invalid_url"

    hostname = parsed.hostname.lower()
    parts = [part for part in parsed.path.split("/") if part]
    if hostname in {"uithub.com", "www.uithub.com", "relatedrepos.com"}:
        return "mutable_mirror"

    if hostname in {"github.com", "www.github.com"}:
        # Only full commit-addressed source or commit pages are immutable. A
        # repository root and refs such as main/master can change after cutoff.
        if len(parts) >= 5 and parts[2] in {"blob", "tree", "raw"}:
            return None if FULL_GIT_SHA_RE.fullmatch(parts[3]) else "mutable_git_ref"
        if len(parts) >= 4 and parts[2] == "commit":
            return None if FULL_GIT_SHA_RE.fullmatch(parts[3]) else "mutable_git_ref"
        return "mutable_git_url"

    if hostname == "raw.githubusercontent.com":
        if len(parts) >= 4 and FULL_GIT_SHA_RE.fullmatch(parts[2]):
            return None
        return "mutable_git_ref"

    return None


def immutable_historical_url(value: Any, cutoff: datetime) -> bool:
    """Return whether a URL itself pins the exact retrievable representation."""

    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    hostname = (parsed.hostname or "").lower()
    parts = [part for part in parsed.path.split("/") if part]

    if hostname in {"github.com", "www.github.com"}:
        return bool(
            (len(parts) >= 5 and parts[2] in {"blob", "tree", "raw"}
             and FULL_GIT_SHA_RE.fullmatch(parts[3]))
            or (len(parts) >= 4 and parts[2] == "commit"
                and FULL_GIT_SHA_RE.fullmatch(parts[3]))
        )
    if hostname == "raw.githubusercontent.com":
        return bool(len(parts) >= 4 and FULL_GIT_SHA_RE.fullmatch(parts[2]))
    if hostname in {"web.archive.org", "www.web.archive.org"}:
        match = WAYBACK_SNAPSHOT_RE.match(parsed.path)
        if not match:
            return False
        try:
            snapshot = datetime.strptime(match.group(1), "%Y%m%d%H%M%S").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            return False
        return snapshot <= cutoff
    return False


def historical_date_evidence(item: dict[str, Any]) -> list[tuple[str, datetime]]:
    """Collect explicit publication evidence without inferring from prose."""

    raw: list[tuple[str, Any]] = [("publishedDate", item.get("publishedDate"))]
    entities = item.get("entities")
    if isinstance(entities, list):
        for index, entity in enumerate(entities):
            if not isinstance(entity, dict):
                continue
            properties = entity.get("properties")
            if not isinstance(properties, dict):
                continue
            for key in ("date", "publishedDate", "publicationDate", "published_at"):
                raw.append((f"entities[{index}].properties.{key}", properties.get(key)))

    # An arXiv identifier independently proves the earliest possible month. It
    # is useful chiefly as a rejection signal when Exa omitted publishedDate.
    url = item.get("url")
    if isinstance(url, str):
        parsed = urlparse(url)
        if parsed.hostname in {"arxiv.org", "www.arxiv.org"}:
            match = ARXIV_ID_RE.fullmatch(parsed.path)
            if match:
                year = 2000 + int(match.group(1))
                month = int(match.group(2))
                try:
                    raw.append(
                        (
                            "url.arxiv_identifier",
                            datetime(year, month, 1, tzinfo=timezone.utc).isoformat(),
                        )
                    )
                except ValueError:
                    raw.append(("url.arxiv_identifier", "invalid"))

    evidence: list[tuple[str, datetime]] = []
    for source, value in raw:
        if value is None:
            continue
        if not isinstance(value, str):
            raise ValueError(f"invalid historical date metadata: {source}")
        evidence.append((source, parse_utc(value)))
    return evidence


def approve_historical_result(
    item: Any, cutoff: datetime
) -> tuple[dict[str, Any] | None, str | None]:
    """Validate one provider result against the strict historical boundary."""

    if not isinstance(item, dict):
        return None, "invalid_result"
    url = item.get("url")
    reason = mutable_url_reason(url)
    if reason:
        return None, reason
    try:
        evidence = historical_date_evidence(item)
    except (TypeError, ValueError):
        return None, "invalid_date"
    if not evidence:
        return None, "missing_date"
    if any(value > cutoff for _, value in evidence):
        return None, "post_cutoff"

    effective = max(value for _, value in evidence)
    immutable = immutable_historical_url(url, cutoff)
    return (
        {
            "url": url,
            "effective_published_at": effective.isoformat(),
            "date_evidence": [
                {"source": source, "value": value.isoformat()}
                for source, value in evidence
            ],
            "content_access": "immutable" if immutable else "metadata-only",
        },
        None,
    )


def positive_int(value: Any, *, default: int, maximum: int) -> int:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError("expected a positive integer")
    return min(value, maximum)


def make_search_payload(
    query: str,
    options: dict[str, Any],
    *,
    max_results: int,
    end_published_date: str,
) -> dict[str, Any]:
    """Validate agent options and construct the policy-controlled Exa request."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    category = options.get("category")
    if category in DATELESS_CATEGORIES:
        raise ValueError(
            f"category {category!r} is disabled because Exa does not apply date filters to it"
        )
    search_type = options.get("type", "auto")
    if search_type not in SEARCH_TYPES:
        raise ValueError(f"unsupported search type: {search_type!r}")

    supported = {
        "num_results",
        "type",
        "category",
        "include_domains",
        "exclude_domains",
        "contents",
    }
    unknown = sorted(set(options) - supported)
    if unknown:
        raise ValueError(f"unsupported search options: {', '.join(unknown)}")

    contents = options.get("contents", {"highlights": True})
    if contents is True:
        contents = {"highlights": True}
    if not isinstance(contents, dict):
        raise ValueError("contents must be an object")
    unknown_contents = sorted(set(contents) - {"highlights", "text"})
    if unknown_contents:
        raise ValueError(
            f"unsupported contents options: {', '.join(unknown_contents)}"
        )
    contents = dict(contents)

    # Cache-only retrieval prevents live crawling during the run. It does not
    # establish that the cached representation predates the benchmark cutoff;
    # response validation below remains mandatory.
    contents["maxAgeHours"] = -1

    payload: dict[str, Any] = {
        "query": query.strip(),
        "numResults": positive_int(
            options.get("num_results"), default=10, maximum=max_results
        ),
        "type": search_type,
        "endPublishedDate": end_published_date,
        "contents": contents,
    }
    for source, target in (
        ("category", "category"),
        ("include_domains", "includeDomains"),
        ("exclude_domains", "excludeDomains"),
    ):
        if source in options:
            payload[target] = options[source]
    return payload
