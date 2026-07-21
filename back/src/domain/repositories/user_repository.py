from abc import ABC, abstractmethod

from src.domain.entities.user import User


class IUserRepository(ABC):
    """Abstract interface for User persistence operations."""

    @abstractmethod
    def save(self, user: User) -> User:
        """Saves or updates a user entity in the database."""
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> User | None:
        """Retrieves a user entity by its primary key ID."""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> User | None:
        """Retrieves a user entity by email address."""
        pass

    @abstractmethod
    def find_by_dni(self, dni: str) -> User | None:
        """Retrieves a user entity by DNI."""
        pass

    @abstractmethod
    def find_by_identifier(self, identifier: str) -> User | None:
        """Retrieves a user entity by email address or DNI."""
        pass
