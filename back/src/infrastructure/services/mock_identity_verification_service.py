import logging

from src.domain.repositories.user_repository import IUserRepository
from src.domain.services.identity_verification_service import IIdentityVerificationService
from src.domain.value_objects.verification_status import VerificationStatus

logger = logging.getLogger(__name__)


class MockIdentityVerificationService(IIdentityVerificationService):
    """Mock implementation simulating RENIEC and SUNARP identity/legal power verification."""

    def __init__(self, user_repository: IUserRepository) -> None:
        self._user_repository = user_repository

    def verify_legal_representative_and_company(
        self, user_id: int, dni: str, ruc: str
    ) -> VerificationStatus:
        """Simulates external RENIEC / SUNARP checks.

        Returns APPROVED for all valid formats in this academic project environment.
        """
        logger.info(
            "Executing simulated RENIEC & SUNARP legal verification for User ID %s, DNI %s, RUC %s",
            user_id,
            dni,
            ruc,
        )

        user = self._user_repository.find_by_id(user_id)
        if user:
            user.verification_status = VerificationStatus.APPROVED
            self._user_repository.save(user)
            logger.info("User ID %s verified and status updated to APPROVED", user_id)
            return VerificationStatus.APPROVED

        return VerificationStatus.PENDING_VERIFICATION
