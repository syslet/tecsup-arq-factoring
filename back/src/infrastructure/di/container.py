from flask import g
from sqlalchemy.orm import Session

from src.application.use_cases.get_current_user import GetCurrentUserUseCase
from src.application.use_cases.login_user import LoginUserUseCase
from src.application.use_cases.logout_user import LogoutUserUseCase
from src.application.use_cases.register_user import RegisterUserUseCase
from src.infrastructure.db.repositories.session_repository_impl import SqlAlchemySessionRepository
from src.infrastructure.db.repositories.user_repository_impl import SqlAlchemyUserRepository
from src.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from src.infrastructure.services.jwt_token_service import PyJwtTokenService


class Container:
    """Dependency injection container for wiring repositories and use cases."""

    def __init__(self, db_session: Session) -> None:
        self.db = db_session
        self.user_repository = SqlAlchemyUserRepository(db_session)
        self.session_repository = SqlAlchemySessionRepository(db_session)
        self.password_hasher = BcryptPasswordHasher()
        self.token_service = PyJwtTokenService()

    @property
    def register_user_use_case(self) -> RegisterUserUseCase:
        return RegisterUserUseCase(
            user_repository=self.user_repository,
            password_hasher=self.password_hasher,
        )

    @property
    def login_user_use_case(self) -> LoginUserUseCase:
        return LoginUserUseCase(
            user_repository=self.user_repository,
            session_repository=self.session_repository,
            password_hasher=self.password_hasher,
            token_service=self.token_service,
        )

    @property
    def logout_user_use_case(self) -> LogoutUserUseCase:
        return LogoutUserUseCase(
            session_repository=self.session_repository,
        )

    @property
    def get_current_user_use_case(self) -> GetCurrentUserUseCase:
        return GetCurrentUserUseCase(
            token_service=self.token_service,
            user_repository=self.user_repository,
            session_repository=self.session_repository,
        )


def get_container() -> Container:
    """Retrieves the request-scoped Container instance from Flask g object.

    Raises:
        RuntimeError: If called outside request context or before Container init.
    """
    container: Container | None = getattr(g, "container", None)
    if container is None:
        raise RuntimeError("Container is not initialized in the request context.")
    return container
