"""In-process structured logs, traces, and metrics with redacted attributes."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock
from time import monotonic_ns
from types import MappingProxyType
from uuid import UUID, uuid4

_ALLOWED_ATTRIBUTE_KEYS = frozenset(
    {
        "actor_id",
        "action",
        "method",
        "path",
        "policy_id",
        "request_id",
        "status_code",
        "tenant_id",
    }
)
_MAX_ATTRIBUTE_STRING_LENGTH = 512


@dataclass(frozen=True, slots=True)
class TelemetrySnapshot:
    """Immutable copy of local telemetry suitable for readiness review."""

    metrics: Mapping[str, int]
    logs: tuple[Mapping[str, object], ...]
    traces: tuple[Mapping[str, object], ...]


class LocalTelemetry:
    """Bounded local telemetry with no exporter and no payload/header capture."""

    def __init__(self, *, maximum_records: int = 500) -> None:
        if maximum_records < 1:
            raise ValueError("maximum_records must be positive")
        self._maximum_records = maximum_records
        self._metrics: Counter[str] = Counter()
        self._logs: list[dict[str, object]] = []
        self._traces: list[dict[str, object]] = []
        self._lock = Lock()

    def increment(self, metric: str) -> None:
        """Increment one local counter with a bounded metric name."""
        if not metric or len(metric) > 100:
            raise ValueError("metric name is invalid")
        with self._lock:
            self._metrics[metric] += 1

    def log(self, event: str, **attributes: object) -> None:
        """Record a structured event after dropping non-approved keys."""
        record: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event": event,
        }
        record.update(self._redact(attributes))
        with self._lock:
            self._logs.append(record)
            del self._logs[: -self._maximum_records]

    @contextmanager
    def trace(self, name: str, **attributes: object) -> Iterator[UUID]:
        """Record one local span without exporting or retaining request content."""
        trace_id = uuid4()
        started = monotonic_ns()
        outcome = "ok"
        try:
            yield trace_id
        except Exception:
            outcome = "error"
            raise
        finally:
            duration_ms = (monotonic_ns() - started) / 1_000_000
            record: dict[str, object] = {
                "trace_id": str(trace_id),
                "name": name,
                "outcome": outcome,
                "duration_ms": round(duration_ms, 3),
            }
            record.update(self._redact(attributes))
            with self._lock:
                self._traces.append(record)
                del self._traces[: -self._maximum_records]

    def snapshot(self) -> TelemetrySnapshot:
        """Return detached, JSON-compatible local evidence."""
        with self._lock:
            return TelemetrySnapshot(
                metrics=MappingProxyType(dict(self._metrics)),
                logs=tuple(MappingProxyType(dict(record)) for record in self._logs),
                traces=tuple(MappingProxyType(dict(record)) for record in self._traces),
            )

    def serialized_snapshot(self) -> str:
        """Serialize the snapshot for local tests without custom encoders."""
        snapshot = self.snapshot()
        return json.dumps(
            {
                "metrics": dict(snapshot.metrics),
                "logs": [dict(record) for record in snapshot.logs],
                "traces": [dict(record) for record in snapshot.traces],
            },
            sort_keys=True,
        )

    @staticmethod
    def _redact(attributes: Mapping[str, object]) -> dict[str, object]:
        redacted: dict[str, object] = {}
        for key, value in attributes.items():
            if key not in _ALLOWED_ATTRIBUTE_KEYS or value is None:
                continue
            if isinstance(value, UUID):
                redacted[key] = str(value)
            elif type(value) is str and len(value) <= _MAX_ATTRIBUTE_STRING_LENGTH:
                redacted[key] = value
            elif type(value) is int:
                redacted[key] = value
        return redacted
