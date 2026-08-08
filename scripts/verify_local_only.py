"""Verify the repository-wide local-only and one-uv-project boundary."""

from __future__ import annotations

import json
import os
import re

# Subprocess use is limited to fixed local verification commands.
import subprocess  # nosec B404
import sys
import tomllib
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_GROUPS = {
    "runtime",
    "data",
    "model",
    "orchestration",
    "test",
    "e2e",
    "lint-type",
    "security",
}
EXPECTED_DIRECTORIES = {
    "apps/web/templates",
    "apps/web/static/css",
    "apps/web/static/js",
    "apps/web/static/vendor",
    "services/api",
    "services/worker",
    "src/scouting/contracts",
    "src/scouting/sources",
    "src/scouting/identity",
    "src/scouting/data_products",
    "src/scouting/features",
    "src/scouting/roles",
    "src/scouting/modeling",
    "src/scouting/evaluation",
    "src/scouting/serving",
    "src/scouting/policy",
    "src/scouting/workflow",
    "src/scouting/observations",
    "src/scouting/operations",
    "src/scouting/storage",
    "src/scouting/web",
    "src/scouting/audit",
    "configs/sources",
    "configs/features",
    "configs/roles",
    "configs/models",
    "configs/policies",
    "configs/environments",
    "migrations",
    "orchestration/task_packets",
    "orchestration/reviews",
    "orchestration/checkpoints",
    "orchestration/templates",
    "scripts",
    "data/source",
    "data/reference",
    "data/working",
    "data/manifests",
    "runs",
    "research/threads",
    "reports/phase-gates",
    "reports/reviews",
    "reports/verification",
    "docs/adr",
    "docs/architecture",
    "docs/model-cards",
    "docs/dataset-cards",
    "docs/runbooks",
    "tests/contracts",
    "tests/unit",
    "tests/integration",
    "tests/e2e",
    "tests/security",
    "tests/performance",
    "tests/fixtures",
}
FORBIDDEN_MANIFEST_NAMES = {
    "package.json",
    "package-lock.json",
    "npm-shrinkwrap.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lock",
    "bun.lockb",
    "Pipfile",
    "Pipfile.lock",
    "poetry.lock",
    "pdm.lock",
    "setup.py",
    "setup.cfg",
}
FORBIDDEN_HOSTED_FILES = {
    ".gitlab-ci.yml",
    "azure-pipelines.yml",
    "bitbucket-pipelines.yml",
    "cloudbuild.yaml",
    "vercel.json",
    "netlify.toml",
    "fly.toml",
    "render.yaml",
    "Procfile",
}
FORBIDDEN_CONTAINER_FILENAMES = {
    "compose.yaml",
    "compose.yml",
    "docker-compose.yaml",
    "docker-compose.yml",
}
FORBIDDEN_RUNTIME_DEPENDENCIES = {
    "docker",
    "mlflow",
    "mlflow-skinny",
    "mlflow-tracing",
    "pgvector",
    "podman",
    "psycopg",
    "redis",
    "testcontainers",
}
IGNORED_WALK_DIRECTORIES = {
    ".git",
    ".venv",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
}
ALLOWED_OUTSIDE_ROOT_READS = {
    "../scouting-ml-production-blueprint.html",
    "../scouting-ml-agent-implementation-workflow.html",
}
CONTROLLING_PLAN_PATHS = (
    ROOT.parent / "scouting-ml-production-blueprint.html",
    ROOT.parent / "scouting-ml-agent-implementation-workflow.html",
)
STRUCTURED_CONFIG_SUFFIXES = {".json", ".toml", ".yaml", ".yml"}
PROHIBITED_URL = re.compile(r"(?:https?|ssh|git)://|git@")
W04_SOURCE_CONFIG = Path("configs/sources/w04-provider.yaml")
ALLOWED_W04_SOURCE_URLS = frozenset(
    {
        "https://creativecommons.org/licenses/by/4.0/",
        "https://doi.org/10.6084/m9.figshare.c.4415000.v5",
        "https://www.nature.com/articles/s41597-019-0247-7",
        "https://ndownloader.figshare.com/files/15073685",
        "https://ndownloader.figshare.com/files/15073697",
        "https://ndownloader.figshare.com/files/15073721",
        "https://ndownloader.figshare.com/files/14464622",
        "https://ndownloader.figshare.com/files/14464685",
        "https://ndownloader.figshare.com/files/21385245",
        "https://ndownloader.figshare.com/files/21385239",
    }
)
POLICY_MESSAGE = (
    "Push blocked: scouting-intelligence is local-only; Git remotes and pushes are prohibited."
)
HOOK_CONTENT = f"""#!/bin/sh
printf '%s\\n' '{POLICY_MESSAGE}'
exit 1
"""


