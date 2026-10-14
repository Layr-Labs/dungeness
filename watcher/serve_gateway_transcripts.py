#!/usr/bin/env python3
"""Local live server for Dungeness gateway transcripts.

Watches run directories, re-renders their transcript HTML in memory whenever
the underlying usage files change, and serves them over HTTP on localhost.

Usage:
    python3 watcher/serve_gateway_transcripts.py [RUN_DIR ...]
        [--runs-root runs/users/bx] [--runs-root /other/repo/runs/users/bx]
        [--port 8765] [--interval 5] [--write]

Standard library only. Builds on watcher/render_gateway_transcript.py.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import importlib.machinery
import importlib.util
import json
import re
import signal
import sys
import threading
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.parse import quote, unquote, urlsplit

SCRIPTS_DIR = Path(__file__).resolve().parent


def _load_renderer():
    name = "render_gateway_transcript"
    if name in sys.modules:
        return sys.modules[name]
    path = SCRIPTS_DIR / "render_gateway_transcript.py"
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module


renderer = _load_renderer()

RUNNING_STATUSES = {"running", "in_progress", "started", "pending", "queued"}
DERIVED_TERMINAL_STATUSES = {"budget exhausted", "cybersecurity blocked"}
DEFAULT_STALE_AFTER_SECONDS = 3600.0
RUN_ID_TIMESTAMP_RE = re.compile(
    r"(?:^|-)(\d{8}(?:T\d{4}(?:\d{2})?Z)?)(?=-|$)"
)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime | None) -> str | None:
    return dt.isoformat(timespec="seconds") if dt else None


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


# ---------------------------------------------------------------------------
# Registry / watcher
# ---------------------------------------------------------------------------


@dataclass
class RunState:
    run_id: str
    run_dir: Path
    version: str | None = None
    html: str | None = None
    summary: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    rendered_at: datetime | None = None
    render_ms: float | None = None
    last_activity: datetime | None = None
    renders: int = 0

    def raw_status(self) -> str | None:
        status = self.summary.get("raw_status")
        if status is None:
            status = self.summary.get("status")
        if status is None:
            status = read_record_status(self.run_dir)
        return str(status) if status is not None else None

    def status(
        self,
        stale_after_seconds: float = DEFAULT_STALE_AFTER_SECONDS,
    ) -> str | None:
        display_status = self.summary.get("status")
        raw_status = self.raw_status()
        if (
            display_status is not None
            and str(display_status).lower() in DERIVED_TERMINAL_STATUSES
        ):
            return str(display_status)
        if (
            raw_status is not None
            and raw_status.lower() in RUNNING_STATUSES
            and self.last_activity is not None
            and (now_utc() - self.last_activity).total_seconds()
            > stale_after_seconds
        ):
            return "stale"
        if display_status is not None:
            return str(display_status)
        return raw_status

    def is_running(
        self,
        stale_after_seconds: float = DEFAULT_STALE_AFTER_SECONDS,
    ) -> bool:
        status = self.status(stale_after_seconds)
        return status is not None and status.lower() in RUNNING_STATUSES


def read_record_status(run_dir: Path) -> str | None:
    record = renderer.read_json(run_dir / "record.json")
    if isinstance(record, dict) and isinstance(record.get("data"), dict):
        status = record["data"].get("status")
        return str(status) if status is not None else None
    return None


def run_id_started_at(run_id: str) -> datetime | None:
    """Return the last Dungeness timestamp embedded in a run id."""
    for value in reversed(RUN_ID_TIMESTAMP_RE.findall(run_id)):
        for timestamp_format in (
            "%Y%m%dT%H%M%SZ",
            "%Y%m%dT%H%MZ",
            "%Y%m%d",
        ):
            try:
                return datetime.strptime(value, timestamp_format).replace(
                    tzinfo=timezone.utc
                )
            except ValueError:
                continue
    return None


def run_started_at(state: RunState) -> datetime | None:
    """Resolve a stable creation time for index ordering."""
    recorded = renderer.parse_ts(state.summary.get("started_at"))
    if recorded is not None:
        return recorded
    return run_id_started_at(state.run_id) or state.last_activity


def tracked_files(run_dir: Path) -> list[Path]:
    files: list[Path] = []
    record = run_dir / "record.json"
    if record.is_file():
        files.append(record)
    usage = run_dir / "usage"
    if usage.is_dir():
        files.extend(sorted(usage.glob("*.jsonl")))
        files.extend(sorted(usage.glob("*.json")))
    harbor = run_dir / "harbor"
    if harbor.is_dir():
        files.extend(sorted(harbor.glob("*/result.json")))
        files.extend(sorted(harbor.glob("*/task__*/result.json")))
        files.extend(sorted(harbor.glob("*/task__*/agent/trajectory.json")))
        files.extend(sorted(harbor.glob("*/task__*/agent/codex.txt")))
        files.extend(sorted(harbor.glob("*/task__*/agent/sessions/**/*.jsonl")))
    return files


def version_key(run_dir: Path) -> tuple[str, datetime | None]:
    """Return (hash over tracked file mtimes/sizes, most recent mtime)."""
    digest = hashlib.sha1()
    latest: float | None = None
    for path in tracked_files(run_dir):
        try:
            stat = path.stat()
        except OSError:
            continue
        digest.update(f"{path.relative_to(run_dir)}|{stat.st_mtime_ns}|{stat.st_size}\n".encode("utf-8"))
        if latest is None or stat.st_mtime > latest:
            latest = stat.st_mtime
    latest_dt = datetime.fromtimestamp(latest, tz=timezone.utc) if latest is not None else None
    return digest.hexdigest()[:16], latest_dt


def normalize_runs_roots(
    runs_root: Path | str | Iterable[Path | str] | None,
) -> list[Path]:
    if runs_root is None:
        return []
    if isinstance(runs_root, (str, Path)):
        return [Path(runs_root)]
    return [Path(root) for root in runs_root]


def discover_runs(
    runs_root: Path | str | Iterable[Path | str] | None,
    explicit: list[Path],
) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for run_dir in explicit:
        run_dir = run_dir.resolve()
        if run_dir.is_dir():
            found[run_dir.name] = run_dir
    for root in normalize_runs_roots(runs_root):
        if root.is_dir():
            for record in sorted(root.rglob("record.json")):
                run_dir = record.parent.resolve()
                # Explicit directories take precedence, followed by roots in
                # command-line order when the same run id exists more than once.
                found.setdefault(run_dir.name, run_dir)
    return found


RenderFn = Callable[[Path], tuple[str, dict[str, Any]]]


class TranscriptRegistry:
    def __init__(
        self,
        explicit: list[Path],
        runs_root: Path | str | Iterable[Path | str] | None,
        interval: float = 5.0,
        write: bool = False,
        render_fn: RenderFn | None = None,
        stale_after: float = DEFAULT_STALE_AFTER_SECONDS,
    ) -> None:
        self.explicit = [Path(p) for p in explicit]
        self.runs_roots = normalize_runs_roots(runs_root)
        # Preserve the old attribute for callers that inspect a single root.
        self.runs_root = self.runs_roots[0] if len(self.runs_roots) == 1 else None
        self.interval = max(0.05, float(interval))
        self.stale_after = max(1.0, float(stale_after))
        self.write = write
        self.render_fn: RenderFn = render_fn or renderer.render_run_with_summary
        self.runs: dict[str, RunState] = {}
        self.lock = threading.RLock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.log: Callable[[str], None] = lambda message: None

    # -- polling ----------------------------------------------------------

    def poll_once(self) -> list[str]:
        """Rescan run directories and re-render any whose version key changed.

        Returns the run ids that were re-rendered."""
        discovered = discover_runs(self.runs_roots, self.explicit)
        rendered: list[str] = []
        with self.lock:
            for run_id in list(self.runs):
                if run_id not in discovered:
                    del self.runs[run_id]
            for run_id, run_dir in discovered.items():
                state = self.runs.get(run_id)
                if state is None:
                    state = RunState(run_id=run_id, run_dir=run_dir)
                    self.runs[run_id] = state
                state.run_dir = run_dir
        for run_id, run_dir in discovered.items():
            key, latest = version_key(run_dir)
            with self.lock:
                state = self.runs.get(run_id)
                if state is None:
                    continue
                state.last_activity = latest
                if state.version == key:
                    continue
            self._render(run_id, run_dir, key)
            rendered.append(run_id)
        return rendered

    def _render(self, run_id: str, run_dir: Path, key: str) -> None:
        started = time.perf_counter()
        html_text: str | None = None
        summary: dict[str, Any] = {}
        error: str | None = None
        try:
            html_text, summary = self.render_fn(run_dir)
        except Exception:  # noqa: BLE001 - render failures must never crash the server
            error = traceback.format_exc()
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        with self.lock:
            state = self.runs.get(run_id)
            if state is None:
                return
            state.version = key
            state.rendered_at = now_utc()
            state.render_ms = elapsed_ms
            state.renders += 1
            if error is None:
                state.html = html_text
                state.summary = summary
                state.error = None
            else:
                state.error = error
                if not state.summary:
                    state.summary = {"status": read_record_status(run_dir)}
        if error is None:
            self.log(f"rendered {run_id} in {elapsed_ms:.0f} ms (version {key})")
            if self.write and html_text is not None:
                try:
                    (run_dir / "transcript.html").write_text(html_text, encoding="utf-8")
                except OSError as exc:
                    self.log(f"could not write transcript.html for {run_id}: {exc}")
        else:
            self.log(f"render FAILED for {run_id}: {error.strip().splitlines()[-1]}")

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self.poll_once()
            except Exception:  # noqa: BLE001
                self.log("watcher error:\n" + traceback.format_exc())
            self._stop.wait(self.interval)

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._loop, name="transcript-watcher", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=self.interval + 5)
            self._thread = None

    # -- queries ------------------------------------------------------------

    def get(self, run_id: str) -> RunState | None:
        with self.lock:
            return self.runs.get(run_id)

    def snapshot(self) -> list[RunState]:
        with self.lock:
            states = list(self.runs.values())
        epoch = datetime.fromtimestamp(0, tz=timezone.utc)
        states.sort(
            key=lambda state: (
                run_started_at(state) or epoch,
                state.run_id,
            ),
            reverse=True,
        )
        return states

    def summaries(self) -> list[dict[str, Any]]:
        out = []
        for state in self.snapshot():
            item = dict(state.summary)
            item.update(
                {
                    "run_id": state.run_id,
                    "run_dir": str(state.run_dir),
                    "raw_status": state.raw_status(),
                    "status": state.status(self.stale_after),
                    "running": state.is_running(self.stale_after),
                    "version": state.version,
                    "rendered_at": iso(state.rendered_at),
                    "render_ms": state.render_ms,
                    "last_activity": iso(state.last_activity),
                    "error": (state.error.strip().splitlines()[-1] if state.error else None),
                }
            )
            out.append(item)
        return out


# ---------------------------------------------------------------------------
# HTML fragments
# ---------------------------------------------------------------------------

INDEX_CSS = """
body{margin:0;font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;background:#f4f5f7;color:#1d2129}
header{background:#111827;color:#f9fafb;padding:14px 24px}header h1{margin:0;font-size:18px}header .sub{color:#cbd5e1;font-size:13px;margin-top:4px}
main{max-width:1300px;margin:0 auto;padding:16px 24px}
table{width:100%;border-collapse:collapse;background:#fff;border:1px solid #e2e5ea;border-radius:10px;overflow:hidden}
th,td{padding:8px 10px;border-bottom:1px solid #eef0f3;text-align:left;font-size:13px;vertical-align:top}
th{background:#f8fafc;color:#6b7280;font-weight:600;text-transform:uppercase;font-size:11px;letter-spacing:.4px}
tr.running{background:#fff7ed}
td.num{text-align:right;font-variant-numeric:tabular-nums}
a{color:#1d4ed8;text-decoration:none}a:hover{text-decoration:underline}
.badge{display:inline-block;padding:1px 7px;border-radius:999px;font-size:11px;font-weight:600}
.badge.running{background:#ea580c;color:#fff;animation:pulse 1.6s infinite}
.badge.completed{background:#dcfce7;color:#14532d}.badge.failed{background:#fecaca;color:#7f1d1d}.badge.other{background:#e5e7eb;color:#374151}
.badge.budget{background:#fef3c7;color:#92400e}.badge.stale{background:#e5e7eb;color:#4b5563}
.badge.security{background:#fae8ff;color:#86198f}
.badge.err{background:#dc2626;color:#fff}
.ratio-red{color:#dc2626;font-weight:700}.ratio-amber{color:#d97706;font-weight:700}.ratio-green{color:#15803d;font-weight:700}
.muted{color:#6b7280;font-size:12px}
@keyframes pulse{0%{opacity:1}50%{opacity:.45}100%{opacity:1}}
"""

INDEX_JS = """
(function(){
  var interval = %(interval_ms)d;
  function esc(v){return v===null||v===undefined?'-':String(v);}
  function num(v){return (v===null||v===undefined)?'-':Number(v).toLocaleString();}
  function usd(v){return (v===null||v===undefined)?'-':'$'+Number(v).toFixed(4);}
  function ratio(v){if(v===null||v===undefined)return '<span class="muted">-</span>';var p=v*100;var c=p<50?'ratio-red':(p<=80?'ratio-amber':'ratio-green');return '<span class="'+c+'">'+p.toFixed(1)+'%%</span>';}
  function score(v){if(v===null||v===undefined)return '-';return Number.isInteger(v)?Number(v).toLocaleString():Number(v).toLocaleString(undefined,{maximumFractionDigits:3});}
  function scoreCell(r){var v=r.result_score!==null&&r.result_score!==undefined?r.result_score:r.best_score;if(v===null||v===undefined)return '-';var out=score(v);if(r.final_verifier_score!==null&&r.final_verifier_score!==undefined){out+='<div class="muted">final verifier</div>';if(r.best_evaluation_score!==null&&r.best_evaluation_score!==undefined&&Number(r.best_evaluation_score)!==Number(r.final_verifier_score)){out+='<div class="muted">best eval '+score(r.best_evaluation_score)+'</div>';}}else{out+='<div class="muted">best evaluation</div>';}return out;}
  function badge(r){if(r.error)return '<span class="badge err">render error</span> ';if(r.running)return '<span class="badge running">RUNNING</span>';var s=(r.status||'unknown').toLowerCase();var c=s==='completed'?'completed':(s==='failed'?'failed':(s==='budget exhausted'?'budget':(s==='cybersecurity blocked'?'security':(s==='stale'?'stale':'other'))));return '<span class="badge '+c+'">'+h(r.status||'unknown')+'</span>';}
  function h(s){return String(s).replace(/[&<>"']/g,function(ch){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch];});}
  function render(runs){
    var tb=document.getElementById('runs');var rows='';
    for(var i=0;i<runs.length;i++){var r=runs[i];
      rows+='<tr class="'+(r.running?'running':'')+'">'
        +'<td><a href="/spec/'+encodeURIComponent(r.run_id)+'">'+h(r.run_id)+'</a>'
        +'<div class="muted"><a href="/run/'+encodeURIComponent(r.run_id)+'">transcript</a></div>'
        +(r.error?'<div class="muted">'+h(r.error)+'</div>':'')+'</td>'
        +'<td>'+badge(r)+'</td>'
        +'<td>'+h(esc(r.started_at))+'</td>'
        +'<td class="num">'+num(r.requests)+'</td>'
        +'<td class="num">'+usd(r.total_usd)+'</td>'
        +'<td class="num">'+ratio(r.cache_ratio)+'</td>'
        +'<td class="num">'+(r.evaluations===undefined?'-':(num(r.evaluations_valid)+' / '+num(r.evaluations_invalid)))+'</td>'
        +'<td class="num">'+scoreCell(r)+'</td>'
        +'<td>'+h(esc(r.last_activity))+'</td>'
        +'<td>'+h(esc(r.rendered_at))+(r.render_ms!=null?' <span class="muted">('+Math.round(r.render_ms)+' ms)</span>':'')+'</td>'
        +'</tr>';}
    if(!runs.length)rows='<tr><td colspan="10" class="muted">no runs discovered yet</td></tr>';
    tb.innerHTML=rows;
    document.getElementById('updated').textContent='index refreshed '+new Date().toLocaleTimeString()+' · '+runs.length+' run(s)';
  }
  function tick(){fetch('/api/runs',{cache:'no-store'}).then(function(r){return r.json();}).then(function(j){render(j.runs||[]);}).catch(function(){document.getElementById('updated').textContent='index refresh failed; retrying';});}
  tick();setInterval(tick,interval);
})();
"""

RUN_SPEC_CSS = """
body{margin:0;font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;background:#f4f5f7;color:#1d2129}
header{background:#111827;color:#f9fafb;padding:16px 24px}header h1{margin:0;font-size:18px}
header .sub{margin-top:5px;color:#cbd5e1;font-size:13px}header a{color:#93c5fd}
main{max-width:1000px;margin:0 auto;padding:18px 24px 60px}
.meta{display:grid;grid-template-columns:max-content 1fr;gap:5px 14px;background:#fff;border:1px solid #e2e5ea;border-radius:10px;padding:12px 14px;margin-bottom:14px}
.meta dt{color:#6b7280}.meta dd{margin:0;overflow-wrap:anywhere}
.note{background:#eff6ff;border-left:4px solid #2563eb;padding:9px 12px;margin:12px 0;color:#1e3a8a}
.warn{background:#fef3c7;border-left:4px solid #d97706;padding:9px 12px;margin:12px 0;color:#78350f}
pre{margin:0;background:#111827;color:#e5e7eb;border-radius:10px;padding:16px;overflow:auto;white-space:pre;font:12px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
a{color:#1d4ed8;text-decoration:none}a:hover{text-decoration:underline}
"""

LIVE_JS = """
(function(){
  var runId=%(run_id)s, version=%(version)s, pollMs=%(poll_ms)d, key='dgt-scroll:'+runId;
  function restore(){var raw=sessionStorage.getItem(key);if(!raw)return;sessionStorage.removeItem(key);try{var o=JSON.parse(raw);if(o.bottom){window.scrollTo(0,document.documentElement.scrollHeight);}else{window.scrollTo(0,o.y||0);}}catch(e){}}
  restore();window.addEventListener('load',restore);
  function atBottom(){return (window.innerHeight+window.scrollY)>=(document.documentElement.scrollHeight-60);}
  function poll(){
    fetch('/api/run/'+encodeURIComponent(runId)+'/version',{cache:'no-store'}).then(function(r){if(!r.ok)throw new Error(r.status);return r.json();}).then(function(j){
      if(j.version && j.version!==version){sessionStorage.setItem(key,JSON.stringify({y:window.scrollY,bottom:atBottom()}));location.reload();}
    }).catch(function(){});
  }
  setInterval(poll,pollMs);
})();
"""


def ratio_class(value: Any) -> str:
    if not isinstance(value, (int, float)):
        return "muted"
    if value < 0.5:
        return "ratio-red"
    if value <= 0.8:
        return "ratio-amber"
    return "ratio-green"


def _run_spec_source_file(run_dir: Path, source_path: str) -> Path | None:
    """Resolve a recorded repository-relative run-spec path safely."""
    relative = Path(source_path)
    if relative.is_absolute() or ".." in relative.parts:
        return None
    for base in run_dir.parents:
        if not (base / "run-specs").is_dir():
            continue
        candidate = (base / relative).resolve()
        try:
            candidate.relative_to(base.resolve())
        except ValueError:
            continue
        if candidate.is_file():
            return candidate
    return None


def run_spec_view(run_dir: Path) -> dict[str, Any]:
    """Return the exact recorded run-spec and its available source metadata."""
    record = renderer.read_json(run_dir / "record.json")
    if not isinstance(record, dict):
        record = {}
    relations = record.get("relations")
    relation = relations.get("run_spec") if isinstance(relations, dict) else None
    data = record.get("data")
    configuration = data.get("configuration") if isinstance(data, dict) else None
    sources = configuration.get("sources") if isinstance(configuration, dict) else None
    captured = sources.get("run_spec") if isinstance(sources, dict) else None

    source_path: str | None = None
    recorded_sha: str | None = None
    document: dict[str, Any] | None = None
    if isinstance(captured, dict):
        if isinstance(captured.get("path"), str):
            source_path = captured["path"]
        if isinstance(captured.get("sha256"), str):
            recorded_sha = captured["sha256"]
        if isinstance(captured.get("document"), dict):
            document = captured["document"]

    source_file = (
        _run_spec_source_file(run_dir, source_path)
        if source_path is not None
        else None
    )
    source_matches: bool | None = None
    source_text: str | None = None
    if source_file is not None:
        try:
            payload = source_file.read_bytes()
            source_matches = (
                hashlib.sha256(payload).hexdigest() == recorded_sha
                if recorded_sha
                else None
            )
            source_text = payload.decode("utf-8", errors="replace")
        except OSError:
            source_file = None

    if source_text is not None and source_matches is not False:
        text = source_text
        display_format = "authored YAML"
    elif document is not None:
        text = json.dumps(document, indent=2, ensure_ascii=False, sort_keys=False)
        display_format = "embedded resolved snapshot (JSON)"
    else:
        text = None
        display_format = None

    return {
        "reference": relation,
        "source_path": source_path,
        "source_file": str(source_file) if source_file is not None else None,
        "recorded_sha256": recorded_sha,
        "source_matches": source_matches,
        "display_format": display_format,
        "text": text,
    }


def render_run_spec_page(state: RunState) -> str:
    spec = run_spec_view(state.run_dir)
    encoded_id = quote(state.run_id, safe="")
    metadata = [
        ("run", state.run_id),
        ("run-spec reference", spec.get("reference") or "not recorded"),
        ("recorded path", spec.get("source_path") or "not recorded"),
        ("recorded SHA-256", spec.get("recorded_sha256") or "not recorded"),
        ("display", spec.get("display_format") or "unavailable"),
    ]
    if spec.get("source_file"):
        metadata.append(("source file", spec["source_file"]))
    meta_html = "".join(
        f"<dt>{esc(label)}</dt><dd><code>{esc(value)}</code></dd>"
        for label, value in metadata
    )

    note = ""
    if spec.get("source_matches") is True:
        note = (
            '<div class="note">The source YAML matches the SHA-256 captured '
            "when this run started.</div>"
        )
    elif spec.get("source_matches") is False:
        note = (
            '<div class="warn">The source YAML has changed since this run. '
            "Showing the embedded resolved snapshot instead.</div>"
        )
    elif spec.get("text") is not None:
        note = (
            '<div class="note">The authored YAML is unavailable; showing the '
            "resolved run-spec snapshot embedded in the run record.</div>"
        )

    text = spec.get("text")
    content = (
        f"<pre>{esc(text)}</pre>"
        if isinstance(text, str)
        else '<div class="warn">This run record does not contain a captured run-spec.</div>'
    )
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        f"<title>Run spec — {esc(state.run_id)}</title>"
        f"<style>{RUN_SPEC_CSS}</style></head><body>"
        f"<header><h1>Run spec · {esc(state.run_id)}</h1>"
        f'<div class="sub"><a href="/">index</a> · '
        f'<a href="/run/{encoded_id}">transcript</a></div></header>'
        f'<main><dl class="meta">{meta_html}</dl>{note}{content}</main>'
        "</body></html>"
    )


def render_index(registry: TranscriptRegistry) -> str:
    rows = []
    for item in registry.summaries():
        status = item.get("status") or "unknown"
        if item.get("error"):
            badge = '<span class="badge err">render error</span>'
        elif item.get("running"):
            badge = '<span class="badge running">RUNNING</span>'
        else:
            css = (
                "completed"
                if status == "completed"
                else "failed"
                if status == "failed"
                else "budget"
                if status == "budget exhausted"
                else "security"
                if status == "cybersecurity blocked"
                else "stale"
                if status == "stale"
                else "other"
            )
            badge = f'<span class="badge {css}">{esc(status)}</span>'
        ratio = item.get("cache_ratio")
        ratio_text = f"{ratio * 100:.1f}%" if isinstance(ratio, (int, float)) else "-"
        usd = item.get("total_usd")
        usd_text = f"${usd:,.4f}" if isinstance(usd, (int, float)) else "-"
        evals = "-" if item.get("evaluations") is None else f"{item.get('evaluations_valid', 0)} / {item.get('evaluations_invalid', 0)}"
        result_score = item.get("result_score")
        if result_score is None:
            result_score = item.get("best_score")
        score_source = item.get("score_source")
        score_html = esc(renderer.fmt_score(result_score))
        if score_source:
            score_html += f'<div class="muted">{esc(score_source)}</div>'
        best_evaluation = item.get("best_evaluation_score")
        final_verifier = item.get("final_verifier_score")
        if (
            isinstance(best_evaluation, (int, float))
            and isinstance(final_verifier, (int, float))
            and best_evaluation != final_verifier
        ):
            score_html += (
                '<div class="muted">best eval '
                f"{esc(renderer.fmt_score(best_evaluation))}</div>"
            )
        render_ms = item.get("render_ms")
        encoded_id = quote(str(item["run_id"]), safe="")
        rows.append(
            f'<tr class="{"running" if item.get("running") else ""}">'
            f'<td><a href="/spec/{encoded_id}">{esc(item["run_id"])}</a>'
            f'<div class="muted"><a href="/run/{encoded_id}">transcript</a></div>'
            + (f'<div class="muted">{esc(item["error"])}</div>' if item.get("error") else "")
            + f"</td><td>{badge}</td><td>{esc(item.get('started_at') or '-')}</td>"
            f'<td class="num">{esc(item.get("requests", "-"))}</td><td class="num">{usd_text}</td>'
            f'<td class="num"><span class="{ratio_class(ratio)}">{ratio_text}</span></td>'
            f'<td class="num">{evals}</td><td class="num">{score_html}</td>'
            f"<td>{esc(item.get('last_activity') or '-')}</td>"
            f"<td>{esc(item.get('rendered_at') or 'pending')}"
            + (f' <span class="muted">({render_ms:.0f} ms)</span>' if isinstance(render_ms, (int, float)) else "")
            + "</td></tr>"
        )
    if not rows:
        rows.append('<tr><td colspan="10" class="muted">no runs discovered yet</td></tr>')
    roots_text = (
        ", ".join(str(path) for path in registry.runs_roots)
        if registry.runs_roots
        else "(explicit run directories only)"
    )
    interval_ms = int(registry.interval * 1000)
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Dungeness gateway transcripts</title>'
        f"<style>{INDEX_CSS}</style></head><body><header><h1>Dungeness gateway transcripts</h1>"
        f'<div class="sub">run roots: {esc(roots_text)} · poll interval {registry.interval:g}s · '
        f'<span id="updated">index rendered {esc(iso(now_utc()))}</span></div></header><main>'
        "<table><thead><tr><th>run</th><th>status</th><th>started</th><th>requests</th><th>spend</th>"
        "<th>cache ratio</th><th>evals valid / invalid</th><th>result score</th><th>last activity</th><th>last render</th></tr></thead>"
        f'<tbody id="runs">{"".join(rows)}</tbody></table>'
        '<p class="muted">Sorted by recorded run start time, newest first. '
        "The timestamp in the run ID and then file activity are used as fallbacks. "
        "Rows highlighted in orange are still running.</p>"
        f"</main><script>{INDEX_JS % {'interval_ms': interval_ms}}</script></body></html>"
    )


def live_reload_script(state: RunState, poll_ms: int) -> str:
    return (
        "<script>"
        + LIVE_JS
        % {
            "run_id": json.dumps(state.run_id),
            "version": json.dumps(state.version),
            "poll_ms": poll_ms,
        }
        + "</script>"
    )


def inject_before_body_end(document: str, fragment: str) -> str:
    marker = "</body>"
    position = document.rfind(marker)
    if position == -1:
        return document + fragment
    return document[:position] + fragment + document[position:]


def render_run_page(
    state: RunState,
    poll_ms: int,
) -> str:
    live_script = live_reload_script(state, poll_ms)
    if state.error is not None and state.html is None:
        return _error_page(state, live_script)
    if state.html is None:
        body = (
            '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Rendering…</title></head>'
            f'<body style="font-family:sans-serif;padding:24px"><h1>{esc(state.run_id)}</h1>'
            "<p>Transcript is being rendered; this page reloads automatically.</p></body></html>"
        )
        return inject_before_body_end(body, live_script)
    document = state.html
    if state.error is not None:
        # Latest render failed; serve the last good HTML with a visible warning.
        warning = (
            '<div style="position:fixed;left:14px;bottom:14px;z-index:1000;background:#7f1d1d;color:#fff;padding:8px 12px;'
            'border-radius:10px;font:12px sans-serif;max-width:520px">latest re-render failed; showing previous version.<br>'
            f"<code>{esc(state.error.strip().splitlines()[-1])}</code></div>"
        )
        document = inject_before_body_end(document, warning)
    return inject_before_body_end(document, live_script)


def _error_page(state: RunState, live_script: str) -> str:
    body = (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Render error</title></head>'
        '<body style="font-family:sans-serif;padding:24px"><h1 style="color:#b91c1c">Render error</h1>'
        f"<p>Run <b>{esc(state.run_id)}</b> at <code>{esc(state.run_dir)}</code> could not be rendered. "
        "The server keeps polling; the page reloads when the files change.</p>"
        f'<pre style="background:#fef2f2;padding:12px;border-radius:8px;white-space:pre-wrap">{esc(state.error)}</pre>'
        "</body></html>"
    )
    return inject_before_body_end(body, live_script)


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------


class TranscriptHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], registry: TranscriptRegistry) -> None:
        self.registry = registry
        super().__init__(address, TranscriptRequestHandler)


class TranscriptRequestHandler(BaseHTTPRequestHandler):
    server: TranscriptHTTPServer
    server_version = "DungenessTranscripts/1.0"
    quiet = True

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        if not self.quiet:
            super().log_message(format, *args)

    # -- helpers ---------------------------------------------------------

    def _send(self, status: int, body: str | bytes, content_type: str = "text/html; charset=utf-8") -> None:
        payload = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)

    def _send_json(self, status: int, payload: Any) -> None:
        self._send(status, json.dumps(payload, ensure_ascii=False, default=str), "application/json; charset=utf-8")

    def _not_found(self, message: str = "not found") -> None:
        self._send(404, f"<!DOCTYPE html><html><body><h1>404</h1><p>{esc(message)}</p><p><a href='/'>index</a></p></body></html>")

    def _lookup(self, raw_id: str) -> RunState | None:
        run_id = unquote(raw_id)
        if not run_id or "/" in run_id or "\\" in run_id or run_id in (".", ".."):
            return None
        return self.server.registry.get(run_id)

    # -- routes ----------------------------------------------------------

    def do_HEAD(self) -> None:  # noqa: N802
        self.do_GET()

    def do_GET(self) -> None:  # noqa: N802
        registry = self.server.registry
        path = urlsplit(self.path).path
        poll_ms = int(max(1.0, registry.interval) * 1000)
        try:
            if path in ("/", "/index.html"):
                self._send(200, render_index(registry))
                return
            if path == "/api/runs":
                self._send_json(200, {"runs": registry.summaries(), "now": iso(now_utc())})
                return
            if path.startswith("/spec/"):
                state = self._lookup(path[len("/spec/"):])
                if state is None:
                    self._not_found("unknown run id")
                    return
                self._send(200, render_run_spec_page(state))
                return
            if path.startswith("/api/run/"):
                remainder = path[len("/api/run/"):]
                if remainder.endswith("/version"):
                    state = self._lookup(remainder[: -len("/version")])
                    if state is None:
                        self._send_json(404, {"error": "unknown run"})
                        return
                    self._send_json(
                        200,
                        {
                            "run_id": state.run_id,
                            "version": state.version,
                            "rendered_at": iso(state.rendered_at),
                            "raw_status": state.raw_status(),
                            "status": state.status(registry.stale_after),
                            "running": state.is_running(registry.stale_after),
                            "error": bool(state.error),
                        },
                    )
                    return
                self._send_json(404, {"error": "unknown api route"})
                return
            if path.startswith("/run/"):
                state = self._lookup(path[len("/run/"):])
                if state is None:
                    self._not_found("unknown run id")
                    return
                self._send(
                    200,
                    render_run_page(state, poll_ms),
                )
                return
            self._not_found()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception:  # noqa: BLE001
            self._send(500, f"<pre>{esc(traceback.format_exc())}</pre>")


def make_server(registry: TranscriptRegistry, host: str = "127.0.0.1", port: int = 8765) -> TranscriptHTTPServer:
    return TranscriptHTTPServer((host, port), registry)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run_dirs", nargs="*", type=Path, help="explicit run directories to serve")
    parser.add_argument(
        "--runs-root",
        dest="runs_roots",
        action="append",
        type=Path,
        default=[],
        metavar="DIR",
        help=(
            "discover every run (has record.json) under this root; "
            "repeat for additional roots"
        ),
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--interval", type=float, default=5.0, help="poll interval in seconds")
    parser.add_argument(
        "--stale-after",
        type=float,
        default=DEFAULT_STALE_AFTER_SECONDS,
        metavar="SECONDS",
        help=(
            "show a nominally running run as stale after this many seconds "
            "without file activity (default: 3600)"
        ),
    )
    parser.add_argument("--write", action="store_true", help="also write transcript.html into each run directory on render")
    parser.add_argument("--verbose", action="store_true", help="log HTTP requests")
    args = parser.parse_args(argv)

    if not args.run_dirs and not args.runs_roots:
        parser.error("give at least one RUN_DIR or --runs-root")

    registry = TranscriptRegistry(
        args.run_dirs,
        args.runs_roots,
        interval=args.interval,
        stale_after=args.stale_after,
        write=args.write,
    )
    registry.log = lambda message: print(f"[{now_utc().strftime('%H:%M:%S')}] {message}", flush=True)
    TranscriptRequestHandler.quiet = not args.verbose
    server = make_server(registry, args.host, args.port)
    host, port = server.server_address[:2]
    print(f"Dungeness transcript server: http://{host}:{port}/  (poll every {args.interval:g}s, Ctrl-C to stop)", flush=True)
    registry.start()
    stopping = threading.Event()

    def request_shutdown(signum: int, _frame: Any) -> None:
        if stopping.is_set():
            return
        stopping.set()
        print(f"\nreceived {signal.Signals(signum).name}; shutting down…", flush=True)
        # shutdown() must run from a thread other than the one in serve_forever().
        threading.Thread(target=server.shutdown, name="shutdown", daemon=True).start()

    # Install explicitly so Ctrl-C works even when SIGINT was inherited as ignored (e.g. `cmd &` in scripts).
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, request_shutdown)
        except (ValueError, OSError):
            pass
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        print("\nshutting down…", flush=True)
    finally:
        registry.stop()
        server.server_close()
        print("server stopped", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
