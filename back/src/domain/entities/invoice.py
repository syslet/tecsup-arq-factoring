from dataclasses import dataclass
from datetime import date

from src.domain.value_objects.currency import Currency
from src.domain.value_objects.ruc import Ruc


@dataclass
class Invoice:
    """Domain entity representing a single factoring invoice (Comprobante de Pago)."""

    id: int | None
    sheet_id: int | None
    invoice_number: str
    drawer_ruc: Ruc
    debtor_ruc: Ruc
    debtor_name: str
    amount: float
    currency: Currency
    issue_date: date
    due_date: date
    days_to_maturity: int
    sunat_status: str = "VALID"
    is_approved: bool = True
    rejection_reason: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.drawer_ruc, str):
            object.__setattr__(self, "drawer_ruc", Ruc(self.drawer_ruc))
        if isinstance(self.debtor_ruc, str):
            object.__setattr__(self, "debtor_ruc", Ruc(self.debtor_ruc))
        if isinstance(self.currency, str):
            object.__setattr__(self, "currency", Currency(self.currency))
