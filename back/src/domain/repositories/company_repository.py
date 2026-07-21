from abc import ABC, abstractmethod

from src.domain.entities.company import Company


class ICompanyRepository(ABC):
    """Abstract interface for Company persistence operations."""

    @abstractmethod
    def save(self, company: Company) -> Company:
        """Saves or updates a company entity in the database."""
        pass

    @abstractmethod
    def find_by_id(self, company_id: int) -> Company | None:
        """Retrieves a company entity by its ID."""
        pass

    @abstractmethod
    def find_by_ruc(self, ruc: str) -> Company | None:
        """Retrieves a company entity by RUC."""
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: int) -> Company | None:
        """Retrieves the company associated with a legal representative user ID."""
        pass
