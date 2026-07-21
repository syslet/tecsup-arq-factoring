from dataclasses import dataclass
from datetime import datetime


@dataclass
class CompanyDocument:
    """Domain entity representing uploaded verification documents for a company."""

    id: int | None
    company_id: int
    document_type: str
    file_name: str
    file_path: str
    uploaded_at: datetime | None = None
