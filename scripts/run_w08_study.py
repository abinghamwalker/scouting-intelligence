"""Prepare and mechanically verify a fresh, local-only W08 study runtime.

The commands deliberately provide synthetic test setup and mechanical receipts only.
They do not record participation, consent, task outcomes, judgements, or gate evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import threading
import webbrowser
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

import uvicorn
from sqlalchemy import text

from scouting.contracts import WorkflowEvidenceOrigin
from scouting.storage.embedded import create_embedded_engine
from scouting.web.w08 import create_w08_app
from scouting.web.w08_study_console import StudyConsoleError, create_w08_study_console

DATABASE_NAME = "w08-study.sqlite3"
EVIDENCE_PACK_DIRECTORY = Path("data/working/w08-evidence-packs")
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CAPTURE_ROOT = REPOSITORY_ROOT / "reports/verification/W08/participants"
_MIN_UNPRIVILEGED_PORT = 1024
_MAX_PORT = 65535


class StudyHarnessError(ValueError):
    """A fail-closed local study-runtime preparation error."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(64 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _resolved_study_root(value: Path, *, must_exist: bool) -> Path:
    unresolved = value.expanduser()
    if unresolved.is_symlink():
        raise StudyHarnessError("invalid local study root")
    root = unresolved.resolve()
    if root == Path(root.anchor):
        raise StudyHarnessError("invalid local study root")
    if must_exist:
        if not root.is_dir():
            raise StudyHarnessError("local study runtime unavailable")
    elif root.exists():
        raise StudyHarnessError("study root must be new and unused")
    return root


def _database_path(root: Path) -> Path:
    database = root / DATABASE_NAME
    if not database.is_file() or database.is_symlink():
        raise StudyHarnessError("local study runtime unavailable")
    if database.resolve().parent != root:
        raise StudyHarnessError("local study runtime unavailable")
    return database


def _validated_port(port: int) -> int:
    if not _MIN_UNPRIVILEGED_PORT <= port <= _MAX_PORT:
        raise StudyHarnessError("port must be an unprivileged TCP port")
    return port


def serve(study_root: Path, port: int) -> None:
    """Seed exactly one new synthetic runtime and bind it to loopback only."""
    root = _resolved_study_root(study_root, must_exist=False)
    bounded_port = _validated_port(port)
    root.mkdir(mode=0o700, parents=True, exist_ok=False)
    app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.HUMAN_ENTERED_LOCAL,
        database_path=root / DATABASE_NAME,
        allowed_root=root,
        seed=True,
    )
    print("Synthetic setup accounts only; runtime entries are human_entered_local.")
    print("This labels provenance mechanically and is not representative-user evidence.")
    for role, values in app.state.synthetic_personas.items():
        print(f"{role}: actor_id={values['actor_id']} password={values['password']}")
    print(f"Starting only http://127.0.0.1:{bounded_port}; do not retain these credentials.")
    uvicorn.run(app, host="127.0.0.1", port=bounded_port, log_level="warning", access_log=False)


def expire_session(study_root: Path, actor_id: str) -> int:
    """Expire one exact active synthetic actor session without reading its token."""
    root = _resolved_study_root(study_root, must_exist=True)
    database = _database_path(root)
    try:
        actor = UUID(actor_id)
    except (TypeError, ValueError) as exc:
        raise StudyHarnessError("study session unavailable") from exc
    engine = create_embedded_engine(database, allowed_root=root, initialize=False)
    try:
        with engine.begin() as connection:
            sessions = (
                connection.execute(
                    text(
                        "SELECT session_id,issued_at FROM local_sessions WHERE actor_id=:actor_id "
                        "AND revoked_at IS NULL AND expires_at > :now ORDER BY issued_at"
                    ),
                    {"actor_id": actor, "now": datetime.now(UTC).isoformat()},
                )
                .mappings()
                .all()
            )
            if len(sessions) != 1:
                raise StudyHarnessError("study session unavailable")
            expired_at = (
                datetime.fromisoformat(str(sessions[0]["issued_at"])) + timedelta(microseconds=1)
            ).isoformat()
            updated = connection.execute(
                text(
                    "UPDATE local_sessions SET expires_at=:expired_at "
                    "WHERE session_id=:session_id AND actor_id=:actor_id "
                    "AND revoked_at IS NULL"
                ),
                {
                    "expired_at": expired_at,
                    "session_id": sessions[0]["session_id"],
                    "actor_id": actor,
                },
            ).rowcount
            if updated != 1:
                raise StudyHarnessError("study session unavailable")
    finally:
        engine.dispose()
    return 1


def _evidence_manifest(root: Path) -> dict[str, object]:
    evidence_root = root / EVIDENCE_PACK_DIRECTORY
    if not evidence_root.exists():
        return {"files": [], "schema_version": 1}
    if not evidence_root.is_dir() or evidence_root.is_symlink():
        raise StudyHarnessError("local evidence receipt unavailable")
    files: list[dict[str, object]] = []
    for path in sorted(evidence_root.rglob("*")):
        if path.is_symlink():
            raise StudyHarnessError("local evidence receipt unavailable")
        if path.is_dir():
            continue
        if not path.is_file():
            raise StudyHarnessError("local evidence receipt unavailable")
        relative = path.relative_to(evidence_root).as_posix()
        files.append(
            {"path": relative, "sha256": _sha256_file(path), "size_bytes": path.stat().st_size}
        )
    return {"files": files, "schema_version": 1}


