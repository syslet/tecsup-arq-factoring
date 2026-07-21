import re
from dataclasses import dataclass

from src.domain.exceptions.auth_exceptions import InvalidCciException


@dataclass(frozen=True)
class CciAccount:
    """Value object representing a Peruvian CCI (Código de Cuenta Interbancario)."""

    value: str

    def __post_init__(self) -> None:
        cleaned = self.value.strip() if self.value else ""
        if not re.match(r"^\d{20}$", cleaned):
            raise InvalidCciException(cleaned)
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value
