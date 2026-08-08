"""Run or inspect the frozen W10 football-expert relevance evaluation."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scouting.evaluation.expert_relevance import (
    DEFAULT_PRESENTATION_PATH,
    DEFAULT_PROTOCOL_PATH,
    DEFAULT_QUERY_PACK_PATH,
    absent_formal_evidence_status,
    load_frozen_presentation,
    load_frozen_protocol,
    load_frozen_query_pack,
    load_protocol_approval,
    run_one_use_formal_evaluation,
)
from scouting.storage.formats import canonical_json_bytes


def _utc_datetime(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected an ISO-8601 datetime") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != UTC.utcoffset(parsed):
        raise argparse.ArgumentTypeError("evaluation datetime must be UTC")
    return parsed.astimezone(UTC)


def _uuid(value: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected a UUID") from exc


def _add_authority_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL_PATH)
    parser.add_argument("--query-pack", type=Path, default=DEFAULT_QUERY_PACK_PATH)
    parser.add_argument("--presentation", type=Path, default=DEFAULT_PRESENTATION_PATH)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    status = commands.add_parser(
        "status",
        help="report absent formal evidence without accepting protected input",
    )
    _add_authority_arguments(status)
    status.add_argument("--approval", type=Path)

    run = commands.add_parser("run", help="consume one protected formal invocation")
    _add_authority_arguments(run)
    run.add_argument("--approval", type=Path, required=True)
    run.add_argument("--protected-input", type=Path, required=True)
    run.add_argument("--output-directory", type=Path, required=True)
    run.add_argument("--invocation-id", type=_uuid, required=True)
    run.add_argument("--evaluated-at", type=_utc_datetime, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    protocol = load_frozen_protocol(arguments.protocol)
    query_pack = load_frozen_query_pack(arguments.query_pack)
    presentation = load_frozen_presentation(arguments.presentation)

    if arguments.command == "status":
        approval = (
            load_protocol_approval(arguments.approval) if arguments.approval is not None else None
        )
        payload = absent_formal_evidence_status(
            protocol,
            query_pack,
            presentation,
            approval,
        )
    else:
        approval = load_protocol_approval(arguments.approval)
        artifacts = run_one_use_formal_evaluation(
            protocol,
            query_pack,
            presentation,
            approval,
            protected_input_path=arguments.protected_input,
            output_directory=arguments.output_directory,
            invocation_id=arguments.invocation_id,
            evaluated_at=arguments.evaluated_at,
        )
        payload = {
            "schema_version": 1,
            "decision": artifacts.result.decision,
            "result_digest": artifacts.result.result_digest,
            "receipt_digest": artifacts.receipt_digest,
            "output_directory": str(arguments.output_directory.absolute()),
        }
    sys.stdout.buffer.write(canonical_json_bytes(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
