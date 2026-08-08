"""Validate the current local governance controls without mutating them."""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, cast

import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
AUTHORIZATION_PATH = Path("configs/policies/authorization.yaml")
DATA_RIGHTS_PATH = Path("configs/policies/data-rights.yaml")
ENVIRONMENT_PATH = Path("configs/environments/w03-local-review.yaml")

_MISSING = object()

REQUIRED_ROLE_ACTIONS: dict[str, frozenset[str]] = {
    "analyst": frozenset({"role_brief.create", "retrieval.create", "shortlist.create"}),
    "scout": frozenset({"observation.create", "observation.flag_disagreement"}),
    "approver": frozenset({"role_brief.approve", "shortlist_entry.approve"}),
    "admin": frozenset({"local_account.assign_role", "audit.read"}),
}
REQUIRED_GLOBAL_DENIES = frozenset(
    {
        "recruitment.autonomous_select",
        "recruitment.autonomous_approve",
        "protected_trait.infer",
        "protected_trait.rank",
        "evidence.external_share",
        "evidence.external_model_send",
        "audit.update",
        "audit.delete",
        "tenant.cross_access",
    }
)
REQUIRED_PROHIBITED_USES = frozenset(
    {
        "real_data_ingestion",
        "open_data_ingestion",
        "licensed_provider_data_ingestion",
        "personal_data_processing",
        "external_export",
        "external_sharing",
        "external_model_call",
        "public_demo",
        "cloud_or_remote_storage",
        "production_recruitment_decision",
    }
)


@dataclass(frozen=True)
class ValidationFailure:
    """One actionable semantic failure."""

    code: str
    field: str
    detail: str


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    """Load a YAML mapping through a read-only file operation."""
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"{path}: expected a YAML mapping at the document root")
    return cast(dict[str, Any], loaded)


def _get(document: Mapping[str, Any], dotted_field: str) -> Any:
    current: Any = document
    for part in dotted_field.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return _MISSING
        current = current[part]
    return current


def _expect_equal(
    failures: list[ValidationFailure],
    document_name: str,
    document: Mapping[str, Any],
    field: str,
    expected: object,
    code: str,
) -> None:
    actual = _get(document, field)
    if actual != expected:
        rendered = "<missing>" if actual is _MISSING else repr(actual)
        failures.append(
            ValidationFailure(
                code=code,
                field=f"{document_name}.{field}",
                detail=f"expected {expected!r}; found {rendered}",
            )
        )


def _string_set(value: Any) -> frozenset[str] | None:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return None
    return frozenset(value)


def _validate_authorization(
    authorization: Mapping[str, Any],
    failures: list[ValidationFailure],
) -> None:
    _expect_equal(
        failures,
        "authorization",
        authorization,
        "schema_version",
        1,
        "AUTH_POLICY_ID",
    )
    _expect_equal(
        failures,
        "authorization",
        authorization,
        "policy_id",
        "w03-authorization-v1",
        "AUTH_POLICY_ID",
    )

    for field in (
        "decision.default",
        "decision.unknown_actor",
        "decision.unknown_role",
        "decision.unknown_action",
        "decision.missing_context",
        "decision.cross_tenant",
    ):
        _expect_equal(
            failures,
            "authorization",
            authorization,
            field,
            "deny",
            "AUTH_DEFAULT_DENY",
        )
    _expect_equal(
        failures,
        "authorization",
        authorization,
        "decision.all_applicable_policies_must_allow",
        True,
        "AUTH_DEFAULT_DENY",
    )

    roles = _get(authorization, "roles")
    if not isinstance(roles, Mapping):
        failures.append(
            ValidationFailure(
                code="AUTH_REQUIRED_ROLE",
                field="authorization.roles",
                detail="expected a role mapping containing analyst, scout, approver and admin",
            )
        )
    else:
        for role, required_actions in REQUIRED_ROLE_ACTIONS.items():
            role_definition = roles.get(role)
            if not isinstance(role_definition, Mapping):
                failures.append(
                    ValidationFailure(
                        code="AUTH_REQUIRED_ROLE",
                        field=f"authorization.roles.{role}",
                        detail=f"required role {role!r} is missing or is not a mapping",
                    )
                )
                continue
            actions = _string_set(role_definition.get("allow"))
            if actions is None:
                failures.append(
                    ValidationFailure(
                        code="AUTH_ROLE_ACTIONS",
                        field=f"authorization.roles.{role}.allow",
                        detail="expected an explicit list of allowed action identifiers",
                    )
                )
                continue
            missing_actions = sorted(required_actions - actions)
            if missing_actions:
                failures.append(
                    ValidationFailure(
                        code="AUTH_ROLE_ACTIONS",
                        field=f"authorization.roles.{role}.allow",
                        detail=f"missing required actions: {missing_actions}",
                    )
                )

    global_denies = _string_set(_get(authorization, "global_denies"))
    if global_denies is None:
        failures.append(
            ValidationFailure(
                code="AUTH_GLOBAL_DENY",
                field="authorization.global_denies",
                detail="expected an explicit list of globally denied actions",
            )
        )
    else:
        missing_denies = sorted(REQUIRED_GLOBAL_DENIES - global_denies)
        if missing_denies:
            failures.append(
                ValidationFailure(
                    code="AUTH_GLOBAL_DENY",
                    field="authorization.global_denies",
                    detail=f"missing required global denies: {missing_denies}",
                )
            )

    _expect_equal(
        failures,
        "authorization",
        authorization,
        "object_rules.all_resources.require_same_tenant",
        True,
        "AUTH_TENANT_DENY",
    )
    _expect_equal(
        failures,
        "authorization",
        authorization,
        "object_rules.audit.append_only",
        True,
        "AUTH_AUDIT_APPEND_ONLY",
    )
    _expect_equal(
        failures,
        "authorization",
        authorization,
        "audit.required_for_material_actions",
        True,
        "AUTH_AUDIT_APPEND_ONLY",
    )


