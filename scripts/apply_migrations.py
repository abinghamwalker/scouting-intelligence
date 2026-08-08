"""Apply the append-only schema to the guarded embedded database."""

from __future__ import annotations

from scouting.storage.embedded import upgrade_database


def main() -> int:
    upgrade_database()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
