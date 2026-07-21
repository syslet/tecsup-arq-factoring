from dataclasses import dataclass
from datetime import date

from src.domain.value_objects.currency import Currency


@dataclass
class Invoice:
    """Domain entity representing a single factoring invoice (Comprobante de Pago)."""

    id: int | None
    sheet_id: int | None
    invoice_number: str
    drawer_ruc: str
    debtor_ruc: str
    debtor_name: str
    amount: float
    currency: Currency
    issue_date: date
    due_date: date
    days_to_maturity: int
    sunat_status: str = "VALID"
    is_approved: bool = True
    rejection_reason: str | None = None
