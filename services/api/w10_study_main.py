"""Composition root for the isolated historical-comparison participant form."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from scouting.storage.expert_study import (
    ExpertStudyConfigurationError,
    HistoricalComparisonPilotStore,
)
from scouting.web.w10_expert_study import create_historical_player_comparison_app

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# Retained stopped-pilot paths remain named for audit and are never opened here.
V2_PILOT_AUTHORITY_PATH = (
    PROJECT_ROOT / "data/working/w10/study/v2/pilot/mechanics-pilot-authority-v1.json"
)
V2_PILOT_DATABASE_PATH = PROJECT_ROOT / "data/working/w10/study/v2/pilot/mechanics-pilot-v2.sqlite3"
HISTORICAL_COMPARISON_PILOT_ROOT = PROJECT_ROOT / "data/working/w10/study/v2/pilot"
HISTORICAL_COMPARISON_AUTHORITY_PATH = (
    HISTORICAL_COMPARISON_PILOT_ROOT / "historical-player-comparison-pilot-authority-v1.json"
)
HISTORICAL_COMPARISON_DATABASE_PATH = (
    HISTORICAL_COMPARISON_PILOT_ROOT / "historical-player-comparison-pilot-v1.sqlite3"
)


def create_production_w10_app() -> FastAPI:
    try:
        store = HistoricalComparisonPilotStore(
            database_path=HISTORICAL_COMPARISON_DATABASE_PATH,
            authority_path=HISTORICAL_COMPARISON_AUTHORITY_PATH,
            allowed_root=HISTORICAL_COMPARISON_PILOT_ROOT,
        )
    except ExpertStudyConfigurationError as exc:
        return create_historical_player_comparison_app(store=None, unavailable_reason=str(exc))
    return create_historical_player_comparison_app(store=store)


app = create_production_w10_app()

if __name__ == "__main__":  # local, loopback-only participant form
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8771)

__all__ = [
    "HISTORICAL_COMPARISON_AUTHORITY_PATH",
    "HISTORICAL_COMPARISON_DATABASE_PATH",
    "V2_PILOT_AUTHORITY_PATH",
    "V2_PILOT_DATABASE_PATH",
    "app",
    "create_production_w10_app",
]
