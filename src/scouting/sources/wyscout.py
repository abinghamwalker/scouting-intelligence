"""Fail-closed local acquisition for the frozen Wyscout Figshare v5 source."""

from __future__ import annotations

import hashlib
import io
import json
import os
import stat
import tempfile
import time
import zipfile
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, Protocol, cast
from urllib.error import URLError
from urllib.parse import parse_qsl, quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

import yaml  # type: ignore[import-untyped]

from scouting.storage import GuardedStorage, canonical_json_bytes

_SOURCE_ID = "wyscout-soccer-match-events-figshare-v5"
_SOURCE_STATUS = "authorised_frozen_poc_source"
_PROVIDER = "Wyscout"
_PUBLISHER = "figshare"
_COLLECTION_ID = 4_415_000
_COLLECTION_VERSION = 5
_COLLECTION_DOI = "10.6084/m9.figshare.c.4415000.v5"
_CLASSIFICATION = "wyscout_figshare_v5_cc_by_4"
_DOWNLOAD_HOST = "ndownloader.figshare.com"
_SOURCE_AVAILABLE_AT = datetime(2020, 1, 28, 14, 24, 27, tzinfo=UTC)
_DATASET_TITLE = "Soccer match event dataset"
_DATASET_AUTHORS = "Pappalardo et al."
_DATA_PAPER_DOI = "10.1038/s41597-019-0247-7"
_LICENCE_NAME = "Creative Commons Attribution 4.0 International"
_LICENCE_ID = "CC-BY-4.0"
_LICENCE_URL = "https://creativecommons.org/licenses/by/4.0/"
_ATTRIBUTION_TEXT = (
    "Data source: Pappalardo et al., Soccer match event dataset, supplied by "
    "Wyscout, figshare collection v5, licensed CC BY 4.0."
)
_CHANGE_NOTICE = (
    "This project normalises source JSON, reconstructs lineup stints and "
    "possessions, and derives player-window aggregates."
)
_PURPOSE_ALLOWED = (
    "local_noncommercial_proof_of_concept",
    "deterministic_raw_to_gold_engineering",
    "feature_and_model_training",
    "model_evaluation",
    "local_internal_ui",
    "attributed_derived_output",
)
_CLAIMS_ALLOWED = (
    "frozen_historical_engineering_evidence",
    "frozen_historical_player_retrieval_evidence",
)
_CLAIMS_FORBIDDEN = (
    "current_player_availability",
    "current_scouting_coverage",
    "live_or_operational_provider_continuity",
    "women_or_youth_coverage",
    "prospective_recruitment_effectiveness",
    "provider_commercial_product_equivalence",
)
_RIGHTS_EVIDENCE = (
    "https://www.nature.com/articles/s41597-019-0247-7",
    "https://doi.org/10.6084/m9.figshare.c.4415000.v5",
)
_INCLUDED_COMPETITIONS = (
    ("England", "England", "English first division"),
    ("France", "France", "French first division"),
    ("Germany", "Germany", "German first division"),
    ("Italy", "Italy", "Italian first division"),
    ("Spain", "Spain", "Spanish first division"),
)
_EXCLUDED_COMPETITIONS = ("UEFA Euro 2016", "FIFA World Cup 2018")
_REFERENCE_COUNTS = {
    "matches_all_seven_competitions": 1_941,
    "events_all_seven_competitions": 3_251_294,
    "players_all_seven_competitions": 4_299,
}
_ABSENT_COVERAGE = (
    "women",
    "youth",
    "native_possession_id",
    "tracking",
    "freeze_frame",
    "record_level_correction_history",
    "first_publication_timestamp_per_record",
)
_VERIFY_STEPS_ORDERED = (
    "exact_url_allowlist",
    "exact_file_name",
    "exact_size_bytes",
    "expected_md5",
    "computed_sha256",
    "safe_archive_members",
)
_REDIRECT_QUERY_KEYS = (
    "X-Amz-Algorithm",
    "X-Amz-Credential",
    "X-Amz-Date",
    "X-Amz-Expires",
    "X-Amz-SignedHeaders",
    "X-Amz-Signature",
)
_REDIRECT_DESTINATION_HOST = "s3-eu-west-1.amazonaws.com"
_REDIRECT_PATH_TEMPLATE = "pfigshare-u-files/{file_id}/{name}"
_REDIRECT_ALGORITHM = "AWS4-HMAC-SHA256"
_REDIRECT_CREDENTIAL_SCOPE = "eu-west-1/s3/aws4_request"
_REDIRECT_CREDENTIAL_SEPARATOR_ENCODING = "literal_slash"
_ACCESS_KEY_CHARACTERS = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
_REVIEWED_OBJECT_IDENTITIES = {
    "competitions.json": (
        7_765_316,
        "10.6084/m9.figshare.7765316.v4",
        15_073_685,
        1_209,
        "3dc210a4805dda5337b0ff9f7eaa407a",
    ),
    "teams.json": (
        7_765_310,
        "10.6084/m9.figshare.7765310.v3",
        15_073_697,
        27_404,
        "1381ff9449f21105090729cf0e086b5b",
    ),
    "players.json": (
        7_765_196,
        "10.6084/m9.figshare.7765196.v3",
        15_073_721,
        1_737_347,
        "f28ddf6326281efeda6488b2169f5609",
    ),
    "matches.zip": (
        7_770_422,
        "10.6084/m9.figshare.7770422.v1",
        14_464_622,
        645_097,
        "51d80beb17480919f69a53a0152c2d71",
    ),
    "events.zip": (
        7_770_599,
        "10.6084/m9.figshare.7770599.v1",
        14_464_685,
        77_323_413,
        "7c20e8647e7eda58d7838a0c7b1ec6ab",
    ),
    "eventid2name.csv": (
        11_743_836,
        "10.6084/m9.figshare.11743836.v1",
        21_385_245,
        1_001,
        "46daf16100ece0c743eedc9adcfea162",
    ),
    "tags2name.csv": (
        11_743_818,
        "10.6084/m9.figshare.11743818.v1",
        21_385_239,
        1_754,
        "e7acb14918d00e40c80a898b1da8fc39",
    ),
}
_OBJECT_NAMES = frozenset(_REVIEWED_OBJECT_IDENTITIES)
_KNOWN_SCOPE_EXCLUDED_SUFFIXES = (
    "European_Championship",
    "World_Cup",
)
_COMPLETION_PATH = "completion-manifest.json"
_CHUNK_SIZE = 1024 * 1024
_MAX_MEMBER_BYTES = 1024 * 1024 * 1024
_MAX_ARCHIVE_BYTES = 4 * 1024 * 1024 * 1024
_MAX_COMPRESSION_RATIO = 200
_MAX_ARCHIVE_MEMBERS = 32


class WyscoutSourceError(RuntimeError):
    """Base failure for configuration, download, admission, or replay."""


class WyscoutConfigError(WyscoutSourceError):
    """Raised when the reviewed source declaration is malformed."""


class WyscoutDownloadError(WyscoutSourceError):
    """Raised when a source object cannot be downloaded and verified."""


class WyscoutArchiveError(WyscoutSourceError):
    """Raised when a ZIP object is unsafe or outside the reviewed member set."""


class WyscoutManifestError(WyscoutSourceError):
    """Raised when completion evidence or its durable payloads conflict."""


@dataclass(frozen=True, slots=True)
class WyscoutSourceObject:
    """One exact object in the reviewed Figshare collection."""

    article_id: int
    article_doi: str
    file_id: int
    name: str
    size_bytes: int
    expected_md5: str
    url: str


@dataclass(frozen=True, slots=True)
class WyscoutRedirectAuthority:
    """Exact one-hop Figshare signed-delivery authority."""

    status_code: int
    maximum_hops: int
    destination_scheme: str
    destination_host: str
    destination_path_template: str
    exact_query_keys: tuple[str, ...]
    algorithm: str
    credential_scope_suffix: str
    credential_separator_encoding: str
    signed_headers: str
    maximum_expiry_seconds: int


