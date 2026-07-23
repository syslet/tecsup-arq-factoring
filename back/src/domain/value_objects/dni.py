import re
from dataclasses import dataclass

from src.domain.exceptions.auth_exceptions import InvalidDniException


@dataclass(frozen=True)
class Dni:
    """Value object representing a Peruvian DNI (Documento Nacional de Identidad)."""

    value: str

    def __post_init__(self) -> None:
        raw = str(self.value) if self.value is not None else ""
        cleaned = raw.strip()
        if not re.match(r"^\d{8}$", cleaned):
            raise InvalidDniException(cleaned)
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value
