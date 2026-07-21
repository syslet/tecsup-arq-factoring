class MockSunatClient:
    """Mock SUNAT client service to validate invoice status."""

    def validate_invoice_status(self, invoice_number: str) -> tuple[str, bool, str | None]:
        """Returns (sunat_status, is_valid, rejection_reason).

        Invoices starting with 'F999' are mocked as invalid/anulada by SUNAT.
        """
        if invoice_number.startswith("F999"):
            return "ANULADO", False, "Comprobante rechazado o anulado en consulta RUC SUNAT"
        return "VALID", True, None
