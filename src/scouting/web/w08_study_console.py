"""Browser-first operator console for the local W08 representative-user study.

The console removes routine shell interaction while preserving the evidence boundary:
it prepares synthetic loopback runtimes and de-identified capture records, but it
cannot provide consent, participant outcomes, independent review, or gate acceptance.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import secrets
import socket
import tempfile
import threading
import time
from collections.abc import Callable, Mapping
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

import uvicorn
import yaml  # type: ignore[import-untyped]
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape

from scouting.contracts import WorkflowEvidenceOrigin
from scouting.web.w08 import create_w08_app

ROOT = Path(__file__).resolve().parents[3]
TEMPLATES = ROOT / "apps/web/templates/w08_study_console"
STATIC = ROOT / "apps/web/static/w08-study-console"
CAPTURE_TEMPLATE = ROOT / "reports/verification/W08/moderated-study-capture-template.yaml"
PROTOCOL = ROOT / "reports/verification/W08/moderated-study-protocol.md"
PILOT_GATE_REPORT = ROOT / "reports/phase-gates/W08/pilot-gate-report.json"

GATE_PARTICIPANT_CODES = tuple(f"W08-U{index:02d}" for index in range(1, 6))
PILOT_PARTICIPANT_CODES = tuple(f"W08-P{index:02d}" for index in range(1, 4))
RESPONSIBILITIES = (
    ("analyst", "Analyst"),
    ("scout", "Scout"),
    ("approver_or_meeting_decision", "Approver / meeting decision"),
)
OUTCOMES = ("NOT_RUN", "PASS", "FAIL", "ASSISTED")
TASKS = (
    {
        "id": "T1",
        "key": "T1_role_brief",
        "title": "Create and submit a role brief",
        "role": "Analyst",
        "summary": (
            "Create a synthetic brief with a responsibility, hard constraint, weighted "
            "preference and exemplar; submit it and explain preserved history."
        ),
    },
    {
        "id": "T2",
        "key": "T2_approval_and_retrieval_boundary",
        "title": "Approve and inspect the retrieval boundary",
        "role": "Approver → analyst → approver",
        "summary": (
            "Approve the exact brief version, create its replay link, identify model/data "
            "versions and explain why LIMITED is not a recommendation."
        ),
    },
    {
        "id": "T3",
        "key": "T3_scout_review_disagreement_amendment",
        "title": "Assign and complete scout review",
        "role": "Analyst → scout",
        "summary": (
            "Assign a synthetic candidate, add the structured observation, disagreement, "
            "next action and amendment; inspect both versions."
        ),
    },
    {
        "id": "T4",
        "key": "T4_shortlist_meeting_history",
        "title": "Exercise shortlist decisions",
        "role": "Approver",
        "summary": (
            "Hold, reject and reconsider the candidate using controlled reasons, then "
            "confirm the complete immutable decision history."
        ),
    },
    {
        "id": "T5",
        "key": "T5_export_and_audit",
        "title": "Export and verify audit evidence",
        "role": "Authorised role → admin denial",
        "summary": (
            "Create the local evidence pack, inspect classification, versions, limitations, "
            "checksum and audit receipt, then exercise the denied admin path."
        ),
    },
    {
        "id": "T6",
        "key": "T6_expiry_conflict_failure_recovery",
        "title": "Recover from expiry, conflict and failure",
        "role": "Current actor",
        "summary": (
            "Use the console to expire the exact session, recover a stale two-tab write "
            "and retry an invalid export without partial records."
        ),
    },
    {
        "id": "T7",
        "key": "T7_keyboard_mobile_interpretation",
        "title": "Keyboard, mobile and interpretation check",
        "role": "Any authorised role",
        "summary": (
            "Repeat an action by keyboard, inspect the mobile layout and explain what "
            "workflow evidence can—and cannot—establish."
        ),
    },
)
TASK_BY_ID = {str(task["id"]): task for task in TASKS}
_CODE_PATTERN = re.compile(r"W08-(?:U0[1-5]|P0[1-3])\Z")
_MODERATOR_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,31}\Z")
_MAX_PORT = 65535


class StudyConsoleError(ValueError):
    """Fail-closed study-console input or runtime error."""


@dataclass
class RuntimeSession:
    """One in-memory control handle for a fresh participant runtime."""

    participant_code: str
    root: Path
    port: int
    app: FastAPI
    server: uvicorn.Server
    thread: threading.Thread
    personas: dict[str, dict[str, str]]
    started_at_utc: str
    guided_study: bool
    receipt: dict[str, object] | None = None
    error: str | None = None

    @property
    def running(self) -> bool:
        return self.thread.is_alive() and not self.server.should_exit


@dataclass
class StudyConsoleManager:
    """Own sequential loopback runtimes without converting mechanics into evidence."""

    study_parent: Path
    expire_session: Callable[[Path, str], int]
    create_receipt: Callable[[Path], dict[str, object]]
    console_base_url: str
    sessions: dict[str, RuntimeSession] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self) -> None:
        self.study_parent = self.study_parent.expanduser().resolve()
        if not self.study_parent.is_dir() or self.study_parent == Path(self.study_parent.anchor):
            raise StudyConsoleError("invalid local study parent")

    def active(self) -> RuntimeSession | None:
        with self._lock:
            return next((session for session in self.sessions.values() if session.running), None)

    def start(self, participant_code: str, port: int) -> RuntimeSession:
        code = _participant_code(participant_code)
        bounded_port = _port(port)
        with self._lock:
            if any(session.running for session in self.sessions.values()):
                raise StudyConsoleError("stop the active participant runtime first")
            if code in self.sessions:
                raise StudyConsoleError("this participant runtime has already been prepared")
            root = (self.study_parent / f"w08-study-{code}").resolve()
            if root.parent != self.study_parent or root.exists() or root.is_symlink():
                raise StudyConsoleError("participant study root must be new and unused")
            if not _port_available(bounded_port):
                raise StudyConsoleError("participant port is unavailable")
            root.mkdir(mode=0o700, parents=False, exist_ok=False)
            try:
                guided_study = _is_pilot(code)
                participant_app = create_w08_app(
                    evidence_origin=WorkflowEvidenceOrigin.HUMAN_ENTERED_LOCAL,
                    database_path=root / "w08-study.sqlite3",
                    allowed_root=root,
                    seed=True,
                    guided_study=guided_study,
                    study_console_url=(
                        f"{self.console_base_url}/participants/{code}" if guided_study else None
                    ),
                )
                config = uvicorn.Config(
                    participant_app,
                    host="127.0.0.1",
                    port=bounded_port,
                    log_level="warning",
                    access_log=False,
                )
                server = uvicorn.Server(config)
                thread = threading.Thread(
                    target=server.run,
                    name=f"w08-study-{code}",
                    daemon=True,
                )
                session = RuntimeSession(
                    participant_code=code,
                    root=root,
                    port=bounded_port,
                    app=participant_app,
                    server=server,
                    thread=thread,
                    personas=copy.deepcopy(participant_app.state.synthetic_personas),
                    started_at_utc=_utc_now(),
                    guided_study=guided_study,
                )
                self.sessions[code] = session
                thread.start()
            except Exception:
                if "participant_app" in locals():
                    participant_app.state.engine.dispose()
                raise
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and session.thread.is_alive():
            if session.server.started:
                return session
            time.sleep(0.02)
        session.app.state.engine.dispose()
        session.error = "participant runtime could not start"
        raise StudyConsoleError(session.error)

    def stop(self, participant_code: str) -> RuntimeSession:
        code = _participant_code(participant_code)
        with self._lock:
            session = self.sessions.get(code)
            if session is None or not session.running:
                raise StudyConsoleError("participant runtime is not active")
            session.server.should_exit = True
        session.thread.join(timeout=10)
        if session.thread.is_alive():
            raise StudyConsoleError("participant runtime did not stop safely")
        session.app.state.engine.dispose()
        session.personas = {}
        try:
            session.receipt = self.create_receipt(session.root)
        except (OSError, ValueError) as error:
            session.error = str(error)
            raise StudyConsoleError("runtime stopped, but its receipt is unavailable") from error
        return session

    def expire(self, participant_code: str, role: str) -> int:
        code = _participant_code(participant_code)
        with self._lock:
            session = self.sessions.get(code)
            if session is None or not session.running:
                raise StudyConsoleError("participant runtime is not active")
            persona = session.personas.get(role)
            if persona is None:
                raise StudyConsoleError("unknown synthetic role")
            actor_id = persona["actor_id"]
            root = session.root
        return self.expire_session(root, actor_id)

    def shutdown(self) -> None:
        active = self.active()
        if active is None:
            return
        try:
            self.stop(active.participant_code)
        except StudyConsoleError:
            active.server.force_exit = True


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _participant_code(value: str) -> str:
    if not _CODE_PATTERN.fullmatch(value):
        raise StudyConsoleError("invalid participant code")
    return value


def _is_pilot(participant_code: str) -> bool:
    return _participant_code(participant_code) in PILOT_PARTICIPANT_CODES


def _port(value: int | str) -> int:
    try:
        port = int(value)
    except (TypeError, ValueError) as error:
        raise StudyConsoleError("invalid participant port") from error
    if not 1024 <= port <= _MAX_PORT:
        raise StudyConsoleError("participant port must be unprivileged")
    return port


def _port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            listener.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(64 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _capture_path(capture_root: Path, participant_code: str) -> Path:
    code = _participant_code(participant_code)
    root = capture_root.resolve()
    path = root / f"{code}.yaml"
    if path.parent.resolve() != root or path.is_symlink():
        raise StudyConsoleError("invalid participant capture path")
    return path


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise StudyConsoleError("participant capture is unavailable") from error
    if not isinstance(value, dict):
        raise StudyConsoleError("participant capture is unavailable")
    return value


def _load_json_mapping(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise StudyConsoleError("pilot gate report is unavailable") from error
    if not isinstance(value, dict):
        raise StudyConsoleError("pilot gate report is unavailable")
    return value


def _load_capture(capture_root: Path, participant_code: str) -> dict[str, Any] | None:
    path = _capture_path(capture_root, participant_code)
    if not path.exists():
        return None
    return _load_yaml_mapping(path)


def _atomic_write_capture(path: Path, capture: Mapping[str, Any]) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.is_symlink():
        raise StudyConsoleError("invalid participant capture path")
    rendered = yaml.safe_dump(dict(capture), sort_keys=False, allow_unicode=False)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(rendered)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_name = temporary.name
        os.replace(temporary_name, path)
    finally:
        if temporary_name is not None and Path(temporary_name).exists():
            Path(temporary_name).unlink()


def _capture_ready(capture: dict[str, Any] | None, *, pilot: bool) -> bool:
    if capture is None:
        return False
    if pilot:
        return bool(capture.get("pilot", {}).get("development_progression_boundary_acknowledged"))
    return bool(capture.get("participant", {}).get("consent_obtained"))


def _capture_status(capture: dict[str, Any] | None, *, pilot: bool = False) -> dict[str, object]:
    if capture is None:
        return {
            "label": "Pilot available" if pilot else "Not started",
            "tone": "pilot" if pilot else "idle",
            "passed": 0,
            "ready": False,
            "consented": False,
        }
    participant = capture.get("participant", {})
    tasks = capture.get("tasks", {})
    outcomes = [str(tasks.get(str(task["key"]), {}).get("outcome", "NOT_RUN")) for task in TASKS]
    passed = outcomes.count("PASS")
    consented = bool(participant.get("consent_obtained"))
    ready = _capture_ready(capture, pilot=pilot)
    if pilot and ready and passed == len(TASKS):
        return {
            "label": "Pilot tasks complete",
            "tone": "pilot-pass",
            "passed": passed,
            "ready": True,
            "consented": False,
        }
    if pilot and ready:
        return {
            "label": "Pilot in progress",
            "tone": "pilot",
            "passed": passed,
            "ready": True,
            "consented": False,
        }
    if consented and passed == len(TASKS):
        return {
            "label": "Tasks passed",
            "tone": "pass",
            "passed": passed,
            "ready": True,
            "consented": True,
        }
    if consented:
        return {
            "label": "In progress",
            "tone": "active",
            "passed": passed,
            "ready": True,
            "consented": True,
        }
    return {
        "label": "Awaiting consent",
        "tone": "idle",
        "passed": passed,
        "ready": False,
        "consented": False,
    }


def _bounded_text(value: str, *, limit: int, field_name: str, required: bool = False) -> str:
    normalized = value.strip()
    if required and not normalized:
        raise StudyConsoleError(f"{field_name} is required")
    if len(normalized) > limit:
        raise StudyConsoleError(f"{field_name} is too long")
    return normalized


def _boolean_form(form: Mapping[str, str], key: str) -> bool:
    return form.get(key) == "true"


def _nullable_boolean(value: str | None) -> bool | None:
    if value in {None, ""}:
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    raise StudyConsoleError("invalid review measure")


def create_w08_study_console(
    *,
    study_parent: Path,
    capture_root: Path,
    expire_session: Callable[[Path, str], int],
    create_receipt: Callable[[Path], dict[str, object]],
    repository_commit: str | None,
    console_base_url: str = "http://127.0.0.1:8767",
) -> FastAPI:
    """Create the local operator console; caller remains responsible for loopback binding."""
    captures = capture_root.expanduser().resolve()
    if captures == Path(captures.anchor):
        raise StudyConsoleError("invalid participant capture root")
    manager = StudyConsoleManager(
        study_parent,
        expire_session,
        create_receipt,
        console_base_url.rstrip("/"),
    )
    pilot_captures = (manager.study_parent / "w08-pilot-captures").resolve()
    if pilot_captures.parent != manager.study_parent:
        raise StudyConsoleError("invalid pilot capture root")
    csrf_token = secrets.token_urlsafe(32)
    templates = Environment(
        loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(("html",))
    )

    def capture_directory(code: str) -> Path:
        return pilot_captures if _is_pilot(code) else captures

    def participant_capture(code: str) -> dict[str, Any] | None:
        return _load_capture(capture_directory(code), code)

    def save_capture(code: str, capture: Mapping[str, Any]) -> None:
        _atomic_write_capture(_capture_path(capture_directory(code), code), capture)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> Any:
        yield
        active = manager.active()
        manager.shutdown()
        if active is not None and active.receipt is not None:
            capture = participant_capture(active.participant_code)
            if capture is not None:
                capture["session"].update(
                    {
                        "local_database_receipt_sha256": active.receipt["database_sha256"],
                        "local_export_root_receipt_sha256": active.receipt[
                            "export_manifest_sha256"
                        ],
                    }
                )
                save_capture(active.participant_code, capture)

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    app.state.manager = manager
    app.state.capture_root = captures
    app.state.pilot_capture_root = pilot_captures
    app.state.repository_commit = repository_commit
    app.mount(
        "/static/w08-study-console",
        StaticFiles(directory=STATIC),
        name="w08-study-console-static",
    )

    @app.middleware("http")
    async def local_headers(request: Request, call_next: Any) -> Any:
        if request.url.hostname not in {"testserver", "127.0.0.1", "localhost", None}:
            return HTMLResponse("not found", status_code=404)
        response = await call_next(request)
        response.headers.update(
            {
                "Content-Security-Policy": (
                    "default-src 'self'; style-src 'self'; img-src 'self'; "
                    "connect-src 'self'; base-uri 'none'; form-action 'self'; "
                    "frame-ancestors 'none'"
                ),
                "Cache-Control": "no-store",
                "Referrer-Policy": "no-referrer",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
            }
        )
        response.set_cookie(
            "w08_console_csrf",
            csrf_token,
            httponly=True,
            samesite="strict",
            secure=False,
        )
        return response

    def page(request: Request, template: str, **context: Any) -> HTMLResponse:
        return HTMLResponse(
            templates.get_template(template).render(
                request=request,
                csrf=csrf_token,
                tasks=TASKS,
                responsibilities=RESPONSIBILITIES,
                outcomes=OUTCOMES,
                **context,
            )
        )

    def failure(request: Request, message: str, status: int = 400) -> HTMLResponse:
        response = page(request, "error.html", title="Action unavailable", message=message)
        response.status_code = status
        return response

    async def form_values(request: Request) -> dict[str, str]:
        if request.headers.get("content-type", "").split(";", 1)[0].lower() != (
            "application/x-www-form-urlencoded"
        ):
            raise StudyConsoleError("unsupported form")
        limit = 64 * 1024
        declared = request.headers.get("content-length")
        if declared is not None and (not declared.isdecimal() or int(declared) > limit):
            raise StudyConsoleError("oversized form")
        chunks: list[bytes] = []
        size = 0
        async for chunk in request.stream():
            if len(chunk) > limit - size:
                raise StudyConsoleError("oversized form")
            size += len(chunk)
            chunks.append(chunk)
        parsed = parse_qs(
            b"".join(chunks).decode("utf-8", "strict"),
            keep_blank_values=True,
            strict_parsing=False,
        )
        values = {key: items[-1] for key, items in parsed.items() if items}
        if (
            values.get("csrf") != csrf_token
            or request.cookies.get("w08_console_csrf") != csrf_token
        ):
            raise StudyConsoleError("local form expired; reload and try again")
        return values

    @app.exception_handler(StudyConsoleError)
    async def invalid_console_action(request: Request, error: StudyConsoleError) -> HTMLResponse:
        return failure(request, str(error))

    @app.get("/", response_class=HTMLResponse)
    def dashboard(request: Request) -> HTMLResponse:
        participants: list[dict[str, object]] = []
        for offset, code in enumerate(GATE_PARTICIPANT_CODES):
            capture = participant_capture(code)
            participants.append(
                {
                    "code": code,
                    "default_port": 18768 + offset,
                    "capture": capture,
                    **_capture_status(capture, pilot=False),
                }
            )
        pilot_participants: list[dict[str, object]] = []
        for offset, code in enumerate(PILOT_PARTICIPANT_CODES):
            capture = participant_capture(code)
            pilot_participants.append(
                {
                    "code": code,
                    "default_port": 18868 + offset,
                    "capture": capture,
                    **_capture_status(capture, pilot=True),
                }
            )
        passed_participants = sum(
            1
            for participant in participants
            if participant["consented"] and participant["passed"] == len(TASKS)
        )
        submitted_pilots = sum(
            1
            for participant in pilot_participants
            if isinstance(participant["capture"], dict)
            and participant["capture"].get("status")
            == "PILOT_CAPTURE_COMPLETE_PENDING_G_W08A_REVIEW"
        )
        pilot_gate = _load_json_mapping(PILOT_GATE_REPORT)
        return page(
            request,
            "dashboard.html",
            title="W08 Study Console",
            participants=participants,
            pilot_participants=pilot_participants,
            submitted_pilots=submitted_pilots,
            pilot_gate=pilot_gate,
            passed_participants=passed_participants,
            active=manager.active(),
            sessions=manager.sessions,
        )

    @app.get("/participants/{participant_code}", response_class=HTMLResponse)
    def participant(participant_code: str, request: Request) -> HTMLResponse:
        code = _participant_code(participant_code)
        pilot = _is_pilot(code)
        capture = participant_capture(code)
        session = manager.sessions.get(code)
        return page(
            request,
            "participant.html",
            title=f"{code} · W08 Study Console",
            participant_code=code,
            is_pilot=pilot,
            capture=capture,
            capture_status=_capture_status(capture, pilot=pilot),
            session=session,
            protocol_sha256=_sha256_file(PROTOCOL),
            repository_commit=repository_commit,
        )

    @app.post("/participants/{participant_code}/consent", response_model=None)
    async def record_consent(
        participant_code: str, request: Request
    ) -> RedirectResponse | HTMLResponse:
        code = _participant_code(participant_code)
        pilot = _is_pilot(code)
        form = await form_values(request)
        if pilot:
            if not _boolean_form(form, "pilot_progression_acknowledged"):
                raise StudyConsoleError(
                    "acknowledge the pilot progression and representative-acceptance boundary"
                )
            selected_responsibilities = ["operator_rehearsal"]
        else:
            selected_responsibilities = [
                key for key, _ in RESPONSIBILITIES if form.get(f"responsibility_{key}") == "true"
            ]
            if not selected_responsibilities:
                raise StudyConsoleError("select at least one representative responsibility")
            if not _boolean_form(form, "qualification_confirmed"):
                raise StudyConsoleError("study-owner qualification must be confirmed")
            if not _boolean_form(form, "consent_obtained"):
                raise StudyConsoleError("participant consent is required before the session")
        moderator_code = _bounded_text(
            form.get("moderator_code", ""), limit=32, field_name="moderator code", required=True
        )
        if not _MODERATOR_PATTERN.fullmatch(moderator_code):
            raise StudyConsoleError("moderator code must be de-identified")
        capture = participant_capture(code)
        if capture is None:
            capture = _load_yaml_mapping(CAPTURE_TEMPLATE)
        existing_code = capture.get("participant", {}).get("participant_code")
        if existing_code not in {None, code}:
            raise StudyConsoleError("participant capture code does not match")
        if pilot:
            capture["record_type"] = "w08_pilot_progression_capture"
            capture["status"] = "PILOT_IN_PROGRESS_DEVELOPMENT_EVIDENCE"
            capture["pilot"] = {
                "gate_id": "G-W08A",
                "progression_gate_evidence": True,
                "representative_acceptance_evidence": False,
                "development_progression_boundary_acknowledged": True,
                "purpose": "end_to_end_smoke_test_and_development_progression_review",
            }
        else:
            capture["status"] = "IN_PROGRESS"
        capture["participant"].update(
            {
                "participant_code": code,
                "representative_responsibilities": selected_responsibilities,
                "qualification_confirmed_by_authorised_study_owner": not pilot,
                "consent_obtained": not pilot,
            }
        )
        capture["session"].update(
            {
                "study_runtime_commit": repository_commit,
                "protocol_sha256": _sha256_file(PROTOCOL),
                "started_at_utc": capture["session"].get("started_at_utc") or _utc_now(),
                "moderator_code": moderator_code,
            }
        )
        save_capture(code, capture)
        return RedirectResponse(f"/participants/{code}", status_code=303)

    @app.post("/participants/{participant_code}/start", response_model=None)
    async def start_runtime(
        participant_code: str, request: Request
    ) -> RedirectResponse | HTMLResponse:
        code = _participant_code(participant_code)
        form = await form_values(request)
        capture = participant_capture(code)
        if capture is None or not _capture_ready(capture, pilot=_is_pilot(code)):
            raise StudyConsoleError(
                "complete pilot setup before starting"
                if _is_pilot(code)
                else "record qualification and consent before starting"
            )
        session = manager.start(code, _port(form.get("port", "")))
        capture["session"].update(
            {
                "started_at_utc": session.started_at_utc,
                "loopback_only_confirmed": True,
            }
        )
        save_capture(code, capture)
        return RedirectResponse(f"/participants/{code}", status_code=303)

    @app.post("/participants/{participant_code}/expire", response_model=None)
    async def expire_actor(
        participant_code: str, request: Request
    ) -> RedirectResponse | HTMLResponse:
        code = _participant_code(participant_code)
        form = await form_values(request)
        manager.expire(code, form.get("role", ""))
        return RedirectResponse(f"/participants/{code}#task-T6", status_code=303)

    @app.post("/participants/{participant_code}/stop", response_model=None)
    async def stop_runtime(
        participant_code: str, request: Request
    ) -> RedirectResponse | HTMLResponse:
        code = _participant_code(participant_code)
        await form_values(request)
        session = manager.stop(code)
        capture = participant_capture(code)
        if capture is not None and session.receipt is not None:
            capture["session"].update(
                {
                    "local_database_receipt_sha256": session.receipt["database_sha256"],
                    "local_export_root_receipt_sha256": session.receipt["export_manifest_sha256"],
                }
            )
            save_capture(code, capture)
        return RedirectResponse(f"/participants/{code}#receipt", status_code=303)

    @app.post("/participants/{participant_code}/tasks/{task_id}", response_model=None)
    async def update_task(
        participant_code: str, task_id: str, request: Request
    ) -> RedirectResponse | HTMLResponse:
        code = _participant_code(participant_code)
        task = TASK_BY_ID.get(task_id)
        if task is None:
            raise StudyConsoleError("unknown study task")
        capture = participant_capture(code)
        if capture is None or not _capture_ready(capture, pilot=_is_pilot(code)):
            raise StudyConsoleError(
                "complete pilot setup before recording outcomes"
                if _is_pilot(code)
                else "record consent before recording outcomes"
            )
        form = await form_values(request)
        outcome = form.get("outcome", "")
        if outcome not in OUTCOMES:
            raise StudyConsoleError("invalid task outcome")
        try:
            elapsed = int(form.get("elapsed_seconds", "0"))
            assistance = int(form.get("assistance_count", "0"))
        except ValueError as error:
            raise StudyConsoleError("elapsed time and assistance must be whole numbers") from error
        if not 0 <= elapsed <= 86400 or not 0 <= assistance <= 100:
            raise StudyConsoleError("task measures are outside the supported range")
        identifiers = [
            item.strip()
            for item in form.get("retained_identifiers", "").splitlines()
            if item.strip()
        ]
        if len(identifiers) > 20 or any(len(item) > 200 for item in identifiers):
            raise StudyConsoleError("too many or oversized retained identifiers")
        observation = _bounded_text(
            form.get("deidentified_observation", ""),
            limit=1000,
            field_name="de-identified observation",
        )
        capture["tasks"][str(task["key"])] = {
            "outcome": outcome,
            "elapsed_seconds": elapsed,
            "assistance_count": assistance,
            "retained_identifiers": identifiers,
            "deidentified_observation": observation or None,
        }
        save_capture(code, capture)
        return RedirectResponse(f"/participants/{code}#task-{task_id}", status_code=303)

    @app.post("/participants/{participant_code}/review", response_model=None)
    async def update_review(
        participant_code: str, request: Request
    ) -> RedirectResponse | HTMLResponse:
        code = _participant_code(participant_code)
        capture = participant_capture(code)
        if not capture:
            raise StudyConsoleError("participant capture has not started")
        form = await form_values(request)
        interpretation = form.get("evidence_boundary_interpretation", "") or None
        if interpretation not in {None, "CORRECT", "PARTIAL", "UNSUPPORTED_INFERENCE"}:
            raise StudyConsoleError("invalid evidence-boundary interpretation")
        confidence_value = form.get("unaided_confidence_1_to_5", "")
        confidence = int(confidence_value) if confidence_value else None
        if confidence is not None and not 1 <= confidence <= 5:
            raise StudyConsoleError("confidence must be between 1 and 5")
        capture["measures"].update(
            {
                "evidence_boundary_interpretation": interpretation,
                "access_denial_disclosed_object_existence": _nullable_boolean(
                    form.get("access_denial_disclosed_object_existence")
                ),
                "material_history_identifiable_and_reversible": _nullable_boolean(
                    form.get("material_history_identifiable_and_reversible")
                ),
                "keyboard_blocker": _nullable_boolean(form.get("keyboard_blocker")),
                "missing_label_landmark_or_visible_focus": _nullable_boolean(
                    form.get("missing_label_landmark_or_visible_focus")
                ),
                "horizontal_overflow": _nullable_boolean(form.get("horizontal_overflow")),
                "unrecoverable_state": _nullable_boolean(form.get("unrecoverable_state")),
                "unaided_confidence_1_to_5": confidence,
            }
        )
        capture["session"]["non_loopback_requests_observed"] = _nullable_boolean(
            form.get("non_loopback_requests_observed")
        )
        findings = [item.strip() for item in form.get("findings", "").splitlines() if item.strip()]
        if len(findings) > 20 or any(len(item) > 500 for item in findings):
            raise StudyConsoleError("too many or oversized de-identified findings")
        capture["findings"] = findings
        save_capture(code, capture)
        return RedirectResponse(f"/participants/{code}#review", status_code=303)

    @app.post("/participants/{participant_code}/complete", response_model=None)
    async def complete_capture(
        participant_code: str, request: Request
    ) -> RedirectResponse | HTMLResponse:
        code = _participant_code(participant_code)
        capture = participant_capture(code)
        if not capture:
            raise StudyConsoleError("participant capture has not started")
        form = await form_values(request)
        pilot = _is_pilot(code)
        required_attestations = (
            ("participant_reviewed", "no_sensitive_data", "no_protected_w06")
            if pilot
            else (
                "participant_reviewed",
                "no_sensitive_data",
                "no_substitution",
                "no_protected_w06",
            )
        )
        if any(not _boolean_form(form, key) for key in required_attestations):
            raise StudyConsoleError("all completion attestations must be confirmed")
        capture["participant"]["participant_reviewed_deidentified_record"] = True
        capture["attestation"][
            "no_name_contact_password_real_player_judgement_or_sensitive_data_recorded"
        ] = _boolean_form(form, "no_sensitive_data")
        capture["attestation"]["no_automated_persona_or_moderator_substituted_for_participant"] = (
            False if pilot else _boolean_form(form, "no_substitution")
        )
        capture["attestation"]["no_protected_w06_output_opened_or_reconstructed"] = _boolean_form(
            form, "no_protected_w06"
        )
        capture["session"]["completed_at_utc"] = _utc_now()
        capture["status"] = (
            "PILOT_CAPTURE_COMPLETE_PENDING_G_W08A_REVIEW"
            if pilot
            else "CAPTURE_COMPLETE_PENDING_MASTER_REPRODUCTION"
        )
        save_capture(code, capture)
        return RedirectResponse(f"/participants/{code}#completion", status_code=303)

    return app
