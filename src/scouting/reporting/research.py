"""Content-addressed JSON and HTML reports for exact W09 research results."""

from __future__ import annotations

import hashlib
import html
import json
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Literal, cast

from scouting.contracts.research import (
    RESEARCH_CLAIM_BOUNDARY,
    ResearchComparison,
    ResearchQueryMode,
    ResearchQueryResult,
    ResearchReportDescriptor,
)
from scouting.contracts.validation import revalidate_exact_contract
from scouting.storage.formats import FormatError, canonical_json_bytes
from scouting.storage.research import research_report_relative_path

type ResearchReportFormat = Literal["json", "html"]
type ResearchRightsClassification = Literal["wyscout_figshare_v5_cc_by_4"]

_HISTORICAL_SCOPE = "Historical resemblance research only."
_CLAIM_LIMITATION = (
    "Outputs describe similarity within the retained 2017/18 historical dataset. "
    "They do not establish football relevance, future performance, or suitability "
    "for decisions."
)


class ResearchReportInputError(ValueError):
    """An input cannot be represented as an exact governed research report."""


@dataclass(frozen=True, slots=True)
class RenderedResearchReport:
    """Immutable report bytes and their exact content-addressed descriptor."""

    payload: bytes
    descriptor: ResearchReportDescriptor


def _validated_result(result: ResearchQueryResult) -> ResearchQueryResult:
    return revalidate_exact_contract(
        result,
        ResearchQueryResult,
        label="research result",
        error_type=ResearchReportInputError,
    )


def _validated_comparison(
    comparison: ResearchComparison | None,
) -> ResearchComparison | None:
    if comparison is None:
        return None
    return revalidate_exact_contract(
        comparison,
        ResearchComparison,
        label="research comparison",
        error_type=ResearchReportInputError,
    )


