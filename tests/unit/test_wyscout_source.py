"""Synthetic and adversarial evidence for the frozen W04 acquisition seam."""

from __future__ import annotations

import hashlib
import io
import json
import runpy
import socket
import stat
import zipfile
from collections.abc import Mapping
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request

import pytest
import yaml  # type: ignore[import-untyped]

import scouting.sources.wyscout as wyscout_source
from scouting.sources import (
    WyscoutArchiveError,
    WyscoutConfigError,
    WyscoutDownloadError,
    WyscoutManifestError,
    WyscoutSourceConfig,
    WyscoutSourceObject,
    acquire_wyscout_v5,
    admit_archive,
    download_source_object,
    load_wyscout_source_config,
)

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs/sources/w04-provider.yaml"
FIXTURE_ROOT = ROOT / "tests/fixtures/wyscout"
ACQUIRED_AT = datetime(2026, 7, 29, 12, 0, tzinfo=UTC)


class _SyntheticResponse:
    def __init__(
        self,
        payload: bytes,
        *,
        url: str,
        status: int = 200,
        declared_size: int | None = None,
    ) -> None:
        self.status = status
        self.headers: Mapping[str, str] = {
            "Content-Length": str(len(payload) if declared_size is None else declared_size)
        }
        self._payload = payload
        self._url = url
        self._offset = 0
        self.read_calls = 0
        self.closed = False

    def geturl(self) -> str:
        return self._url

    def read(self, amount: int = -1) -> bytes:
        self.read_calls += 1
        if amount < 0:
            amount = len(self._payload) - self._offset
        chunk = self._payload[self._offset : self._offset + amount]
        self._offset += len(chunk)
        return chunk

    def close(self) -> None:
        self.closed = True


class _SyntheticOpener:
    def __init__(
        self,
        payloads: Mapping[str, bytes],
        *,
        final_urls: Mapping[str, str] | None = None,
        failures: Mapping[str, int] | None = None,
    ) -> None:
        self.payloads = dict(payloads)
        self.final_urls = dict(final_urls or {})
        self.failures = dict(failures or {})
        self.calls: list[tuple[str, float]] = []
        self.responses: list[_SyntheticResponse] = []

    def __call__(self, url: str, timeout_seconds: float) -> _SyntheticResponse:
        self.calls.append((url, timeout_seconds))
        remaining_failures = self.failures.get(url, 0)
        if remaining_failures:
            self.failures[url] = remaining_failures - 1
            raise TimeoutError("synthetic retry")
        payload = self.payloads[url]
        response = _SyntheticResponse(
            payload,
            url=self.final_urls.get(url, url),
        )
        self.responses.append(response)
        return response


