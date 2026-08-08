"""Pure, dependency-free ranking metric and bootstrap calculations.

This module deliberately accepts and returns only canonical primitive values.  Contract
models are constructed by the thin adapters in ``evaluation`` and ``evaluation.core``.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass
from typing import cast

METRICS = ("precision", "recall", "ndcg", "coverage")


@dataclass(frozen=True, slots=True)
class Calculation:
    per_query: tuple[dict[str, object], ...]
    aggregate: dict[str, object]
    interval: dict[str, object]


def _digest(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode(
            "utf-8"
        )
    ).hexdigest()


def _sequence_digest(values: tuple[str, ...]) -> str:
    return hashlib.sha256(
        json.dumps(values, ensure_ascii=True, separators=(",", ":")).encode()
    ).hexdigest()


def _metric_payload(
    *,
    metric: str,
    k: int,
    protocol_digest: str,
    query_ids: tuple[str, ...],
    input_digest: str,
    value: float | None = None,
    numerator: float | None = None,
    denominator: float | None = None,
    reason: str | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "metric": metric,
        "k": k,
        "protocol_digest": protocol_digest,
        "evaluated_query_digest": _sequence_digest(query_ids),
        "input_digest": input_digest,
        "value": value,
        "numerator": numerator,
        "denominator": denominator,
        "status": "COMPUTED" if value is not None else "INSUFFICIENT_DENOMINATOR",
        "reason": reason,
    }
    payload["result_digest"] = _digest(payload)
    return payload


def canonical_score(score: int | float) -> float:
    """Normalize integer and float score representations at the shared boundary."""
    value = float(score)
    if not math.isfinite(value) or (value == 0.0 and math.copysign(1.0, value) < 0):
        raise ValueError("ranked item requires a non-empty candidate and finite canonical score")
    return value


def _row_payload(
    row: tuple[str, tuple[str, ...], tuple[int | float, ...], tuple[str, ...]],
) -> dict[str, object]:
    query_id, candidate_ids, scores, labels = row
    return {
        "query_id": query_id,
        "candidate_universe": tuple(sorted(candidate_ids)),
        "items": tuple(
            zip(candidate_ids, (canonical_score(score) for score in scores), labels, strict=True)
        ),
    }


def derive_ranking_metric_children(
    *,
    protocol_digest: str,
    declared_k: tuple[int, ...],
    partial_gain: float,
    partial_counts_for_precision_recall: bool,
    bootstrap_seed: int,
    bootstrap_resamples: int,
    bootstrap_confidence: float,
    bootstrap_method: str,
    rows: tuple[tuple[str, tuple[str, ...], tuple[int | float, ...], tuple[str, ...]], ...],
    metric: str,
    k: int,
) -> Calculation:
    """Return canonical primitive metric and percentile-bootstrap payloads."""
    if metric not in METRICS:
        raise ValueError("protocol does not support query bootstrap for metric")
    if k not in declared_k:
        raise ValueError("bootstrap metric and k must be declared by protocol")
    ordered = tuple(sorted(rows, key=lambda row: row[0]))
    if not ordered or len({row[0] for row in ordered}) != len(ordered):
        raise ValueError("bootstrap rows must be non-empty with unique query IDs")

    def result(
        row: tuple[str, tuple[str, ...], tuple[int | float, ...], tuple[str, ...]],
    ) -> dict[str, object]:
        query_id, candidate_ids, _, labels = row
        input_digest = _digest({"row": _row_payload(row), "k": k})
        if len(candidate_ids) < k:
            return _metric_payload(
                metric=metric,
                k=k,
                protocol_digest=protocol_digest,
                query_ids=(query_id,),
                input_digest=input_digest,
                reason="candidate_universe_smaller_than_k",
            )
        if any(label in {"UNJUDGED", "ABSTAIN"} for label in labels):
            return _metric_payload(
                metric=metric,
                k=k,
                protocol_digest=protocol_digest,
                query_ids=(query_id,),
                input_digest=input_digest,
                reason="incomplete_or_abstained_labels",
            )

        def pr_gain(label: str) -> float:
            return (
                1.0
                if label == "RELEVANT"
                else partial_gain
                if label == "PARTIAL" and partial_counts_for_precision_recall
                else 0.0
            )

        def ndcg_gain(label: str) -> float:
            return 1.0 if label == "RELEVANT" else partial_gain if label == "PARTIAL" else 0.0

        top = labels[:k]
        if metric == "precision":
            numerator, denominator = sum(map(pr_gain, top)), float(k)
        elif metric == "recall":
            denominator = sum(map(pr_gain, labels))
            if denominator == 0.0:
                return _metric_payload(
                    metric=metric,
                    k=k,
                    protocol_digest=protocol_digest,
                    query_ids=(query_id,),
                    input_digest=input_digest,
                    reason="no_eligible_relevance_denominator",
                )
            numerator = sum(map(pr_gain, top))
        elif metric == "ndcg":
            numerator = sum(
                ndcg_gain(label) / math.log2(index + 2) for index, label in enumerate(top)
            )
            denominator = sum(
                gain / math.log2(index + 2)
                for index, gain in enumerate(sorted(map(ndcg_gain, labels), reverse=True)[:k])
            )
            if denominator == 0.0:
                return _metric_payload(
                    metric=metric,
                    k=k,
                    protocol_digest=protocol_digest,
                    query_ids=(query_id,),
                    input_digest=input_digest,
                    reason="no_eligible_ndcg_denominator",
                )
        else:
            numerator, denominator = float(k), float(len(candidate_ids))
        return _metric_payload(
            metric=metric,
            k=k,
            protocol_digest=protocol_digest,
            query_ids=(query_id,),
            input_digest=input_digest,
            value=numerator / denominator,
            numerator=numerator,
            denominator=denominator,
        )

    per_query = tuple(result(row) for row in ordered)
    query_ids = tuple(row[0] for row in ordered)
    aggregate_input = {
        "query_metric_digests": tuple(item["result_digest"] for item in per_query),
        "rows": tuple(_row_payload(row) for row in ordered),
        "metric": metric,
        "k": k,
    }
    input_digest = _digest(aggregate_input)
    if any(item.get("value") is None for item in per_query):
        aggregate = _metric_payload(
            metric=metric,
            k=k,
            protocol_digest=protocol_digest,
            query_ids=query_ids,
            input_digest=input_digest,
            reason="insufficient_query_metric",
        )
        interval: dict[str, object] = {
            "metric_result_digest": aggregate["result_digest"],
            "protocol_digest": protocol_digest,
            "evaluated_query_digest": _sequence_digest(query_ids),
            "input_digest": input_digest,
            "seed": bootstrap_seed,
            "resamples": bootstrap_resamples,
            "confidence": bootstrap_confidence,
            "method": bootstrap_method,
            "point_value": None,
            "resample_digest": None,
            "lower": None,
            "upper": None,
            "status": "INSUFFICIENT_DENOMINATOR",
            "reason": "insufficient_query_metric",
        }
        interval["interval_digest"] = _digest(interval)
        return Calculation(per_query, aggregate, interval)
    values = tuple(float(cast(float, item["value"])) for item in per_query)
    aggregate = _metric_payload(
        metric=metric,
        k=k,
        protocol_digest=protocol_digest,
        query_ids=query_ids,
        input_digest=input_digest,
        value=sum(values) / len(values),
        numerator=sum(values),
        denominator=float(len(values)),
    )
    # Deterministic statistical bootstrap PRNG; never security or credential randomness.
    rng = random.Random(bootstrap_seed)  # nosec B311
    samples = sorted(
        sum(values[rng.randrange(len(values))] for _ in values) / len(values)
        for _ in range(bootstrap_resamples)
    )
    alpha = (1.0 - bootstrap_confidence) / 2.0
    resample_digest = _digest(
        {
            "protocol_digest": protocol_digest,
            "query_metric_digests": tuple(item["result_digest"] for item in per_query),
            "values": values,
            "metric": metric,
            "k": k,
            "seed": bootstrap_seed,
            "resamples": bootstrap_resamples,
            "confidence": bootstrap_confidence,
            "method": bootstrap_method,
            "samples": samples,
        }
    )
    interval = {
        "metric_result_digest": aggregate["result_digest"],
        "protocol_digest": protocol_digest,
        "evaluated_query_digest": _sequence_digest(query_ids),
        "input_digest": input_digest,
        "point_value": aggregate["value"],
        "resample_digest": resample_digest,
        "seed": bootstrap_seed,
        "resamples": bootstrap_resamples,
        "confidence": bootstrap_confidence,
        "method": bootstrap_method,
        "lower": samples[int(math.floor(alpha * (len(samples) - 1)))],
        "upper": samples[int(math.ceil((1.0 - alpha) * (len(samples) - 1)))],
        "status": "COMPUTED",
        "reason": None,
    }
    interval["interval_digest"] = _digest(interval)
    return Calculation(per_query, aggregate, interval)
