from dataclasses import dataclass
from datetime import UTC, datetime

from src.domain.value_objects.dni import Dni
from src.domain.value_objects.user_role import UserRole
from src.domain.value_objects.verification_status import VerificationStatus


@dataclass
class User:
    """Domain entity representing a user (legal representative) in the system."""

    id: int | None
    email: str
    password_hash: str
    full_name: str
    role: UserRole
    dni: Dni
    phone: str | None = None
    verification_status: VerificationStatus = VerificationStatus.PENDING_VERIFICATION
    is_active: bool = True
    failed_login_attempts: int = 0
    is_locked: bool = False
    locked_until: datetime | None = None
    last_login_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if isinstance(self.dni, str):
            object.__setattr__(self, "dni", Dni(self.dni))
        if isinstance(self.role, str):
            object.__setattr__(self, "role", UserRole(self.role))
        if isinstance(self.verification_status, str):
            object.__setattr__(
                self, "verification_status", VerificationStatus(self.verification_status)
            )

    def increment_failed_attempts(self, max_allowed: int = 5) -> None:
        """Increments failed login counter and locks account if threshold reached."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= max_allowed:
            self.is_locked = True

    def reset_failed_attempts(self) -> None:
        """Resets failed login attempt counter and sets last login timestamp."""
        self.failed_login_attempts = 0
        self.last_login_at = datetime.now(UTC)

    def can_operate(self) -> bool:
        """Returns True if the user account is approved to perform financial operations."""
        return (
            self.is_active
            and not self.is_locked
            and self.verification_status == VerificationStatus.APPROVED
        )
