from src.domain.entities.invoice_sheet import InvoiceSheet
from src.domain.entities.negotiation_history import NegotiationHistory
from src.domain.repositories.invoice_sheet_repository import IInvoiceSheetRepository
from src.domain.repositories.negotiation_repository import INegotiationRepository
from src.domain.services.pricing_service import IPricingService
from src.infrastructure.services.pricing_service_impl import StandardPricingService


class NegotiateQuoteUseCase:
    """Use case allowing clients to request rate adjustments on invoice sheets."""

    TOLERANCE_THRESHOLD = 0.015  # 1.5% executive tolerance

    def __init__(
        self,
        sheet_repository: IInvoiceSheetRepository,
        negotiation_repository: INegotiationRepository,
        pricing_service: IPricingService | None = None,
    ) -> None:
        self._sheet_repository = sheet_repository
        self._negotiation_repository = negotiation_repository
        self._pricing_service = pricing_service or StandardPricingService()

    def execute(
        self,
        sheet_id: int,
        user_id: int,
        requested_rate: float,
        notes: str | None = None,
    ) -> tuple[NegotiationHistory, InvoiceSheet]:
        sheet = self._sheet_repository.find_by_id(sheet_id)
        if not sheet:
            raise ValueError("Planilla no encontrada")

        if sheet.status not in ("QUOTED", "COUNTER_OFFERED"):
            raise ValueError(f"No se puede negociar una planilla en estado '{sheet.status}'")

        rate_diff = abs(requested_rate - sheet.monthly_rate)

        if rate_diff <= self.TOLERANCE_THRESHOLD:
            # Auto-approved counter offer under tolerance threshold
            quote = self._pricing_service.calculate_quote(
                invoices=sheet.invoices,
                currency=sheet.currency,
                advance_rate=sheet.advance_rate,
                monthly_rate=requested_rate,
            )
            sheet.monthly_rate = requested_rate
            sheet.interest_fee = quote.interest_fee
            sheet.net_disbursement = quote.net_disbursement
            sheet.status = "COUNTER_OFFERED"
            negotiation_status = "ACCEPTED"
        else:
            # Requires admin approval
            sheet.status = "NEGOTIATION_REQUESTED"
            negotiation_status = "PENDING"

        updated_sheet = self._sheet_repository.save(sheet)

        negotiation = NegotiationHistory(
            id=None,
            sheet_id=sheet_id,
            requested_rate=requested_rate,
            offered_rate=sheet.monthly_rate,
            requested_by_user_id=user_id,
            status=negotiation_status,
            notes=notes,
        )
        saved_negotiation = self._negotiation_repository.save(negotiation)

        return saved_negotiation, updated_sheet