def _validate_data_rights(
    data_rights: Mapping[str, Any],
    failures: list[ValidationFailure],
) -> None:
    _expect_equal(failures, "data_rights", data_rights, "schema_version", 1, "RIGHTS_POLICY_ID")
    _expect_equal(
        failures,
        "data_rights",
        data_rights,
        "policy_id",
        "w03-synthetic-data-rights-v1",
        "RIGHTS_POLICY_ID",
    )
    _expect_equal(failures, "data_rights", data_rights, "default", "deny", "RIGHTS_DEFAULT_DENY")

    required_classification: dict[str, object] = {
        "authorised_classification.id": "w03_synthetic_generated",
        "authorised_classification.origin": "generated",
        "authorised_classification.location": "local_project_roots_only",
        "authorised_classification.personal_data": False,
        "authorised_classification.real_person_or_club_data": False,
        "authorised_classification.provider_data": False,
        "authorised_classification.confidential_user_data": False,
        "authorised_classification.exportable": False,
        "authorised_classification.externally_shareable": False,
        "authorised_classification.evidence_use": "test_only",
        "admission.on_missing_or_unknown_classification": "reject",
        "admission.inherit_strictest_upstream_rights": True,
    }
    for field, expected in required_classification.items():
        _expect_equal(
            failures,
            "data_rights",
            data_rights,
            field,
            expected,
            "RIGHTS_SYNTHETIC_ONLY",
        )

    for field in (
        "export.allowed",
        "export.local_evidence_pack_allowed",
        "export.network_transfer_allowed",
        "export.removable_media_transfer_allowed",
    ):
        _expect_equal(
            failures,
            "data_rights",
            data_rights,
            field,
            False,
            "RIGHTS_EXPORT_DENIED",
        )

    prohibited_uses = _string_set(_get(data_rights, "prohibited_uses"))
    if prohibited_uses is None:
        failures.append(
            ValidationFailure(
                code="RIGHTS_PROHIBITED_USE",
                field="data_rights.prohibited_uses",
                detail="expected an explicit list of prohibited uses",
            )
        )
    else:
        missing_uses = sorted(REQUIRED_PROHIBITED_USES - prohibited_uses)
        if missing_uses:
            failures.append(
                ValidationFailure(
                    code="RIGHTS_PROHIBITED_USE",
                    field="data_rights.prohibited_uses",
                    detail=f"missing required prohibited uses: {missing_uses}",
                )
            )


