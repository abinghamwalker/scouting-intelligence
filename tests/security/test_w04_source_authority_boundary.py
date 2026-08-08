"""Independent adversarial checks for the frozen W04 source authority."""

from __future__ import annotations

import copy
import re
import socket
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import pytest
import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.verify_local_only import (  # noqa: E402
    ALLOWED_W04_SOURCE_URLS,
    is_allowed_config_url,
)

SOURCE_CONFIG = ROOT / "configs/sources/w04-provider.yaml"
RIGHTS_CONFIG = ROOT / "configs/policies/data-rights.yaml"
DATASET_CARD = ROOT / "docs/dataset-cards/w04-source.md"
DECISION_REPORT = ROOT / "reports/phase-gates/W04/provider-rights-decision-required.md"
PREFLIGHT_REPORT = ROOT / "reports/phase-gates/W04/archive-directory-preflight.md"
REDIRECT_PREFLIGHT_REPORT = ROOT / "reports/phase-gates/W04/download-redirect-preflight.md"

COLLECTION_DOI = "10.6084/m9.figshare.c.4415000.v5"
COLLECTION_RELEASE = "2020-01-28T14:24:27Z"
DOMESTIC_COUNTRIES = ("England", "France", "Germany", "Italy", "Spain")
KNOWN_SCOPE_EXCLUDED = {
    "matches": (
        "matches_European_Championship.json",
        "matches_World_Cup.json",
    ),
    "events": (
        "events_European_Championship.json",
        "events_World_Cup.json",
    ),
}
FORBIDDEN_CLAIMS = {
    "current_player_availability",
    "current_scouting_coverage",
    "live_or_operational_provider_continuity",
    "women_or_youth_coverage",
    "prospective_recruitment_effectiveness",
    "provider_commercial_product_equivalence",
}
REDIRECT_QUERY_KEYS = (
    "X-Amz-Algorithm",
    "X-Amz-Credential",
    "X-Amz-Date",
    "X-Amz-Expires",
    "X-Amz-SignedHeaders",
    "X-Amz-Signature",
)
REDIRECT_AUTHORITY = {
    "status_code": 302,
    "maximum_hops": 1,
    "destination_scheme": "https",
    "destination_host": "s3-eu-west-1.amazonaws.com",
    "destination_path_template": "pfigshare-u-files/{file_id}/{name}",
    "exact_query_keys": list(REDIRECT_QUERY_KEYS),
    "algorithm": "AWS4-HMAC-SHA256",
    "credential_scope_suffix": "eu-west-1/s3/aws4_request",
    "credential_separator_encoding": "literal_slash",
    "signed_headers": "host",
    "maximum_expiry_seconds": 60,
}


