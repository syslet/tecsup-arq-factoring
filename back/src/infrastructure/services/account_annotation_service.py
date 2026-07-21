import uuid


class AccountAnnotationService:
    """Mock integration with CAVALI / RADIAN / SUNAT for digital invoice account annotation (Anotación en Cuenta)."""

    def register_account_annotation(self, sheet_code: str, invoices_count: int) -> str:
        """Generates a unique CAVALI / SUNAT account annotation transaction ID."""
        token = str(uuid.uuid4()).split("-")[0].upper()
        return f"CAVALI-{token}"
