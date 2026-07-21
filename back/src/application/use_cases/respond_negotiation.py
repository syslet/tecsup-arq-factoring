from src.domain.entities.invoice_sheet import InvoiceSheet
from src.domain.repositories.invoice_sheet_repository import IInvoiceSheetRepository
from src.domain.repositories.negotiation_repository import INegotiationRepository
from src.domain.services.pricing_engine import PricingEngine


class RespondNegotiationUseCase:
    """Use case for administrators or account executives to respond to rate negotiations."""

    def __init__(
        self,
        sheet_repository: IInvoiceSheetRepository,
        negotiation_repository: INegotiationRepository,
        pricing_engine: PricingEngine | None = None,
    ) -> None:
        self._sheet_repository = sheet_repository
        self._negotiation_repository = negotiation_repository
        self._pricing_engine = pricing_engine or PricingEngine()

    def execute(
        self,
        sheet_id: int,
        accepted: bool,
        counter_rate: float | None = None,
        notes: str | None = None,
    ) -> InvoiceSheet:
        sheet = self._sheet_repository.find_by_id(sheet_id)
        if not sheet:
            raise ValueError("Planilla no encontrada")

        history = self._negotiation_repository.find_by_sheet_id(sheet_id)
        latest_negotiation = history[0] if history else None

        if accepted:
            final_rate = counter_rate or (
                latest_negotiation.requested_rate if latest_negotiation else sheet.monthly_rate
            )
            quote = self._pricing_engine.calculate_quote(
                invoices=sheet.invoices,
                currency=sheet.currency,
                advance_rate=sheet.advance_rate,
                monthly_rate=final_rate,
            )
            sheet.monthly_rate = final_rate
            sheet.interest_fee = quote.interest_fee
            sheet.net_disbursement = quote.net_disbursement
            sheet.status = "APPROVED" if not counter_rate else "COUNTER_OFFERED"

            if latest_negotiation:
                latest_negotiation.status = "ACCEPTED" if not counter_rate else "COUNTER_OFFERED"
                latest_negotiation.offered_rate = final_rate
                self._negotiation_repository.save(latest_negotiation)
        else:
            sheet.status = "REJECTED"
            if latest_negotiation:
                latest_negotiation.status = "REJECTED"
                self._negotiation_repository.save(latest_negotiation)

        return self._sheet_repository.save(sheet)
