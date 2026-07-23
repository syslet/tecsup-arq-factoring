from src.domain.entities.invoice import Invoice
from src.domain.services.pricing_service import IPricingService, PricingQuote
from src.domain.value_objects.currency import Currency


class StandardPricingService(IPricingService):
    """Infrastructure implementation of factoring pricing calculation engine."""

    DEFAULT_ADVANCE_RATE = 0.85  # 85% advance rate
    DEFAULT_MONTHLY_RATE = 0.02  # 2% TEM (Tasa Efectiva Mensual)
    FIXED_COMMISSION_PEN = 50.00
    FIXED_COMMISSION_USD = 15.00

    def calculate_quote(
        self,
        invoices: list[Invoice],
        currency: Currency,
        advance_rate: float = DEFAULT_ADVANCE_RATE,
        monthly_rate: float = DEFAULT_MONTHLY_RATE,
    ) -> PricingQuote:
        approved_invoices = [inv for inv in invoices if inv.is_approved]
        rejected_count = len(invoices) - len(approved_invoices)

        if not approved_invoices:
            return PricingQuote(
                total_amount=0.0,
                advance_amount=0.0,
                interest_fee=0.0,
                commission=0.0,
                net_disbursement=0.0,
                advance_rate=advance_rate,
                monthly_rate=monthly_rate,
                approved_invoices_count=0,
                rejected_invoices_count=rejected_count,
            )

        total_amount = sum(inv.amount for inv in approved_invoices)
        advance_amount = round(total_amount * advance_rate, 2)

        total_interest = 0.0
        daily_rate = monthly_rate / 30.0

        for inv in approved_invoices:
            inv_advance = inv.amount * advance_rate
            inv_interest = inv_advance * daily_rate * max(inv.days_to_maturity, 1)
            total_interest += inv_interest

        interest_fee = round(total_interest, 2)
        commission = (
            self.FIXED_COMMISSION_PEN if currency == Currency.PEN else self.FIXED_COMMISSION_USD
        )

        net_disbursement = round(advance_amount - interest_fee - commission, 2)

        return PricingQuote(
            total_amount=round(total_amount, 2),
            advance_amount=advance_amount,
            interest_fee=interest_fee,
            commission=commission,
            net_disbursement=max(net_disbursement, 0.0),
            advance_rate=advance_rate,
            monthly_rate=monthly_rate,
            approved_invoices_count=len(approved_invoices),
            rejected_invoices_count=rejected_count,
        )
