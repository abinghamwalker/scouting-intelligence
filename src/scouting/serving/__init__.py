"""Single deterministic serving interface for the W03 synthetic journey."""

from .m0 import (
    M0_SERVING_CORE_VERSION,
    M0ServingCore,
    M0ServingError,
    M0ServingReason,
    serve_m0_batch,
    serve_m0_request,
)
from .synthetic import (
    RetrievalPresentationProfile,
    ServingDenied,
    ServingExplanation,
    ServingOutcome,
    SyntheticArtifactCatalog,
    SyntheticDomainSnapshot,
    SyntheticServingService,
)

__all__ = [
    "M0_SERVING_CORE_VERSION",
    "M0ServingCore",
    "M0ServingError",
    "M0ServingReason",
    "RetrievalPresentationProfile",
    "ServingDenied",
    "ServingExplanation",
    "ServingOutcome",
    "SyntheticArtifactCatalog",
    "SyntheticDomainSnapshot",
    "SyntheticServingService",
    "serve_m0_batch",
    "serve_m0_request",
]
