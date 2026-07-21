from src.domain.entities.user import User
from src.domain.exceptions.auth_exceptions import (
    InactiveUserException,
    InvalidTokenException,
    UnauthorizedException,
)
from src.domain.repositories.session_repository import ISessionRepository
from src.domain.repositories.user_repository import IUserRepository
from src.domain.services.token_service import ITokenService


class GetCurrentUserUseCase:
    """Use case for validating JWT token and retrieving active user."""

    def __init__(
        self,
        token_service: ITokenService,
        user_repository: IUserRepository,
        session_repository: ISessionRepository,
    ) -> None:
        self._token_service = token_service
        self._user_repository = user_repository
        self._session_repository = session_repository

    def execute(self, token: str) -> User:
        """Decodes JWT, validates session status, and retrieves User entity.

        Args:
            token: Access token string.

        Returns:
            The authenticated User entity.

        Raises:
            InvalidTokenException: If token is invalid or expired.
            UnauthorizedException: If session is revoked or user not found.
            InactiveUserException: If user account is disabled.
        """
        payload = self._token_service.decode_token(token)
        jti = payload.get("jti")
        user_id = payload.get("sub")

        if not jti or not user_id:
            raise InvalidTokenException("Invalid token payload structure.")

        # Check session validity
        session = self._session_repository.find_by_jti(jti)
        if not session or not session.is_valid():
            raise UnauthorizedException("Session has expired or was revoked.")

        user = self._user_repository.find_by_id(int(user_id))
        if not user:
            raise UnauthorizedException("User not found.")

        if not user.is_active:
            raise InactiveUserException()

        return user
