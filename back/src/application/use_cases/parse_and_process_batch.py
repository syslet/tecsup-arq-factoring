import csv
import io
import json
from datetime import datetime

from src.application.use_cases.process_invoice_sheet import (
    InvoiceItemInput,
    ProcessInvoiceSheetUseCase,
    ProcessSheetCommand,
)
from src.domain.entities.invoice_sheet import InvoiceSheet
from src.domain.repositories.storage_repository import IStorageService


class ParseAndProcessBatchUseCase:
    """Use case to parse uploaded CSV or JSON invoice files and delegate to ProcessInvoiceSheetUseCase."""

    def __init__(
        self,
        process_sheet_use_case: ProcessInvoiceSheetUseCase,
        storage_service: IStorageService,
    ) -> None:
        self._process_sheet_use_case = process_sheet_use_case
        self._storage_service = storage_service

    def execute(
        self,
        file_bytes: bytes,
        filename: str,
        company_id: int,
        drawer_ruc: str,
        currency: str = "PEN",
    ) -> InvoiceSheet:
        # Save file to storage volume first
        stored_name = self._storage_service.save_file(
            file_bytes=file_bytes, filename=filename, subfolder="invoices"
        )

        invoices_input: list[InvoiceItemInput] = []

        if filename.lower().endswith(".json"):
            invoices_input = self._parse_json(file_bytes)
        elif filename.lower().endswith(".csv"):
            invoices_input = self._parse_csv(file_bytes)
        else:
            raise ValueError("Unsupported file format. Only CSV and JSON files are allowed.")

        command = ProcessSheetCommand(
            company_id=company_id,
            drawer_ruc=drawer_ruc,
            currency=currency,
            invoices=invoices_input,
        )

        return self._process_sheet_use_case.execute(command)

    def _parse_json(self, file_bytes: bytes) -> list[InvoiceItemInput]:
        data = json.loads(file_bytes.decode("utf-8"))
        items = data if isinstance(data, list) else data.get("invoices", [])

        result: list[InvoiceItemInput] = []
        for item in items:
            issue_d = datetime.strptime(item["issue_date"], "%Y-%m-%d").date()
            due_d = datetime.strptime(item["due_date"], "%Y-%m-%d").date()
            result.append(
                InvoiceItemInput(
                    invoice_number=str(item["invoice_number"]),
                    debtor_ruc=str(item["debtor_ruc"]),
                    debtor_name=str(item.get("debtor_name", "Empresa Deudora")),
                    amount=float(item["amount"]),
                    issue_date=issue_d,
                    due_date=due_d,
                )
            )
        return result

    def _parse_csv(self, file_bytes: bytes) -> list[InvoiceItemInput]:
        content = file_bytes.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(content))

        result: list[InvoiceItemInput] = []
        for row in reader:
            issue_d = datetime.strptime(row["issue_date"].strip(), "%Y-%m-%d").date()
            due_d = datetime.strptime(row["due_date"].strip(), "%Y-%m-%d").date()
            result.append(
                InvoiceItemInput(
                    invoice_number=row["invoice_number"].strip(),
                    debtor_ruc=row["debtor_ruc"].strip(),
                    debtor_name=row.get("debtor_name", "Empresa Deudora").strip(),
                    amount=float(row["amount"].strip()),
                    issue_date=issue_d,
                    due_date=due_d,
                )
            )
        return result
