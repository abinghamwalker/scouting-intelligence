from __future__ import annotations

import socket
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.validate_w03_governance import (  # noqa: E402
    AUTHORIZATION_PATH,
    DATA_RIGHTS_PATH,
    ENVIRONMENT_PATH,
    REQUIRED_ROLE_ACTIONS,
    ValidationFailure,
    load_yaml_mapping,
    validate_controls,
    validate_governance,
)


def _documents() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        load_yaml_mapping(ROOT / AUTHORIZATION_PATH),
        load_yaml_mapping(ROOT / DATA_RIGHTS_PATH),
        load_yaml_mapping(ROOT / ENVIRONMENT_PATH),
    )


def _codes(failures: list[ValidationFailure]) -> set[str]:
    return {failure.code for failure in failures}


def _set_nested(document: dict[str, Any], field: str, value: object) -> None:
    parts = field.split(".")
    current = document
    for part in parts[:-1]:
        current = current[part]
    current[parts[-1]] = value


def test_accepted_controls_pass_semantic_validation() -> None:
    assert validate_governance(ROOT) == []


@pytest.mark.parametrize(
    ("document_name", "field", "code"),
    (
        ("authorization", "policy_id", "AUTH_POLICY_ID"),
        ("data_rights", "policy_id", "RIGHTS_POLICY_ID"),
        ("environment", "environment_id", "ENVIRONMENT_ID"),
    ),
)
def test_frozen_control_identifiers_are_required(
    document_name: str,
    field: str,
    code: str,
) -> None:
    authorization, data_rights, environment = _documents()
    documents = {
        "authorization": authorization,
        "data_rights": data_rights,
        "environment": environment,
    }
    _set_nested(documents[document_name], field, "unexpected-id")

    failures = validate_controls(authorization, data_rights, environment)

    assert code in _codes(failures)
    assert any(failure.field == f"{document_name}.{field}" for failure in failures)


@pytest.mark.parametrize("role", sorted(REQUIRED_ROLE_ACTIONS))
def test_each_required_role_is_mandatory(role: str) -> None:
    authorization, data_rights, environment = _documents()
    del authorization["roles"][role]

    failures = validate_controls(authorization, data_rights, environment)

    assert "AUTH_REQUIRED_ROLE" in _codes(failures)
    assert any(failure.field == f"authorization.roles.{role}" for failure in failures)


def test_required_role_actions_are_semantically_checked() -> None:
    authorization, data_rights, environment = _documents()
    authorization["roles"]["approver"]["allow"].remove("shortlist_entry.approve")

    failures = validate_controls(authorization, data_rights, environment)

    assert "AUTH_ROLE_ACTIONS" in _codes(failures)
    assert any("shortlist_entry.approve" in failure.detail for failure in failures)


@pytest.mark.parametrize(
    ("document_name", "field"),
    (
        ("authorization", "decision.default"),
        ("authorization", "decision.unknown_action"),
        ("data_rights", "default"),
    ),
)
def test_permissive_defaults_are_rejected(document_name: str, field: str) -> None:
    authorization, data_rights, environment = _documents()
    selected = authorization if document_name == "authorization" else data_rights
    _set_nested(selected, field, "allow")

    failures = validate_controls(authorization, data_rights, environment)

    assert {"AUTH_DEFAULT_DENY", "RIGHTS_DEFAULT_DENY"} & _codes(failures)
    assert any(failure.field == f"{document_name}.{field}" for failure in failures)


def test_required_global_denies_cannot_be_removed() -> None:
    authorization, data_rights, environment = _documents()
    authorization["global_denies"].remove("audit.delete")

    failures = validate_controls(authorization, data_rights, environment)

    assert "AUTH_GLOBAL_DENY" in _codes(failures)
    assert any("audit.delete" in failure.detail for failure in failures)


@pytest.mark.parametrize(
    "field",
    (
        "authorised_classification.personal_data",
        "authorised_classification.provider_data",
        "authorised_classification.exportable",
        "authorised_classification.externally_shareable",
    ),
)
def test_synthetic_rights_cannot_be_widened(field: str) -> None:
    authorization, data_rights, environment = _documents()
    _set_nested(data_rights, field, True)

    failures = validate_controls(authorization, data_rights, environment)

    assert "RIGHTS_SYNTHETIC_ONLY" in _codes(failures)
    assert any(failure.field == f"data_rights.{field}" for failure in failures)


