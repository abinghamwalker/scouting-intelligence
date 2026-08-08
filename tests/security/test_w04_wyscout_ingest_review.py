"""Independent stop-condition evidence for the W04 Wyscout acquisition seam.

Every transport response and payload in this module is fabricated in memory.
"""

from __future__ import annotations

import copy
import hashlib
import io
import json
import runpy
import socket
import stat
import zipfile
from collections.abc import Mapping
from contextlib import AbstractContextManager
from dataclasses import replace
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, BinaryIO, cast
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
from scouting.storage import GuardedStorage, canonical_json_bytes

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs/sources/w04-provider.yaml"
ACQUIRED_AT = datetime(2026, 7, 29, 12, 0, tzinfo=UTC)

_SIGNED_REDIRECT_URL = (
    "https://s3-eu-west-1.amazonaws.com/"
    "pfigshare-u-files/15073685/competitions.json"
    "?X-Amz-Algorithm=AWS4-HMAC-SHA256"
    "&X-Amz-Credential=ASIAEXAMPLEKEY01/20260729/eu-west-1/s3/aws4_request"
    "&X-Amz-Date=20260729T120000Z"
    "&X-Amz-Expires=60"
    "&X-Amz-SignedHeaders=host"
    f"&X-Amz-Signature={'a' * 64}"
)


class _SyntheticResponse:
    def __init__(
        self,
        payload: bytes,
        *,
        final_url: str,
        status: int = 200,
        declared_size: str | int | None = None,
        include_content_length: bool = True,
    ) -> None:
        self.status = status
        self.headers: Mapping[str, str] = (
            {"Content-Length": str(len(payload) if declared_size is None else declared_size)}
            if include_content_length
            else {}
        )
        self._payload = payload
        self._final_url = final_url
        self._offset = 0
        self.read_calls = 0
        self.closed = False

    def geturl(self) -> str:
        return self._final_url

    def read(self, amount: int = -1) -> bytes:
        self.read_calls += 1
        if amount < 0:
            amount = len(self._payload) - self._offset
        chunk = self._payload[self._offset : self._offset + amount]
        self._offset += len(chunk)
        return chunk

    def close(self) -> None:
        self.closed = True


