import logging

from src.domain.entities.user import User
from src.domain.repositories.user_repository import IUserRepository
from src.domain.services.password_hasher import IPasswordHasher
from src.domain.value_objects.user_role import UserRole
from src.domain.value_objects.verification_status import VerificationStatus

logger = logging.getLogger(__name__)


class SeedAdminUserUseCase:
    """Use case to ensure default admin user exists on application startup."""

    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher: IPasswordHasher,
        admin_email: str = "admin@factoring.com",
        admin_password: str = "Admin123!",
        admin_name: str = "System Administrator",
        admin_dni: str = "00000000",
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._admin_email = admin_email
        self._admin_password = admin_password
        self._admin_name = admin_name
        self._admin_dni = admin_dni

    def execute(self) -> User:
        """Checks for existing admin user and creates one if missing."""
        existing_admin = self._user_repository.find_by_email(self._admin_email)
        if existing_admin:
            logger.info("Default admin user already exists: %s", self._admin_email)
            return existing_admin

        hashed_password = self._password_hasher.hash(self._admin_password)
        admin_user = User(
            id=None,
            email=self._admin_email.lower().strip(),
            password_hash=hashed_password,
            full_name=self._admin_name,
            dni=self._admin_dni,
            role=UserRole.ADMINISTRADOR,
            verification_status=VerificationStatus.APPROVED,
            is_active=True,
        )

        saved_user = self._user_repository.save(admin_user)
        logger.info("Created default admin user: %s", self._admin_email)
        return saved_user
