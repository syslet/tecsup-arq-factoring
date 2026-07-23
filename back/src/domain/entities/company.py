from dataclasses import dataclass
from datetime import datetime

from src.domain.value_objects.cci_account import CciAccount
from src.domain.value_objects.currency import Currency
from src.domain.value_objects.ruc import Ruc


@dataclass
class Company:
    """Domain entity representing a corporate client (Empresa/Girador)."""

    id: int | None
    ruc: Ruc
    business_name: str
    legal_representative_user_id: int
    bank_name: str
    bank_account_number: str
    cci: CciAccount
    currency: Currency = Currency.PEN
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if isinstance(self.ruc, str):
            object.__setattr__(self, "ruc", Ruc(self.ruc))
        if isinstance(self.cci, str):
            object.__setattr__(self, "cci", CciAccount(self.cci))
        if isinstance(self.currency, str):
            object.__setattr__(self, "currency", Currency(self.currency))
