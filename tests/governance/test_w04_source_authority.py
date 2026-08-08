from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlparse

import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.verify_local_only import (  # noqa: E402
    ALLOWED_W04_SOURCE_URLS,
    is_allowed_config_url,
)

SOURCE_CONFIG = ROOT / "configs/sources/w04-provider.yaml"
RIGHTS_CONFIG = ROOT / "configs/policies/data-rights.yaml"
DECISION_REPORT = ROOT / "reports/phase-gates/W04/provider-rights-decision-required.md"

EXPECTED_COLLECTION_DOI = "10.6084/m9.figshare.c.4415000.v5"
EXPECTED_RELEASE = "2020-01-28T14:24:27Z"
EXPECTED_COUNTRIES = {"England", "France", "Germany", "Italy", "Spain"}
EXPECTED_OBJECTS = {
    "competitions.json": (15073685, 1209, "3dc210a4805dda5337b0ff9f7eaa407a"),
    "teams.json": (15073697, 27404, "1381ff9449f21105090729cf0e086b5b"),
    "players.json": (15073721, 1737347, "f28ddf6326281efeda6488b2169f5609"),
    "matches.zip": (14464622, 645097, "51d80beb17480919f69a53a0152c2d71"),
    "events.zip": (14464685, 77323413, "7c20e8647e7eda58d7838a0c7b1ec6ab"),
    "eventid2name.csv": (21385245, 1001, "46daf16100ece0c743eedc9adcfea162"),
    "tags2name.csv": (21385239, 1754, "e7acb14918d00e40c80a898b1da8fc39"),
}