@pytest.fixture(autouse=True)
def deny_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def denied_connection(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("unit tests must not open a network connection")

    monkeypatch.setattr(socket, "create_connection", denied_connection)


@pytest.fixture
def reviewed_config() -> WyscoutSourceConfig:
    return load_wyscout_source_config(CONFIG_PATH)


@pytest.fixture
def synthetic_source(
    reviewed_config: WyscoutSourceConfig,
) -> tuple[WyscoutSourceConfig, dict[str, bytes]]:
    payloads_by_name = {
        "competitions.json": (FIXTURE_ROOT / "competitions.json").read_bytes(),
        "teams.json": b'[{"wyId":9201,"name":"Synthetic Home"}]',
        "players.json": b'[{"wyId":9401,"shortName":"Synthetic Player"}]',
        "matches.zip": _approved_archive(reviewed_config, "matches.zip"),
        "events.zip": _approved_archive(reviewed_config, "events.zip"),
        "eventid2name.csv": (FIXTURE_ROOT / "eventid2name.csv").read_bytes(),
        "tags2name.csv": (FIXTURE_ROOT / "tags2name.csv").read_bytes(),
    }
    synthetic_objects = tuple(
        replace(
            source_object,
            size_bytes=len(payloads_by_name[source_object.name]),
            expected_md5=hashlib.md5(
                payloads_by_name[source_object.name],
                usedforsecurity=False,
            ).hexdigest(),
        )
        for source_object in reviewed_config.objects
    )
    config = replace(reviewed_config, objects=synthetic_objects)
    return config, {
        source_object.url: payloads_by_name[source_object.name] for source_object in config.objects
    }


def test_reviewed_source_config_loads_with_exact_identity(
    reviewed_config: WyscoutSourceConfig,
) -> None:
    assert reviewed_config.source_id == "wyscout-soccer-match-events-figshare-v5"
    assert reviewed_config.collection_version == 5
    assert reviewed_config.collection_doi == "10.6084/m9.figshare.c.4415000.v5"
    assert reviewed_config.source_available_at == datetime(
        2020,
        1,
        28,
        14,
        24,
        27,
        tzinfo=UTC,
    )
    assert reviewed_config.redirect_authority.status_code == 302
    assert reviewed_config.redirect_authority.maximum_hops == 1
    assert reviewed_config.redirect_authority.destination_host == "s3-eu-west-1.amazonaws.com"
    assert reviewed_config.redirect_authority.credential_separator_encoding == "literal_slash"
    assert {source_object.name for source_object in reviewed_config.objects} == {
        "competitions.json",
        "teams.json",
        "players.json",
        "matches.zip",
        "events.zip",
        "eventid2name.csv",
        "tags2name.csv",
    }


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("unknown_key", "keys must be exact"),
        ("wrong_type", "strict integer"),
        ("unapproved_url", "outside the exact URL shape"),
        ("unapproved_file_id", "reviewed object manifest"),
    ],
)
def test_source_config_rejects_unknown_keys_types_and_urls(
    tmp_path: Path,
    mutation: str,
    message: str,
) -> None:
    document = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    if mutation == "unknown_key":
        document["identity"]["unreviewed"] = True
    elif mutation == "wrong_type":
        document["objects"][0]["size_bytes"] = "1209"
    elif mutation == "unapproved_url":
        document["objects"][0]["url"] = "https://example.invalid/files/15073685"
    else:
        document["objects"][0]["file_id"] = 15_073_686
        document["objects"][0]["url"] = "https://ndownloader.figshare.com/files/15073686"
    config_path = tmp_path / "source.yaml"
    config_path.write_text(yaml.safe_dump(document), encoding="utf-8")

    with pytest.raises(WyscoutConfigError, match=message):
        load_wyscout_source_config(config_path)


@pytest.mark.parametrize(
    "authority_group",
    [
        "identity",
        "purpose",
        "claim",
        "rights",
        "rights_evidence",
        "attribution",
        "coverage",
        "archive",
        "temporal",
        "acquisition",
        "redirect",
        "redirect_separator",
    ],
)
def test_source_config_freezes_every_authority_group(
    tmp_path: Path,
    authority_group: str,
) -> None:
    document = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    if authority_group == "identity":
        document["identity"]["dataset_title"] = "Unreviewed title"
    elif authority_group == "purpose":
        document["purpose"]["allowed"][0] = "unreviewed_purpose"
    elif authority_group == "claim":
        document["purpose"]["claims_forbidden"].pop()
    elif authority_group == "rights":
        document["rights"]["licence_url"] = "https://example.invalid/licence"
    elif authority_group == "rights_evidence":
        document["rights"]["evidence"][0] = "https://example.invalid/evidence"
    elif authority_group == "attribution":
        document["rights"]["attribution"]["change_notice"] = "Unreviewed change notice."
    elif authority_group == "coverage":
        document["coverage"]["population"] = "unreviewed_population"
    elif authority_group == "archive":
        document["archive_admission"]["excluded_member_handling"] = "extract_everything"
    elif authority_group == "temporal":
        document["temporal_semantics"]["late_data_policy"] = "infer_early"
    elif authority_group == "acquisition":
        document["acquisition"]["resume_supported"] = False
    elif authority_group == "redirect":
        document["acquisition"]["redirect_authority"]["maximum_expiry_seconds"] = 61
    else:
        document["acquisition"]["redirect_authority"]["credential_separator_encoding"] = (
            "percent_encoded"
        )
    config_path = tmp_path / f"{authority_group}.yaml"
    config_path.write_text(yaml.safe_dump(document), encoding="utf-8")

    with pytest.raises(WyscoutConfigError):
        load_wyscout_source_config(config_path)


def test_download_uses_exact_url_and_verifies_both_digests(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
) -> None:
    config, payloads = synthetic_source
    source_object = config.objects[0]
    opener = _SyntheticOpener(payloads)

    verified = download_source_object(
        config,
        source_object,
        working_root=tmp_path / "working",
        opener=opener,
        timeout_seconds=2.0,
        retry_delay_seconds=0,
    )

    assert verified.payload == payloads[source_object.url]
    assert verified.md5 == source_object.expected_md5
    assert verified.sha256 == hashlib.sha256(verified.payload).hexdigest()
    assert opener.calls == [(source_object.url, 2.0)]
    assert list((tmp_path / "working").iterdir()) == []


