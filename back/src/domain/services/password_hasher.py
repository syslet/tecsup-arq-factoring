from abc import ABC, abstractmethod


class IPasswordHasher(ABC):
    """Abstract interface for password hashing and verification."""

    @abstractmethod
    def hash(self, plain_password: str) -> str:
        """Hashes a plain text password."""
        pass

    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verifies a plain text password against a hash."""
        pass