def run(*command: str) -> subprocess.CompletedProcess[str]:
    """Run a local command without allowing shell interpretation."""
    # Callers provide fixed local verification commands.
    return subprocess.run(  # nosec B603
        list(command),
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def walk_project() -> Iterable[Path]:
    """Yield project paths while pruning Git internals and the root environment."""
    for current, directories, files in os.walk(ROOT):
        directories[:] = sorted(
            directory for directory in directories if directory not in IGNORED_WALK_DIRECTORIES
        )
        current_path = Path(current)
        for directory in directories:
            yield current_path / directory
        for filename in sorted(files):
            yield current_path / filename


def relative(paths: Iterable[Path]) -> list[str]:
    """Return sorted project-relative paths."""
    return sorted(str(path.relative_to(ROOT)) for path in paths)


def scalar_strings(value: Any) -> Iterable[str]:
    """Yield every string scalar from a nested configuration value."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for nested in value.values():
            yield from scalar_strings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from scalar_strings(nested)


def load_structured_config(path: Path) -> Any:
    """Load JSON, TOML, or YAML without executing configuration content."""
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if path.suffix == ".toml":
        with path.open("rb") as config_file:
            return tomllib.load(config_file)
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def is_allowed_config_url(config_path: Path, value: str) -> bool:
    """Allow only the exact reviewed W04 evidence and acquisition URLs."""
    literal_authority_path = ROOT / W04_SOURCE_CONFIG
    return config_path == literal_authority_path and value in ALLOWED_W04_SOURCE_URLS


def main() -> int:
    """Run every repository local-only invariant and emit one JSON result."""
    checks: list[dict[str, str]] = []
    failures: list[str] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})
        if not passed:
            failures.append(f"{name}: {detail}")

    project_paths = list(walk_project())

    remotes = run("git", "remote")
    remote_names = [line for line in remotes.stdout.splitlines() if line.strip()]
    record(
        "git_remotes",
        remotes.returncode == 0 and not remote_names,
        "zero configured remotes" if not remote_names else f"configured: {remote_names}",
    )

    branch = run("git", "branch", "--show-current")
    record(
        "git_branch",
        branch.returncode == 0 and branch.stdout.strip() == "main",
        f"active branch: {branch.stdout.strip() or '<unborn>'}",
    )

    hook_path_result = run("git", "rev-parse", "--git-path", "hooks/pre-push")
    active_hook = Path(hook_path_result.stdout.strip()).resolve()
    expected_hook = (ROOT / ".git/hooks/pre-push").resolve()
    hook_content_is_exact = (
        active_hook == expected_hook
        and active_hook.is_file()
        and active_hook.read_text(encoding="utf-8") == HOOK_CONTENT
    )
    hook_check = (
        # The exact approved hook content is verified first.
        subprocess.run(  # nosec B603
            [str(active_hook)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if hook_path_result.returncode == 0 and hook_content_is_exact
        else None
    )
    guard_passed = (
        hook_check is not None
        and os.access(active_hook, os.X_OK)
        and hook_check.returncode == 1
        and hook_check.stdout.strip() == POLICY_MESSAGE
    )
    record(
        "pre_push_guard",
        guard_passed,
        (
            f"{active_hook.relative_to(ROOT)} is executable and simulated exit is 1"
            if guard_passed
            else "active hook is missing, non-executable, or did not reject the simulated push"
        ),
    )

    pyprojects = [path for path in project_paths if path.name == "pyproject.toml"]
    locks = [path for path in project_paths if path.name == "uv.lock"]
    record(
        "one_pyproject", pyprojects == [ROOT / "pyproject.toml"], f"found: {relative(pyprojects)}"
    )
    record("one_uv_lock", locks == [ROOT / "uv.lock"], f"found: {relative(locks)}")

    virtual_environments = [ROOT / ".venv"] if (ROOT / ".venv").is_dir() else []
    virtual_environments.extend(
        path for path in project_paths if path.is_dir() and path.name in {".venv", "venv", "env"}
    )
    unique_environments = sorted(set(virtual_environments))
    record(
        "one_root_venv",
        unique_environments == [ROOT / ".venv"],
        f"found: {relative(unique_environments)}",
    )
    record(
        "running_from_root_venv",
        Path(sys.prefix).resolve() == (ROOT / ".venv").resolve(),
        f"sys.prefix: {Path(sys.prefix).resolve()}",
    )

    python_boundary = sys.version_info[:2] == (3, 12)
    record(
        "python_runtime",
        python_boundary,
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    )
    python_pin = (ROOT / ".python-version").read_text(encoding="utf-8").strip()
    record("python_pin", python_pin == "3.12", f".python-version: {python_pin!r}")

    with (ROOT / "pyproject.toml").open("rb") as project_file:
        project = tomllib.load(project_file)
    requires_python = project.get("project", {}).get("requires-python")
    record(
        "requires_python",
        requires_python == ">=3.12,<3.13",
        f"requires-python: {requires_python!r}",
    )
    groups = set(project.get("dependency-groups", {}))
    record(
        "dependency_groups",
        groups == EXPECTED_GROUPS,
        f"groups: {sorted(groups)}",
    )

    dependency_text = json.dumps(
        {
            "project": project.get("project", {}).get("dependencies", []),
            "groups": project.get("dependency-groups", {}),
            "sources": project.get("tool", {}).get("uv", {}).get("sources", {}),
        },
        sort_keys=True,
    )
    forbidden_dependency_url = re.search(r"(?:git\+|git@|ssh://|https?://)", dependency_text)
    record(
        "no_git_or_url_dependencies",
        forbidden_dependency_url is None,
        "dependency declarations contain no Git or direct URL sources",
    )

    forbidden_manifests = [
        path
        for path in project_paths
        if path.name in FORBIDDEN_MANIFEST_NAMES
        or path.name.lower().startswith("requirements")
        and path.suffix.lower() in {".in", ".txt"}
    ]
    record(
        "no_alternate_package_managers",
        not forbidden_manifests,
        f"forbidden manifests: {relative(forbidden_manifests)}",
    )

    node_manifests = [
        path
        for path in project_paths
        if path.name
        in {
            "package.json",
            "package-lock.json",
            "npm-shrinkwrap.json",
            "pnpm-lock.yaml",
            "yarn.lock",
            "bun.lock",
            "bun.lockb",
        }
    ]
    record("no_node_manifests", not node_manifests, f"found: {relative(node_manifests)}")

    hosted_paths = [
        path
        for path in project_paths
        if path.name in FORBIDDEN_HOSTED_FILES
        or ".github/workflows" in str(path.relative_to(ROOT))
        or ".circleci" in path.parts
        or ".openai/hosting.json" in str(path.relative_to(ROOT))
        or path.suffix == ".tf"
    ]
    record(
        "no_hosted_ci_or_deployment",
        not hosted_paths,
        f"found: {relative(hosted_paths)}",
    )

    container_artifacts = [
        path
        for path in project_paths
        if path.name in FORBIDDEN_CONTAINER_FILENAMES
        or path.name.startswith("compose.")
        or path.name.startswith("docker-compose.")
        or path.name.startswith("Dockerfile")
        or ".devcontainer" in path.parts
    ]
    record(
        "no_container_definitions",
        not container_artifacts,
        f"found: {relative(container_artifacts)}",
    )

    declared_dependencies = [
        dependency
        for dependencies in project.get("dependency-groups", {}).values()
        if isinstance(dependencies, list)
        for dependency in dependencies
        if isinstance(dependency, str)
    ]
    forbidden_runtime_dependencies = sorted(
        dependency
        for dependency in declared_dependencies
        if re.split(r"[^a-z0-9_-]", dependency.lower(), maxsplit=1)[0]
        in FORBIDDEN_RUNTIME_DEPENDENCIES
    )
    record(
        "no_external_service_dependencies",
        not forbidden_runtime_dependencies,
        f"found: {forbidden_runtime_dependencies}",
    )

    with (ROOT / "uv.lock").open("rb") as lock_file:
        locked = tomllib.load(lock_file)
    forbidden_locked_packages = sorted(
        package["name"]
        for package in locked.get("package", [])
        if isinstance(package, dict)
        and isinstance(package.get("name"), str)
        and package["name"].lower() in FORBIDDEN_RUNTIME_DEPENDENCIES
    )
    record(
        "no_external_service_packages_in_lock",
        not forbidden_locked_packages,
        f"found: {forbidden_locked_packages}",
    )

    master_plan = load_structured_config(ROOT / "orchestration/master_plan.yaml")
    phase_registry = load_structured_config(ROOT / "orchestration/phase_registry.yaml")
    architecture = (
        master_plan.get("architecture_constraints", {}) if isinstance(master_plan, dict) else {}
    )
    registry_authority = (
        phase_registry.get("architecture_authority", {}) if isinstance(phase_registry, dict) else {}
    )
    plans_are_container_free = all(
        path.is_file()
        and "container-free" in path.read_text(encoding="utf-8").lower()
        and "Docker Compose" not in path.read_text(encoding="utf-8")
        for path in CONTROLLING_PLAN_PATHS
    )
    container_free_authority = (
        architecture.get("runtime") == "container_free"
        and architecture.get("operational_store") == "embedded_sqlite"
        and registry_authority.get("container_free_required") is True
        and registry_authority.get("embedded_sqlite_required") is True
        and registry_authority.get("external_database_cache_queue_allowed") is False
        and (ROOT / "docs/adr/0004-container-free-embedded-runtime.md").is_file()
        and plans_are_container_free
    )
    record(
        "container_free_architecture_authority",
        container_free_authority,
        (
            "ADR, master plan, phase registry and both controlling plans require "
            "container-free embedded operation"
            if container_free_authority
            else "container-free authority is missing or inconsistent"
        ),
    )

    structured_configs = [
        path
        for path in project_paths
        if path.is_file()
        and path.suffix in STRUCTURED_CONFIG_SUFFIXES
        and (
            path == ROOT / "pyproject.toml"
            or path.is_relative_to(ROOT / "configs")
            or path.is_relative_to(ROOT / "orchestration")
        )
    ]
    config_parse_failures: list[str] = []
    outside_root_config: list[str] = []
    prohibited_config_urls: list[str] = []
    for config_path in structured_configs:
        try:
            loaded_config = load_structured_config(config_path)
        except (
            OSError,
            ValueError,
            json.JSONDecodeError,
            tomllib.TOMLDecodeError,
            yaml.YAMLError,
        ) as error:
            config_parse_failures.append(f"{config_path.relative_to(ROOT)}: {error}")
            continue
        for value in scalar_strings(loaded_config):
            if PROHIBITED_URL.search(value) and not is_allowed_config_url(config_path, value):
                prohibited_config_urls.append(f"{config_path.relative_to(ROOT)}: {value}")
            if value.startswith("../") and value not in ALLOWED_OUTSIDE_ROOT_READS:
                outside_root_config.append(f"{config_path.relative_to(ROOT)}: {value}")
            value_path = Path(value)
            if value_path.is_absolute() and not value_path.resolve().is_relative_to(ROOT):
                outside_root_config.append(f"{config_path.relative_to(ROOT)}: {value}")
    record(
        "structured_config_parses",
        not config_parse_failures,
        f"failures: {config_parse_failures}",
    )
    record(
        "no_outside_root_config",
        not outside_root_config,
        f"found: {sorted(set(outside_root_config))}",
    )
    record(
        "no_prohibited_config_urls",
        not prohibited_config_urls,
        f"found: {sorted(set(prohibited_config_urls))}",
    )

    missing_directories = sorted(
        directory for directory in EXPECTED_DIRECTORIES if not (ROOT / directory).is_dir()
    )
    record(
        "approved_directory_skeleton",
        not missing_directories,
        f"missing: {missing_directories}",
    )

    escaped_symlinks = []
    for path in project_paths:
        if path.is_symlink() and not path.resolve().is_relative_to(ROOT):
            escaped_symlinks.append(path)
    record(
        "no_outside_root_symlinks",
        not escaped_symlinks,
        f"found: {relative(escaped_symlinks)}",
    )

    ignored_venv = run("git", "check-ignore", "-q", ".venv")
    record(
        "root_venv_ignored",
        ignored_venv.returncode == 0,
        ".venv is ignored by local Git",
    )

    status = "PASS" if not failures else "FAIL"
    print(
        json.dumps(
            {
                "schema_version": 1,
                "validator": "verify_local_only",
                "scope": "repository local-only and one-root-uv-project boundary",
                "status": status,
                "checks": checks,
                "failures": failures,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    try:
        exit_code = main()
    except (
        OSError,
        RuntimeError,
        ValueError,
        json.JSONDecodeError,
        tomllib.TOMLDecodeError,
        yaml.YAMLError,
    ) as error:
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "validator": "verify_local_only",
                    "scope": "repository local-only and one-root-uv-project boundary",
                    "status": "FAIL",
                    "checks": [],
                    "failures": [
                        {
                            "code": "LOCAL_ONLY_VALIDATOR_ERROR",
                            "detail": str(error),
                        }
                    ],
                },
                indent=2,
                sort_keys=True,
            )
        )
        exit_code = 1
    raise SystemExit(exit_code)