@dataclass(frozen=True, slots=True)
class WyscoutSourceConfig:
    """Strict reviewed values needed by acquisition and completion evidence."""

    schema_version: int
    source_id: str
    status: str
    dataset_title: str
    provider: str
    dataset_authors: str
    publisher: str
    collection_id: int
    collection_version: int
    collection_doi: str
    collection_published_at: datetime
    data_paper_doi: str
    licence_name: str
    licence_id: str
    licence_url: str
    attribution_text: str
    change_notice: str
    objects: tuple[WyscoutSourceObject, ...]
    matches_members: tuple[str, ...]
    events_members: tuple[str, ...]
    matches_excluded_members: tuple[str, ...]
    events_excluded_members: tuple[str, ...]
    excluded_member_handling: str
    source_available_at: datetime
    source_available_at_basis: str
    redirect_authority: WyscoutRedirectAuthority
    destination_root: str
    working_root: str

    @property
    def allowed_urls(self) -> frozenset[str]:
        return frozenset(source_object.url for source_object in self.objects)

    def archive_members_for(self, object_name: str) -> tuple[str, ...]:
        if object_name == "matches.zip":
            return self.matches_members
        if object_name == "events.zip":
            return self.events_members
        raise WyscoutArchiveError("object is not an admitted archive")

    def excluded_archive_members_for(self, object_name: str) -> tuple[str, ...]:
        if object_name == "matches.zip":
            return self.matches_excluded_members
        if object_name == "events.zip":
            return self.events_excluded_members
        raise WyscoutArchiveError("object is not an admitted archive")


@dataclass(frozen=True, slots=True)
class VerifiedDownload:
    """Verified bytes and both required content identities."""

    source_object: WyscoutSourceObject
    payload: bytes
    md5: str
    sha256: str


@dataclass(frozen=True, slots=True)
class AdmittedArchiveMember:
    """One safe, fully read member of an admitted archive."""

    archive_name: str
    name: str
    payload: bytes
    sha256: str


@dataclass(frozen=True, slots=True)
class ScopeExcludedArchiveMember:
    """Directory-only evidence for a known member whose payload is not opened."""

    archive_name: str
    name: str
    compressed_size_bytes: int
    declared_size_bytes: int
    directory_crc32: str


@dataclass(frozen=True, slots=True)
class ArchiveAdmission:
    """Admitted payloads plus directory-only evidence for scoped exclusions."""

    admitted_members: tuple[AdmittedArchiveMember, ...]
    scope_excluded_members: tuple[ScopeExcludedArchiveMember, ...]


@dataclass(frozen=True, slots=True)
class WyscoutAcquisitionResult:
    """Stable completion-manifest result for a new acquisition or replay."""

    manifest_relative_path: str
    manifest_bytes: bytes
    manifest_sha256: str
    manifest_created: bool


class DownloadStream(Protocol):
    """Small response boundary used by the real and synthetic transports."""

    status: int
    headers: Mapping[str, str]

    def geturl(self) -> str: ...

    def read(self, amount: int = -1) -> bytes: ...

    def close(self) -> None: ...


type DownloadOpener = Callable[[str, float], DownloadStream]


def _review_purpose(root: Mapping[str, object]) -> None:
    purpose = _mapping(
        root["purpose"],
        {"allowed", "claims_allowed", "claims_forbidden"},
        context="purpose",
    )
    purpose_allowed = _string_tuple(purpose["allowed"], context="purpose.allowed")
    claims_allowed = _string_tuple(
        purpose["claims_allowed"],
        context="purpose.claims_allowed",
    )
    claims_forbidden = _string_tuple(
        purpose["claims_forbidden"],
        context="purpose.claims_forbidden",
    )
    if (
        purpose_allowed != _PURPOSE_ALLOWED
        or claims_allowed != _CLAIMS_ALLOWED
        or claims_forbidden != _CLAIMS_FORBIDDEN
    ):
        raise WyscoutConfigError("purpose and claim authority is not reviewed")


def _review_rights(root: Mapping[str, object]) -> tuple[dict[str, object], str, str]:
    rights = _mapping(
        root["rights"],
        {
            "licence_name",
            "licence_id",
            "licence_url",
            "evidence",
            "local_retention",
            "raw_reproduction",
            "transformation",
            "feature_and_model_use",
            "internal_display",
            "derived_export",
            "raw_redistribution",
            "commercial_use",
            "project_control",
            "attribution",
        },
        context="rights",
    )
    rights_evidence = _string_tuple(rights["evidence"], context="rights.evidence")
    rights_values = {
        key: _string(rights[key], context=f"rights.{key}")
        for key in (
            "local_retention",
            "raw_reproduction",
            "transformation",
            "feature_and_model_use",
            "internal_display",
            "derived_export",
            "raw_redistribution",
            "commercial_use",
        )
    }
    if rights_evidence != _RIGHTS_EVIDENCE or rights_values != {
        "local_retention": "allowed",
        "raw_reproduction": "allowed",
        "transformation": "allowed",
        "feature_and_model_use": "allowed",
        "internal_display": "allowed",
        "derived_export": "allowed_with_attribution",
        "raw_redistribution": "allowed_with_attribution",
        "commercial_use": "allowed_with_attribution",
    }:
        raise WyscoutConfigError("rights authority is not reviewed")
    project_control = _mapping(
        rights["project_control"],
        {
            "raw_export",
            "network_transfer_after_acquisition",
            "public_or_hosted_display",
            "external_model_call",
        },
        context="rights.project_control",
    )
    for key, value in project_control.items():
        if _string(value, context=f"rights.project_control.{key}") != "forbidden":
            raise WyscoutConfigError("rights project control is not reviewed")
    attribution = _mapping(
        rights["attribution"],
        {"required", "text", "licence_link_required", "change_notice"},
        context="rights.attribution",
    )
    if not _boolean(attribution["required"], context="rights.attribution.required"):
        raise WyscoutConfigError("source attribution must be required")
    if not _boolean(
        attribution["licence_link_required"],
        context="rights.attribution.licence_link_required",
    ):
        raise WyscoutConfigError("source licence link must be required")
    attribution_text = _string(
        attribution["text"],
        context="rights.attribution.text",
    )
    change_notice = _string(
        attribution["change_notice"],
        context="rights.attribution.change_notice",
    )
    if attribution_text != _ATTRIBUTION_TEXT or change_notice != _CHANGE_NOTICE:
        raise WyscoutConfigError("attribution authority is not reviewed")
    return rights, attribution_text, change_notice


def _review_coverage(root: Mapping[str, object]) -> tuple[str, ...]:
    coverage = _mapping(
        root["coverage"],
        {
            "population",
            "domestic_season",
            "included_competitions",
            "excluded_from_first_pass",
            "collection_reference_counts",
            "absent",
        },
        context="coverage",
    )
    population = _string(coverage["population"], context="coverage.population")
    domestic_season = _string(
        coverage["domestic_season"],
        context="coverage.domestic_season",
    )
    included_competitions = _sequence(
        coverage["included_competitions"],
        context="coverage.included_competitions",
    )
    competitions: list[tuple[str, str, str]] = []
    for index, raw_competition in enumerate(included_competitions):
        competition = _mapping(
            raw_competition,
            {"country", "source_file_suffix", "competition"},
            context=f"coverage.included_competitions[{index}]",
        )
        competitions.append(
            (
                _string(
                    competition["country"],
                    context=f"included competition {index} country",
                ),
                _string(
                    competition["source_file_suffix"],
                    context=f"included competition {index} suffix",
                ),
                _string(
                    competition["competition"],
                    context=f"included competition {index} name",
                ),
            )
        )
    suffixes = tuple(competition[1] for competition in competitions)
    excluded_competitions = _string_tuple(
        coverage["excluded_from_first_pass"],
        context="coverage.excluded_from_first_pass",
    )
    reference_counts = _mapping(
        coverage["collection_reference_counts"],
        {
            "matches_all_seven_competitions",
            "events_all_seven_competitions",
            "players_all_seven_competitions",
        },
        context="coverage.collection_reference_counts",
    )
    parsed_reference_counts = {
        key: _positive_int(
            value,
            context=f"coverage.collection_reference_counts.{key}",
        )
        for key, value in reference_counts.items()
    }
    absent_coverage = _string_tuple(coverage["absent"], context="coverage.absent")
    if (
        population != "male_senior"
        or domestic_season != "2017/2018"
        or tuple(competitions) != _INCLUDED_COMPETITIONS
        or excluded_competitions != _EXCLUDED_COMPETITIONS
        or parsed_reference_counts != _REFERENCE_COUNTS
        or absent_coverage != _ABSENT_COVERAGE
    ):
        raise WyscoutConfigError("coverage authority is not reviewed")
    return suffixes


