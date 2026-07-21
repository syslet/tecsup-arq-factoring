import re
from dataclasses import dataclass

from src.domain.exceptions.auth_exceptions import WeakPasswordException


@dataclass(frozen=True)
class Password:
    """Value object representing a strong user password."""

    value: str

    def __post_init__(self) -> None:
        val = self.value or ""
        if len(val) < 8:
            raise WeakPasswordException("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", val):
            raise WeakPasswordException("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", val):
            raise WeakPasswordException("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", val):
            raise WeakPasswordException("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", val):
            raise WeakPasswordException("Password must contain at least one special character.")

    def __str__(self) -> str:
        return "*****"
