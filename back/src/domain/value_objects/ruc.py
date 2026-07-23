import re
from dataclasses import dataclass

from src.domain.exceptions.auth_exceptions import InvalidRucException


@dataclass(frozen=True)
class Ruc:
    """Value object representing a Peruvian RUC (Registro Único de Contribuyentes)."""

    value: str

    VALID_PREFIXES = ("10", "15", "17", "20")

    def __post_init__(self) -> None:
        raw = str(self.value) if self.value is not None else ""
        cleaned = raw.strip()
        if not re.match(r"^\d{11}$", cleaned) or not cleaned.startswith(self.VALID_PREFIXES):
            raise InvalidRucException(cleaned)
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value
