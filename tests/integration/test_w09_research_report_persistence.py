"""Integration evidence for rendered W09 reports and immutable local persistence."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
from test_w09_research_storage import (
    _REPORT_GENERATED,
    _comparison,
    _digest,
    _request,
    _result,
)

from scouting.contracts.research import SavedResearchExperiment, canonical_research_digest
from scouting.reporting.research import render_research_report
from scouting.storage.embedded import create_embedded_engine
from scouting.storage.guarded import GuardedStorage
from scouting.storage.research import RESEARCH_REPORT_ROOT_NAME, ResearchExperimentStore

_CREATED_AT = datetime(2026, 8, 5, 10, 3, tzinfo=UTC)
_RIGHTS = "wyscout_figshare_v5_cc_by_4"
_ATTRIBUTION = "Wyscout public dataset on figshare, CC BY 4.0."
_RIGHTS_LIMITATIONS = ("Retained historical 2017/18 source scope only.",)


@pytest.mark.parametrize("report_format", ["json", "html"])
def test_rendered_report_saves_loads_and_replays_exact_bytes(
    tmp_path: Path,
    report_format: str,
) -> None:
    engine = create_embedded_engine(
        tmp_path / "research.sqlite3",
        allowed_root=tmp_path,
    )
    storage = GuardedStorage({RESEARCH_REPORT_ROOT_NAME: tmp_path / "research-reports"})
    store = ResearchExperimentStore(engine, storage)
    request = _request(limit=2)
    result = _result(request)
    comparison = _comparison(request, result)
    rendered = render_research_report(
        result,
        comparison=comparison,
        report_format=report_format,
        generated_at=_REPORT_GENERATED,
        rights_classification=_RIGHTS,
        attribution=_ATTRIBUTION,
        rights_limitations=_RIGHTS_LIMITATIONS,
    )
    fields = {
        "experiment_id": UUID(
            "50000000-0000-0000-0000-000000000001"
            if report_format == "json"
            else "50000000-0000-0000-0000-000000000002"
        ),
        "name": f"W09 deterministic {report_format} report",
        "note": "Frozen local historical-player research evidence.",
        "created_at": _CREATED_AT,
        "request": result.request,
        "result": result,
        "comparison": comparison,
        "report": rendered.descriptor,
    }
    draft = SavedResearchExperiment.model_construct(
        **fields,
        experiment_digest=_digest(0),
    )
    experiment = SavedResearchExperiment(
        **fields,
        experiment_digest=canonical_research_digest(
            draft.model_dump(mode="json", exclude={"experiment_digest"})
        ),
    )

    assert store.save_experiment(experiment, rendered.payload) == experiment
    assert store.load_experiment(experiment.experiment_id) == experiment
    summaries = store.list_experiments()
    assert len(summaries) == 1
    assert summaries[0].experiment_id == experiment.experiment_id
    assert summaries[0].query_id == experiment.request.query_id
    assert summaries[0].result_id == experiment.result.result_id
    assert summaries[0].report_format == experiment.report.report_format
    assert summaries[0].report_digest == experiment.report.report_digest
    assert summaries[0].experiment_digest == experiment.experiment_digest
    assert (
        storage.read_bytes(
            RESEARCH_REPORT_ROOT_NAME,
            rendered.descriptor.report_relative_path,
        )
        == rendered.payload
    )
    engine.dispose()