def _review_objects(root: Mapping[str, object]) -> tuple[WyscoutSourceObject, ...]:
    raw_objects = _sequence(root["objects"], context="objects")
    objects = tuple(
        _source_object(raw_object, index=index) for index, raw_object in enumerate(raw_objects)
    )
    if {source_object.name for source_object in objects} != _OBJECT_NAMES or tuple(
        source_object.name for source_object in objects
    ) != tuple(_REVIEWED_OBJECT_IDENTITIES):
        raise WyscoutConfigError("source objects must exactly match the reviewed object names")
    _require_unique(
        (source_object.name for source_object in objects),
        context="source object names",
    )
    _require_unique(
        (source_object.file_id for source_object in objects),
        context="source object file IDs",
    )
    _require_unique(
        (source_object.url for source_object in objects),
        context="source object URLs",
    )
    return objects


def _review_archive(
    root: Mapping[str, object],
    *,
    suffixes: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...], str]:
    archive = _mapping(
        root["archive_admission"],
        {
            "matches",
            "events",
            "known_scope_excluded",
            "excluded_member_handling",
            "reject_unknown_members",
            "reject_links",
            "reject_absolute_or_parent_paths",
        },
        context="archive_admission",
    )
    for key in (
        "reject_unknown_members",
        "reject_links",
        "reject_absolute_or_parent_paths",
    ):
        if not _boolean(archive[key], context=f"archive_admission.{key}"):
            raise WyscoutConfigError(f"archive_admission.{key} must be true")
    matches_members = _string_tuple(
        archive["matches"],
        context="archive_admission.matches",
    )
    events_members = _string_tuple(
        archive["events"],
        context="archive_admission.events",
    )
    known_scope_excluded = _mapping(
        archive["known_scope_excluded"],
        {"matches", "events"},
        context="archive_admission.known_scope_excluded",
    )
    matches_excluded_members = _string_tuple(
        known_scope_excluded["matches"],
        context="archive_admission.known_scope_excluded.matches",
    )
    events_excluded_members = _string_tuple(
        known_scope_excluded["events"],
        context="archive_admission.known_scope_excluded.events",
    )
    excluded_member_handling = _string(
        archive["excluded_member_handling"],
        context="archive_admission.excluded_member_handling",
    )
    if excluded_member_handling != "verify_directory_entry_but_do_not_extract_or_admit_payload":
        raise WyscoutConfigError("excluded archive member handling is not reviewed")
    expected_matches = tuple(f"matches_{suffix}.json" for suffix in suffixes)
    expected_events = tuple(f"events_{suffix}.json" for suffix in suffixes)
    if matches_members != expected_matches or events_members != expected_events:
        raise WyscoutConfigError("archive members must match the five declared competitions")
    expected_excluded_matches = tuple(
        f"matches_{suffix}.json" for suffix in _KNOWN_SCOPE_EXCLUDED_SUFFIXES
    )
    expected_excluded_events = tuple(
        f"events_{suffix}.json" for suffix in _KNOWN_SCOPE_EXCLUDED_SUFFIXES
    )
    if (
        matches_excluded_members != expected_excluded_matches
        or events_excluded_members != expected_excluded_events
    ):
        raise WyscoutConfigError("scope-excluded archive members are not reviewed")
    if set(matches_members) & set(matches_excluded_members) or set(events_members) & set(
        events_excluded_members
    ):
        raise WyscoutConfigError("admitted and scope-excluded archive members overlap")
    return (
        matches_members,
        events_members,
        matches_excluded_members,
        events_excluded_members,
        excluded_member_handling,
    )


def _review_temporal(root: Mapping[str, object]) -> tuple[dict[str, object], datetime]:
    temporal = _mapping(
        root["temporal_semantics"],
        {
            "match_observed_at",
            "event_observed_at",
            "source_available_at",
            "source_available_at_basis",
            "generated_at_is_evidence",
            "historical_replay_before_collection_release",
            "correction_policy",
            "late_data_policy",
            "research_only_when_availability_missing",
        },
        context="temporal_semantics",
    )
    temporal_values = {
        key: _string(temporal[key], context=f"temporal_semantics.{key}")
        for key in (
            "match_observed_at",
            "event_observed_at",
            "source_available_at_basis",
            "historical_replay_before_collection_release",
            "correction_policy",
            "late_data_policy",
        )
    }
    if _boolean(
        temporal["generated_at_is_evidence"],
        context="temporal_semantics.generated_at_is_evidence",
    ):
        raise WyscoutConfigError("generated_at cannot be evidence")
    if not _boolean(
        temporal["research_only_when_availability_missing"],
        context="temporal_semantics.research_only_when_availability_missing",
    ):
        raise WyscoutConfigError("missing availability must remain research only")
    if temporal_values != {
        "match_observed_at": "matches.dateutc",
        "event_observed_at": "match_start_plus_match_period_and_event_sec",
        "source_available_at_basis": "frozen_collection_release_time",
        "historical_replay_before_collection_release": "forbidden",
        "correction_policy": "frozen_v5_no_record_level_correction_channel",
        "late_data_policy": "no_inference_before_collection_release",
    }:
        raise WyscoutConfigError("temporal authority is not reviewed")
    source_available_at = _utc(
        temporal["source_available_at"],
        context="temporal_semantics.source_available_at",
    )
    return temporal, source_available_at


def _review_acquisition(
    root: Mapping[str, object],
) -> tuple[WyscoutRedirectAuthority, str, str]:
    acquisition = _mapping(
        root["acquisition"],
        {
            "method",
            "credentials_required",
            "account_required",
            "redirect_authority",
            "destination_root",
            "working_root",
            "tracked_payloads",
            "verify_before_admission",
            "immutable_manifest",
            "retries_bounded",
            "resume_supported",
        },
        context="acquisition",
    )
    if _string(acquisition["method"], context="acquisition.method") != (
        "unauthenticated_https_file_download"
    ):
        raise WyscoutConfigError("acquisition method is not reviewed")
    for key in ("credentials_required", "account_required", "tracked_payloads"):
        if _boolean(acquisition[key], context=f"acquisition.{key}"):
            raise WyscoutConfigError(f"acquisition.{key} must be false")
    for key in ("immutable_manifest", "retries_bounded", "resume_supported"):
        if not _boolean(acquisition[key], context=f"acquisition.{key}"):
            raise WyscoutConfigError(f"acquisition.{key} must be true")
    redirect_authority = _redirect_authority(acquisition["redirect_authority"])
    verify_steps = _string_tuple(
        acquisition["verify_before_admission"],
        context="acquisition.verify_before_admission",
    )
    if verify_steps != _VERIFY_STEPS_ORDERED:
        raise WyscoutConfigError("acquisition verification steps must be exact")
    destination_root = _safe_relative_root(
        acquisition["destination_root"],
        context="acquisition.destination_root",
    )
    working_root = _safe_relative_root(
        acquisition["working_root"],
        context="acquisition.working_root",
    )
    if destination_root != "data/source/wyscout/v5" or working_root != "data/working/wyscout/v5":
        raise WyscoutConfigError("acquisition roots are not reviewed")
    return redirect_authority, destination_root, working_root


