from abc import ABC, abstractmethod

from src.domain.entities.company_document import CompanyDocument


class ICompanyDocumentRepository(ABC):
    """Interface for company document persistence operations."""

    @abstractmethod
    def save(self, document: CompanyDocument) -> CompanyDocument:
        """Persists a new company document."""
        pass

    @abstractmethod
    def find_by_company_id(self, company_id: int) -> list[CompanyDocument]:
        """Retrieves all documents for a specific company."""
        pass
