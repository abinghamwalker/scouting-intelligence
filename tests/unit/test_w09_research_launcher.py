"""Focused contract checks for the loopback-only W09 launcher."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = PROJECT_ROOT / "scripts/start_w09_research_workbench.command"
EXPECTED_PREFIX = (
    "run",
    "--locked",
    "uvicorn",
    "services.api.w09_main:app",
    "--host",
    "127.0.0.1",
    "--port",
)


def _run_with_fake_uv(tmp_path: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_uv = fake_bin / "uv"
    fake_uv.write_text(
        "#!/bin/zsh\n"
        'print -r -- "cwd=$PWD"\n'
        'print -r -- "argc=$#"\n'
        'for argument in "$@"; do\n'
        '  print -r -- "arg=$argument"\n'
        "done\n"
    )
    fake_uv.chmod(0o700)
    environment = os.environ.copy()
    environment["PATH"] = f"{fake_bin}{os.pathsep}{environment['PATH']}"
    return subprocess.run(  # noqa: S603  # nosec B603
        ["zsh", os.fspath(LAUNCHER), *arguments],
        cwd=tmp_path,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )


def _expected_stdout(port: str) -> list[str]:
    command = (*EXPECTED_PREFIX, port, "--no-access-log")
    return [
        f"Starting W09 research workbench at http://127.0.0.1:{port}/",
        "Press Control-C in this terminal to stop the workbench.",
        f"cwd={PROJECT_ROOT}",
        f"argc={len(command)}",
        *(f"arg={argument}" for argument in command),
    ]


def test_launcher_has_valid_zsh_syntax_and_static_local_only_guards() -> None:
    completed = subprocess.run(  # noqa: S603  # nosec B603
        ["zsh", "-n", os.fspath(LAUNCHER)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr

    payload = LAUNCHER.read_text()
    tokens = payload.split()
    assert payload.startswith("#!/bin/zsh\nset -euo pipefail\n")
    assert payload.count("exec uv run --locked uvicorn services.api.w09_main:app") == 1
    assert "--host 127.0.0.1" in payload
    assert "--no-access-log" in tokens
    for forbidden in (
        "--reload",
        "--access-log",
        "0.0.0.0",
        "nohup",
        "caffeinate",
        "open",
        "&",
    ):
        assert forbidden not in tokens


def test_launcher_uses_default_port_and_exact_uvicorn_composition(tmp_path: Path) -> None:
    completed = _run_with_fake_uv(tmp_path)

    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
    assert completed.stdout.splitlines() == _expected_stdout("8769")


@pytest.mark.parametrize("port", ("1024", "43119", "65535"))
def test_launcher_accepts_one_numeric_port_in_range(tmp_path: Path, port: str) -> None:
    completed = _run_with_fake_uv(tmp_path, port)

    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
    assert completed.stdout.splitlines() == _expected_stdout(port)


@pytest.mark.parametrize(
    "port",
    ("", "1023", "65536", "not-a-port", "8769x", "999999999999999999999999"),
)
def test_launcher_rejects_invalid_ports_without_invoking_uv(tmp_path: Path, port: str) -> None:
    completed = _run_with_fake_uv(tmp_path, port)

    assert completed.returncode == 64
    assert completed.stdout == ""
    assert completed.stderr == "Port must be a numeric value from 1024 to 65535.\n"


def test_launcher_rejects_more_than_one_argument_without_invoking_uv(
    tmp_path: Path,
) -> None:
    completed = _run_with_fake_uv(tmp_path, "8769", "8770")

    assert completed.returncode == 64
    assert completed.stdout == ""
    assert completed.stderr == "Usage: start_w09_research_workbench.command [port]\n"
