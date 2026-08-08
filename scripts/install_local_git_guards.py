"""Install and verify the repository-local, deliberately failing pre-push hook."""

from __future__ import annotations

import argparse
import json
import os
import shutil

# Subprocess use is limited to fixed local Git commands and an exact verified hook.
import subprocess  # nosec B404
import sys
from pathlib import Path

POLICY_MESSAGE = (
    "Push blocked: scouting-intelligence is local-only; Git remotes and pushes are prohibited."
)
HOOK_CONTENT = f"""#!/bin/sh
printf '%s\\n' '{POLICY_MESSAGE}'
exit 1
"""
GIT_EXECUTABLE = shutil.which("git")


def run_git(root: Path, *args: str) -> str:
    """Run Git in the project and return stripped stdout."""
    if GIT_EXECUTABLE is None:
        raise RuntimeError("Git executable is unavailable")
    # The executable and arguments are locally fixed.
    completed = subprocess.run(  # nosec B603
        [GIT_EXECUTABLE, *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def repository_root() -> Path:
    """Resolve the repository root containing this installer."""
    script_root = Path(__file__).resolve().parents[1]
    root = Path(run_git(script_root, "rev-parse", "--show-toplevel")).resolve()
    if root != script_root:
        raise RuntimeError(f"installer must run from its owning repository: {script_root}")
    return root


def hook_path(root: Path) -> Path:
    """Return the active pre-push path after pinning hooks to this local repository."""
    git_dir_raw = run_git(root, "rev-parse", "--git-dir")
    git_dir = Path(git_dir_raw)
    if not git_dir.is_absolute():
        git_dir = root / git_dir
    git_dir = git_dir.resolve()
    expected_git_dir = (root / ".git").resolve()
    if git_dir != expected_git_dir:
        raise RuntimeError(f"unexpected Git directory: {git_dir}")

    hooks_dir = git_dir / "hooks"
    run_git(root, "config", "--local", "core.hooksPath", str(hooks_dir))
    resolved_hook = Path(run_git(root, "rev-parse", "--git-path", "hooks/pre-push")).resolve()
    expected_hook = (hooks_dir / "pre-push").resolve()
    if resolved_hook != expected_hook:
        raise RuntimeError(
            f"active pre-push path is outside the local Git directory: {resolved_hook}"
        )
    return expected_hook


def install_hook(path: Path) -> None:
    """Write the hook atomically and make it executable."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(HOOK_CONTENT, encoding="utf-8")
    temporary.chmod(0o755)
    os.replace(temporary, path)


def verify_hook(root: Path, path: Path) -> dict[str, object]:
    """Verify content, executable mode, activation, message, and deliberate failure."""
    if not path.is_file():
        raise RuntimeError(f"pre-push hook is missing: {path}")
    if path.read_text(encoding="utf-8") != HOOK_CONTENT:
        raise RuntimeError("pre-push hook content does not match the approved local-only guard")
    if not os.access(path, os.X_OK):
        raise RuntimeError("pre-push hook is not executable")

    # The hook content and location are verified immediately above.
    completed = subprocess.run(  # nosec B603
        [str(path)],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 1:
        raise RuntimeError(f"pre-push hook returned {completed.returncode}, expected 1")
    if completed.stdout.strip() != POLICY_MESSAGE:
        raise RuntimeError("pre-push hook did not print the approved local-only policy")

    return {
        "status": "PASS",
        "hook": str(path.relative_to(root)),
        "executable": True,
        "simulated_exit_code": completed.returncode,
        "message": completed.stdout.strip(),
    }


def main() -> int:
    """Install unless checking only, then emit machine-readable evidence."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the active guard without rewriting it",
    )
    args = parser.parse_args()

    try:
        root = repository_root()
        path = hook_path(root)
        if not args.check:
            install_hook(path)
        print(json.dumps(verify_hook(root, path), indent=2, sort_keys=True))
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, indent=2), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