@pytest.fixture(autouse=True)
def deny_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep every independent authority challenge local and document-only."""

    def denied_connection(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("authority review must not open a network connection")

    monkeypatch.setattr(socket, "create_connection", denied_connection)


def _mapping(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return cast(dict[str, Any], loaded)


def test_url_exception_rejects_equivalent_but_unreviewed_url_variants() -> None:
    reviewed_url = "https://ndownloader.figshare.com/files/15073685"
    variants = {
        "http://ndownloader.figshare.com/files/15073685",
        "https://NDOWNLOADER.FIGSHARE.COM/files/15073685",
        "https://ndownloader.figshare.com:443/files/15073685",
        "https://ndownloader.figshare.com/files/15073685/",
        "https://ndownloader.figshare.com/files//15073685",
        "https://ndownloader.figshare.com/files/%31%35%30%37%33%36%38%35",
        "https://ndownloader.figshare.com/files/15073685?download=1",
        "https://ndownloader.figshare.com/files/15073685#fragment",
        "https://user@ndownloader.figshare.com/files/15073685",
        f" {reviewed_url}",
    }

    assert reviewed_url in ALLOWED_W04_SOURCE_URLS
    assert is_allowed_config_url(SOURCE_CONFIG, reviewed_url)
    assert all(not is_allowed_config_url(SOURCE_CONFIG, variant) for variant in variants)


def test_url_exception_rejects_nonliteral_authority_path_variants(
    tmp_path: Path,
) -> None:
    reviewed_url = "https://ndownloader.figshare.com/files/15073685"
    parent_variant = Path(f"{SOURCE_CONFIG.parent}/../sources/{SOURCE_CONFIG.name}")
    symlink_variant = tmp_path / "w04-provider-alias.yaml"
    symlink_variant.symlink_to(SOURCE_CONFIG)

    assert parent_variant != SOURCE_CONFIG
    assert symlink_variant != SOURCE_CONFIG
    assert is_allowed_config_url(SOURCE_CONFIG, reviewed_url)
    accepted_variants = [
        variant
        for variant in (parent_variant, symlink_variant)
        if is_allowed_config_url(variant, reviewed_url)
    ]
    assert accepted_variants == []


def _assert_rights_inheritance(
    source: dict[str, Any],
    policy: dict[str, Any],
) -> None:
    source_rights = source["rights"]
    project_control = source_rights["project_control"]
    classification = policy["w04_authorised_classification"]
    admission = policy["w04_admission"]

    assert source_rights["raw_redistribution"] == "allowed_with_attribution"
    assert source_rights["commercial_use"] == "allowed_with_attribution"
    assert source_rights["attribution"]["required"] is True
    assert project_control == {
        "raw_export": "forbidden",
        "network_transfer_after_acquisition": "forbidden",
        "public_or_hosted_display": "forbidden",
        "external_model_call": "forbidden",
    }
    assert classification["project_raw_export"] == "forbidden"
    assert classification["external_sharing"] == "forbidden_by_local_project_boundary"
    assert classification["cloud_or_remote_storage"] == ("forbidden_by_local_project_boundary")
    assert classification["public_demo"] == "forbidden_by_local_project_boundary"
    assert classification["derivatives_inherit"] == [
        "source_manifest_id",
        "licence",
        "attribution",
        "change_notice",
        "frozen_historical_claim_boundary",
    ]
    assert admission["raw_export"] == "deny"
    assert admission["network_transfer_after_bounded_acquisition"] == "deny"


@pytest.mark.parametrize(
    ("document", "path", "weakened_value"),
    (
        ("source", ("rights", "project_control", "raw_export"), "allowed"),
        (
            "source",
            ("rights", "project_control", "network_transfer_after_acquisition"),
            "allowed",
        ),
        (
            "policy",
            ("w04_authorised_classification", "external_sharing"),
            "allowed_with_attribution",
        ),
        ("policy", ("w04_admission", "raw_export"), "allow"),
    ),
)
def test_upstream_cc_by_grant_cannot_weaken_project_denials(
    document: str,
    path: tuple[str, ...],
    weakened_value: str,
) -> None:
    source = _mapping(SOURCE_CONFIG)
    policy = _mapping(RIGHTS_CONFIG)
    _assert_rights_inheritance(source, policy)

    target = source if document == "source" else policy
    mutated = copy.deepcopy(target)
    cursor = mutated
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = weakened_value

    with pytest.raises(AssertionError):
        _assert_rights_inheritance(
            mutated if document == "source" else source,
            mutated if document == "policy" else policy,
        )


def _assert_domestic_archive_scope(source: dict[str, Any]) -> None:
    coverage = source["coverage"]
    archive = source["archive_admission"]
    expected_matches = [f"matches_{country}.json" for country in DOMESTIC_COUNTRIES]
    expected_events = [f"events_{country}.json" for country in DOMESTIC_COUNTRIES]
    expected_excluded = {
        archive_group: list(members) for archive_group, members in KNOWN_SCOPE_EXCLUDED.items()
    }

    assert coverage["population"] == "male_senior"
    assert coverage["domestic_season"] == "2017/2018"
    assert [item["source_file_suffix"] for item in coverage["included_competitions"]] == (
        list(DOMESTIC_COUNTRIES)
    )
    assert archive["matches"] == expected_matches
    assert archive["events"] == expected_events
    assert archive["known_scope_excluded"] == expected_excluded
    assert (
        archive["excluded_member_handling"]
        == "verify_directory_entry_but_do_not_extract_or_admit_payload"
    )
    assert all(
        re.fullmatch(r"(?:matches|events)_(?:England|France|Germany|Italy|Spain)\.json", member)
        for member in (*archive["matches"], *archive["events"])
    )
    for archive_group in ("matches", "events"):
        admitted = archive[archive_group]
        excluded = archive["known_scope_excluded"][archive_group]
        assert len(admitted) == len(set(admitted)) == 5
        assert len(excluded) == len(set(excluded)) == 2
        assert set(admitted).isdisjoint(excluded)
    assert archive["reject_unknown_members"] is True
    assert archive["reject_links"] is True
    assert archive["reject_absolute_or_parent_paths"] is True


def _preflight_directory_entries(report: str, archive_title: str) -> tuple[str, ...]:
    section = report.split(f"## {archive_title} object", maxsplit=1)[1]
    section = section.split("## ", maxsplit=1)[0]
    lines = (line.strip() for line in section.splitlines())
    return tuple(
        line.removeprefix("- `").removesuffix("`")
        for line in lines
        if line.startswith("- `") and line.endswith("`")
    )


@pytest.mark.parametrize(
    ("archive_group", "archive_title"),
    (("events", "Events"), ("matches", "Matches")),
)
def test_archive_scope_matches_exact_recorded_seven_entry_preflight(
    archive_group: str,
    archive_title: str,
) -> None:
    """Each ZIP has five admitted and two exact scope-excluded directory entries."""
    source = _mapping(SOURCE_CONFIG)
    _assert_domestic_archive_scope(source)
    archive = source["archive_admission"]
    declared = {
        *archive[archive_group],
        *archive["known_scope_excluded"][archive_group],
    }
    observed = _preflight_directory_entries(
        PREFLIGHT_REPORT.read_text(encoding="utf-8"),
        archive_title,
    )

    assert len(observed) == len(set(observed)) == 7
    assert set(observed) == declared


def test_known_tournament_members_are_disjoint_and_have_no_payload_authority() -> None:
    """Directory verification does not grant extraction or admission authority."""
    source = _mapping(SOURCE_CONFIG)
    archive = source["archive_admission"]
    _assert_domestic_archive_scope(source)

    assert (
        archive["excluded_member_handling"]
        == "verify_directory_entry_but_do_not_extract_or_admit_payload"
    )
    for archive_group, excluded_members in KNOWN_SCOPE_EXCLUDED.items():
        assert set(excluded_members).isdisjoint(archive[archive_group])

    for authority_artifact in (
        DATASET_CARD.read_text(encoding="utf-8"),
        DECISION_REPORT.read_text(encoding="utf-8"),
        PREFLIGHT_REPORT.read_text(encoding="utf-8"),
    ):
        normalised = " ".join(authority_artifact.lower().split())
        assert re.search(r"\bnot\b.{0,80}\bextract", normalised)
        assert re.search(r"\bnot\b.{0,80}\badmit", normalised)


@pytest.mark.parametrize(
    ("archive_group", "excluded_member"),
    (
        ("matches", "matches_European_Championship.json"),
        ("matches", "matches_World_Cup.json"),
        ("events", "events_European_Championship.json"),
        ("events", "events_World_Cup.json"),
    ),
)
def test_scope_excluded_members_cannot_be_reclassified_as_admitted(
    archive_group: str,
    excluded_member: str,
) -> None:
    source = _mapping(SOURCE_CONFIG)
    _assert_domestic_archive_scope(source)
    mutated = copy.deepcopy(source)
    mutated["archive_admission"][archive_group].append(excluded_member)

    with pytest.raises(AssertionError):
        _assert_domestic_archive_scope(mutated)


@pytest.mark.parametrize(
    ("archive_group", "unknown_member"),
    (
        ("matches", "matches_Portugal.json"),
        ("matches", "matches_Europe.json"),
        ("matches", "README.txt"),
        ("events", "events_Portugal.json"),
        ("events", "events_Europe.json"),
        ("events", "metadata.json"),
    ),
)
def test_any_other_archive_member_remains_unknown_and_denied(
    archive_group: str,
    unknown_member: str,
) -> None:
    source = _mapping(SOURCE_CONFIG)
    archive = source["archive_admission"]
    declared = {
        *archive[archive_group],
        *archive["known_scope_excluded"][archive_group],
    }

    assert unknown_member not in declared
    assert archive["reject_unknown_members"] is True

    mutated = copy.deepcopy(source)
    mutated["archive_admission"][archive_group].append(unknown_member)
    with pytest.raises(AssertionError):
        _assert_domestic_archive_scope(mutated)


@pytest.mark.parametrize(
    ("archive_group", "membership_class"),
    (
        ("matches", "admitted"),
        ("matches", "excluded"),
        ("events", "admitted"),
        ("events", "excluded"),
    ),
)
def test_duplicate_archive_members_fail_the_frozen_scope(
    archive_group: str,
    membership_class: str,
) -> None:
    source = _mapping(SOURCE_CONFIG)
    _assert_domestic_archive_scope(source)
    mutated = copy.deepcopy(source)
    members = (
        mutated["archive_admission"][archive_group]
        if membership_class == "admitted"
        else mutated["archive_admission"]["known_scope_excluded"][archive_group]
    )
    members.append(members[0])

    with pytest.raises(AssertionError):
        _assert_domestic_archive_scope(mutated)


@pytest.mark.parametrize(
    ("archive_group", "unreviewed_member"),
    (
        ("matches", "matches_Europe.json"),
        ("events", "events_World_Cup.json"),
        ("events", "events_Portugal.json"),
        ("matches", "../matches_England.json"),
    ),
)
def test_tournament_unknown_and_unsafe_archive_members_cannot_enter_scope(
    archive_group: str,
    unreviewed_member: str,
) -> None:
    source = _mapping(SOURCE_CONFIG)
    _assert_domestic_archive_scope(source)
    mutated = copy.deepcopy(source)
    mutated["archive_admission"][archive_group].append(unreviewed_member)

    with pytest.raises(AssertionError):
        _assert_domestic_archive_scope(mutated)


def test_archive_safety_switches_are_all_mandatory() -> None:
    source = _mapping(SOURCE_CONFIG)
    for safeguard in (
        "reject_unknown_members",
        "reject_links",
        "reject_absolute_or_parent_paths",
    ):
        mutated = copy.deepcopy(source)
        mutated["archive_admission"][safeguard] = False
        with pytest.raises(AssertionError):
            _assert_domestic_archive_scope(mutated)


def _assert_temporal_authority(source: dict[str, Any]) -> None:
    temporal = source["temporal_semantics"]
    assert source["identity"]["collection_published_at"] == COLLECTION_RELEASE
    assert temporal["source_available_at"] == COLLECTION_RELEASE
    assert temporal["source_available_at_basis"] == "frozen_collection_release_time"
    assert temporal["historical_replay_before_collection_release"] == "forbidden"
    assert temporal["generated_at_is_evidence"] is False
    assert temporal["late_data_policy"] == "no_inference_before_collection_release"
    assert temporal["research_only_when_availability_missing"] is True


def test_collection_release_is_the_immutable_availability_floor() -> None:
    source = _mapping(SOURCE_CONFIG)
    _assert_temporal_authority(source)

    for weakened_field in ("source_available_at", "source_available_at_basis"):
        mutated = copy.deepcopy(source)
        mutated["temporal_semantics"][weakened_field] = (
            "2020-01-28T14:24:26Z"
            if weakened_field == "source_available_at"
            else "file_acquisition_time"
        )
        with pytest.raises(AssertionError):
            _assert_temporal_authority(mutated)

    mutated = copy.deepcopy(source)
    mutated["temporal_semantics"]["historical_replay_before_collection_release"] = "allowed"
    with pytest.raises(AssertionError):
        _assert_temporal_authority(mutated)


def _assert_claim_boundary(source: dict[str, Any]) -> None:
    allowed = set(source["purpose"]["claims_allowed"])
    forbidden = set(source["purpose"]["claims_forbidden"])
    assert allowed == {
        "frozen_historical_engineering_evidence",
        "frozen_historical_player_retrieval_evidence",
    }
    assert forbidden == FORBIDDEN_CLAIMS
    assert allowed.isdisjoint(forbidden)


@pytest.mark.parametrize("forbidden_claim", sorted(FORBIDDEN_CLAIMS))
def test_current_live_population_and_effectiveness_claims_cannot_be_admitted(
    forbidden_claim: str,
) -> None:
    source = _mapping(SOURCE_CONFIG)
    _assert_claim_boundary(source)
    mutated = copy.deepcopy(source)
    mutated["purpose"]["claims_forbidden"].remove(forbidden_claim)
    mutated["purpose"]["claims_allowed"].append(forbidden_claim)

    with pytest.raises(AssertionError):
        _assert_claim_boundary(mutated)


def test_authority_identity_and_restrictions_are_consistent_across_artifacts() -> None:
    source = _mapping(SOURCE_CONFIG)
    policy = _mapping(RIGHTS_CONFIG)
    card = DATASET_CARD.read_text(encoding="utf-8")
    decision = DECISION_REPORT.read_text(encoding="utf-8")
    classification = policy["w04_authorised_classification"]

    assert source["identity"]["collection_doi"] == COLLECTION_DOI
    assert source["identity"]["collection_published_at"] == COLLECTION_RELEASE
    assert classification["source_config"] == "configs/sources/w04-provider.yaml"
    assert classification["exact_version"] == COLLECTION_DOI
    assert classification["licence"] == source["rights"]["licence_id"]
    assert classification["current_or_prospective_scouting_claim"] == "forbidden"
    for artifact in (card, decision):
        assert COLLECTION_DOI in artifact
        assert COLLECTION_RELEASE in artifact
        assert "raw export" in artifact.lower()
        assert "external" in artifact.lower()
        assert "current" in artifact.lower()


def _assert_redirect_authority(source: dict[str, Any]) -> None:
    acquisition = source["acquisition"]

    assert acquisition["method"] == "unauthenticated_https_file_download"
    assert acquisition["credentials_required"] is False
    assert acquisition["account_required"] is False
    assert acquisition["redirect_authority"] == REDIRECT_AUTHORITY
    assert len(source["objects"]) == 7
    assert len({item["file_id"] for item in source["objects"]}) == 7
    assert len({item["name"] for item in source["objects"]}) == 7
    for item in source["objects"]:
        assert item["url"] == (f"https://ndownloader.figshare.com/files/{item['file_id']}")


def _signed_redirect_url(
    source_object: Mapping[str, Any],
    *,
    scheme: str = "https",
    authority: str = "s3-eu-west-1.amazonaws.com",
    path: str | None = None,
    query_overrides: Mapping[str, str] | None = None,
    omit_query: tuple[str, ...] = (),
    extra_query: tuple[tuple[str, str], ...] = (),
    fragment: str = "",
) -> str:
    query = {
        "X-Amz-Algorithm": "AWS4-HMAC-SHA256",
        "X-Amz-Credential": ("SYNTHETICACCESS1234/20260729/eu-west-1/s3/aws4_request"),
        "X-Amz-Date": "20260729T120000Z",
        "X-Amz-Expires": "60",
        "X-Amz-SignedHeaders": "host",
        "X-Amz-Signature": "a" * 64,
    }
    query.update(query_overrides or {})
    pairs = (
        tuple((key, query[key]) for key in REDIRECT_QUERY_KEYS if key not in omit_query)
        + extra_query
    )
    destination_path = path or (
        f"/pfigshare-u-files/{source_object['file_id']}/{source_object['name']}"
    )
    return urlunsplit(
        (
            scheme,
            authority,
            destination_path,
            urlencode(pairs),
            fragment,
        )
    )


def _redirect_is_authorised(
    source: dict[str, Any],
    source_object: Mapping[str, Any],
    *,
    status_code: int,
    hop_number: int,
    destination_url: str,
) -> bool:
    """Consumer-side proof that the declaration is sufficient to fail closed."""

    authority = source["acquisition"]["redirect_authority"]
    if source_object not in source["objects"]:
        return False
    if status_code != authority["status_code"] or hop_number != authority["maximum_hops"]:
        return False

    parsed = urlsplit(destination_url)
    if (
        parsed.scheme != authority["destination_scheme"]
        or parsed.netloc != authority["destination_host"]
        or parsed.path
        != (
            "/"
            + authority["destination_path_template"].format(
                file_id=source_object["file_id"],
                name=source_object["name"],
            )
        )
        or parsed.fragment
    ):
        return False

    raw_pairs = parsed.query.split("&")
    raw_keys = [pair.partition("=")[0] for pair in raw_pairs]
    if len(raw_pairs) != len(authority["exact_query_keys"]) or set(raw_keys) != set(
        authority["exact_query_keys"]
    ):
        return False
    try:
        parsed_pairs = parse_qsl(
            parsed.query,
            keep_blank_values=True,
            strict_parsing=True,
        )
    except ValueError:
        return False
    if len(parsed_pairs) != len(authority["exact_query_keys"]):
        return False
    query = dict(parsed_pairs)
    if (
        set(query) != set(authority["exact_query_keys"])
        or query["X-Amz-Algorithm"] != authority["algorithm"]
        or query["X-Amz-SignedHeaders"] != authority["signed_headers"]
    ):
        return False

    credential_match = re.fullmatch(
        (
            r"(?P<access_key>[A-Z0-9]{16,128})/"
            r"(?P<date>[0-9]{8})/" + re.escape(authority["credential_scope_suffix"])
        ),
        query["X-Amz-Credential"],
    )
    date_match = re.fullmatch(
        r"(?P<date>[0-9]{8})T(?P<time>[0-9]{6})Z",
        query["X-Amz-Date"],
    )
    try:
        time.strptime(query["X-Amz-Date"], "%Y%m%dT%H%M%SZ")
    except ValueError:
        return False
    expiry = query["X-Amz-Expires"]
    if (
        credential_match is None
        or date_match is None
        or credential_match["date"] != date_match["date"]
        or re.fullmatch(r"[1-9][0-9]*", expiry) is None
        or int(expiry) > authority["maximum_expiry_seconds"]
        or re.fullmatch(r"[0-9a-f]{64}", query["X-Amz-Signature"]) is None
    ):
        return False
    return True


def test_redirect_authority_is_exact_and_matches_recorded_preflight() -> None:
    source = _mapping(SOURCE_CONFIG)
    _assert_redirect_authority(source)

    card = DATASET_CARD.read_text(encoding="utf-8")
    decision = DECISION_REPORT.read_text(encoding="utf-8")
    preflight = REDIRECT_PREFLIGHT_REPORT.read_text(encoding="utf-8")
    for artifact in (card, preflight):
        normalised = " ".join(artifact.split())
        assert "s3-eu-west-1.amazonaws.com" in normalised
        assert "60 seconds" in normalised or "60-second" in normalised
        assert re.search(r"\b(?:one|single)\b.{0,80}\b(?:hop|HTTP 302)\b", normalised)
    normalised_decision = " ".join(decision.split())
    assert "normative source config" in normalised_decision
    assert "60 seconds" in normalised_decision
    assert re.search(
        r"\b(?:one|single)\b.{0,80}\b(?:hop|HTTP 302)\b",
        normalised_decision,
    )
    assert "Observed expiry: 10 seconds" in preflight
    assert "No response body or dataset record was downloaded" in preflight


@pytest.mark.parametrize(
    ("field", "weakened_value"),
    (
        ("status_code", 301),
        ("maximum_hops", 2),
        ("destination_scheme", "http"),
        ("destination_host", "s3.amazonaws.com"),
        ("destination_path_template", "{file_id}/{name}"),
        ("exact_query_keys", list(REDIRECT_QUERY_KEYS[:-1])),
        ("exact_query_keys", list(reversed(REDIRECT_QUERY_KEYS))),
        ("exact_query_keys", [*REDIRECT_QUERY_KEYS, REDIRECT_QUERY_KEYS[-1]]),
        ("exact_query_keys", [*REDIRECT_QUERY_KEYS, "unreviewed"]),
        ("algorithm", "AWS4-HMAC-SHA1"),
        ("credential_scope_suffix", "us-east-1/s3/aws4_request"),
        ("signed_headers", "host;x-amz-security-token"),
        ("maximum_expiry_seconds", 61),
    ),
)
def test_redirect_declaration_cannot_be_broadened(
    field: str,
    weakened_value: object,
) -> None:
    source = _mapping(SOURCE_CONFIG)
    _assert_redirect_authority(source)
    mutated = copy.deepcopy(source)
    mutated["acquisition"]["redirect_authority"][field] = weakened_value

    with pytest.raises(AssertionError):
        _assert_redirect_authority(mutated)


def test_each_exact_source_object_has_one_conforming_synthetic_delivery_url() -> None:
    source = _mapping(SOURCE_CONFIG)
    _assert_redirect_authority(source)

    for source_object in source["objects"]:
        assert _redirect_is_authorised(
            source,
            source_object,
            status_code=302,
            hop_number=1,
            destination_url=_signed_redirect_url(source_object),
        )


@pytest.mark.parametrize(
    ("status_code", "hop_number", "url_changes"),
    (
        (301, 1, {}),
        (307, 1, {}),
        (302, 0, {}),
        (302, 2, {}),
        (302, 1, {"scheme": "http"}),
        (302, 1, {"authority": "s3.amazonaws.com"}),
        (302, 1, {"authority": "s3-eu-west-1.amazonaws.com:443"}),
        (302, 1, {"authority": "user@s3-eu-west-1.amazonaws.com"}),
        (302, 1, {"path": "/pfigshare-u-files/999/competitions.json"}),
        (302, 1, {"path": "/pfigshare-u-files/15073685/teams.json"}),
        (302, 1, {"path": "/other-bucket/15073685/competitions.json"}),
        (302, 1, {"fragment": "unreviewed"}),
        (
            302,
            1,
            {"query_overrides": {"X-Amz-Algorithm": "AWS4-HMAC-SHA1"}},
        ),
        (
            302,
            1,
            {
                "query_overrides": {
                    "X-Amz-Credential": ("SYNTHETICACCESS1234/20260729/us-east-1/s3/aws4_request")
                }
            },
        ),
        (
            302,
            1,
            {
                "query_overrides": {
                    "X-Amz-Credential": ("SYNTHETICACCESS1234/20260728/eu-west-1/s3/aws4_request")
                }
            },
        ),
        (
            302,
            1,
            {"query_overrides": {"X-Amz-Date": "2026-07-29T12:00:00Z"}},
        ),
        (
            302,
            1,
            {"query_overrides": {"X-Amz-Date": "20260230T120000Z"}},
        ),
        (302, 1, {"query_overrides": {"X-Amz-Expires": "0"}}),
        (302, 1, {"query_overrides": {"X-Amz-Expires": "01"}}),
        (302, 1, {"query_overrides": {"X-Amz-Expires": "61"}}),
        (302, 1, {"query_overrides": {"X-Amz-Expires": "unbounded"}}),
        (
            302,
            1,
            {"query_overrides": {"X-Amz-SignedHeaders": "host;x-amz-date"}},
        ),
        (302, 1, {"query_overrides": {"X-Amz-Signature": "A" * 64}}),
        (302, 1, {"query_overrides": {"X-Amz-Signature": "a" * 63}}),
        (302, 1, {"query_overrides": {"X-Amz-Signature": "g" * 64}}),
        (302, 1, {"omit_query": ("X-Amz-Signature",)}),
        (302, 1, {"extra_query": (("X-Amz-Signature", "b" * 64),)}),
        (302, 1, {"extra_query": (("unreviewed", "1"),)}),
    ),
)
def test_redirect_variants_fail_closed(
    status_code: int,
    hop_number: int,
    url_changes: dict[str, Any],
) -> None:
    source = _mapping(SOURCE_CONFIG)
    source_object = source["objects"][0]

    assert not _redirect_is_authorised(
        source,
        source_object,
        status_code=status_code,
        hop_number=hop_number,
        destination_url=_signed_redirect_url(source_object, **url_changes),
    )


def test_redirect_cannot_authorise_a_new_source_object_or_url_exception() -> None:
    source = _mapping(SOURCE_CONFIG)
    reviewed_object = source["objects"][0]
    unreviewed_object = copy.deepcopy(reviewed_object)
    unreviewed_object["file_id"] = 99_999_999
    unreviewed_object["name"] = "unreviewed.json"
    unreviewed_object["url"] = "https://ndownloader.figshare.com/files/99999999"
    reviewed_destination = _signed_redirect_url(reviewed_object)
    unreviewed_destination = _signed_redirect_url(unreviewed_object)

    assert not _redirect_is_authorised(
        source,
        unreviewed_object,
        status_code=302,
        hop_number=1,
        destination_url=unreviewed_destination,
    )
    assert reviewed_destination not in ALLOWED_W04_SOURCE_URLS
    assert unreviewed_destination not in ALLOWED_W04_SOURCE_URLS
    assert not is_allowed_config_url(SOURCE_CONFIG, reviewed_destination)
    assert not is_allowed_config_url(SOURCE_CONFIG, unreviewed_destination)


def test_delivery_hop_grants_no_credentials_storage_or_external_transfer() -> None:
    source = _mapping(SOURCE_CONFIG)
    policy = _mapping(RIGHTS_CONFIG)
    classification = policy["w04_authorised_classification"]
    admission = policy["w04_admission"]

    assert source["acquisition"]["credentials_required"] is False
    assert source["acquisition"]["account_required"] is False
    assert source["rights"]["project_control"] == {
        "raw_export": "forbidden",
        "network_transfer_after_acquisition": "forbidden",
        "public_or_hosted_display": "forbidden",
        "external_model_call": "forbidden",
    }
    assert classification["cloud_or_remote_storage"] == ("forbidden_by_local_project_boundary")
    assert classification["external_sharing"] == ("forbidden_by_local_project_boundary")
    assert classification["public_demo"] == "forbidden_by_local_project_boundary"
    assert admission["network_transfer_after_bounded_acquisition"] == "deny"

    preflight = " ".join(REDIRECT_PREFLIGHT_REPORT.read_text(encoding="utf-8").lower().split())
    assert "not a project credential" in preflight
    assert "does not authorise cloud storage" in preflight
    assert "post-acquisition network transfer" in preflight
    assert "public endpoints" in preflight
    assert "any new source" in preflight
