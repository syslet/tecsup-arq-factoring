import uuid
from dataclasses import dataclass
from datetime import date

from src.domain.entities.group_economic import GroupEconomicRule
from src.domain.entities.invoice import Invoice
from src.domain.entities.invoice_sheet import InvoiceSheet
from src.domain.repositories.invoice_sheet_repository import IInvoiceSheetRepository
from src.domain.services.pricing_engine import PricingEngine
from src.domain.value_objects.currency import Currency
from src.infrastructure.services.mock_sunat_client import MockSunatClient


@dataclass
class InvoiceItemInput:
    invoice_number: str
    debtor_ruc: str
    debtor_name: str
    amount: float
    issue_date: date
    due_date: date


@dataclass
class ProcessSheetCommand:
    company_id: int
    drawer_ruc: str
    currency: str
    invoices: list[InvoiceItemInput]


class ProcessInvoiceSheetUseCase:
    """Use case for validating invoice batch payloads and executing pricing simulation."""

    def __init__(
        self,
        sheet_repository: IInvoiceSheetRepository,
        sunat_client: MockSunatClient | None = None,
        pricing_engine: PricingEngine | None = None,
    ) -> None:
        self._sheet_repository = sheet_repository
        self._sunat_client = sunat_client or MockSunatClient()
        self._pricing_engine = pricing_engine or PricingEngine()

    def execute(self, command: ProcessSheetCommand) -> InvoiceSheet:
        # Rule 1: 1 to 90 invoices
        num_invoices = len(command.invoices)
        if num_invoices < 1 or num_invoices > 90:
            raise ValueError(
                f"La planilla debe contener entre 1 y 90 facturas. Recibidas: {num_invoices}"
            )

        currency_enum = Currency(command.currency)
        today = date.today()
        invoice_entities: list[Invoice] = []

        for inv_input in command.invoices:
            days_to_maturity = (inv_input.due_date - today).days
            if days_to_maturity <= 0:
                days_to_maturity = (inv_input.due_date - inv_input.issue_date).days

            # Rule 2: Expiration <= 180 days
            if days_to_maturity > 180:
                raise ValueError(
                    f"Factura {inv_input.invoice_number} excede el plazo máximo de 180 días ({days_to_maturity} días)."
                )

            is_approved = True
            rejection_reason = None

            # Rule 3: SUNAT Mock Verification
            sunat_status, is_valid_sunat, sunat_err = self._sunat_client.validate_invoice_status(
                inv_input.invoice_number
            )
            if not is_valid_sunat:
                is_approved = False
                rejection_reason = sunat_err or "Comprobante no válido en SUNAT"

            # Rule 4: Economic Group Anti-fraud (Girador != Aceptante en mismo Grupo Económico)
            if is_approved and GroupEconomicRule.is_same_economic_group(
                command.drawer_ruc, inv_input.debtor_ruc
            ):
                is_approved = False
                rejection_reason = (
                    "Autofacturación o autofinanciamiento detectado: "
                    "Girador y Aceptante pertenecen al mismo Grupo Económico."
                )

            invoice_entities.append(
                Invoice(
                    id=None,
                    sheet_id=None,
                    invoice_number=inv_input.invoice_number,
                    drawer_ruc=command.drawer_ruc,
                    debtor_ruc=inv_input.debtor_ruc,
                    debtor_name=inv_input.debtor_name,
                    amount=inv_input.amount,
                    currency=currency_enum,
                    issue_date=inv_input.issue_date,
                    due_date=inv_input.due_date,
                    days_to_maturity=max(days_to_maturity, 1),
                    sunat_status=sunat_status,
                    is_approved=is_approved,
                    rejection_reason=rejection_reason,
                )
            )

        # Rule 5: Pricing calculation
        quote = self._pricing_engine.calculate_quote(invoice_entities, currency=currency_enum)

        sheet_code = f"PLN-{today.year}-{str(uuid.uuid4())[:8].upper()}"
        sheet_entity = InvoiceSheet(
            id=None,
            company_id=command.company_id,
            sheet_code=sheet_code,
            currency=currency_enum,
            total_amount=quote.total_amount,
            advance_amount=quote.advance_amount,
            interest_fee=quote.interest_fee,
            commission=quote.commission,
            net_disbursement=quote.net_disbursement,
            advance_rate=quote.advance_rate,
            monthly_rate=quote.monthly_rate,
            status="QUOTED",
            invoices=invoice_entities,
        )

        return self._sheet_repository.save(sheet_entity)
