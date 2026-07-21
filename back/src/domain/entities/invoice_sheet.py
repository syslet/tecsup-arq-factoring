from dataclasses import dataclass, field
from datetime import datetime

from src.domain.entities.invoice import Invoice
from src.domain.value_objects.currency import Currency


@dataclass
class InvoiceSheet:
    """Domain entity representing a factoring batch payload (Planilla de Facturas)."""

    id: int | None
    company_id: int
    sheet_code: str
    currency: Currency
    total_amount: float
    advance_amount: float
    interest_fee: float
    commission: float
    net_disbursement: float
    advance_rate: float = 0.85
    monthly_rate: float = 0.02
    status: str = "QUOTED"
    invoices: list[Invoice] = field(default_factory=list)
    created_at: datetime | None = None
