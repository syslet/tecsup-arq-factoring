from dataclasses import dataclass
from datetime import datetime

from src.domain.value_objects.cci_account import CciAccount
from src.domain.value_objects.currency import Currency


@dataclass
class Disbursement:
    """Domain entity representing a bank disbursement and digital account annotation."""

    id: int | None
    sheet_id: int
    annotation_code: str
    amount: float
    currency: Currency
    bank_name: str
    bank_account_number: str
    cci: CciAccount
    status: str = "DISBURSED"
    executed_at: datetime | None = None

    def __post_init__(self) -> None:
        if isinstance(self.cci, str):
            object.__setattr__(self, "cci", CciAccount(self.cci))
        if isinstance(self.currency, str):
            object.__setattr__(self, "currency", Currency(self.currency))