def _validate_environment(
    environment: Mapping[str, Any],
    failures: list[ValidationFailure],
) -> None:
    _expect_equal(failures, "environment", environment, "schema_version", 1, "ENVIRONMENT_ID")
    _expect_equal(
        failures,
        "environment",
        environment,
        "environment_id",
        "w03-local-review",
        "ENVIRONMENT_ID",
    )
    _expect_equal(
        failures,
        "environment",
        environment,
        "runtime.tenant_mode",
        "single-tenant",
        "ENV_LOCAL_ONLY",
    )
    _expect_equal(
        failures,
        "environment",
        environment,
        "network.bind_scope",
        "loopback_only",
        "ENV_LOOPBACK_ONLY",
    )
    _expect_equal(
        failures,
        "environment",
        environment,
        "network.allowed_bind_addresses",
        ["127.0.0.1"],
        "ENV_LOOPBACK_ONLY",
    )

    services = _get(environment, "services")
    if not isinstance(services, Mapping):
        failures.append(
            ValidationFailure(
                code="ENV_SERVICE_BIND",
                field="environment.services",
                detail="expected a service mapping with explicit local bindings",
            )
        )
    else:
        for service_name, service in services.items():
            if not isinstance(service, Mapping):
                failures.append(
                    ValidationFailure(
                        code="ENV_SERVICE_BIND",
                        field=f"environment.services.{service_name}",
                        detail="expected a service mapping",
                    )
                )
                continue
            if "bind_address" in service and service["bind_address"] != "127.0.0.1":
                failures.append(
                    ValidationFailure(
                        code="ENV_SERVICE_BIND",
                        field=f"environment.services.{service_name}.bind_address",
                        detail=(
                            "expected loopback address '127.0.0.1'; "
                            f"found {service['bind_address']!r}"
                        ),
                    )
                )
            if "bind_address" in service and service.get("exposure") != "loopback_only":
                failures.append(
                    ValidationFailure(
                        code="ENV_SERVICE_BIND",
                        field=f"environment.services.{service_name}.exposure",
                        detail=(
                            "a bound service must declare 'loopback_only'; "
                            f"found {service.get('exposure')!r}"
                        ),
                    )
                )
        for service_name in ("fastapi",):
            _expect_equal(
                failures,
                "environment",
                environment,
                f"services.{service_name}.bind_address",
                "127.0.0.1",
                "ENV_SERVICE_BIND",
            )
            _expect_equal(
                failures,
                "environment",
                environment,
                f"services.{service_name}.exposure",
                "loopback_only",
                "ENV_SERVICE_BIND",
            )
        for forbidden_service in ("postgres", "postgres_pgvector", "redis"):
            if forbidden_service in services:
                failures.append(
                    ValidationFailure(
                        code="ENV_CONTAINER_FREE",
                        field=f"environment.services.{forbidden_service}",
                        detail="external database/cache services are forbidden",
                    )
                )
        for service_name, service in services.items():
            if isinstance(service, Mapping) and service.get("execution") in {
                "docker",
                "docker_compose",
                "container",
            }:
                failures.append(
                    ValidationFailure(
                        code="ENV_CONTAINER_FREE",
                        field=f"environment.services.{service_name}.execution",
                        detail="container execution is forbidden",
                    )
                )

    for field in (
        "runtime.public_endpoint_allowed",
        "runtime.cloud_resource_allowed",
        "runtime.remote_deployment_allowed",
        "runtime.external_model_call_allowed",
        "runtime.containers_allowed",
        "runtime.external_service_processes_allowed",
        "network.lan_bind_allowed",
        "network.public_bind_allowed",
        "network.external_runtime_connections_allowed",
        "identity.external_identity_allowed",
        "identity.hosted_identity_allowed",
        "data.real_data_allowed",
        "data.personal_data_allowed",
        "data.external_export_allowed",
        "data.external_sharing_allowed",
        "storage.outside_root_reads_allowed",
        "storage.outside_root_writes_allowed",
        "storage.escaped_symlinks_allowed",
        "telemetry.hosted_telemetry_allowed",
        "telemetry.external_telemetry_export_allowed",
        "telemetry.confidential_payload_logging_allowed",
        "secrets.committed_values_allowed",
        "delivery.git_remote_allowed",
        "delivery.hosted_ci_allowed",
        "delivery.public_registry_allowed",
        "delivery.infrastructure_deployment_allowed",
        "delivery.container_definition_allowed",
        "storage.external_database_allowed",
        "storage.external_cache_or_queue_allowed",
    ):
        _expect_equal(
            failures,
            "environment",
            environment,
            field,
            False,
            "ENV_REMOTE_OR_EXTERNAL_DISABLED",
        )

    _expect_equal(
        failures,
        "environment",
        environment,
        "identity.deny_by_default",
        True,
        "ENV_LOCAL_ONLY",
    )
    _expect_equal(
        failures,
        "environment",
        environment,
        "data.allowed_classifications",
        ["w03_synthetic_generated"],
        "ENV_DATA_BOUNDARY",
    )
    _expect_equal(
        failures,
        "environment",
        environment,
        "data.frozen_synthetic_fixtures_only",
        True,
        "ENV_DATA_BOUNDARY",
    )
    _expect_equal(
        failures,
        "environment",
        environment,
        "services.worker.network_listener",
        False,
        "ENV_SERVICE_BIND",
    )
    _expect_equal(
        failures,
        "environment",
        environment,
        "services.embedded_sqlite.execution",
        "root_uv_environment",
        "ENV_CONTAINER_FREE",
    )
    _expect_equal(
        failures,
        "environment",
        environment,
        "services.embedded_sqlite.required",
        True,
        "ENV_CONTAINER_FREE",
    )
    _expect_equal(
        failures,
        "environment",
        environment,
        "services.embedded_sqlite.network_listener",
        False,
        "ENV_CONTAINER_FREE",
    )
    _expect_equal(
        failures,
        "environment",
        environment,
        "services.embedded_sqlite.credentials_required",
        False,
        "ENV_CONTAINER_FREE",
    )
    _expect_equal(
        failures,
        "environment",
        environment,
        "services.embedded_sqlite.single_tenant_enforced",
        True,
        "ENV_CONTAINER_FREE",
    )
    _expect_equal(
        failures,
        "environment",
        environment,
        "storage.operational_store",
        "embedded_sqlite",
        "ENV_CONTAINER_FREE",
    )
    _expect_equal(
        failures,
        "environment",
        environment,
        "storage.analytical_store",
        "parquet_duckdb",
        "ENV_CONTAINER_FREE",
    )
    _expect_equal(
        failures,
        "environment",
        environment,
        "services.model_registry.enabled",
        False,
        "ENV_REMOTE_OR_EXTERNAL_DISABLED",
    )
    _expect_equal(
        failures,
        "environment",
        environment,
        "services.model_registry.implementation",
        "versioned_local_manifests",
        "ENV_CONTAINER_FREE",
    )
    _expect_equal(
        failures,
        "environment",
        environment,
        "services.model_registry.external_service_allowed",
        False,
        "ENV_CONTAINER_FREE",
    )


