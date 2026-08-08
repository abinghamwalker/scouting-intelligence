"""Fail-closed authentication, authorization, and eligibility policy."""

from .authentication import (
    AuthenticationDenied,
    SessionAuthenticator,
    SyntheticAccount,
    SyntheticPrincipal,
)
from .authorization import (
    AuthorizationDecision,
    AuthorizationDenied,
    AuthorizationPolicy,
    AuthorizationRequest,
    ResourceContext,
)
from .eligibility import EligibilityDecision, SyntheticRightsPolicy
from .r1 import (
    LocalRole,
    LocalSessionService,
    R1AuthenticationDenied,
    R1AuthorizationDenied,
    R1AuthorizationPolicy,
    R1Principal,
    R1Resource,
)

__all__ = [
    "AuthenticationDenied",
    "AuthorizationDecision",
    "AuthorizationDenied",
    "AuthorizationPolicy",
    "AuthorizationRequest",
    "EligibilityDecision",
    "ResourceContext",
    "SessionAuthenticator",
    "SyntheticAccount",
    "SyntheticPrincipal",
    "SyntheticRightsPolicy",
    "LocalRole",
    "LocalSessionService",
    "R1AuthenticationDenied",
    "R1AuthorizationDenied",
    "R1AuthorizationPolicy",
    "R1Principal",
    "R1Resource",
]