def receipt(study_root: Path) -> dict[str, object]:
    """Return non-sensitive, deterministic byte receipts after the server has stopped."""
    root = _resolved_study_root(study_root, must_exist=True)
    database = _database_path(root)
    if any((root / f"{DATABASE_NAME}{suffix}").exists() for suffix in ("-wal", "-shm")):
        raise StudyHarnessError("study runtime must be stopped before receipt")
    manifest = _evidence_manifest(root)
    files = manifest["files"]
    if not isinstance(files, list):
        raise StudyHarnessError("local evidence receipt unavailable")
    canonical_manifest = _canonical_json(manifest)
    return {
        "database_sha256": _sha256_file(database),
        "export_file_count": len(files),
        "export_manifest": manifest,
        "export_manifest_sha256": hashlib.sha256(canonical_manifest).hexdigest(),
        "status": "mechanical_receipt_only",
    }


def _repository_commit() -> str | None:
    """Read the checked-out commit without invoking Git from the study application."""
    git_path = REPOSITORY_ROOT / ".git"
    if git_path.is_file():
        declaration = git_path.read_text(encoding="utf-8").strip()
        if not declaration.startswith("gitdir: "):
            return None
        git_path = (git_path.parent / declaration.removeprefix("gitdir: ")).resolve()
    head_path = git_path / "HEAD"
    if not head_path.is_file():
        return None
    head = head_path.read_text(encoding="utf-8").strip()
    if not head.startswith("ref: "):
        return head if len(head) == 40 else None
    reference = head.removeprefix("ref: ")
    loose_reference = git_path / reference
    if loose_reference.is_file():
        value = loose_reference.read_text(encoding="utf-8").strip()
        return value if len(value) == 40 else None
    packed_refs = git_path / "packed-refs"
    if packed_refs.is_file():
        for line in packed_refs.read_text(encoding="utf-8").splitlines():
            if line.startswith(("#", "^")):
                continue
            parts = line.split(" ", 1)
            if len(parts) == 2 and parts[1] == reference and len(parts[0]) == 40:
                return parts[0]
    return None


def console(
    *,
    study_parent: Path,
    capture_root: Path,
    port: int,
    open_browser: bool,
) -> None:
    """Run the browser-first study operator console on loopback only."""
    bounded_port = _validated_port(port)
    app = create_w08_study_console(
        study_parent=study_parent,
        capture_root=capture_root,
        expire_session=expire_session,
        create_receipt=receipt,
        repository_commit=_repository_commit(),
        console_base_url=f"http://127.0.0.1:{bounded_port}",
    )
    url = f"http://127.0.0.1:{bounded_port}"
    print(f"W08 Study Console: {url}")
    print(
        "Local operator aid: pilot captures may be submitted for G-W08A review, "
        "but the console cannot accept a gate or create representative-user evidence."
    )
    if open_browser:
        opener = threading.Timer(0.75, webbrowser.open, args=(url,))
        opener.daemon = True
        opener.start()
    uvicorn.run(app, host="127.0.0.1", port=bounded_port, log_level="warning", access_log=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="prepare a local synthetic W08 study runtime")
    commands = parser.add_subparsers(dest="command", required=True)

    serve_command = commands.add_parser("serve", help="create one fresh loopback study runtime")
    serve_command.add_argument("--study-root", type=Path, required=True)
    serve_command.add_argument("--port", type=int, default=8768)

    expiry_command = commands.add_parser(
        "expire-session", help="expire one exact synthetic session"
    )
    expiry_command.add_argument("--study-root", type=Path, required=True)
    expiry_command.add_argument("--actor-id", required=True)

    receipt_command = commands.add_parser(
        "receipt", help="emit post-stop local mechanical receipts"
    )
    receipt_command.add_argument("--study-root", type=Path, required=True)

    console_command = commands.add_parser(
        "console", help="run the browser-first local study operator console"
    )
    console_command.add_argument("--study-parent", type=Path, default=Path("/private/tmp"))
    console_command.add_argument("--capture-root", type=Path, default=DEFAULT_CAPTURE_ROOT)
    console_command.add_argument("--port", type=int, default=8767)
    console_command.add_argument(
        "--no-open-browser", action="store_true", help="do not open the console automatically"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "serve":
            serve(args.study_root, args.port)
            return 0
        if args.command == "expire-session":
            print(
                json.dumps(
                    {"expired_session_count": expire_session(args.study_root, args.actor_id)}
                )
            )
            return 0
        if args.command == "receipt":
            print(json.dumps(receipt(args.study_root), sort_keys=True))
            return 0
        if args.command == "console":
            console(
                study_parent=args.study_parent,
                capture_root=args.capture_root,
                port=args.port,
                open_browser=not args.no_open_browser,
            )
            return 0
    except (OSError, StudyConsoleError, StudyHarnessError) as error:
        print(f"local study harness unavailable: {error}")
        return 2
    raise AssertionError(f"unexpected command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
