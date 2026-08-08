"""Deterministic local reporting for the historical research workbench."""

from .research import (
    RenderedResearchReport,
    ResearchReportInputError,
    render_research_report,
)

__all__ = [
    "RenderedResearchReport",
    "ResearchReportInputError",
    "render_research_report",
]
