from abc import ABC, abstractmethod

from src.domain.entities.session import UserSession


class ISessionRepository(ABC):
    """Abstract interface for Session persistence & caching operations.

    This interface abstracts session storage (DB, In-Memory, or future Redis).
    """

    @abstractmethod
    def save(self, session: UserSession) -> UserSession:
        """Saves a new user session."""
        pass

    @abstractmethod
    def find_by_jti(self, token_jti: str) -> UserSession | None:
        """Finds an active session by token identifier (JTI)."""
        pass

    @abstractmethod
    def revoke_by_jti(self, token_jti: str) -> bool:
        """Revokes a session by its token JTI."""
        pass

    @abstractmethod
    def revoke_all_user_sessions(self, user_id: int) -> int:
        """Revokes all active sessions for a given user."""
        pass
