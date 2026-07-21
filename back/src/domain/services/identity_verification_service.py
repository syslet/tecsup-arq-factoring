from abc import ABC, abstractmethod

from src.domain.value_objects.verification_status import VerificationStatus


class IIdentityVerificationService(ABC):
    """Domain service interface for asynchronous identity and legal power verification (RENIEC / SUNARP)."""

    @abstractmethod
    def verify_legal_representative_and_company(
        self, user_id: int, dni: str, ruc: str
    ) -> VerificationStatus:
        """Performs mock verification against RENIEC and SUNARP registries."""
        pass
