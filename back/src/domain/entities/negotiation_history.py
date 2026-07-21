from dataclasses import dataclass
from datetime import datetime


@dataclass
class NegotiationHistory:
    """Domain entity representing a rate negotiation attempt for an invoice sheet."""

    id: int | None
    sheet_id: int
    requested_rate: float
    offered_rate: float
    requested_by_user_id: int
    status: str  # PENDING, APPROVED, COUNTER_OFFERED, REJECTED
    notes: str | None = None
    created_at: datetime | None = None