def load_wyscout_source_config(path: Path) -> WyscoutSourceConfig:
    """Load the reviewed declaration with exact-key and strict-type validation."""

    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise WyscoutConfigError("source configuration is unavailable") from exc
    root = _mapping(
        document,
        {
            "schema_version",
            "source_id",
            "status",
            "identity",
            "purpose",
            "rights",
            "coverage",
            "objects",
            "archive_admission",
            "temporal_semantics",
            "acquisition",
        },
        context="source configuration",
    )
    identity = _mapping(
        root["identity"],
        {
            "dataset_title",
            "source_data_provider",
            "dataset_authors",
            "publisher",
            "collection_id",
            "collection_version",
            "collection_doi",
            "collection_published_at",
            "data_paper_doi",
        },
        context="identity",
    )
    _review_purpose(root)
    rights, attribution_text, change_notice = _review_rights(root)
    suffixes = _review_coverage(root)
    objects = _review_objects(root)
    (
        matches_members,
        events_members,
        matches_excluded_members,
        events_excluded_members,
        excluded_member_handling,
    ) = _review_archive(root, suffixes=suffixes)
    temporal, source_available_at = _review_temporal(root)
    redirect_authority, destination_root, working_root = _review_acquisition(root)

    collection_published_at = _utc(
        identity["collection_published_at"],
        context="identity.collection_published_at",
    )
    if collection_published_at != source_available_at:
        raise WyscoutConfigError("source availability must equal the collection release")

    config = WyscoutSourceConfig(
        schema_version=_strict_int(root["schema_version"], context="schema_version"),
        source_id=_string(root["source_id"], context="source_id"),
        status=_string(root["status"], context="status"),
        dataset_title=_string(identity["dataset_title"], context="identity.dataset_title"),
        provider=_string(
            identity["source_data_provider"],
            context="identity.source_data_provider",
        ),
        dataset_authors=_string(
            identity["dataset_authors"],
            context="identity.dataset_authors",
        ),
        publisher=_string(identity["publisher"], context="identity.publisher"),
        collection_id=_positive_int(
            identity["collection_id"],
            context="identity.collection_id",
        ),
        collection_version=_positive_int(
            identity["collection_version"],
            context="identity.collection_version",
        ),
        collection_doi=_string(
            identity["collection_doi"],
            context="identity.collection_doi",
        ),
        collection_published_at=collection_published_at,
        data_paper_doi=_string(
            identity["data_paper_doi"],
            context="identity.data_paper_doi",
        ),
        licence_name=_string(rights["licence_name"], context="rights.licence_name"),
        licence_id=_string(rights["licence_id"], context="rights.licence_id"),
        licence_url=_https_url(rights["licence_url"], context="rights.licence_url"),
        attribution_text=attribution_text,
        change_notice=change_notice,
        objects=objects,
        matches_members=matches_members,
        events_members=events_members,
        matches_excluded_members=matches_excluded_members,
        events_excluded_members=events_excluded_members,
        excluded_member_handling=excluded_member_handling,
        source_available_at=source_available_at,
        source_available_at_basis=_string(
            temporal["source_available_at_basis"],
            context="temporal_semantics.source_available_at_basis",
        ),
        redirect_authority=redirect_authority,
        destination_root=destination_root,
        working_root=working_root,
    )
    _validate_reviewed_identity(config)
    return config


def download_source_object(
    config: WyscoutSourceConfig,
    source_object: WyscoutSourceObject,
    *,
    working_root: Path,
    opener: DownloadOpener | None = None,
    timeout_seconds: float = 30.0,
    max_attempts: int = 3,
    retry_delay_seconds: float = 0.1,
) -> VerifiedDownload:
    """Download one exact allowlisted object through a bounded verified temp file."""
    if (
        source_object not in config.objects
        or source_object.url not in config.allowed_urls
        or not _runtime_object_url_is_exact(source_object)
    ):
        raise WyscoutDownloadError("source object is not in the exact URL allowlist")
    if config.redirect_authority != _reviewed_redirect_authority():
        raise WyscoutDownloadError("runtime redirect authority is not reviewed")
    if not 0.1 <= timeout_seconds <= 120.0:
        raise ValueError("timeout_seconds must be between 0.1 and 120")
    if not 1 <= max_attempts <= 5:
        raise ValueError("max_attempts must be between 1 and 5")
    if not 0.0 <= retry_delay_seconds <= 5.0:
        raise ValueError("retry_delay_seconds must be between 0 and 5")
    safe_working_root = _safe_absolute_root(working_root, context="working root")
    last_error: BaseException | None = None
    for attempt in range(1, max_attempts + 1):
        temporary_path: Path | None = None
        response: DownloadStream | None = None
        try:
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{source_object.name}.",
                suffix=".partial",
                dir=safe_working_root,
            )
            temporary_path = Path(temporary_name)
            if opener is None:
                response = _open_with_reviewed_redirect(
                    config,
                    source_object,
                    source_object.url,
                    timeout_seconds,
                )
            else:
                response = opener(source_object.url, timeout_seconds)
            if not _response_url_is_allowed(
                config,
                source_object,
                response.geturl(),
            ):
                raise WyscoutDownloadError("download redirected to an unapproved URL")
            if response.status != 200:
                if 500 <= response.status <= 599:
                    raise _RetryableDownloadError("provider returned a retryable status")
                raise WyscoutDownloadError("provider returned a non-success status")
            declared_size = response.headers.get("Content-Length")
            if declared_size is not None:
                try:
                    parsed_size = int(declared_size)
                except ValueError as exc:
                    raise WyscoutDownloadError("Content-Length is invalid") from exc
                if parsed_size != source_object.size_bytes:
                    raise WyscoutDownloadError("Content-Length does not match reviewed size")

            md5 = hashlib.md5(usedforsecurity=False)
            sha256 = hashlib.sha256()
            size = 0
            with os.fdopen(descriptor, "wb") as temporary:
                descriptor = -1
                while chunk := response.read(_CHUNK_SIZE):
                    if not isinstance(chunk, bytes):
                        raise WyscoutDownloadError("download stream returned non-bytes")
                    size += len(chunk)
                    if size > source_object.size_bytes:
                        raise WyscoutDownloadError("download exceeds reviewed size")
                    md5.update(chunk)
                    sha256.update(chunk)
                    temporary.write(chunk)
                temporary.flush()
                os.fsync(temporary.fileno())
            if size != source_object.size_bytes:
                raise WyscoutDownloadError("download size does not match reviewed size")
            computed_md5 = md5.hexdigest()
            if computed_md5 != source_object.expected_md5:
                raise WyscoutDownloadError("download MD5 does not match reviewed digest")
            payload = temporary_path.read_bytes()
            return VerifiedDownload(
                source_object=source_object,
                payload=payload,
                md5=computed_md5,
                sha256=sha256.hexdigest(),
            )
        except (_RetryableDownloadError, TimeoutError, URLError, OSError) as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            if retry_delay_seconds:
                time.sleep(retry_delay_seconds)
        finally:
            try:
                if response is not None:
                    response.close()
            finally:
                if temporary_path is not None:
                    temporary_path.unlink(missing_ok=True)
                if "descriptor" in locals() and descriptor >= 0:
                    os.close(descriptor)
    raise WyscoutDownloadError("bounded download attempts exhausted") from last_error


def admit_archive(
    config: WyscoutSourceConfig,
    source_object: WyscoutSourceObject,
    payload: bytes | BinaryIO,
) -> ArchiveAdmission:
    """Admit reviewed payloads and retain directory-only evidence for exclusions."""
    expected_names = config.archive_members_for(source_object.name)
    excluded_names = config.excluded_archive_members_for(source_object.name)
    complete_names = expected_names + excluded_names
    archive_source = io.BytesIO(payload) if isinstance(payload, bytes) else payload
    try:
        archive = zipfile.ZipFile(archive_source)
    except (OSError, zipfile.BadZipFile) as exc:
        raise WyscoutArchiveError("archive is invalid") from exc
    with archive:
        infos = archive.infolist()
        if not infos or len(infos) > _MAX_ARCHIVE_MEMBERS:
            raise WyscoutArchiveError("archive member count is outside the bound")
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise WyscoutArchiveError("archive contains duplicate members")
        if set(names) != set(complete_names):
            raise WyscoutArchiveError("archive members do not match the approved set")
        total_expanded = 0
        by_name: dict[str, zipfile.ZipInfo] = {}
        for info in infos:
            _validate_archive_info(info)
            total_expanded += info.file_size
            if total_expanded > _MAX_ARCHIVE_BYTES:
                raise WyscoutArchiveError("archive expansion exceeds the total bound")
            by_name[info.filename] = info

        admitted: list[AdmittedArchiveMember] = []
        for name in expected_names:
            info = by_name[name]
            try:
                with archive.open(info, "r") as stream:
                    member_payload = _read_member(stream, expected_size=info.file_size)
            except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
                raise WyscoutArchiveError("archive member cannot be read completely") from exc
            admitted.append(
                AdmittedArchiveMember(
                    archive_name=source_object.name,
                    name=name,
                    payload=member_payload,
                    sha256=hashlib.sha256(member_payload).hexdigest(),
                )
            )
        excluded = tuple(
            ScopeExcludedArchiveMember(
                archive_name=source_object.name,
                name=name,
                compressed_size_bytes=by_name[name].compress_size,
                declared_size_bytes=by_name[name].file_size,
                directory_crc32=f"{by_name[name].CRC:08x}",
            )
            for name in excluded_names
        )
        return ArchiveAdmission(
            admitted_members=tuple(admitted),
            scope_excluded_members=excluded,
        )


