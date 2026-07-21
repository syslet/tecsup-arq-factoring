from dataclasses import dataclass
from datetime import datetime

from src.domain.value_objects.currency import Currency


@dataclass
class Company:
    """Domain entity representing a corporate client (Empresa/Girador)."""

    id: int | None
    ruc: str
    business_name: str
    legal_representative_user_id: int
    bank_name: str
    bank_account_number: str
    cci: str
    currency: Currency = Currency.PEN
    created_at: datetime | None = None
    updated_at: datetime | None = None
