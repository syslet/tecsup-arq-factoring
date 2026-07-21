from abc import ABC, abstractmethod
from typing import Any


class ITokenService(ABC):
    """Abstract interface for JWT token generation and verification."""

    @abstractmethod
    def create_access_token(self, user_id: int, email: str, role: str, jti: str) -> str:
        """Generates a JWT access token."""
        pass

    @abstractmethod
    def decode_token(self, token: str) -> dict[str, Any]:
        """Decodes and validates a JWT token."""
        pass
