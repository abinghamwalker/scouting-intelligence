"""Local-only ASGI entry point for W08; bind only to 127.0.0.1 in a manual study."""

from scouting.contracts import WorkflowEvidenceOrigin
from scouting.web.w08 import create_w08_app

app = create_w08_app(evidence_origin=WorkflowEvidenceOrigin.HUMAN_ENTERED_LOCAL)