def _require_exact_text(value: object, *, field: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{field} must be exact text")
    if not value or value != value.strip() or len(value) > 512:
        raise ResearchReportInputError(
            f"{field} must be trimmed, non-empty text of at most 512 characters"
        )
    if unicodedata.normalize("NFC", value) != value or any(
        0xD800 <= ord(character) <= 0xDFFF for character in value
    ):
        raise ResearchReportInputError(f"{field} must be canonical Unicode text")
    return value


def _validated_rights_limitations(value: tuple[str, ...]) -> tuple[str, ...]:
    if type(value) is not tuple or not value:
        raise TypeError("rights_limitations must be a non-empty exact tuple")
    limitations = tuple(
        _require_exact_text(item, field=f"rights_limitations[{index}]")
        for index, item in enumerate(value)
    )
    if len(limitations) != len(set(limitations)):
        raise ResearchReportInputError("rights limitations must be unique")
    return limitations


def _validated_generated_at(value: datetime, *, result: ResearchQueryResult) -> datetime:
    if type(value) is not datetime:
        raise TypeError("generated_at must be an exact datetime")
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ResearchReportInputError("generated_at must be timezone-aware UTC")
    if value < result.generated_at:
        raise ResearchReportInputError("report cannot be generated before its result")
    return value


def _validate_comparison_binding(
    result: ResearchQueryResult,
    comparison: ResearchComparison | None,
) -> None:
    if comparison is None:
        return
    request = comparison.request
    candidates_by_grain = {candidate.grain_id: candidate for candidate in result.candidates}
    if (
        request.result_id != result.result_id
        or request.result_digest != result.result_digest
        or request.query_digest != result.request.query_digest
        or request.pins != result.request.pins
        or not set(request.grain_ids).issubset(candidates_by_grain)
    ):
        raise ResearchReportInputError(
            "comparison must be pinned to candidates from the exact research result"
        )
    for row in comparison.rows:
        candidate = candidates_by_grain[row.grain_id]
        if (
            row.player_id != candidate.player_id
            or row.competition_id != candidate.competition_id
            or row.position_code != candidate.position_code
        ):
            raise ResearchReportInputError(
                "comparison row identity must equal its ranked result candidate"
            )


def _utc_text(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _report_document(
    *,
    result: ResearchQueryResult,
    comparison: ResearchComparison | None,
    generated_at: datetime,
    rights_classification: ResearchRightsClassification,
    attribution: str,
    rights_limitations: tuple[str, ...],
) -> dict[str, Any]:
    request = result.request
    return {
        "schema_version": 1,
        "report_kind": "historical_player_research",
        "generated_at": _utc_text(generated_at),
        "claim": {
            "boundary": RESEARCH_CLAIM_BOUNDARY,
            "statement": _HISTORICAL_SCOPE,
        },
        "limitations": [_CLAIM_LIMITATION, *rights_limitations],
        "rights": {
            "classification": rights_classification,
            "attribution": attribution,
            "limitations": list(rights_limitations),
        },
        "version_pins": request.pins.model_dump(mode="json"),
        "digests": {
            "query_digest": request.query_digest,
            "result_digest": result.result_digest,
            "comparison_request_digest": (
                comparison.request.comparison_request_digest if comparison is not None else None
            ),
            "comparison_digest": (comparison.comparison_digest if comparison is not None else None),
        },
        "query": request.model_dump(mode="json"),
        "population": result.population.model_dump(mode="json"),
        "ranked_historical_players": [
            candidate.model_dump(mode="json") for candidate in result.candidates
        ],
        "comparison": comparison.model_dump(mode="json") if comparison is not None else None,
        "warnings": list(result.warnings),
    }


def _escaped(value: object) -> str:
    if value is None:
        rendered = "—"
    elif type(value) is bool:
        rendered = "true" if value else "false"
    elif isinstance(value, (dict, list, tuple)):
        rendered = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    else:
        rendered = str(value)
    return html.escape(rendered, quote=True)


def _definition_rows(items: tuple[tuple[str, object], ...]) -> str:
    return "\n".join(
        f'<tr><th scope="row">{_escaped(label)}</th><td>{_escaped(value)}</td></tr>'
        for label, value in items
    )


def _list_items(items: tuple[str, ...]) -> str:
    return "\n".join(f"<li>{_escaped(item)}</li>" for item in items)


def _candidate_html(result: ResearchQueryResult) -> str:
    sections: list[str] = []
    for candidate in result.candidates:
        contribution_rows = "\n".join(
            "<tr>"
            f"<td>{_escaped(item.feature_name)}</td>"
            f"<td>{_escaped(item.weight)}</td>"
            f"<td>{_escaped(item.query_value)}</td>"
            f"<td>{_escaped(item.candidate_value)}</td>"
            f"<td>{_escaped(item.scaled_query_value)}</td>"
            f"<td>{_escaped(item.scaled_candidate_value)}</td>"
            f"<td>{_escaped(item.scaled_contrast)}</td>"
            f"<td>{_escaped(item.normalized_query_component)}</td>"
            f"<td>{_escaped(item.normalized_candidate_component)}</td>"
            f"<td>{_escaped(item.contribution)}</td>"
            "</tr>"
            for item in candidate.contributions
        )
        sections.append(
            '<article class="candidate">\n'
            f"<h3>#{candidate.rank} — {_escaped(candidate.display_name)}</h3>\n"
            "<table><tbody>"
            + _definition_rows(
                (
                    ("Grain ID", candidate.grain_id),
                    ("Player ID", candidate.player_id),
                    ("Competition ID", candidate.competition_id),
                    ("Position", candidate.position_code),
                    ("Minutes", candidate.minutes),
                    ("Score", candidate.score),
                    ("Claim boundary", candidate.claim_boundary),
                )
            )
            + "</tbody></table>\n"
            "<h4>Raw, scaled, and score contributions</h4>\n"
            '<div class="scroll"><table><thead><tr>'
            "<th>Feature</th><th>Weight</th><th>Query raw</th><th>Player raw</th>"
            "<th>Query scaled</th><th>Player scaled</th><th>Scaled contrast</th>"
            "<th>Query normalized</th><th>Player normalized</th><th>Contribution</th>"
            "</tr></thead><tbody>"
            f"{contribution_rows}</tbody></table></div>\n"
            "<h4>Limitations</h4>\n"
            f"<ul>{_list_items(candidate.limitations)}</ul>\n"
            "</article>"
        )
    return "\n".join(sections)


def _query_target_rows(result: ResearchQueryResult) -> tuple[tuple[str, object], ...]:
    request = result.request
    target: object
    if request.mode is ResearchQueryMode.EXEMPLAR:
        target = request.exemplar_grain_id
    else:
        target = [item.model_dump(mode="json") for item in request.profile]
    return (
        ("Query ID", request.query_id),
        ("Requested at", _utc_text(request.requested_at)),
        ("Feature cutoff", _utc_text(request.feature_cutoff_ts)),
        ("Mode", request.mode.value),
        ("Method", request.method.value),
        ("Target", target),
        ("Weights", [item.model_dump(mode="json") for item in request.weights]),
        ("Filters", request.filters.model_dump(mode="json")),
        ("Limit", request.limit),
    )


def _html_report(
    document: dict[str, Any],
    *,
    result: ResearchQueryResult,
    comparison: ResearchComparison | None,
    rights_limitations: tuple[str, ...],
) -> bytes:
    pins = result.request.pins.model_dump(mode="json")
    pin_rows = tuple((key.replace("_", " ").title(), value) for key, value in pins.items())
    population_rows = tuple(
        (key.replace("_", " ").title(), value)
        for key, value in result.population.model_dump(mode="json").items()
    )
    exact_json = canonical_json_bytes(document).decode("utf-8", errors="strict")
    comparison_section = (
        "<p>No comparison was attached to this report.</p>"
        if comparison is None
        else (
            "<p>The selected rows are bound to this exact result and retain identity, "
            "coverage, temporal, feature, and lineage evidence.</p>\n"
            f"<pre>{_escaped(comparison.model_dump(mode='json'))}</pre>"
        )
    )
    source_limitations = (_CLAIM_LIMITATION, *rights_limitations)
    markup = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Historical player research report</title>
<style>
:root {{ color-scheme: light; font-family: system-ui, sans-serif; line-height: 1.45; }}
body {{ color: #17202a; background: #f5f6f7; margin: 0; }}
main {{ max-width: 1180px; margin: auto; padding: 2rem; }}
h1, h2, h3, h4 {{ line-height: 1.2; }}
.boundary {{ border-left: .35rem solid #835c00; background: #fff4cf; padding: 1rem; }}
.candidate, section {{
  background: white; border: 1px solid #d8dde2; border-radius: .4rem;
  padding: 1rem; margin: 1rem 0;
}}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #d8dde2; padding: .45rem; text-align: left; vertical-align: top; }}
th {{ background: #eef1f4; }}
.scroll {{ overflow-x: auto; }}
pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #f4f5f6; padding: 1rem; }}
</style>
</head>
<body><main>
<h1>Historical player research report</h1>
<p class="boundary"><strong>{_escaped(_HISTORICAL_SCOPE)}</strong><br>{
        _escaped(_CLAIM_LIMITATION)
    }</p>
<section><h2>Report authority</h2><table><tbody>{
        _definition_rows(
            (
                ("Generated at", document["generated_at"]),
                ("Rights classification", document["rights"]["classification"]),
                ("Attribution", document["rights"]["attribution"]),
                ("Claim boundary", RESEARCH_CLAIM_BOUNDARY),
                ("Query digest", result.request.query_digest),
                ("Result digest", result.result_digest),
                (
                    "Comparison request digest",
                    comparison.request.comparison_request_digest if comparison else None,
                ),
                ("Comparison digest", comparison.comparison_digest if comparison else None),
            )
        )
    }</tbody></table><h3>Limitations</h3><ul>{_list_items(source_limitations)}</ul></section>
<section><h2>Query</h2><table><tbody>{
        _definition_rows(_query_target_rows(result))
    }</tbody></table></section>
<section><h2>Exact version pins</h2><table><tbody>{
        _definition_rows(pin_rows)
    }</tbody></table></section>
<section><h2>Full-population accounting</h2><table><tbody>{
        _definition_rows(population_rows)
    }</tbody></table></section>
<section><h2>Warnings</h2><ul>{_list_items(result.warnings)}</ul></section>
<section><h2>Ordered historical-player results</h2>{_candidate_html(result)}</section>
<section><h2>Selected comparison</h2>{comparison_section}</section>
<section><h2>Exact machine-readable report data</h2>
<p>This canonical JSON is embedded for complete local inspection.</p><pre>{
        html.escape(exact_json, quote=True)
    }</pre></section>
</main></body></html>
"""
    return markup.encode("utf-8", errors="strict")


def render_research_report(
    result: ResearchQueryResult,
    *,
    comparison: ResearchComparison | None = None,
    report_format: str,
    generated_at: datetime,
    rights_classification: str,
    attribution: str,
    rights_limitations: tuple[str, ...],
) -> RenderedResearchReport:
    """Render deterministic bytes bound to one exact result and optional comparison."""

    validated_result = _validated_result(result)
    validated_comparison = _validated_comparison(comparison)
    if type(report_format) is not str or report_format not in {"json", "html"}:
        raise ResearchReportInputError("report_format must be exactly 'json' or 'html'")
    if (
        type(rights_classification) is not str
        or rights_classification != "wyscout_figshare_v5_cc_by_4"
    ):
        raise ResearchReportInputError("rights classification is unsupported")
    validated_attribution = _require_exact_text(attribution, field="attribution")
    validated_limitations = _validated_rights_limitations(rights_limitations)
    validated_generated_at = _validated_generated_at(
        generated_at,
        result=validated_result,
    )
    _validate_comparison_binding(validated_result, validated_comparison)
    document = _report_document(
        result=validated_result,
        comparison=validated_comparison,
        generated_at=validated_generated_at,
        rights_classification=cast(ResearchRightsClassification, rights_classification),
        attribution=validated_attribution,
        rights_limitations=validated_limitations,
    )
    try:
        payload = (
            canonical_json_bytes(document)
            if report_format == "json"
            else _html_report(
                document,
                result=validated_result,
                comparison=validated_comparison,
                rights_limitations=validated_limitations,
            )
        )
    except (FormatError, UnicodeError) as exc:
        raise ResearchReportInputError("report content is not canonical UTF-8") from exc
    report_digest = hashlib.sha256(payload).hexdigest()
    descriptor = ResearchReportDescriptor(
        report_format=cast(ResearchReportFormat, report_format),
        report_relative_path=research_report_relative_path(
            report_digest,
            cast(ResearchReportFormat, report_format),
        ),
        report_digest=report_digest,
        generated_at=validated_generated_at,
        pins=validated_result.request.pins,
        query_digest=validated_result.request.query_digest,
        result_digest=validated_result.result_digest,
        comparison_digest=(
            validated_comparison.comparison_digest if validated_comparison is not None else None
        ),
    )
    return RenderedResearchReport(payload=payload, descriptor=descriptor)


__all__ = [
    "RenderedResearchReport",
    "ResearchReportFormat",
    "ResearchReportInputError",
    "ResearchRightsClassification",
    "render_research_report",
]
