import logging

from src.domain.services.identity_verification_service import IIdentityVerificationService
from src.domain.value_objects.verification_status import VerificationStatus

logger = logging.getLogger(__name__)


class MockIdentityVerificationService(IIdentityVerificationService):
    """Mock implementation simulating RENIEC and SUNARP identity/legal power verification."""

    def verify_legal_representative_and_company(
        self, user_id: int, dni: str, ruc: str
    ) -> VerificationStatus:
        """Simulates external RENIEC / SUNARP checks.

        Never auto-approves: a passing check leaves the caller to keep the user
        PENDING_VERIFICATION for manual admin review. Raises to signal failure.
        """
        logger.info(
            "Executing simulated RENIEC & SUNARP legal verification for User ID %s, DNI %s, RUC %s",
            user_id,
            dni,
            ruc,
        )
        return VerificationStatus.PENDING_VERIFICATION
