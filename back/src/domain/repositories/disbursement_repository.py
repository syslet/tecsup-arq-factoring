from abc import ABC, abstractmethod

from src.domain.entities.disbursement import Disbursement


class IDisbursementRepository(ABC):
    """Interface for disbursement persistence operations."""

    @abstractmethod
    def save(self, disbursement: Disbursement) -> Disbursement:
        """Persists a new disbursement record."""
        pass

    @abstractmethod
    def find_by_sheet_id(self, sheet_id: int) -> Disbursement | None:
        """Finds a disbursement by sheet ID."""
        pass

    @abstractmethod
    def find_by_id(self, disbursement_id: int) -> Disbursement | None:
        """Finds a disbursement by ID."""
        pass

    @abstractmethod
    def find_by_company_id(self, company_id: int) -> list[Disbursement]:
        """Finds all disbursements for a company."""
        pass
