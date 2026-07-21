from dataclasses import dataclass
from datetime import datetime

from src.domain.value_objects.currency import Currency


@dataclass
class Disbursement:
    """Domain entity representing a bank disbursement and CAVALI/SUNAT account annotation."""

    id: int | None
    sheet_id: int
    annotation_code: str
    amount: float
    currency: Currency
    bank_name: str
    bank_account_number: str
    cci: str
    status: str = "DISBURSED"
    executed_at: datetime | None = None