def validate_controls(
    authorization: Mapping[str, Any],
    data_rights: Mapping[str, Any],
    environment: Mapping[str, Any],
) -> list[ValidationFailure]:
    """Validate already-loaded controls without changing the supplied mappings."""
    failures: list[ValidationFailure] = []
    _validate_authorization(authorization, failures)
    _validate_data_rights(data_rights, failures)
    _validate_environment(environment, failures)
    return failures


def validate_governance(root: Path = ROOT) -> list[ValidationFailure]:
    """Read and validate the three frozen control files."""
    documents: dict[str, dict[str, Any]] = {}
    failures: list[ValidationFailure] = []
    for name, relative_path in (
        ("authorization", AUTHORIZATION_PATH),
        ("data_rights", DATA_RIGHTS_PATH),
        ("environment", ENVIRONMENT_PATH),
    ):
        try:
            documents[name] = load_yaml_mapping(root / relative_path)
        except (OSError, ValueError, yaml.YAMLError) as error:
            failures.append(
                ValidationFailure(
                    code="DOCUMENT_LOAD_ERROR",
                    field=str(relative_path),
                    detail=str(error),
                )
            )
    if failures:
        return failures
    return validate_controls(
        documents["authorization"],
        documents["data_rights"],
        documents["environment"],
    )


def main() -> int:
    """Emit one machine-readable result and return non-zero on any failure."""
    failures = validate_governance()
    status = "PASS" if not failures else "FAIL"
    print(
        json.dumps(
            {
                "schema_version": 1,
                "validator": "validate_w03_governance",
                "scope": "current W03-derived authorization, data-rights and local-review controls",
                "status": status,
                "failures": [asdict(failure) for failure in failures],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