def acquire_wyscout_v5(
    config: WyscoutSourceConfig,
    *,
    destination_root: Path,
    working_root: Path,
    acquired_at: datetime,
    opener: DownloadOpener | None = None,
    timeout_seconds: float = 30.0,
    max_attempts: int = 3,
    retry_delay_seconds: float = 0.1,
) -> WyscoutAcquisitionResult:
    """Acquire all exact objects and write the completion manifest last."""
    _require_utc_datetime(acquired_at, context="acquired_at")
    if acquired_at < config.source_available_at:
        raise WyscoutManifestError("acquisition cannot predate collection availability")
    storage = GuardedStorage(
        {"source": _safe_absolute_root(destination_root, context="destination root")}
    )
    try:
        existing_manifest = storage.read_bytes("source", _COMPLETION_PATH)
    except FileNotFoundError:
        existing_manifest = None
    if existing_manifest is not None:
        _validate_existing_manifest(config, storage, existing_manifest)
        return WyscoutAcquisitionResult(
            manifest_relative_path=_COMPLETION_PATH,
            manifest_bytes=existing_manifest,
            manifest_sha256=hashlib.sha256(existing_manifest).hexdigest(),
            manifest_created=False,
        )

    object_records: list[dict[str, object]] = []
    member_records: list[dict[str, object]] = []
    excluded_member_records: list[dict[str, object]] = []
    for source_object in config.objects:
        verified = download_source_object(
            config,
            source_object,
            working_root=working_root,
            opener=opener,
            timeout_seconds=timeout_seconds,
            max_attempts=max_attempts,
            retry_delay_seconds=retry_delay_seconds,
        )
        admission: ArchiveAdmission | None = None
        if source_object.name.endswith(".zip"):
            admission = admit_archive(config, source_object, verified.payload)
        object_path = f"objects/{source_object.name}"
        storage.write_bytes(
            "source",
            object_path,
            verified.payload,
            media_type="application/zip"
            if source_object.name.endswith(".zip")
            else "application/octet-stream",
            lineage={
                "collection_doi": config.collection_doi,
                "source_id": config.source_id,
                "source_url": source_object.url,
            },
            retention={
                "local_retention": "allowed",
                "raw_export": "forbidden",
            },
        )
        object_records.append(
            {
                "article_doi": source_object.article_doi,
                "article_id": source_object.article_id,
                "computed_md5": verified.md5,
                "expected_md5": source_object.expected_md5,
                "file_id": source_object.file_id,
                "name": source_object.name,
                "object_path": object_path,
                "sha256": verified.sha256,
                "size_bytes": len(verified.payload),
                "url": source_object.url,
            }
        )
        for member in admission.admitted_members if admission is not None else ():
            member_path = f"archive-members/{member.name}"
            storage.write_bytes(
                "source",
                member_path,
                member.payload,
                media_type="application/json",
                lineage={
                    "archive_name": member.archive_name,
                    "archive_sha256": verified.sha256,
                    "collection_doi": config.collection_doi,
                    "source_id": config.source_id,
                },
                retention={
                    "local_retention": "allowed",
                    "raw_export": "forbidden",
                },
            )
            member_records.append(
                {
                    "archive_name": member.archive_name,
                    "member_path": member_path,
                    "name": member.name,
                    "sha256": member.sha256,
                    "size_bytes": len(member.payload),
                }
            )
        if admission is not None:
            excluded_member_records.extend(
                _scope_excluded_member_record(member) for member in admission.scope_excluded_members
            )

    document = _completion_document(
        config,
        acquired_at=acquired_at,
        object_records=object_records,
        member_records=member_records,
        excluded_member_records=excluded_member_records,
    )
    manifest_bytes = canonical_json_bytes(document)
    receipt = storage.write_bytes(
        "source",
        _COMPLETION_PATH,
        manifest_bytes,
        media_type="application/json",
        lineage={
            "collection_doi": config.collection_doi,
            "source_id": config.source_id,
        },
        retention={
            "immutable": True,
            "raw_export": "forbidden",
        },
    )
    return WyscoutAcquisitionResult(
        manifest_relative_path=_COMPLETION_PATH,
        manifest_bytes=manifest_bytes,
        manifest_sha256=receipt.sha256,
        manifest_created=receipt.payload_created,
    )


class _RetryableDownloadError(RuntimeError):
    pass


