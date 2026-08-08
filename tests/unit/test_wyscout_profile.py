from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

_SCRIPT_PATH = Path(__file__).parents[2] / "scripts/profile_wyscout_v5.py"
_SPEC = importlib.util.spec_from_file_location("profile_wyscout_v5", _SCRIPT_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("could not load profile_wyscout_v5.py")
profile_wyscout_v5 = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = profile_wyscout_v5
_SPEC.loader.exec_module(profile_wyscout_v5)

DeclaredFile = profile_wyscout_v5.DeclaredFile
ProfileError = profile_wyscout_v5.ProfileError
build_profile = profile_wyscout_v5.build_profile
iter_json_array = profile_wyscout_v5.iter_json_array
main = profile_wyscout_v5.main


def _write(path: Path, content: bytes) -> tuple[int, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return len(content), hashlib.sha256(content).hexdigest()


def _json_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def _snapshot(tmp_path: Path) -> tuple[Path, str, set[Path]]:
    root = tmp_path / "wyscout-v5"
    direct_payloads = {
        "competitions.json": _json_bytes(
            [{"wyId": 1, "area": {"id": 44, "name": "FABRICATED AREA"}}]
        ),
        "teams.json": _json_bytes(
            [
                {"wyId": 10, "name": "FABRICATED TEAM"},
                {"wyId": 11, "name": "SECOND FABRICATED TEAM"},
            ]
        ),
        "players.json": _json_bytes(
            [{"wyId": 100, "shortName": "PRIVATE PLAYER NAME", "height": None}]
        ),
        "eventid2name.csv": (
            b"event,subevent,event_label,subevent_label\n"
            b"1,10,FABRICATED EVENT,FABRICATED SUBEVENT\n"
        ),
        "tags2name.csv": b"Tag,Label,Description\n101,FABRICATED TAG,FABRICATED DESCRIPTION\n",
    }
    object_records: list[dict[str, object]] = []
    opened_source_paths: set[Path] = set()
    for name, payload in direct_payloads.items():
        relative = f"objects/{name}"
        size, digest = _write(root / relative, payload)
        object_records.append(
            {
                "name": name,
                "object_path": relative,
                "sha256": digest,
                "size_bytes": size,
            }
        )
        opened_source_paths.add((root / relative).resolve())

    for archive_name in ("matches.zip", "events.zip"):
        relative = f"objects/{archive_name}"
        payload = b"THIS ARCHIVE OBJECT MUST NEVER BE OPENED"
        size, digest = _write(root / relative, payload)
        object_records.append(
            {
                "name": archive_name,
                "object_path": relative,
                "sha256": digest,
                "size_bytes": size,
            }
        )

    match_payload = _json_bytes(
        [
            {
                "wyId": 1000,
                "competitionId": 1,
                "duration": "Regular",
                "dateutc": "2020-01-01 12:00:00",
                "teamsData": {
                    "10": {
                        "teamId": 10,
                        "formation": {
                            "lineup": [{"playerId": 100}],
                            "bench": [{"playerId": 999}],
                            "substitutions": [{"minute": 60, "playerIn": 100, "playerOut": 999}],
                        },
                    },
                    "11": {
                        "teamId": 11,
                        "formation": {
                            "lineup": [],
                            "bench": [],
                            "substitutions": "null",
                        },
                    },
                },
            }
        ]
    )
    event_payload = _json_bytes(
        [
            {
                "id": 500,
                "eventId": 1,
                "subEventId": 10,
                "tags": [{"id": 101}],
                "playerId": 100,
                "matchId": 1000,
                "teamId": 10,
                "matchPeriod": "1H",
                "eventSec": 12.345,
                "positions": [{"x": -1, "y": 50}, {"x": 100, "y": 100}],
            },
            {
                "id": 501,
                "eventId": 2,
                "subEventId": 11,
                "tags": [{"id": 999}],
                "playerId": 0,
                "matchId": 1000,
                "teamId": 11,
                "matchPeriod": "2H",
                "eventSec": 0,
                "positions": [{"x": 50, "y": 101}],
            },
        ]
    )
    admitted_records: list[dict[str, object]] = []
    for archive_name, member_name, payload in (
        ("matches.zip", "matches_Fabricated.json", match_payload),
        ("events.zip", "events_Fabricated.json", event_payload),
    ):
        relative = f"archive-members/{member_name}"
        size, digest = _write(root / relative, payload)
        admitted_records.append(
            {
                "archive_name": archive_name,
                "name": member_name,
                "member_path": relative,
                "sha256": digest,
                "size_bytes": size,
            }
        )
        opened_source_paths.add((root / relative).resolve())

    excluded_canary = root / "excluded" / "DO_NOT_OPEN.json"
    _write(excluded_canary, b"DO NOT OPEN")
    manifest = {
        "schema_version": 1,
        "source_id": "wyscout-v5-fabricated",
        "state": "complete",
        "classification": "fabricated-test-only",
        "licence": {"licence_id": "FABRICATED-LICENCE"},
        "acquisition": {
            "source_available_at": "2020-01-28",
            "acquired_at": "2026-07-29T00:00:00Z",
        },
        "objects": object_records,
        "admitted_archive_members": admitted_records,
        "scope_excluded_archive_members": [
            {
                "archive_name": "events.zip",
                "name": "excluded/",
                "disposition": "excluded",
            }
        ],
    }
    manifest_bytes = _json_bytes(manifest)
    manifest_path = root / "completion-manifest.json"
    manifest_path.write_bytes(manifest_bytes)
    opened_source_paths.add(manifest_path.resolve())
    return root, hashlib.sha256(manifest_bytes).hexdigest(), opened_source_paths


def test_profile_is_stable_aggregate_only_and_opens_only_admitted_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, completion_digest, allowed_paths = _snapshot(tmp_path)
    opened_paths: set[Path] = set()
    original_open = Path.open

    def recording_open(path: Path, *args: object, **kwargs: object) -> object:
        opened_paths.add(path.resolve())
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", recording_open)
    first = build_profile(root, completion_digest)
    second = build_profile(root, completion_digest)

    assert first == second
    assert opened_paths <= allowed_paths
    assert (root / "objects/matches.zip").resolve() not in opened_paths
    assert (root / "objects/events.zip").resolve() not in opened_paths
    assert (root / "excluded/DO_NOT_OPEN.json").resolve() not in opened_paths
    report = first.decode()
    assert "PRIVATE PLAYER NAME" not in report
    assert "FABRICATED TEAM" not in report
    assert "FABRICATED EVENT" not in report
    assert "| events | 2 |" in report
    assert "| classification | fabricated-test-only |" in report
    assert "| licence_id | FABRICATED-LICENCE |" in report
    assert "objects/matches.zip" in report
    assert "| matches_Fabricated.json | 1 |" in report
    assert "| events_Fabricated.json | 2 |" in report
    assert "| teamsData key → teams.wyId | 2 | 2 | 0 | 0 | 0 |" in report
    assert "| event matchId → matches.wyId | 2 | 2 | 0 | 0 | 0 |" in report
    assert "| event playerId → players.wyId | 2 | 1 | 0 | 1 | 0 |" in report
    assert "| distinct event record id values | 2 |" in report
    assert "| duplicate event record id values | 0 |" in report
    assert "| event teamId not in referenced match teamsData | 0 |" in report
    assert "| event/member match-partition mismatches | 0 |" in report
    assert "| maximum measured eventSec decimal scale | 3 |" in report
    assert "| literal-null-string substitution containers | 1 |" in report
    assert "| positions with one coordinate | 1 |" in report
    assert "| positions with two coordinates | 1 |" in report
    assert "| coordinate values outside inclusive 0..100 | 2 |" in report
    assert "| 1H | 1 | 1 | 0 | 12.345 | 12.345 | 1 | 12.345 | 12.345 |" in report
    assert "The event maxima are observed lower-bound evidence only." in report


def test_production_cli_rejects_fixture_source_and_output_paths(tmp_path: Path) -> None:
    root, completion_digest, _ = _snapshot(tmp_path)
    output = tmp_path / "profile.md"
    arguments = [
        "--source-root",
        str(root),
        "--output",
        str(output),
        "--expected-completion-sha256",
        completion_digest,
    ]

    assert main(arguments) == 1
    assert not output.exists()
    assert main([*arguments, "--check"]) == 1
    assert not output.exists()


def test_manifest_path_escape_is_rejected_before_source_open(tmp_path: Path) -> None:
    root, _completion_digest, _ = _snapshot(tmp_path)
    manifest_path = root / "completion-manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["objects"][0]["object_path"] = "../escape.json"
    manifest_bytes = _json_bytes(manifest)
    manifest_path.write_bytes(manifest_bytes)

    with pytest.raises(ProfileError, match="normalized relative path"):
        build_profile(root, hashlib.sha256(manifest_bytes).hexdigest())


def test_streaming_parser_rejects_record_over_memory_bound(tmp_path: Path) -> None:
    path = tmp_path / "large.json"
    content = _json_bytes([{"large": "x" * 100}])
    size, digest = _write(path, content)
    declared = DeclaredFile("large.json", path, digest, size)

    with pytest.raises(ProfileError, match="bounded parser limit"):
        list(iter_json_array(declared, chunk_bytes=4, max_buffer_chars=16))