def _mapping(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return cast(dict[str, Any], loaded)


def test_exact_dataset_version_and_frozen_claim_boundary() -> None:
    source = _mapping(SOURCE_CONFIG)

    assert source["status"] == "authorised_frozen_poc_source"
    assert source["identity"]["collection_version"] == 5
    assert source["identity"]["collection_doi"] == EXPECTED_COLLECTION_DOI
    assert source["identity"]["collection_published_at"] == EXPECTED_RELEASE
    assert source["rights"]["licence_id"] == "CC-BY-4.0"
    assert source["purpose"]["claims_forbidden"] == [
        "current_player_availability",
        "current_scouting_coverage",
        "live_or_operational_provider_continuity",
        "women_or_youth_coverage",
        "prospective_recruitment_effectiveness",
        "provider_commercial_product_equivalence",
    ]


def test_first_pass_is_exactly_five_domestic_2017_18_partitions() -> None:
    source = _mapping(SOURCE_CONFIG)
    coverage = source["coverage"]

    assert coverage["population"] == "male_senior"
    assert coverage["domestic_season"] == "2017/2018"
    assert {entry["country"] for entry in coverage["included_competitions"]} == (EXPECTED_COUNTRIES)
    assert coverage["excluded_from_first_pass"] == [
        "UEFA Euro 2016",
        "FIFA World Cup 2018",
    ]
    assert source["archive_admission"]["matches"] == [
        f"matches_{country}.json" for country in sorted(EXPECTED_COUNTRIES)
    ]
    assert source["archive_admission"]["events"] == [
        f"events_{country}.json" for country in sorted(EXPECTED_COUNTRIES)
    ]
    assert source["archive_admission"]["known_scope_excluded"] == {
        "matches": [
            "matches_European_Championship.json",
            "matches_World_Cup.json",
        ],
        "events": [
            "events_European_Championship.json",
            "events_World_Cup.json",
        ],
    }
    assert (
        source["archive_admission"]["excluded_member_handling"]
        == "verify_directory_entry_but_do_not_extract_or_admit_payload"
    )
    admitted = {
        *source["archive_admission"]["matches"],
        *source["archive_admission"]["events"],
    }
    excluded = {
        *source["archive_admission"]["known_scope_excluded"]["matches"],
        *source["archive_admission"]["known_scope_excluded"]["events"],
    }
    assert admitted.isdisjoint(excluded)


def test_file_allowlist_freezes_figshare_ids_sizes_and_md5() -> None:
    source = _mapping(SOURCE_CONFIG)
    objects = source["objects"]

    assert len(objects) == len(EXPECTED_OBJECTS)
    assert len({item["name"] for item in objects}) == len(objects)
    assert len({item["file_id"] for item in objects}) == len(objects)
    for item in objects:
        file_id, size_bytes, expected_md5 = EXPECTED_OBJECTS[item["name"]]
        assert item["file_id"] == file_id
        assert item["size_bytes"] == size_bytes
        assert item["expected_md5"] == expected_md5
        assert re.fullmatch(r"[0-9a-f]{32}", item["expected_md5"])
        parsed = urlparse(item["url"])
        assert parsed.scheme == "https"
        assert parsed.hostname == "ndownloader.figshare.com"
        assert parsed.path == f"/files/{file_id}"
        assert parsed.params == parsed.query == parsed.fragment == ""


def test_redirect_authority_is_one_exact_short_lived_figshare_delivery_hop() -> None:
    source = _mapping(SOURCE_CONFIG)

    assert source["acquisition"]["redirect_authority"] == {
        "status_code": 302,
        "maximum_hops": 1,
        "destination_scheme": "https",
        "destination_host": "s3-eu-west-1.amazonaws.com",
        "destination_path_template": "pfigshare-u-files/{file_id}/{name}",
        "exact_query_keys": [
            "X-Amz-Algorithm",
            "X-Amz-Credential",
            "X-Amz-Date",
            "X-Amz-Expires",
            "X-Amz-SignedHeaders",
            "X-Amz-Signature",
        ],
        "algorithm": "AWS4-HMAC-SHA256",
        "credential_scope_suffix": "eu-west-1/s3/aws4_request",
        "credential_separator_encoding": "literal_slash",
        "signed_headers": "host",
        "maximum_expiry_seconds": 60,
    }


def test_local_only_verifier_allows_only_exact_reviewed_source_urls(tmp_path: Path) -> None:
    source = _mapping(SOURCE_CONFIG)
    configured_urls = {
        source["rights"]["licence_url"],
        *source["rights"]["evidence"],
        *(item["url"] for item in source["objects"]),
    }

    assert configured_urls == ALLOWED_W04_SOURCE_URLS
    assert all(is_allowed_config_url(SOURCE_CONFIG, url) for url in configured_urls)
    assert not is_allowed_config_url(SOURCE_CONFIG, "https://example.com/unreviewed")
    assert not is_allowed_config_url(
        SOURCE_CONFIG,
        "https://ndownloader.figshare.com/files/14464685?redirect=unreviewed",
    )
    assert not is_allowed_config_url(
        ROOT / "configs/models/unreviewed.yaml", next(iter(configured_urls))
    )
    parent_alias = Path(f"{SOURCE_CONFIG.parent}/../sources/{SOURCE_CONFIG.name}")
    symlink_alias = tmp_path / SOURCE_CONFIG.name
    symlink_alias.symlink_to(SOURCE_CONFIG)
    assert parent_alias != SOURCE_CONFIG
    assert symlink_alias != SOURCE_CONFIG
    assert not is_allowed_config_url(parent_alias, next(iter(configured_urls)))
    assert not is_allowed_config_url(symlink_alias, next(iter(configured_urls)))


def test_rights_allow_derivation_but_local_policy_denies_external_paths() -> None:
    source = _mapping(SOURCE_CONFIG)
    policy = _mapping(RIGHTS_CONFIG)
    classification = policy["w04_authorised_classification"]

    assert source["rights"]["transformation"] == "allowed"
    assert source["rights"]["feature_and_model_use"] == "allowed"
    assert source["rights"]["attribution"]["required"] is True
    assert source["rights"]["project_control"] == {
        "raw_export": "forbidden",
        "network_transfer_after_acquisition": "forbidden",
        "public_or_hosted_display": "forbidden",
        "external_model_call": "forbidden",
    }
    assert classification["exact_version"] == EXPECTED_COLLECTION_DOI
    assert classification["transformation"] == "allowed"
    assert classification["model_training_and_evaluation"] == "allowed"
    assert classification["project_raw_export"] == "forbidden"
    assert classification["external_sharing"] == "forbidden_by_local_project_boundary"
    assert policy["w04_admission"]["raw_export"] == "deny"
    assert policy["w04_admission"]["network_transfer_after_bounded_acquisition"] == "deny"


def test_temporal_availability_fails_closed_at_collection_release() -> None:
    source = _mapping(SOURCE_CONFIG)
    temporal = source["temporal_semantics"]

    assert temporal["source_available_at"] == EXPECTED_RELEASE
    assert temporal["source_available_at_basis"] == "frozen_collection_release_time"
    assert temporal["historical_replay_before_collection_release"] == "forbidden"
    assert temporal["generated_at_is_evidence"] is False
    assert temporal["research_only_when_availability_missing"] is True


def test_source_payload_roots_are_ignored_and_decision_is_not_blocked() -> None:
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
    report = DECISION_REPORT.read_text(encoding="utf-8")

    assert "data/source/*" in ignored
    assert "data/working/*" in ignored
    assert "Status: **DECIDED" in report
    assert "Status: **BLOCKED" not in report
    assert EXPECTED_COLLECTION_DOI in report