def test_download_accepts_the_exact_reviewed_signed_delivery_url(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
) -> None:
    config, payloads = synthetic_source
    source_object = config.objects[0]
    signed_url = _signed_delivery_url(source_object)
    opener = _SyntheticOpener(
        payloads,
        final_urls={source_object.url: signed_url},
    )

    verified = download_source_object(
        config,
        source_object,
        working_root=tmp_path / "working",
        opener=opener,
        retry_delay_seconds=0,
    )

    assert verified.payload == payloads[source_object.url]
    assert opener.responses[0].geturl() == signed_url
    assert "X-Amz-Credential=ASIAEXAMPLEKEY01/20260729/" in signed_url
    assert "%2F" not in signed_url
    assert opener.responses[0].read_calls > 0


def test_download_accepts_the_128_character_access_key_boundary(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
) -> None:
    config, payloads = synthetic_source
    source_object = config.objects[0]
    signed_url = _delivery_url(
        source_object,
        fields=_signed_query_fields(access_key="Z" * 128),
    )
    opener = _SyntheticOpener(
        payloads,
        final_urls={source_object.url: signed_url},
    )

    verified = download_source_object(
        config,
        source_object,
        working_root=tmp_path / "working",
        opener=opener,
        retry_delay_seconds=0,
    )

    assert verified.payload == payloads[source_object.url]
    assert opener.responses[0].read_calls > 0


def test_download_rejects_runtime_redirect_authority_expansion(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
) -> None:
    config, payloads = synthetic_source
    expanded_config = replace(
        config,
        redirect_authority=replace(
            config.redirect_authority,
            maximum_expiry_seconds=120,
        ),
    )
    opener = _SyntheticOpener(payloads)

    with pytest.raises(WyscoutDownloadError, match="runtime redirect authority"):
        download_source_object(
            expanded_config,
            expanded_config.objects[0],
            working_root=tmp_path / "working",
            opener=opener,
        )

    assert opener.calls == []


def test_redirect_handler_allows_one_exact_302_and_rejects_a_second_hop(
    reviewed_config: WyscoutSourceConfig,
) -> None:
    source_object = reviewed_config.objects[0]
    signed_url = _signed_delivery_url(source_object)
    handler = wyscout_source._AuthorisedRedirectHandler(
        reviewed_config.redirect_authority,
        source_object,
        source_object.url,
    )

    redirected = handler.redirect_request(
        Request(source_object.url),
        None,
        302,
        "Found",
        {},
        signed_url,
    )

    assert redirected is not None
    assert redirected.full_url == signed_url
    with pytest.raises(WyscoutDownloadError, match="one-hop"):
        handler.redirect_request(
            redirected,
            None,
            302,
            "Found",
            {},
            signed_url,
        )


def test_redirect_handler_rejects_any_status_other_than_302(
    reviewed_config: WyscoutSourceConfig,
) -> None:
    source_object = reviewed_config.objects[0]
    handler = wyscout_source._AuthorisedRedirectHandler(
        reviewed_config.redirect_authority,
        source_object,
        source_object.url,
    )

    with pytest.raises(WyscoutDownloadError, match="status"):
        handler.redirect_request(
            Request(source_object.url),
            None,
            301,
            "Moved",
            {},
            _signed_delivery_url(source_object),
        )


