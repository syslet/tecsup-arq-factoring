from src.domain.repositories.session_repository import ISessionRepository


class LogoutUserUseCase:
    """Use case for ending a user session and invalidating token."""

    def __init__(self, session_repository: ISessionRepository) -> None:
        self._session_repository = session_repository

    def execute(self, token_jti: str) -> bool:
        """Revokes session associated with token JTI.

        Args:
            token_jti: Unique JWT identifier.

        Returns:
            True if session was revoked.
        """
        return self._session_repository.revoke_by_jti(token_jti)
