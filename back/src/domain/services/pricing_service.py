from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.domain.entities.invoice import Invoice
from src.domain.value_objects.currency import Currency


@dataclass
class PricingQuote:
    """Domain Value Object representing the output calculation of a factoring quote."""

    total_amount: float
    advance_amount: float
    interest_fee: float
    commission: float
    net_disbursement: float
    advance_rate: float
    monthly_rate: float
    approved_invoices_count: int
    rejected_invoices_count: int


class IPricingService(ABC):
    """Abstract Domain Service interface for calculating factoring rates and quotes."""

    @abstractmethod
    def calculate_quote(
        self,
        invoices: list[Invoice],
        currency: Currency,
        advance_rate: float = 0.85,
        monthly_rate: float = 0.02,
    ) -> PricingQuote:
        """Calculates total advance amount, interest fee, commission and net disbursement."""
        pass
