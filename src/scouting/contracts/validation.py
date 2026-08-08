"""Shared validation helpers for exact in-process contract authorities."""

from __future__ import annotations

from pydantic import ValidationError

from scouting.contracts.primitives import ContractModel


def revalidate_exact_contract[T: ContractModel, E: Exception](
    value: T,
    model: type[T],
    *,
    label: str,
    error_type: type[E],
) -> T:
    """Copy and revalidate one exact contract, mapping validation to a domain error."""

    if type(value) is not model:
        raise TypeError(f"{label} must be an exact {model.__name__}")
    try:
        return model.model_validate(value.model_dump(mode="python"))
    except ValidationError as exc:
        raise error_type(f"{label} contract rejected") from exc