@pytest.mark.parametrize(
    "field",
    (
        "export.allowed",
        "export.local_evidence_pack_allowed",
        "export.network_transfer_allowed",
        "export.removable_media_transfer_allowed",
    ),
)
def test_every_data_rights_export_path_is_denied(field: str) -> None:
    authorization, data_rights, environment = _documents()
    _set_nested(data_rights, field, True)

    failures = validate_controls(authorization, data_rights, environment)

    assert "RIGHTS_EXPORT_DENIED" in _codes(failures)
    assert any(failure.field == f"data_rights.{field}" for failure in failures)


def test_required_prohibited_uses_cannot_be_removed() -> None:
    authorization, data_rights, environment = _documents()
    data_rights["prohibited_uses"].remove("external_sharing")

    failures = validate_controls(authorization, data_rights, environment)

    assert "RIGHTS_PROHIBITED_USE" in _codes(failures)
    assert any("external_sharing" in failure.detail for failure in failures)


def test_non_loopback_service_bind_is_rejected() -> None:
    authorization, data_rights, environment = _documents()
    environment["services"]["fastapi"]["bind_address"] = "0.0.0.0"

    failures = validate_controls(authorization, data_rights, environment)

    assert "ENV_SERVICE_BIND" in _codes(failures)
    assert any(failure.field == "environment.services.fastapi.bind_address" for failure in failures)


def test_required_embedded_store_cannot_be_removed() -> None:
    authorization, data_rights, environment = _documents()
    del environment["services"]["embedded_sqlite"]

    failures = validate_controls(authorization, data_rights, environment)

    assert "ENV_CONTAINER_FREE" in _codes(failures)
    assert any(
        failure.field.startswith("environment.services.embedded_sqlite.") for failure in failures
    )


def test_container_execution_is_rejected() -> None:
    authorization, data_rights, environment = _documents()
    environment["services"]["embedded_sqlite"]["execution"] = "docker_compose"

    failures = validate_controls(authorization, data_rights, environment)

    assert "ENV_CONTAINER_FREE" in _codes(failures)
    assert any("container execution is forbidden" in failure.detail for failure in failures)


def test_network_allowlist_must_remain_loopback_only() -> None:
    authorization, data_rights, environment = _documents()
    environment["network"]["allowed_bind_addresses"].append("0.0.0.0")

    failures = validate_controls(authorization, data_rights, environment)

    assert "ENV_LOOPBACK_ONLY" in _codes(failures)


@pytest.mark.parametrize(
    "field",
    (
        "runtime.public_endpoint_allowed",
        "runtime.cloud_resource_allowed",
        "runtime.remote_deployment_allowed",
        "runtime.external_model_call_allowed",
        "identity.external_identity_allowed",
        "telemetry.hosted_telemetry_allowed",
        "delivery.git_remote_allowed",
        "delivery.infrastructure_deployment_allowed",
    ),
)
def test_remote_cloud_and_external_enablement_is_rejected(field: str) -> None:
    authorization, data_rights, environment = _documents()
    _set_nested(environment, field, True)

    failures = validate_controls(authorization, data_rights, environment)

    assert "ENV_REMOTE_OR_EXTERNAL_DISABLED" in _codes(failures)
    assert any(failure.field == f"environment.{field}" for failure in failures)


def test_validator_is_read_only_and_does_not_open_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    control_paths = (
        ROOT / AUTHORIZATION_PATH,
        ROOT / DATA_RIGHTS_PATH,
        ROOT / ENVIRONMENT_PATH,
    )
    before = {path: path.read_bytes() for path in control_paths}

    def _reject_network(*args: object, **kwargs: object) -> None:
        raise AssertionError(f"unexpected network call: args={args!r}, kwargs={kwargs!r}")

    monkeypatch.setattr(socket, "create_connection", _reject_network)

    assert validate_governance(ROOT) == []
    assert {path: path.read_bytes() for path in control_paths} == before