@pytest.mark.parametrize(
    "mutation",
    [
        "scheme",
        "scheme_case_alias",
        "host",
        "userinfo",
        "port",
        "fragment",
        "path_file_id",
        "path_name",
        "path_encoding_alias",
        "query_extra",
        "query_missing",
        "query_duplicate",
        "query_key_encoding_alias",
        "algorithm",
        "algorithm_encoding_alias",
        "credential_date",
        "credential_region",
        "credential_service",
        "credential_terminal",
        "credential_encoded_separator",
        "credential_mixed_separator",
        "credential_double_encoded_separator",
        "credential_backslash_separator",
        "credential_empty_segment",
        "credential_extra_segment",
        "access_key_short",
        "access_key_long",
        "access_key_lowercase",
        "access_key_punctuation",
        "date_offset",
        "date_invalid",
        "expiry_zero",
        "expiry_excessive",
        "expiry_alias",
        "signed_headers",
        "signature_uppercase",
        "signature_short",
        "signature_nonhex",
    ],
)
def test_download_rejects_every_material_signed_redirect_mutation_before_read(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
    mutation: str,
) -> None:
    config, payloads = synthetic_source
    source_object = config.objects[0]
    opener = _SyntheticOpener(
        payloads,
        final_urls={
            source_object.url: _mutated_signed_delivery_url(
                source_object,
                mutation,
            )
        },
    )

    with pytest.raises(WyscoutDownloadError, match="redirected"):
        download_source_object(
            config,
            source_object,
            working_root=tmp_path / mutation,
            opener=opener,
            retry_delay_seconds=0,
        )

    assert opener.responses[0].read_calls == 0
    assert opener.responses[0].closed is True
    assert list((tmp_path / mutation).iterdir()) == []


def test_oversized_numeric_expiry_is_domain_error_before_body_read(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
) -> None:
    config, payloads = synthetic_source
    source_object = config.objects[0]
    fields = [
        (key, "9" * 5_000 if key == "X-Amz-Expires" else value)
        for key, value in _signed_query_fields()
    ]
    opener = _SyntheticOpener(
        payloads,
        final_urls={
            source_object.url: _delivery_url(
                source_object,
                fields=fields,
            )
        },
    )

    with pytest.raises(WyscoutDownloadError, match="redirected"):
        download_source_object(
            config,
            source_object,
            working_root=tmp_path / "working",
            opener=opener,
            retry_delay_seconds=0,
        )

    assert opener.responses[0].read_calls == 0
    assert opener.responses[0].closed is True
    assert list((tmp_path / "working").iterdir()) == []


def test_download_retries_only_within_the_declared_bound(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
) -> None:
    config, payloads = synthetic_source
    source_object = config.objects[0]
    opener = _SyntheticOpener(
        payloads,
        failures={source_object.url: 1},
    )

    verified = download_source_object(
        config,
        source_object,
        working_root=tmp_path / "working",
        opener=opener,
        max_attempts=2,
        retry_delay_seconds=0,
    )

    assert verified.payload == payloads[source_object.url]
    assert len(opener.calls) == 2
    assert list((tmp_path / "working").iterdir()) == []


def test_download_rejects_redirect_and_non_allowlisted_object(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
) -> None:
    config, payloads = synthetic_source
    source_object = config.objects[0]
    redirecting = _SyntheticOpener(
        payloads,
        final_urls={source_object.url: "https://example.invalid/unreviewed"},
    )
    with pytest.raises(WyscoutDownloadError, match="redirected"):
        download_source_object(
            config,
            source_object,
            working_root=tmp_path / "redirect-working",
            opener=redirecting,
        )

    unreviewed = replace(
        source_object,
        file_id=999,
        url="https://ndownloader.figshare.com/files/999",
    )
    with pytest.raises(WyscoutDownloadError, match="allowlist"):
        download_source_object(
            config,
            unreviewed,
            working_root=tmp_path / "unreviewed-working",
            opener=redirecting,
        )

    malicious = replace(
        source_object,
        url=f"https://example.invalid/files/{source_object.file_id}",
    )
    malicious_config = replace(
        config,
        objects=(malicious, *config.objects[1:]),
    )
    with pytest.raises(WyscoutDownloadError, match="allowlist"):
        download_source_object(
            malicious_config,
            malicious,
            working_root=tmp_path / "malicious-working",
            opener=redirecting,
        )
    assert len(redirecting.calls) == 1


@pytest.mark.parametrize("corruption", ["size", "md5"])
def test_download_rejects_size_and_digest_mismatch(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
    corruption: str,
) -> None:
    config, payloads = synthetic_source
    source_object = config.objects[0]
    if corruption == "size":
        invalid_object = replace(source_object, size_bytes=source_object.size_bytes + 1)
        invalid_config = replace(
            config,
            objects=(invalid_object, *config.objects[1:]),
        )
        message = "Content-Length"
    else:
        invalid_object = replace(source_object, expected_md5="0" * 32)
        invalid_config = replace(
            config,
            objects=(invalid_object, *config.objects[1:]),
        )
        message = "MD5"
    opener = _SyntheticOpener(payloads)

    with pytest.raises(WyscoutDownloadError, match=message):
        download_source_object(
            invalid_config,
            invalid_object,
            working_root=tmp_path / corruption,
            opener=opener,
        )
    assert list((tmp_path / corruption).iterdir()) == []