class _AuthorisedRedirectHandler(HTTPRedirectHandler):
    def __init__(
        self,
        authority: WyscoutRedirectAuthority,
        source_object: WyscoutSourceObject,
        source_url: str,
    ) -> None:
        super().__init__()
        self._authority = authority
        self._source_object = source_object
        self._source_url = source_url
        self._hops = 0

    def redirect_request(
        self,
        req: Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> Request | None:
        del fp, msg, headers
        next_hop = self._hops + 1
        _validate_redirect_hop(
            self._authority,
            self._source_object,
            source_url=self._source_url,
            request_url=req.full_url,
            destination_url=newurl,
            status_code=code,
            hop_number=next_hop,
        )
        self._hops = next_hop
        return Request(
            newurl,
            headers=dict(req.headers),
            origin_req_host=req.origin_req_host,
            unverifiable=True,
            method="GET",
        )


def _open_with_reviewed_redirect(
    config: WyscoutSourceConfig,
    source_object: WyscoutSourceObject,
    url: str,
    timeout_seconds: float,
) -> DownloadStream:
    request = Request(url, headers={"User-Agent": "scouting-local-w04/1"})
    response = build_opener(
        _AuthorisedRedirectHandler(
            config.redirect_authority,
            source_object,
            url,
        )
    ).open(request, timeout=timeout_seconds)
    return cast(DownloadStream, response)


def _source_object(value: object, *, index: int) -> WyscoutSourceObject:
    item = _mapping(
        value,
        {
            "article_id",
            "article_doi",
            "file_id",
            "name",
            "size_bytes",
            "expected_md5",
            "url",
        },
        context=f"objects[{index}]",
    )
    file_id = _positive_int(item["file_id"], context=f"objects[{index}].file_id")
    url = _https_url(item["url"], context=f"objects[{index}].url")
    parsed = urlsplit(url)
    if (
        parsed.hostname != _DOWNLOAD_HOST
        or parsed.port is not None
        or parsed.query
        or parsed.fragment
        or parsed.path != f"/files/{file_id}"
        or url != f"https://{_DOWNLOAD_HOST}/files/{file_id}"
    ):
        raise WyscoutConfigError(f"objects[{index}].url is outside the exact URL shape")
    expected_md5 = _string(
        item["expected_md5"],
        context=f"objects[{index}].expected_md5",
    )
    if len(expected_md5) != 32 or any(
        character not in "0123456789abcdef" for character in expected_md5
    ):
        raise WyscoutConfigError(f"objects[{index}].expected_md5 is invalid")
    return WyscoutSourceObject(
        article_id=_positive_int(
            item["article_id"],
            context=f"objects[{index}].article_id",
        ),
        article_doi=_string(
            item["article_doi"],
            context=f"objects[{index}].article_doi",
        ),
        file_id=file_id,
        name=_string(item["name"], context=f"objects[{index}].name"),
        size_bytes=_positive_int(
            item["size_bytes"],
            context=f"objects[{index}].size_bytes",
        ),
        expected_md5=expected_md5,
        url=url,
    )


def _redirect_authority(value: object) -> WyscoutRedirectAuthority:
    item = _mapping(
        value,
        {
            "status_code",
            "maximum_hops",
            "destination_scheme",
            "destination_host",
            "destination_path_template",
            "exact_query_keys",
            "algorithm",
            "credential_scope_suffix",
            "credential_separator_encoding",
            "signed_headers",
            "maximum_expiry_seconds",
        },
        context="acquisition.redirect_authority",
    )
    authority = WyscoutRedirectAuthority(
        status_code=_positive_int(
            item["status_code"],
            context="acquisition.redirect_authority.status_code",
        ),
        maximum_hops=_positive_int(
            item["maximum_hops"],
            context="acquisition.redirect_authority.maximum_hops",
        ),
        destination_scheme=_string(
            item["destination_scheme"],
            context="acquisition.redirect_authority.destination_scheme",
        ),
        destination_host=_string(
            item["destination_host"],
            context="acquisition.redirect_authority.destination_host",
        ),
        destination_path_template=_string(
            item["destination_path_template"],
            context="acquisition.redirect_authority.destination_path_template",
        ),
        exact_query_keys=_string_tuple(
            item["exact_query_keys"],
            context="acquisition.redirect_authority.exact_query_keys",
        ),
        algorithm=_string(
            item["algorithm"],
            context="acquisition.redirect_authority.algorithm",
        ),
        credential_scope_suffix=_string(
            item["credential_scope_suffix"],
            context="acquisition.redirect_authority.credential_scope_suffix",
        ),
        credential_separator_encoding=_string(
            item["credential_separator_encoding"],
            context="acquisition.redirect_authority.credential_separator_encoding",
        ),
        signed_headers=_string(
            item["signed_headers"],
            context="acquisition.redirect_authority.signed_headers",
        ),
        maximum_expiry_seconds=_positive_int(
            item["maximum_expiry_seconds"],
            context="acquisition.redirect_authority.maximum_expiry_seconds",
        ),
    )
    if authority != _reviewed_redirect_authority():
        raise WyscoutConfigError("redirect authority is not reviewed")
    return authority


def _reviewed_redirect_authority() -> WyscoutRedirectAuthority:
    return WyscoutRedirectAuthority(
        status_code=302,
        maximum_hops=1,
        destination_scheme="https",
        destination_host=_REDIRECT_DESTINATION_HOST,
        destination_path_template=_REDIRECT_PATH_TEMPLATE,
        exact_query_keys=_REDIRECT_QUERY_KEYS,
        algorithm=_REDIRECT_ALGORITHM,
        credential_scope_suffix=_REDIRECT_CREDENTIAL_SCOPE,
        credential_separator_encoding=_REDIRECT_CREDENTIAL_SEPARATOR_ENCODING,
        signed_headers="host",
        maximum_expiry_seconds=60,
    )


def _validate_reviewed_identity(config: WyscoutSourceConfig) -> None:
    expected = (
        config.schema_version == 1
        and config.source_id == _SOURCE_ID
        and config.status == _SOURCE_STATUS
        and config.dataset_title == _DATASET_TITLE
        and config.provider == _PROVIDER
        and config.dataset_authors == _DATASET_AUTHORS
        and config.publisher == _PUBLISHER
        and config.collection_id == _COLLECTION_ID
        and config.collection_version == _COLLECTION_VERSION
        and config.collection_doi == _COLLECTION_DOI
        and config.data_paper_doi == _DATA_PAPER_DOI
        and config.licence_name == _LICENCE_NAME
        and config.licence_id == _LICENCE_ID
        and config.licence_url == _LICENCE_URL
        and config.attribution_text == _ATTRIBUTION_TEXT
        and config.change_notice == _CHANGE_NOTICE
        and config.collection_published_at == _SOURCE_AVAILABLE_AT
        and config.source_available_at == _SOURCE_AVAILABLE_AT
        and config.source_available_at_basis == "frozen_collection_release_time"
    )
    if not expected:
        raise WyscoutConfigError("source identity does not match the reviewed collection")
    for source_object in config.objects:
        reviewed = _REVIEWED_OBJECT_IDENTITIES[source_object.name]
        reviewed_url = f"https://{_DOWNLOAD_HOST}/files/{reviewed[2]}"
        if (
            source_object.article_id,
            source_object.article_doi,
            source_object.file_id,
            source_object.size_bytes,
            source_object.expected_md5,
            source_object.url,
        ) != (*reviewed, reviewed_url):
            raise WyscoutConfigError("source objects do not match the reviewed object manifest")


def _validate_archive_info(info: zipfile.ZipInfo) -> None:
    name = info.filename
    parsed = PurePosixPath(name)
    if (
        not name
        or "\\" in name
        or parsed.is_absolute()
        or any(part in {"", ".", ".."} for part in name.split("/"))
        or len(parsed.parts) != 1
    ):
        raise WyscoutArchiveError("archive member path is unsafe")
    if info.is_dir() or info.flag_bits & 0x1:
        raise WyscoutArchiveError("archive links, directories, or encrypted members are denied")
    mode = info.external_attr >> 16
    file_type = stat.S_IFMT(mode)
    if file_type not in {0, stat.S_IFREG}:
        raise WyscoutArchiveError("archive links and special files are denied")
    if info.file_size < 0 or info.file_size > _MAX_MEMBER_BYTES:
        raise WyscoutArchiveError("archive member size exceeds the bound")
    if info.file_size and (
        info.compress_size <= 0 or info.file_size > info.compress_size * _MAX_COMPRESSION_RATIO
    ):
        raise WyscoutArchiveError("archive member compression ratio exceeds the bound")


def _read_member(stream: Any, *, expected_size: int) -> bytes:
    chunks: list[bytes] = []
    size = 0
    while chunk := stream.read(_CHUNK_SIZE):
        if not isinstance(chunk, bytes):
            raise WyscoutArchiveError("archive member returned non-bytes")
        size += len(chunk)
        if size > expected_size or size > _MAX_MEMBER_BYTES:
            raise WyscoutArchiveError("archive member expands beyond its declaration")
        chunks.append(chunk)
    if size != expected_size:
        raise WyscoutArchiveError("archive member is incomplete")
    return b"".join(chunks)


def _runtime_object_url_is_exact(source_object: WyscoutSourceObject) -> bool:
    reviewed = _REVIEWED_OBJECT_IDENTITIES.get(source_object.name)
    if reviewed is None:
        return False
    reviewed_article_id, reviewed_article_doi, reviewed_file_id, _, _ = reviewed
    parsed = urlsplit(source_object.url)
    return (
        source_object.article_id == reviewed_article_id
        and source_object.article_doi == reviewed_article_doi
        and source_object.file_id == reviewed_file_id
        and parsed.scheme == "https"
        and parsed.hostname == _DOWNLOAD_HOST
        and parsed.port is None
        and not parsed.username
        and not parsed.password
        and not parsed.query
        and not parsed.fragment
        and parsed.path == f"/files/{reviewed_file_id}"
        and source_object.url == f"https://{_DOWNLOAD_HOST}/files/{reviewed_file_id}"
    )


def _validate_redirect_hop(
    authority: WyscoutRedirectAuthority,
    source_object: WyscoutSourceObject,
    *,
    source_url: str,
    request_url: str,
    destination_url: str,
    status_code: int,
    hop_number: int,
) -> None:
    if hop_number != 1 or hop_number > authority.maximum_hops:
        raise WyscoutDownloadError("download redirect exceeds the exact one-hop authority")
    if status_code != authority.status_code:
        raise WyscoutDownloadError("download redirect status is not authorised")
    if request_url != source_url or source_url != source_object.url:
        raise WyscoutDownloadError("download redirect did not originate at the exact source URL")
    _validate_signed_destination(authority, source_object, destination_url)


def _response_url_is_allowed(
    config: WyscoutSourceConfig,
    source_object: WyscoutSourceObject,
    response_url: str,
) -> bool:
    if response_url == source_object.url:
        return True
    try:
        _validate_signed_destination(
            config.redirect_authority,
            source_object,
            response_url,
        )
    except WyscoutDownloadError:
        return False
    return True


def _validate_signed_destination(
    authority: WyscoutRedirectAuthority,
    source_object: WyscoutSourceObject,
    destination_url: str,
) -> None:
    try:
        parsed = urlsplit(destination_url)
    except ValueError as exc:
        raise WyscoutDownloadError("signed redirect URL is malformed") from exc
    expected_path = "/" + authority.destination_path_template.format(
        file_id=source_object.file_id,
        name=source_object.name,
    )
    expected_origin = f"{authority.destination_scheme}://{authority.destination_host}"
    if (
        not destination_url.startswith(f"{expected_origin}/")
        or parsed.scheme != authority.destination_scheme
        or parsed.netloc != authority.destination_host
        or parsed.hostname != authority.destination_host
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path != expected_path
        or not parsed.query
        or parsed.fragment
    ):
        raise WyscoutDownloadError("signed redirect target is outside the exact authority")

    raw_fields = parsed.query.split("&")
    if len(raw_fields) != len(authority.exact_query_keys):
        raise WyscoutDownloadError("signed redirect query field count is invalid")
    raw_values: dict[str, str] = {}
    for field in raw_fields:
        key, separator, raw_value = field.partition("=")
        if (
            separator != "="
            or not raw_value
            or key not in authority.exact_query_keys
            or key in raw_values
        ):
            raise WyscoutDownloadError("signed redirect query keys are invalid")
        raw_values[key] = raw_value
    if set(raw_values) != set(authority.exact_query_keys):
        raise WyscoutDownloadError("signed redirect query keys are invalid")
    try:
        parsed_fields = parse_qsl(
            parsed.query,
            keep_blank_values=True,
            strict_parsing=True,
        )
    except ValueError as exc:
        raise WyscoutDownloadError("signed redirect query is malformed") from exc
    values: dict[str, str] = {}
    for (raw_key, raw_value), (decoded_key, decoded_value) in zip(
        ((field.partition("=")[0], field.partition("=")[2]) for field in raw_fields),
        parsed_fields,
        strict=True,
    ):
        safe_value_characters = (
            "/-_.~"
            if decoded_key == "X-Amz-Credential"
            and authority.credential_separator_encoding == _REDIRECT_CREDENTIAL_SEPARATOR_ENCODING
            else "-_.~"
        )
        if (
            decoded_key != raw_key
            or quote(decoded_value, safe=safe_value_characters) != raw_value
            or decoded_key in values
        ):
            raise WyscoutDownloadError("signed redirect query encoding is not canonical")
        values[decoded_key] = decoded_value

    if values["X-Amz-Algorithm"] != authority.algorithm:
        raise WyscoutDownloadError("signed redirect algorithm is not authorised")
    signature_date = values["X-Amz-Date"]
    try:
        parsed_date = datetime.strptime(signature_date, "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
    except ValueError as exc:
        raise WyscoutDownloadError("signed redirect date is not canonical UTC") from exc
    if parsed_date.strftime("%Y%m%dT%H%M%SZ") != signature_date:
        raise WyscoutDownloadError("signed redirect date is not canonical UTC")

    if authority.credential_separator_encoding != _REDIRECT_CREDENTIAL_SEPARATOR_ENCODING:
        raise WyscoutDownloadError("signed redirect credential separator is not authorised")
    credential_parts = values["X-Amz-Credential"].split("/")
    access_key = credential_parts[0] if credential_parts else ""
    if (
        len(credential_parts) != 5
        or not 16 <= len(access_key) <= 128
        or any(character not in _ACCESS_KEY_CHARACTERS for character in access_key)
        or credential_parts[1] != signature_date[:8]
        or "/".join(credential_parts[2:]) != authority.credential_scope_suffix
    ):
        raise WyscoutDownloadError("signed redirect credential scope is not authorised")

    expiry_text = values["X-Amz-Expires"]
    maximum_expiry_digits = len(str(authority.maximum_expiry_seconds))
    if (
        not expiry_text.isascii()
        or not expiry_text.isdecimal()
        or not 1 <= len(expiry_text) <= maximum_expiry_digits
    ):
        raise WyscoutDownloadError("signed redirect expiry is not canonical")
    expiry_seconds = int(expiry_text)
    if str(expiry_seconds) != expiry_text:
        raise WyscoutDownloadError("signed redirect expiry is not canonical")
    if not 1 <= expiry_seconds <= authority.maximum_expiry_seconds:
        raise WyscoutDownloadError("signed redirect expiry exceeds the authority")
    if values["X-Amz-SignedHeaders"] != authority.signed_headers:
        raise WyscoutDownloadError("signed redirect headers are not authorised")
    signature = values["X-Amz-Signature"]
    if len(signature) != 64 or any(character not in "0123456789abcdef" for character in signature):
        raise WyscoutDownloadError("signed redirect signature is invalid")


def _completion_document(
    config: WyscoutSourceConfig,
    *,
    acquired_at: datetime,
    object_records: list[dict[str, object]],
    member_records: list[dict[str, object]],
    excluded_member_records: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "acquisition": {
            "acquired_at": _utc_text(acquired_at),
            "source_available_at": _utc_text(config.source_available_at),
            "source_available_at_basis": config.source_available_at_basis,
        },
        "admitted_archive_members": member_records,
        "classification": _CLASSIFICATION,
        "collection": {
            "collection_doi": config.collection_doi,
            "collection_id": config.collection_id,
            "collection_published_at": _utc_text(config.collection_published_at),
            "collection_version": config.collection_version,
        },
        "licence": {
            "attribution_text": config.attribution_text,
            "change_notice": config.change_notice,
            "licence_id": config.licence_id,
            "licence_name": config.licence_name,
            "licence_url": config.licence_url,
        },
        "objects": object_records,
        "provider": config.provider,
        "schema_version": 1,
        "scope_excluded_archive_members": excluded_member_records,
        "source_id": config.source_id,
        "state": "complete",
    }


def _scope_excluded_member_record(
    member: ScopeExcludedArchiveMember,
) -> dict[str, object]:
    return {
        "archive_name": member.archive_name,
        "compressed_size_bytes": member.compressed_size_bytes,
        "declared_size_bytes": member.declared_size_bytes,
        "directory_crc32": member.directory_crc32,
        "disposition": "directory_verified_payload_not_opened_or_admitted",
        "name": member.name,
    }


def _validate_existing_manifest(
    config: WyscoutSourceConfig,
    storage: GuardedStorage,
    manifest_bytes: bytes,
) -> None:
    try:
        document = json.loads(manifest_bytes)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise WyscoutManifestError("completion manifest is invalid") from exc
    if not isinstance(document, dict) or canonical_json_bytes(document) != manifest_bytes:
        raise WyscoutManifestError("completion manifest is not canonical")
    expected_top = {
        "acquisition",
        "admitted_archive_members",
        "classification",
        "collection",
        "licence",
        "objects",
        "provider",
        "schema_version",
        "scope_excluded_archive_members",
        "source_id",
        "state",
    }
    if set(document) != expected_top:
        raise WyscoutManifestError("completion manifest keys are invalid")
    if (
        document["schema_version"] != 1
        or document["state"] != "complete"
        or document["source_id"] != config.source_id
        or document["provider"] != config.provider
        or document["classification"] != _CLASSIFICATION
    ):
        raise WyscoutManifestError("completion manifest identity conflicts")
    acquisition = _manifest_mapping(document["acquisition"], context="acquisition")
    acquired_at = _utc(acquisition.get("acquired_at"), context="acquisition.acquired_at")
    if acquired_at < config.source_available_at:
        raise WyscoutManifestError("completion acquisition predates availability")
    if acquisition != {
        "acquired_at": _utc_text(acquired_at),
        "source_available_at": _utc_text(config.source_available_at),
        "source_available_at_basis": config.source_available_at_basis,
    }:
        raise WyscoutManifestError("completion temporal evidence conflicts")
    if (
        document["collection"]
        != _completion_document(
            config,
            acquired_at=acquired_at,
            object_records=[],
            member_records=[],
            excluded_member_records=[],
        )["collection"]
    ):
        raise WyscoutManifestError("completion collection identity conflicts")
    if (
        document["licence"]
        != _completion_document(
            config,
            acquired_at=acquired_at,
            object_records=[],
            member_records=[],
            excluded_member_records=[],
        )["licence"]
    ):
        raise WyscoutManifestError("completion licence evidence conflicts")
    object_records = _manifest_sequence(document["objects"], context="objects")
    if len(object_records) != len(config.objects):
        raise WyscoutManifestError("completion object count conflicts")
    archive_admissions: dict[str, ArchiveAdmission] = {}
    for source_object, raw_record in zip(config.objects, object_records, strict=True):
        record = _manifest_mapping(raw_record, context="object record")
        object_path = f"objects/{source_object.name}"
        md5 = hashlib.md5(usedforsecurity=False)
        sha256 = hashlib.sha256()
        size_bytes = 0
        with storage.open_binary("source", object_path) as stream:
            while chunk := stream.read(_CHUNK_SIZE):
                size_bytes += len(chunk)
                md5.update(chunk)
                sha256.update(chunk)
            computed_md5 = md5.hexdigest()
            computed_sha256 = sha256.hexdigest()
            expected_record = {
                "article_doi": source_object.article_doi,
                "article_id": source_object.article_id,
                "computed_md5": computed_md5,
                "expected_md5": source_object.expected_md5,
                "file_id": source_object.file_id,
                "name": source_object.name,
                "object_path": object_path,
                "sha256": computed_sha256,
                "size_bytes": size_bytes,
                "url": source_object.url,
            }
            if (
                record != expected_record
                or size_bytes != source_object.size_bytes
                or computed_md5 != source_object.expected_md5
            ):
                raise WyscoutManifestError("completion object evidence conflicts")
            if source_object.name.endswith(".zip"):
                stream.seek(0)
                archive_admissions[source_object.name] = admit_archive(
                    config,
                    source_object,
                    stream,
                )
    member_records = _manifest_sequence(
        document["admitted_archive_members"],
        context="admitted_archive_members",
    )
    expected_pairs = tuple(("matches.zip", name) for name in config.matches_members) + tuple(
        ("events.zip", name) for name in config.events_members
    )
    if len(member_records) != len(expected_pairs):
        raise WyscoutManifestError("completion archive-member count conflicts")
    for (archive_name, member_name), raw_record in zip(
        expected_pairs,
        member_records,
        strict=True,
    ):
        record = _manifest_mapping(raw_record, context="archive member record")
        member_path = f"archive-members/{member_name}"
        payload = storage.read_bytes("source", member_path)
        admitted_member = next(
            member
            for member in archive_admissions[archive_name].admitted_members
            if member.name == member_name
        )
        expected_record = {
            "archive_name": archive_name,
            "member_path": member_path,
            "name": member_name,
            "sha256": hashlib.sha256(payload).hexdigest(),
            "size_bytes": len(payload),
        }
        if record != expected_record or payload != admitted_member.payload:
            raise WyscoutManifestError("completion archive-member evidence conflicts")
    excluded_records = _manifest_sequence(
        document["scope_excluded_archive_members"],
        context="scope_excluded_archive_members",
    )
    expected_excluded_records = [
        _scope_excluded_member_record(member)
        for archive_name in ("matches.zip", "events.zip")
        for member in archive_admissions[archive_name].scope_excluded_members
    ]
    if excluded_records != expected_excluded_records:
        raise WyscoutManifestError("completion scope-exclusion evidence conflicts")


def _mapping(value: object, expected: set[str], *, context: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise WyscoutConfigError(f"{context} must be an object")
    actual = set(value)
    if actual != expected:
        raise WyscoutConfigError(
            f"{context} keys must be exact; "
            f"missing={sorted(expected - actual)}, unknown={sorted(actual - expected)}"
        )
    return cast(dict[str, object], value)


def _sequence(value: object, *, context: str) -> list[object]:
    if not isinstance(value, list) or not value:
        raise WyscoutConfigError(f"{context} must be a non-empty array")
    return cast(list[object], value)


def _string(value: object, *, context: str) -> str:
    if type(value) is not str or not value or value != value.strip():
        raise WyscoutConfigError(f"{context} must be a non-empty trimmed string")
    return value


def _string_tuple(value: object, *, context: str) -> tuple[str, ...]:
    items = tuple(
        _string(item, context=f"{context}[{index}]")
        for index, item in enumerate(_sequence(value, context=context))
    )
    _require_unique(items, context=context)
    return items


def _boolean(value: object, *, context: str) -> bool:
    if type(value) is not bool:
        raise WyscoutConfigError(f"{context} must be a strict boolean")
    return value


def _strict_int(value: object, *, context: str) -> int:
    if type(value) is not int:
        raise WyscoutConfigError(f"{context} must be a strict integer")
    return value


def _positive_int(value: object, *, context: str) -> int:
    parsed = _strict_int(value, context=context)
    if parsed <= 0:
        raise WyscoutConfigError(f"{context} must be positive")
    return parsed


def _https_url(value: object, *, context: str) -> str:
    url = _string(value, context=context)
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.username or parsed.password:
        raise WyscoutConfigError(f"{context} must be an unauthenticated HTTPS URL")
    return url


def _safe_relative_root(value: object, *, context: str) -> str:
    raw = _string(value, context=context)
    parsed = PurePosixPath(raw)
    if parsed.is_absolute() or any(part in {"", ".", ".."} for part in raw.split("/")):
        raise WyscoutConfigError(f"{context} must be a normal relative path")
    return raw


def _utc(value: object, *, context: str) -> datetime:
    text_value = _string(value, context=context)
    if not text_value.endswith("Z"):
        raise WyscoutConfigError(f"{context} must be canonical UTC")
    try:
        parsed = datetime.fromisoformat(text_value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise WyscoutConfigError(f"{context} must be canonical UTC") from exc
    _require_utc_datetime(parsed, context=context)
    return parsed


def _require_utc_datetime(value: datetime, *, context: str) -> None:
    if not isinstance(value, datetime) or value.utcoffset() != timedelta(0):
        raise WyscoutManifestError(f"{context} must be timezone-aware UTC")


def _utc_text(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _require_unique(values: Any, *, context: str) -> None:
    materialised = tuple(values)
    if len(materialised) != len(set(materialised)):
        raise WyscoutConfigError(f"{context} must be unique")


def _safe_absolute_root(path: Path, *, context: str) -> Path:
    if not path.is_absolute():
        raise WyscoutSourceError(f"{context} must be absolute")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.is_symlink():
        raise WyscoutSourceError(f"{context} cannot be a symlink")
    resolved = path.resolve(strict=True)
    if not resolved.is_dir():
        raise WyscoutSourceError(f"{context} must be a directory")
    return resolved


def _manifest_mapping(value: object, *, context: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise WyscoutManifestError(f"completion {context} must be an object")
    return cast(dict[str, object], value)


def _manifest_sequence(value: object, *, context: str) -> list[object]:
    if not isinstance(value, list):
        raise WyscoutManifestError(f"completion {context} must be an array")
    return cast(list[object], value)


__all__ = [
    "AdmittedArchiveMember",
    "ArchiveAdmission",
    "DownloadOpener",
    "ScopeExcludedArchiveMember",
    "VerifiedDownload",
    "WyscoutAcquisitionResult",
    "WyscoutArchiveError",
    "WyscoutConfigError",
    "WyscoutDownloadError",
    "WyscoutManifestError",
    "WyscoutRedirectAuthority",
    "WyscoutSourceConfig",
    "WyscoutSourceError",
    "WyscoutSourceObject",
    "acquire_wyscout_v5",
    "admit_archive",
    "download_source_object",
    "load_wyscout_source_config",
]
