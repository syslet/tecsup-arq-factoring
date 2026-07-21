from abc import ABC, abstractmethod

from src.domain.entities.invoice_sheet import InvoiceSheet


class IInvoiceSheetRepository(ABC):
    """Interface for invoice sheet persistence operations."""

    @abstractmethod
    def save(self, sheet: InvoiceSheet) -> InvoiceSheet:
        """Persists or updates an invoice sheet with its associated invoices."""
        pass

    @abstractmethod
    def find_by_id(self, sheet_id: int) -> InvoiceSheet | None:
        """Finds an invoice sheet by its ID."""
        pass

    @abstractmethod
    def find_by_company_id(self, company_id: int) -> list[InvoiceSheet]:
        """Finds all invoice sheets belonging to a specific company."""
        pass