def test_archive_admits_only_the_complete_reviewed_member_set(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
) -> None:
    config, payloads = synthetic_source
    archive_object = _object_named(config, "matches.zip")

    admission = admit_archive(
        config,
        archive_object,
        payloads[archive_object.url],
    )

    admitted = admission.admitted_members
    assert tuple(member.name for member in admitted) == config.matches_members
    assert admitted[0].payload == (FIXTURE_ROOT / "matches_England.json").read_bytes()
    assert all(member.archive_name == "matches.zip" for member in admitted)
    assert (
        tuple(member.name for member in admission.scope_excluded_members)
        == config.matches_excluded_members
    )
    assert all(member.archive_name == "matches.zip" for member in admission.scope_excluded_members)


def test_archive_never_opens_scope_excluded_payloads(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, payloads = synthetic_source
    archive_object = _object_named(config, "events.zip")
    original_open = zipfile.ZipFile.open
    opened_names: list[str] = []

    def recording_open(
        archive: zipfile.ZipFile,
        name: str | zipfile.ZipInfo,
        mode: str = "r",
        pwd: bytes | None = None,
        *,
        force_zip64: bool = False,
    ) -> object:
        opened_names.append(name.filename if isinstance(name, zipfile.ZipInfo) else name)
        return original_open(
            archive,
            name,
            mode,
            pwd,
            force_zip64=force_zip64,
        )

    monkeypatch.setattr(zipfile.ZipFile, "open", recording_open)

    admission = admit_archive(
        config,
        archive_object,
        payloads[archive_object.url],
    )

    assert opened_names == list(config.events_members)
    assert not set(opened_names) & set(config.events_excluded_members)
    assert (
        tuple(member.name for member in admission.scope_excluded_members)
        == config.events_excluded_members
    )


@pytest.mark.parametrize(
    "mutation",
    [
        "unknown",
        "missing",
        "duplicate",
        "absolute",
        "parent",
        "backslash",
        "symlink",
        "special_file",
        "excessive_expansion",
    ],
)
def test_archive_rejects_unsafe_or_incomplete_members(
    reviewed_config: WyscoutSourceConfig,
    mutation: str,
) -> None:
    archive_object = _object_named(reviewed_config, "matches.zip")
    payload = _mutated_archive(reviewed_config, mutation)

    with pytest.raises(WyscoutArchiveError):
        admit_archive(reviewed_config, archive_object, payload)


def test_acquisition_writes_manifest_last_and_replays_without_network(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
) -> None:
    config, payloads = synthetic_source
    destination = tmp_path / "source"
    working = tmp_path / "working"
    opener = _SyntheticOpener(payloads)

    first = acquire_wyscout_v5(
        config,
        destination_root=destination,
        working_root=working,
        acquired_at=ACQUIRED_AT,
        opener=opener,
        retry_delay_seconds=0,
    )
    first_calls = tuple(opener.calls)

    def no_replay_download(url: str, timeout: float) -> _SyntheticResponse:
        del url, timeout
        raise AssertionError("exact replay must not download")

    replay = acquire_wyscout_v5(
        config,
        destination_root=destination,
        working_root=working,
        acquired_at=ACQUIRED_AT.replace(hour=13),
        opener=no_replay_download,
        retry_delay_seconds=0,
    )
    manifest = json.loads(first.manifest_bytes)

    assert len(first_calls) == len(config.objects)
    assert first.manifest_created is True
    assert replay.manifest_created is False
    assert replay.manifest_bytes == first.manifest_bytes
    assert replay.manifest_sha256 == first.manifest_sha256
    assert manifest["state"] == "complete"
    assert manifest["collection"]["collection_version"] == 5
    assert manifest["classification"] == "wyscout_figshare_v5_cc_by_4"
    assert manifest["acquisition"] == {
        "acquired_at": "2026-07-29T12:00:00Z",
        "source_available_at": "2020-01-28T14:24:27Z",
        "source_available_at_basis": "frozen_collection_release_time",
    }
    assert manifest["licence"]["licence_id"] == "CC-BY-4.0"
    assert "Pappalardo" in manifest["licence"]["attribution_text"]
    assert len(manifest["objects"]) == 7
    assert len(manifest["admitted_archive_members"]) == 10
    assert len(manifest["scope_excluded_archive_members"]) == 4
    excluded_names = {record["name"] for record in manifest["scope_excluded_archive_members"]}
    assert excluded_names == {
        *config.matches_excluded_members,
        *config.events_excluded_members,
    }
    assert all(
        record["disposition"] == "directory_verified_payload_not_opened_or_admitted"
        for record in manifest["scope_excluded_archive_members"]
    )
    assert not any((destination / "archive-members" / name).exists() for name in excluded_names)
    assert (destination / "completion-manifest.json").read_bytes() == first.manifest_bytes


def test_existing_manifest_replay_rejects_conflicting_local_bytes(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
) -> None:
    config, payloads = synthetic_source
    destination = tmp_path / "source"
    working = tmp_path / "working"
    acquire_wyscout_v5(
        config,
        destination_root=destination,
        working_root=working,
        acquired_at=ACQUIRED_AT,
        opener=_SyntheticOpener(payloads),
        retry_delay_seconds=0,
    )
    (destination / "objects" / config.objects[0].name).write_bytes(b"conflicting bytes")

    with pytest.raises(WyscoutManifestError, match="conflicts"):
        acquire_wyscout_v5(
            config,
            destination_root=destination,
            working_root=working,
            acquired_at=ACQUIRED_AT,
            opener=lambda url, timeout: (_ for _ in ()).throw(
                AssertionError(f"unexpected download {url} {timeout}")
            ),
            retry_delay_seconds=0,
        )


def test_failed_final_object_never_writes_completion_manifest(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
) -> None:
    config, payloads = synthetic_source
    final_object = config.objects[-1]
    corrupted_payloads = dict(payloads)
    corrupted_payloads[final_object.url] = b"wrong"
    destination = tmp_path / "source"

    with pytest.raises(WyscoutDownloadError):
        acquire_wyscout_v5(
            config,
            destination_root=destination,
            working_root=tmp_path / "working",
            acquired_at=ACQUIRED_AT,
            opener=_SyntheticOpener(corrupted_payloads),
            retry_delay_seconds=0,
        )

    assert not (destination / "completion-manifest.json").exists()
    assert not (destination / "completion-manifest.json.manifest.json").exists()


def test_unsafe_archive_writes_no_members_or_completion(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
) -> None:
    config, payloads = synthetic_source
    matches = _object_named(config, "matches.zip")
    unsafe_payloads = dict(payloads)
    unsafe_payloads[matches.url] = _mutated_archive(config, "unknown")
    unsafe_matches = replace(
        matches,
        size_bytes=len(unsafe_payloads[matches.url]),
        expected_md5=hashlib.md5(
            unsafe_payloads[matches.url],
            usedforsecurity=False,
        ).hexdigest(),
    )
    unsafe_config = replace(
        config,
        objects=tuple(
            unsafe_matches if item.name == matches.name else item for item in config.objects
        ),
    )
    destination = tmp_path / "source"

    with pytest.raises(WyscoutArchiveError):
        acquire_wyscout_v5(
            unsafe_config,
            destination_root=destination,
            working_root=tmp_path / "working",
            acquired_at=ACQUIRED_AT,
            opener=_SyntheticOpener(unsafe_payloads),
            retry_delay_seconds=0,
        )

    assert not (destination / "archive-members").exists()
    assert not (destination / "completion-manifest.json").exists()


def test_cli_import_does_not_acquire_or_open_network() -> None:
    namespace = runpy.run_path(
        str(ROOT / "scripts/acquire_wyscout_v5.py"),
        run_name="w04_import_only",
    )

    assert callable(namespace["main"])


def _signed_delivery_url(source_object: WyscoutSourceObject) -> str:
    return _delivery_url(
        source_object,
        fields=_signed_query_fields(),
    )


def _mutated_signed_delivery_url(
    source_object: WyscoutSourceObject,
    mutation: str,
) -> str:
    scheme = "https"
    netloc = "s3-eu-west-1.amazonaws.com"
    path = f"/pfigshare-u-files/{source_object.file_id}/{source_object.name}"
    fragment = ""
    fields = _signed_query_fields()
    raw_query: str | None = None

    def replace_value(key: str, value: str) -> None:
        index = next(index for index, (candidate, _) in enumerate(fields) if candidate == key)
        fields[index] = (key, value)

    if mutation == "scheme":
        scheme = "http"
    elif mutation == "scheme_case_alias":
        scheme = "HTTPS"
    elif mutation == "host":
        netloc = "s3.amazonaws.com"
    elif mutation == "userinfo":
        netloc = f"user@{netloc}"
    elif mutation == "port":
        netloc = f"{netloc}:443"
    elif mutation == "fragment":
        fragment = "unreviewed"
    elif mutation == "path_file_id":
        path = f"/pfigshare-u-files/{source_object.file_id + 1}/{source_object.name}"
    elif mutation == "path_name":
        path = f"/pfigshare-u-files/{source_object.file_id}/unreviewed.json"
    elif mutation == "path_encoding_alias":
        path = f"/pfigshare-u-files/{source_object.file_id}/%63{source_object.name[1:]}"
    elif mutation == "query_extra":
        fields.append(("X-Amz-Unreviewed", "1"))
    elif mutation == "query_missing":
        fields.pop()
    elif mutation == "query_duplicate":
        fields.append(fields[-1])
    elif mutation == "algorithm":
        replace_value("X-Amz-Algorithm", "AWS4-HMAC-SHA1")
    elif mutation == "credential_date":
        replace_value(
            "X-Amz-Credential",
            "ASIAEXAMPLEKEY01/20260728/eu-west-1/s3/aws4_request",
        )
    elif mutation == "credential_region":
        replace_value(
            "X-Amz-Credential",
            "ASIAEXAMPLEKEY01/20260729/us-east-1/s3/aws4_request",
        )
    elif mutation == "credential_service":
        replace_value(
            "X-Amz-Credential",
            "ASIAEXAMPLEKEY01/20260729/eu-west-1/ec2/aws4_request",
        )
    elif mutation == "credential_terminal":
        replace_value(
            "X-Amz-Credential",
            "ASIAEXAMPLEKEY01/20260729/eu-west-1/s3/unreviewed",
        )
    elif mutation == "credential_empty_segment":
        replace_value(
            "X-Amz-Credential",
            "ASIAEXAMPLEKEY01/20260729//s3/aws4_request",
        )
    elif mutation == "credential_extra_segment":
        replace_value(
            "X-Amz-Credential",
            "ASIAEXAMPLEKEY01/20260729/eu-west-1/s3/aws4_request/extra",
        )
    elif mutation == "access_key_short":
        replace_value(
            "X-Amz-Credential",
            f"{'A' * 15}/20260729/eu-west-1/s3/aws4_request",
        )
    elif mutation == "access_key_long":
        replace_value(
            "X-Amz-Credential",
            f"{'A' * 129}/20260729/eu-west-1/s3/aws4_request",
        )
    elif mutation == "access_key_lowercase":
        replace_value(
            "X-Amz-Credential",
            "ASIAEXAMPLEKEY0a/20260729/eu-west-1/s3/aws4_request",
        )
    elif mutation == "access_key_punctuation":
        replace_value(
            "X-Amz-Credential",
            "ASIAEXAMPLEKEY-1/20260729/eu-west-1/s3/aws4_request",
        )
    elif mutation == "date_offset":
        replace_value("X-Amz-Date", "20260729T120000+0000")
    elif mutation == "date_invalid":
        replace_value("X-Amz-Date", "20260729T250000Z")
    elif mutation == "expiry_zero":
        replace_value("X-Amz-Expires", "0")
    elif mutation == "expiry_excessive":
        replace_value("X-Amz-Expires", "61")
    elif mutation == "expiry_alias":
        replace_value("X-Amz-Expires", "010")
    elif mutation == "signed_headers":
        replace_value("X-Amz-SignedHeaders", "host;x-amz-date")
    elif mutation == "signature_uppercase":
        replace_value("X-Amz-Signature", "A" * 64)
    elif mutation == "signature_short":
        replace_value("X-Amz-Signature", "a" * 63)
    elif mutation == "signature_nonhex":
        replace_value("X-Amz-Signature", "g" * 64)

    if mutation in {
        "query_key_encoding_alias",
        "algorithm_encoding_alias",
        "credential_encoded_separator",
        "credential_mixed_separator",
        "credential_double_encoded_separator",
        "credential_backslash_separator",
    }:
        raw_query = _signed_query_text(fields)
        if mutation == "query_key_encoding_alias":
            raw_query = raw_query.replace("X-Amz-Date=", "%58-Amz-Date=", 1)
        elif mutation == "algorithm_encoding_alias":
            raw_query = raw_query.replace(
                "AWS4-HMAC-SHA256",
                "%41WS4-HMAC-SHA256",
                1,
            )
        elif mutation == "credential_encoded_separator":
            raw_query = urlencode(fields, quote_via=quote, safe="")
        elif mutation == "credential_mixed_separator":
            raw_query = raw_query.replace("/", "%2F", 1)
        elif mutation == "credential_double_encoded_separator":
            raw_query = raw_query.replace("/", "%252F", 1)
        else:
            raw_query = raw_query.replace("/", "\\")
    return _delivery_url(
        source_object,
        fields=fields,
        scheme=scheme,
        netloc=netloc,
        path=path,
        fragment=fragment,
        raw_query=raw_query,
    )


def _delivery_url(
    source_object: WyscoutSourceObject,
    *,
    fields: list[tuple[str, str]],
    scheme: str = "https",
    netloc: str = "s3-eu-west-1.amazonaws.com",
    path: str | None = None,
    fragment: str = "",
    raw_query: str | None = None,
) -> str:
    selected_path = path or (f"/pfigshare-u-files/{source_object.file_id}/{source_object.name}")
    query = raw_query or _signed_query_text(fields)
    return f"{scheme}://{netloc}{selected_path}?{query}" + (f"#{fragment}" if fragment else "")


def _signed_query_fields(
    *,
    access_key: str = "ASIAEXAMPLEKEY01",
) -> list[tuple[str, str]]:
    return [
        ("X-Amz-Algorithm", "AWS4-HMAC-SHA256"),
        (
            "X-Amz-Credential",
            f"{access_key}/20260729/eu-west-1/s3/aws4_request",
        ),
        ("X-Amz-Date", "20260729T120000Z"),
        ("X-Amz-Expires", "10"),
        ("X-Amz-SignedHeaders", "host"),
        ("X-Amz-Signature", "a" * 64),
    ]


def _signed_query_text(fields: list[tuple[str, str]]) -> str:
    return "&".join(
        f"{quote(key, safe='')}={quote(value, safe='/' if key == 'X-Amz-Credential' else '')}"
        for key, value in fields
    )


def _object_named(config: WyscoutSourceConfig, name: str) -> WyscoutSourceObject:
    return next(source_object for source_object in config.objects if source_object.name == name)


def _approved_archive(config: WyscoutSourceConfig, archive_name: str) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        names = config.archive_members_for(archive_name) + config.excluded_archive_members_for(
            archive_name
        )
        for name in names:
            if name == "matches_England.json":
                payload = (FIXTURE_ROOT / name).read_bytes()
            elif name == "events_England.json":
                payload = (FIXTURE_ROOT / name).read_bytes()
            else:
                payload = json.dumps(
                    [{"synthetic_member": name}],
                    separators=(",", ":"),
                ).encode()
            archive.writestr(name, payload)
    return output.getvalue()


def _mutated_archive(config: WyscoutSourceConfig, mutation: str) -> bytes:
    names = list(config.matches_members + config.matches_excluded_members)
    if mutation == "unknown":
        names.append("matches_Unreviewed.json")
    elif mutation == "missing":
        names.pop()
    elif mutation == "absolute":
        names[0] = "/matches_England.json"
    elif mutation == "parent":
        names[0] = "../matches_England.json"
    elif mutation == "backslash":
        names[0] = "folder\\matches_England.json"
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for index, name in enumerate(names):
            payload = (
                b"0" * 300_000
                if mutation == "excessive_expansion" and index == 0
                else b'[{"synthetic":true}]'
            )
            if mutation in {"symlink", "special_file"} and index == 0:
                info = zipfile.ZipInfo(name)
                info.create_system = 3
                file_type = stat.S_IFLNK if mutation == "symlink" else stat.S_IFCHR
                info.external_attr = (file_type | 0o777) << 16
                archive.writestr(info, payload)
            else:
                archive.writestr(name, payload)
            if mutation == "duplicate" and index == 0:
                with pytest.warns(UserWarning, match="Duplicate name"):
                    archive.writestr(name, payload)
    return output.getvalue()
