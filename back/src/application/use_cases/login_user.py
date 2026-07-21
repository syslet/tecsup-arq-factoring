import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from src.domain.entities.session import UserSession
from src.domain.entities.user import User
from src.domain.exceptions.auth_exceptions import (
    AccountLockedException,
    InactiveUserException,
    InvalidCredentialsException,
)
from src.domain.repositories.session_repository import ISessionRepository
from src.domain.repositories.user_repository import IUserRepository
from src.domain.services.password_hasher import IPasswordHasher
from src.domain.services.token_service import ITokenService


@dataclass
class LoginCommand:
    """Input payload for user login using Email or DNI."""

    identifier: str
    password: str
    ip_address: str | None = None
    user_agent: str | None = None


class LoginUserUseCase:
    """Use case for user authentication, lockout management and session creation."""

    def __init__(
        self,
        user_repository: IUserRepository,
        session_repository: ISessionRepository,
        password_hasher: IPasswordHasher,
        token_service: ITokenService,
        session_ttl_hours: int = 24,
        max_failed_attempts: int = 5,
    ) -> None:
        self._user_repository = user_repository
        self._session_repository = session_repository
        self._password_hasher = password_hasher
        self._token_service = token_service
        self._session_ttl_hours = session_ttl_hours
        self._max_failed_attempts = max_failed_attempts

    def execute(self, command: LoginCommand) -> tuple[User, str, UserSession]:
        """Executes authentication workflow with security checks.

        Args:
            command: The login parameters (Email or DNI + password).

        Returns:
            Tuple containing User entity, JWT token string, and UserSession entity.

        Raises:
            InvalidCredentialsException: If user not found or password incorrect.
            InactiveUserException: If user account is disabled.
            AccountLockedException: If account is locked due to too many failed attempts.
        """
        user = self._user_repository.find_by_identifier(command.identifier)
        if not user or not user.password_hash:
            raise InvalidCredentialsException()

        if user.is_locked:
            raise AccountLockedException()

        if not user.is_active:
            raise InactiveUserException()

        if not self._password_hasher.verify(command.password, user.password_hash):
            user.increment_failed_attempts(max_allowed=self._max_failed_attempts)
            self._user_repository.save(user)
            if user.is_locked:
                raise AccountLockedException(
                    "Account locked due to 5 consecutive failed login attempts."
                )
            raise InvalidCredentialsException()

        # Reset failed login attempt counter and save timestamp
        user.reset_failed_attempts()
        saved_user = self._user_repository.save(user)

        assert saved_user.id is not None
        jti = str(uuid.uuid4())
        access_token = self._token_service.create_access_token(
            user_id=saved_user.id,
            email=saved_user.email,
            role=saved_user.role.value,
            jti=jti,
        )

        now = datetime.now(UTC)
        expires_at = now + timedelta(hours=self._session_ttl_hours)

        session = UserSession(
            id=None,
            user_id=saved_user.id,
            token_jti=jti,
            ip_address=command.ip_address,
            user_agent=command.user_agent,
            is_revoked=False,
            created_at=now,
            expires_at=expires_at,
        )
        saved_session = self._session_repository.save(session)

        return saved_user, access_token, saved_session