@pytest.fixture(autouse=True)
def deny_real_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make an accidental real transport call an immediate test failure."""

    def denied_connection(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("W04 review tests must not open a network connection")

    monkeypatch.setattr(socket, "create_connection", denied_connection)


def _source_document() -> dict[str, Any]:
    return cast(
        dict[str, Any],
        yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")),
    )


def _write_document(
    tmp_path: Path,
    document: dict[str, Any],
    *,
    name: str,
) -> Path:
    path = tmp_path / name
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def test_canonical_redirect_authority_is_loaded_as_runtime_authority() -> None:
    """The reviewed source configuration must be executable, not merely documentary."""

    config = load_wyscout_source_config(CONFIG_PATH)
    authority = getattr(config, "redirect_authority", None)

    assert authority is not None
    assert getattr(authority, "maximum_hops", None) == 1
    assert getattr(authority, "destination_host", None) == ("s3-eu-west-1.amazonaws.com")
    assert getattr(authority, "credential_separator_encoding", None) == "literal_slash"


def test_fabricated_reviewed_one_hop_redirect_is_accepted(
    tmp_path: Path,
) -> None:
    """A conforming synthetic signed redirect must pass without weakening URL checks."""

    config = load_wyscout_source_config(CONFIG_PATH)
    payload = b'{"synthetic":"redirect-only review payload"}'
    original = config.objects[0]
    synthetic = replace(
        original,
        size_bytes=len(payload),
        expected_md5=hashlib.md5(payload, usedforsecurity=False).hexdigest(),
    )
    config = replace(config, objects=(synthetic, *config.objects[1:]))
    response = _SyntheticResponse(payload, final_url=_SIGNED_REDIRECT_URL)

    verified = download_source_object(
        config,
        synthetic,
        working_root=tmp_path / "working",
        opener=lambda url, timeout: response,
        max_attempts=1,
        retry_delay_seconds=0.0,
    )

    assert verified.payload == payload
    assert response.closed
    assert response.read_calls > 0
    assert "X-Amz-Credential=ASIAEXAMPLEKEY01/20260729/" in _SIGNED_REDIRECT_URL
    assert "%2F" not in _SIGNED_REDIRECT_URL


def test_reviewed_identity_and_rights_cannot_change_while_loading(
    tmp_path: Path,
) -> None:
    """Expose every reviewed field the pre-redirect parser accepts as mutable."""

    baseline = _source_document()
    mutations: tuple[tuple[str, tuple[str, ...], object], ...] = (
        ("identity.dataset_title", ("identity", "dataset_title"), "Altered dataset"),
        ("identity.dataset_authors", ("identity", "dataset_authors"), "Other authors"),
        (
            "identity.data_paper_doi",
            ("identity", "data_paper_doi"),
            "10.0000/unreviewed",
        ),
        ("rights.licence_name", ("rights", "licence_name"), "Altered licence"),
        (
            "rights.licence_url",
            ("rights", "licence_url"),
            "https://example.invalid/unreviewed",
        ),
        (
            "rights.evidence",
            ("rights", "evidence"),
            ["https://example.invalid/unreviewed"],
        ),
        (
            "rights.attribution.text",
            ("rights", "attribution", "text"),
            "Altered attribution",
        ),
        (
            "rights.attribution.change_notice",
            ("rights", "attribution", "change_notice"),
            "Altered change notice",
        ),
    )
    accepted_mutations: list[str] = []

    for index, (label, keys, value) in enumerate(mutations):
        document = copy.deepcopy(baseline)
        target: dict[str, Any] = document
        for key in keys[:-1]:
            target = cast(dict[str, Any], target[key])
        target[keys[-1]] = value
        path = _write_document(tmp_path, document, name=f"mutation-{index}.yaml")
        try:
            load_wyscout_source_config(path)
        except WyscoutConfigError:
            continue
        accepted_mutations.append(label)

    assert accepted_mutations == []


def _redirect_url_with_credential(credential: str) -> str:
    return _SIGNED_REDIRECT_URL.replace(
        "ASIAEXAMPLEKEY01/20260729/eu-west-1/s3/aws4_request",
        credential,
    )


@pytest.mark.parametrize(
    "credential",
    (
        "ASIAEXAMPLEKEY01%2F20260729%2Feu-west-1%2Fs3%2Faws4_request",
        "ASIAEXAMPLEKEY01%2F20260729/eu-west-1/s3/aws4_request",
        "ASIAEXAMPLEKEY01%252F20260729/eu-west-1/s3/aws4_request",
        r"ASIAEXAMPLEKEY01\20260729\eu-west-1\s3\aws4_request",
        "ASIAEXAMPLEKEY01/20260729//s3/aws4_request",
        "ASIAEXAMPLEKEY01/20260729/eu-west-1/s3/aws4_request/extra",
        f"{'A' * 15}/20260729/eu-west-1/s3/aws4_request",
        f"{'A' * 129}/20260729/eu-west-1/s3/aws4_request",
        "ASIAEXAMPLEKEY0a/20260729/eu-west-1/s3/aws4_request",
    ),
)
def test_credential_aliases_reject_before_body_read(
    tmp_path: Path,
    credential: str,
) -> None:
    config = load_wyscout_source_config(CONFIG_PATH)
    payload = b'{"synthetic":"credential-boundary"}'
    original = config.objects[0]
    synthetic = replace(
        original,
        size_bytes=len(payload),
        expected_md5=hashlib.md5(payload, usedforsecurity=False).hexdigest(),
    )
    config = replace(config, objects=(synthetic, *config.objects[1:]))
    response = _SyntheticResponse(
        payload,
        final_url=_redirect_url_with_credential(credential),
    )

    error: Exception | None = None
    try:
        download_source_object(
            config,
            synthetic,
            working_root=tmp_path / "working",
            opener=lambda url, timeout: response,
            max_attempts=1,
            retry_delay_seconds=0.0,
        )
    except Exception as caught:
        error = caught

    assert response.read_calls == 0
    assert response.closed
    assert list((tmp_path / "working").iterdir()) == []
    assert isinstance(error, WyscoutDownloadError)


def test_redirect_status_origin_and_second_hop_are_exact() -> None:
    config = load_wyscout_source_config(CONFIG_PATH)
    source_object = config.objects[0]

    for status in (301, 303, 307, 308):
        handler = wyscout_source._AuthorisedRedirectHandler(
            config.redirect_authority,
            source_object,
            source_object.url,
        )
        with pytest.raises(WyscoutDownloadError):
            handler.redirect_request(
                Request(source_object.url),
                None,
                status,
                "synthetic",
                {},
                _SIGNED_REDIRECT_URL,
            )

    handler = wyscout_source._AuthorisedRedirectHandler(
        config.redirect_authority,
        source_object,
        source_object.url,
    )
    redirected = handler.redirect_request(
        Request(source_object.url),
        None,
        302,
        "synthetic",
        {},
        _SIGNED_REDIRECT_URL,
    )
    assert redirected is not None
    with pytest.raises(WyscoutDownloadError):
        handler.redirect_request(
            redirected,
            None,
            302,
            "synthetic",
            {},
            _SIGNED_REDIRECT_URL,
        )

    wrong_origin = wyscout_source._AuthorisedRedirectHandler(
        config.redirect_authority,
        source_object,
        source_object.url,
    )
    with pytest.raises(WyscoutDownloadError):
        wrong_origin.redirect_request(
            Request("https://ndownloader.figshare.com/files/999"),
            None,
            302,
            "synthetic",
            {},
            _SIGNED_REDIRECT_URL,
        )


@pytest.mark.parametrize(
    "expiry",
    (
        "0",
        "61",
        "-1",
        "+1",
        "01",
        "1.0",
        "1_0",
        "１２",
        "9" * 5_000,
    ),
)
def test_malformed_numeric_expiry_is_domain_error_before_body_read(
    tmp_path: Path,
    expiry: str,
) -> None:
    config = load_wyscout_source_config(CONFIG_PATH)
    payload = b'{"synthetic":"numeric-boundary"}'
    original = config.objects[0]
    synthetic = replace(
        original,
        size_bytes=len(payload),
        expected_md5=hashlib.md5(payload, usedforsecurity=False).hexdigest(),
    )
    config = replace(config, objects=(synthetic, *config.objects[1:]))
    response = _SyntheticResponse(
        payload,
        final_url=_SIGNED_REDIRECT_URL.replace("X-Amz-Expires=60", f"X-Amz-Expires={expiry}"),
    )

    error: Exception | None = None
    try:
        download_source_object(
            config,
            synthetic,
            working_root=tmp_path / "working",
            opener=lambda url, timeout: response,
            max_attempts=1,
            retry_delay_seconds=0.0,
        )
    except Exception as caught:
        error = caught

    assert response.read_calls == 0
    assert response.closed
    assert list((tmp_path / "working").iterdir()) == []
    assert isinstance(error, WyscoutDownloadError)


class _PayloadOpener:
    def __init__(self, payloads: Mapping[str, bytes]) -> None:
        self.payloads = dict(payloads)
        self.calls: list[tuple[str, float]] = []
        self.responses: list[_SyntheticResponse] = []

    def __call__(self, url: str, timeout_seconds: float) -> _SyntheticResponse:
        self.calls.append((url, timeout_seconds))
        response = _SyntheticResponse(self.payloads[url], final_url=url)
        self.responses.append(response)
        return response


class _QueueOpener:
    def __init__(self, items: list[_SyntheticResponse | Exception]) -> None:
        self.items = list(items)
        self.calls: list[tuple[str, float]] = []

    def __call__(self, url: str, timeout_seconds: float) -> _SyntheticResponse:
        self.calls.append((url, timeout_seconds))
        item = self.items.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


@pytest.fixture
def reviewed_config() -> WyscoutSourceConfig:
    return load_wyscout_source_config(CONFIG_PATH)


@pytest.fixture
def synthetic_source(
    reviewed_config: WyscoutSourceConfig,
) -> tuple[WyscoutSourceConfig, dict[str, bytes]]:
    payloads_by_name = {
        "competitions.json": b'[{"synthetic":"competitions"}]',
        "teams.json": b'[{"synthetic":"teams"}]',
        "players.json": b'[{"synthetic":"players"}]',
        "matches.zip": _archive_payload(reviewed_config, "matches.zip"),
        "events.zip": _archive_payload(reviewed_config, "events.zip"),
        "eventid2name.csv": b"id,name\n1,synthetic\n",
        "tags2name.csv": b"id,name\n1,synthetic\n",
    }
    objects = tuple(
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
    config = replace(reviewed_config, objects=objects)
    return config, {
        source_object.url: payloads_by_name[source_object.name] for source_object in objects
    }


def _object_named(config: WyscoutSourceConfig, name: str) -> WyscoutSourceObject:
    return next(source_object for source_object in config.objects if source_object.name == name)


def _archive_payload(
    config: WyscoutSourceConfig,
    archive_name: str,
    *,
    mutation: str = "safe",
) -> bytes:
    admitted = list(config.archive_members_for(archive_name))
    excluded = list(config.excluded_archive_members_for(archive_name))
    names = admitted + excluded
    if mutation == "unknown":
        names.append(f"{archive_name.removesuffix('.zip')}_Unreviewed.json")
    elif mutation == "missing":
        names.pop()
    elif mutation == "absolute":
        names[0] = f"/{names[0]}"
    elif mutation == "parent":
        names[0] = f"../{names[0]}"
    elif mutation == "backslash":
        names[0] = f"folder\\{names[0]}"

    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for index, name in enumerate(names):
            payload = (
                b"0" * 300_000
                if mutation == "expansion" and index == 0
                else json.dumps(
                    [{"synthetic_member": name}],
                    separators=(",", ":"),
                ).encode()
            )
            if mutation in {"symlink", "special"} and index == 0:
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
    result = output.getvalue()
    return _mark_first_member_encrypted(result) if mutation == "encrypted" else result


def _mark_first_member_encrypted(payload: bytes) -> bytes:
    result = bytearray(payload)
    for signature, flag_offset in ((b"PK\x03\x04", 6), (b"PK\x01\x02", 8)):
        index = result.find(signature)
        assert index >= 0
        flags = int.from_bytes(
            result[index + flag_offset : index + flag_offset + 2],
            "little",
        )
        result[index + flag_offset : index + flag_offset + 2] = (flags | 0x1).to_bytes(2, "little")
    return bytes(result)


def _no_network_opener(url: str, timeout_seconds: float) -> _SyntheticResponse:
    raise AssertionError(f"replay attempted network: {url} {timeout_seconds}")


def _mutated_redirect_url(mutation: str) -> str:
    url = _SIGNED_REDIRECT_URL
    replacements = {
        "scheme": ("https://", "http://"),
        "host": ("s3-eu-west-1.amazonaws.com", "s3.amazonaws.com"),
        "port": (
            "s3-eu-west-1.amazonaws.com/",
            "s3-eu-west-1.amazonaws.com:443/",
        ),
        "userinfo": (
            "s3-eu-west-1.amazonaws.com/",
            "user@s3-eu-west-1.amazonaws.com/",
        ),
        "path_file": ("15073685/competitions.json", "15073686/competitions.json"),
        "path_name": ("15073685/competitions.json", "15073685/teams.json"),
        "path_bucket": ("pfigshare-u-files", "unreviewed-bucket"),
        "path_encoding": ("competitions.json", "%63ompetitions.json"),
        "algorithm": ("AWS4-HMAC-SHA256", "AWS4-HMAC-SHA1"),
        "credential_date": ("/20260729/", "/20260728/"),
        "credential_region": ("/eu-west-1/", "/us-east-1/"),
        "credential_service": ("/s3/aws4_request", "/ec2/aws4_request"),
        "date_format": ("20260729T120000Z", "2026-07-29T12:00:00Z"),
        "date_invalid": ("20260729T120000Z", "20260729T250000Z"),
        "signed_headers": ("X-Amz-SignedHeaders=host", "X-Amz-SignedHeaders=host%3Bx"),
        "signature_upper": ("a" * 64, "A" * 64),
        "signature_short": ("a" * 64, "a" * 63),
        "signature_nonhex": ("a" * 64, "g" * 64),
    }
    if mutation == "fragment":
        return f"{url}#unreviewed"
    if mutation == "query_missing":
        return url.replace(
            f"&X-Amz-Signature={'a' * 64}",
            "",
        )
    if mutation == "query_extra":
        return f"{url}&X-Amz-Unreviewed=1"
    if mutation == "query_duplicate":
        return f"{url}&X-Amz-Signature={'a' * 64}"
    if mutation == "query_key_encoding":
        return url.replace("X-Amz-Date=", "%58-Amz-Date=")
    before, after = replacements[mutation]
    return url.replace(before, after, 1)


@pytest.mark.parametrize(
    "mutation",
    (
        "scheme",
        "host",
        "port",
        "userinfo",
        "fragment",
        "path_file",
        "path_name",
        "path_bucket",
        "path_encoding",
        "query_missing",
        "query_extra",
        "query_duplicate",
        "query_key_encoding",
        "algorithm",
        "credential_date",
        "credential_region",
        "credential_service",
        "date_format",
        "date_invalid",
        "signed_headers",
        "signature_upper",
        "signature_short",
        "signature_nonhex",
    ),
)
def test_signed_target_mutations_are_domain_errors_before_body_read(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
    mutation: str,
) -> None:
    config, payloads = synthetic_source
    source_object = config.objects[0]
    response = _SyntheticResponse(
        payloads[source_object.url],
        final_url=_mutated_redirect_url(mutation),
    )

    with pytest.raises(WyscoutDownloadError):
        download_source_object(
            config,
            source_object,
            working_root=tmp_path / mutation,
            opener=lambda url, timeout: response,
            max_attempts=1,
            retry_delay_seconds=0.0,
        )

    assert response.read_calls == 0
    assert response.closed
    assert list((tmp_path / mutation).iterdir()) == []


@pytest.mark.parametrize("status", (400, 401, 404, 429))
def test_unexpected_response_status_rejects_without_retry_or_body_read(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
    status: int,
) -> None:
    config, payloads = synthetic_source
    source_object = config.objects[0]
    response = _SyntheticResponse(
        payloads[source_object.url],
        final_url=source_object.url,
        status=status,
    )
    opener = _QueueOpener([response])

    with pytest.raises(WyscoutDownloadError, match="non-success"):
        download_source_object(
            config,
            source_object,
            working_root=tmp_path / str(status),
            opener=opener,
            max_attempts=3,
            retry_delay_seconds=0.0,
        )

    assert len(opener.calls) == 1
    assert response.read_calls == 0
    assert response.closed
    assert list((tmp_path / str(status)).iterdir()) == []


def test_retryable_status_is_bounded_and_cleans_each_attempt(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
) -> None:
    config, payloads = synthetic_source
    source_object = config.objects[0]
    responses = [
        _SyntheticResponse(
            payloads[source_object.url],
            final_url=source_object.url,
            status=status,
        )
        for status in (500, 502, 503)
    ]
    opener = _QueueOpener(list(responses))

    with pytest.raises(WyscoutDownloadError, match="bounded"):
        download_source_object(
            config,
            source_object,
            working_root=tmp_path / "working",
            opener=opener,
            max_attempts=3,
            retry_delay_seconds=0.0,
        )

    assert len(opener.calls) == 3
    assert all(response.read_calls == 0 and response.closed for response in responses)
    assert list((tmp_path / "working").iterdir()) == []


def test_timeout_retry_succeeds_only_within_bound(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
) -> None:
    config, payloads = synthetic_source
    source_object = config.objects[0]
    response = _SyntheticResponse(
        payloads[source_object.url],
        final_url=source_object.url,
    )
    opener = _QueueOpener([TimeoutError("synthetic"), response])

    verified = download_source_object(
        config,
        source_object,
        working_root=tmp_path / "working",
        opener=opener,
        max_attempts=2,
        retry_delay_seconds=0.0,
    )

    assert verified.payload == payloads[source_object.url]
    assert len(opener.calls) == 2
    assert response.closed
    assert list((tmp_path / "working").iterdir()) == []


@pytest.mark.parametrize(
    "declared_size",
    ("invalid", "9" * 5_000, -1, 0, 1, 999_999),
)
def test_invalid_content_length_rejects_before_body_read_and_cleans(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
    declared_size: str | int,
) -> None:
    config, payloads = synthetic_source
    source_object = config.objects[0]
    response = _SyntheticResponse(
        payloads[source_object.url],
        final_url=source_object.url,
        declared_size=declared_size,
    )

    with pytest.raises(WyscoutDownloadError):
        download_source_object(
            config,
            source_object,
            working_root=tmp_path / "working",
            opener=lambda url, timeout: response,
            max_attempts=1,
            retry_delay_seconds=0.0,
        )

    assert response.read_calls == 0
    assert response.closed
    assert list((tmp_path / "working").iterdir()) == []


def test_missing_content_length_still_verifies_actual_bytes(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
) -> None:
    config, payloads = synthetic_source
    source_object = config.objects[0]
    response = _SyntheticResponse(
        payloads[source_object.url],
        final_url=source_object.url,
        include_content_length=False,
    )

    verified = download_source_object(
        config,
        source_object,
        working_root=tmp_path / "working",
        opener=lambda url, timeout: response,
        max_attempts=1,
        retry_delay_seconds=0.0,
    )

    assert verified.payload == payloads[source_object.url]
    assert response.closed
    assert list((tmp_path / "working").iterdir()) == []


@pytest.mark.parametrize("corruption", ("short", "long", "md5"))
def test_actual_length_and_hash_mismatch_fail_with_cleanup(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
    corruption: str,
) -> None:
    config, payloads = synthetic_source
    source_object = config.objects[0]
    payload = payloads[source_object.url]
    response_payload = (
        payload[:-1]
        if corruption == "short"
        else payload + b"x"
        if corruption == "long"
        else payload
    )
    if corruption == "md5":
        source_object = replace(source_object, expected_md5="0" * 32)
        config = replace(config, objects=(source_object, *config.objects[1:]))
    response = _SyntheticResponse(
        response_payload,
        final_url=source_object.url,
        include_content_length=False,
    )

    with pytest.raises(WyscoutDownloadError):
        download_source_object(
            config,
            source_object,
            working_root=tmp_path / corruption,
            opener=lambda url, timeout: response,
            max_attempts=1,
            retry_delay_seconds=0.0,
        )

    assert response.read_calls > 0
    assert response.closed
    assert list((tmp_path / corruption).iterdir()) == []


@pytest.mark.parametrize("archive_name", ("matches.zip", "events.zip"))
def test_archive_equality_opens_only_admitted_member_payloads(
    reviewed_config: WyscoutSourceConfig,
    monkeypatch: pytest.MonkeyPatch,
    archive_name: str,
) -> None:
    payload = _archive_payload(reviewed_config, archive_name)
    source_object = _object_named(reviewed_config, archive_name)
    opened_names: list[str] = []
    original_open = zipfile.ZipFile.open

    def recording_open(
        archive: zipfile.ZipFile,
        name: str | zipfile.ZipInfo,
        mode: str = "r",
        pwd: bytes | None = None,
        *,
        force_zip64: bool = False,
    ) -> Any:
        opened_names.append(name.filename if isinstance(name, zipfile.ZipInfo) else name)
        return original_open(
            archive,
            name,
            mode,
            pwd,
            force_zip64=force_zip64,
        )

    monkeypatch.setattr(zipfile.ZipFile, "open", recording_open)
    admission = admit_archive(reviewed_config, source_object, payload)

    admitted_names = reviewed_config.archive_members_for(archive_name)
    excluded_names = reviewed_config.excluded_archive_members_for(archive_name)
    assert tuple(member.name for member in admission.admitted_members) == admitted_names
    assert tuple(member.name for member in admission.scope_excluded_members) == excluded_names
    assert opened_names == list(admitted_names)
    assert set(opened_names).isdisjoint(excluded_names)


@pytest.mark.parametrize(
    "mutation",
    (
        "unknown",
        "missing",
        "duplicate",
        "absolute",
        "parent",
        "backslash",
        "symlink",
        "special",
        "encrypted",
        "expansion",
    ),
)
@pytest.mark.parametrize("archive_name", ("matches.zip", "events.zip"))
def test_archive_rejects_non_exact_or_unsafe_payloads(
    reviewed_config: WyscoutSourceConfig,
    archive_name: str,
    mutation: str,
) -> None:
    source_object = _object_named(reviewed_config, archive_name)

    with pytest.raises(WyscoutArchiveError):
        admit_archive(
            reviewed_config,
            source_object,
            _archive_payload(reviewed_config, archive_name, mutation=mutation),
        )


def _acquire_synthetic(
    config: WyscoutSourceConfig,
    payloads: Mapping[str, bytes],
    *,
    destination_root: Path,
    working_root: Path,
) -> _PayloadOpener:
    opener = _PayloadOpener(payloads)
    result = acquire_wyscout_v5(
        config,
        destination_root=destination_root,
        working_root=working_root,
        acquired_at=ACQUIRED_AT,
        opener=opener,
        max_attempts=1,
        retry_delay_seconds=0.0,
    )
    assert result.manifest_created
    return opener


def test_acquisition_persists_completion_last_and_never_excluded_payloads(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, payloads = synthetic_source
    destination_root = tmp_path / "source"
    writes: list[str] = []
    original_write = GuardedStorage.write_bytes

    def recording_write(
        storage: GuardedStorage,
        root_name: str,
        relative_path: str | Path,
        payload: bytes,
        **kwargs: Any,
    ) -> Any:
        writes.append(str(relative_path))
        return original_write(
            storage,
            root_name,
            relative_path,
            payload,
            **kwargs,
        )

    monkeypatch.setattr(GuardedStorage, "write_bytes", recording_write)
    opener = _acquire_synthetic(
        config,
        payloads,
        destination_root=destination_root,
        working_root=tmp_path / "working",
    )

    expected_objects = [f"objects/{source_object.name}" for source_object in config.objects]
    expected_members = [
        f"archive-members/{name}"
        for archive_name in ("matches.zip", "events.zip")
        for name in config.archive_members_for(archive_name)
    ]
    excluded_names = {
        name
        for archive_name in ("matches.zip", "events.zip")
        for name in config.excluded_archive_members_for(archive_name)
    }
    manifest_bytes = (destination_root / "completion-manifest.json").read_bytes()
    document = json.loads(manifest_bytes)

    assert writes == [
        *expected_objects[:4],
        *expected_members[:5],
        expected_objects[4],
        *expected_members[5:],
        *expected_objects[5:],
        "completion-manifest.json",
    ]
    assert writes[-1] == "completion-manifest.json"
    assert all(response.closed for response in opener.responses)
    assert canonical_json_bytes(document) == manifest_bytes
    assert document["state"] == "complete"
    assert document["acquisition"] == {
        "acquired_at": "2026-07-29T12:00:00Z",
        "source_available_at": "2020-01-28T14:24:27Z",
        "source_available_at_basis": "frozen_collection_release_time",
    }
    assert document["licence"] == {
        "attribution_text": config.attribution_text,
        "change_notice": config.change_notice,
        "licence_id": config.licence_id,
        "licence_name": config.licence_name,
        "licence_url": config.licence_url,
    }
    assert {
        record["name"] for record in document["scope_excluded_archive_members"]
    } == excluded_names
    assert all(
        not (destination_root / "archive-members" / name).exists() for name in excluded_names
    )
    assert b"X-Amz-" not in manifest_bytes


def test_replay_is_network_free_and_reverifies_every_durable_payload(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, payloads = synthetic_source
    destination_root = tmp_path / "source"
    _acquire_synthetic(
        config,
        payloads,
        destination_root=destination_root,
        working_root=tmp_path / "working",
    )
    reads: list[str] = []
    streamed_objects: list[str] = []
    original_read = GuardedStorage.read_bytes
    original_open_binary = GuardedStorage.open_binary

    def recording_read(
        storage: GuardedStorage,
        root_name: str,
        relative_path: str | Path,
    ) -> bytes:
        reads.append(str(relative_path))
        return original_read(storage, root_name, relative_path)

    def recording_open_binary(
        storage: GuardedStorage,
        root_name: str,
        relative_path: str | Path,
    ) -> AbstractContextManager[BinaryIO]:
        streamed_objects.append(str(relative_path))
        return original_open_binary(storage, root_name, relative_path)

    monkeypatch.setattr(GuardedStorage, "read_bytes", recording_read)
    monkeypatch.setattr(GuardedStorage, "open_binary", recording_open_binary)
    replay = acquire_wyscout_v5(
        config,
        destination_root=destination_root,
        working_root=tmp_path / "replay-working",
        acquired_at=ACQUIRED_AT + timedelta(days=1),
        opener=_no_network_opener,
    )

    expected_reads = [
        "completion-manifest.json",
        *(
            f"archive-members/{name}"
            for archive_name in ("matches.zip", "events.zip")
            for name in config.archive_members_for(archive_name)
        ),
    ]
    assert reads == expected_reads
    assert streamed_objects == [f"objects/{source_object.name}" for source_object in config.objects]
    assert not replay.manifest_created
    assert replay.manifest_bytes == (destination_root / "completion-manifest.json").read_bytes()


@pytest.mark.parametrize(
    "durable_path",
    (
        "objects/competitions.json",
        "objects/matches.zip",
        "archive-members/matches_England.json",
    ),
)
def test_replay_rejects_changed_durable_payload_without_network(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
    durable_path: str,
) -> None:
    config, payloads = synthetic_source
    destination_root = tmp_path / "source"
    _acquire_synthetic(
        config,
        payloads,
        destination_root=destination_root,
        working_root=tmp_path / "working",
    )
    (destination_root / durable_path).write_bytes(b"synthetic durable corruption")

    with pytest.raises((WyscoutManifestError, WyscoutArchiveError)):
        acquire_wyscout_v5(
            config,
            destination_root=destination_root,
            working_root=tmp_path / "replay-working",
            acquired_at=ACQUIRED_AT,
            opener=_no_network_opener,
        )


def _mutated_completion_bytes(manifest_bytes: bytes, mutation: str) -> bytes:
    if mutation == "malformed":
        return b"{"
    document = cast(dict[str, Any], json.loads(manifest_bytes))
    if mutation == "noncanonical":
        return json.dumps(document, indent=2).encode()
    if mutation == "missing_key":
        del document["state"]
    elif mutation == "rights":
        document["licence"]["licence_url"] = "https://example.invalid/unreviewed"
    elif mutation == "temporal":
        document["acquisition"]["acquired_at"] = "2020-01-28T14:24:26Z"
    elif mutation == "object":
        document["objects"][0]["sha256"] = "0" * 64
    else:
        raise AssertionError(f"unknown completion mutation: {mutation}")
    return canonical_json_bytes(document)


@pytest.mark.parametrize(
    "mutation",
    ("malformed", "noncanonical", "missing_key", "rights", "temporal", "object"),
)
def test_replay_rejects_malformed_or_conflicting_completion_without_network(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
    mutation: str,
) -> None:
    config, payloads = synthetic_source
    destination_root = tmp_path / "source"
    _acquire_synthetic(
        config,
        payloads,
        destination_root=destination_root,
        working_root=tmp_path / "working",
    )
    manifest_path = destination_root / "completion-manifest.json"
    manifest_path.write_bytes(_mutated_completion_bytes(manifest_path.read_bytes(), mutation))

    with pytest.raises(WyscoutManifestError):
        acquire_wyscout_v5(
            config,
            destination_root=destination_root,
            working_root=tmp_path / "replay-working",
            acquired_at=ACQUIRED_AT,
            opener=_no_network_opener,
        )


@pytest.mark.parametrize(
    "acquired_at",
    (
        datetime(2020, 1, 28, 14, 24, 26, tzinfo=UTC),
        datetime(2026, 7, 29, 12, 0),
        datetime(2026, 7, 29, 13, 0, tzinfo=timezone(timedelta(hours=1))),
    ),
)
def test_invalid_acquisition_time_rejects_before_network_or_persistence(
    synthetic_source: tuple[WyscoutSourceConfig, dict[str, bytes]],
    tmp_path: Path,
    acquired_at: datetime,
) -> None:
    config, payloads = synthetic_source
    opener = _PayloadOpener(payloads)
    destination_root = tmp_path / "source"

    with pytest.raises(WyscoutManifestError):
        acquire_wyscout_v5(
            config,
            destination_root=destination_root,
            working_root=tmp_path / "working",
            acquired_at=acquired_at,
            opener=opener,
        )

    assert opener.calls == []
    assert not destination_root.exists()


def test_cli_import_has_no_transport_or_persistence_side_effect(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def deny_guarded_storage(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("CLI import instantiated storage")

    monkeypatch.setattr(GuardedStorage, "__init__", deny_guarded_storage)
    namespace = runpy.run_path(
        str(ROOT / "scripts/acquire_wyscout_v5.py"),
        run_name="w04_review_import_only",
    )

    assert callable(namespace["main"])
    assert list(tmp_path.iterdir()) == []
