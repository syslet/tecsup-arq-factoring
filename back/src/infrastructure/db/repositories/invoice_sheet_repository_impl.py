from sqlalchemy.orm import Session

from src.domain.entities.invoice import Invoice
from src.domain.entities.invoice_sheet import InvoiceSheet
from src.domain.repositories.invoice_sheet_repository import IInvoiceSheetRepository
from src.domain.value_objects.currency import Currency
from src.domain.value_objects.ruc import Ruc
from src.infrastructure.db.models import InvoiceModel, InvoiceSheetModel


class SqlAlchemyInvoiceSheetRepository(IInvoiceSheetRepository):
    """SQLAlchemy implementation of IInvoiceSheetRepository."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, sheet: InvoiceSheet) -> InvoiceSheet:
        if sheet.id is not None:
            sheet_model = self._db.query(InvoiceSheetModel).filter_by(id=sheet.id).first()
            if sheet_model:
                sheet_model.status = sheet.status
                sheet_model.total_amount = sheet.total_amount
                sheet_model.advance_amount = sheet.advance_amount
                sheet_model.interest_fee = sheet.interest_fee
                sheet_model.commission = sheet.commission
                sheet_model.net_disbursement = sheet.net_disbursement
                sheet_model.advance_rate = sheet.advance_rate
                sheet_model.monthly_rate = sheet.monthly_rate
                self._db.commit()
                self._db.refresh(sheet_model)
                return self._to_entity(sheet_model)

        sheet_curr = sheet.currency.value
        sheet_model = InvoiceSheetModel(
            company_id=sheet.company_id,
            sheet_code=sheet.sheet_code,
            currency=sheet_curr,
            total_amount=sheet.total_amount,
            advance_amount=sheet.advance_amount,
            interest_fee=sheet.interest_fee,
            commission=sheet.commission,
            net_disbursement=sheet.net_disbursement,
            advance_rate=sheet.advance_rate,
            monthly_rate=sheet.monthly_rate,
            status=sheet.status,
        )
        self._db.add(sheet_model)
        self._db.flush()

        for inv in sheet.invoices:
            drawer_str = inv.drawer_ruc.value
            debtor_str = inv.debtor_ruc.value
            inv_curr = inv.currency.value
            inv_model = InvoiceModel(
                sheet_id=sheet_model.id,
                invoice_number=inv.invoice_number,
                drawer_ruc=drawer_str,
                debtor_ruc=debtor_str,
                debtor_name=inv.debtor_name,
                amount=inv.amount,
                currency=inv_curr,
                issue_date=inv.issue_date,
                due_date=inv.due_date,
                days_to_maturity=inv.days_to_maturity,
                sunat_status=inv.sunat_status,
                is_approved=inv.is_approved,
                rejection_reason=inv.rejection_reason,
            )
            self._db.add(inv_model)

        self._db.commit()
        self._db.refresh(sheet_model)
        return self._to_entity(sheet_model)

    def find_by_id(self, sheet_id: int) -> InvoiceSheet | None:
        model = self._db.query(InvoiceSheetModel).filter_by(id=sheet_id).first()
        return self._to_entity(model) if model else None

    def find_by_company_id(self, company_id: int) -> list[InvoiceSheet]:
        models = (
            self._db.query(InvoiceSheetModel)
            .filter_by(company_id=company_id)
            .order_by(InvoiceSheetModel.created_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_all(self) -> list[InvoiceSheet]:
        models = (
            self._db.query(InvoiceSheetModel).order_by(InvoiceSheetModel.created_at.desc()).all()
        )
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: InvoiceSheetModel) -> InvoiceSheet:
        invoices = [
            Invoice(
                id=inv.id,
                sheet_id=inv.sheet_id,
                invoice_number=inv.invoice_number,
                drawer_ruc=Ruc(inv.drawer_ruc),
                debtor_ruc=Ruc(inv.debtor_ruc),
                debtor_name=inv.debtor_name,
                amount=inv.amount,
                currency=Currency(inv.currency),
                issue_date=inv.issue_date,
                due_date=inv.due_date,
                days_to_maturity=inv.days_to_maturity,
                sunat_status=inv.sunat_status,
                is_approved=inv.is_approved,
                rejection_reason=inv.rejection_reason,
            )
            for inv in model.invoices
        ]
        return InvoiceSheet(
            id=model.id,
            company_id=model.company_id,
            sheet_code=model.sheet_code,
            currency=Currency(model.currency),
            total_amount=model.total_amount,
            advance_amount=model.advance_amount,
            interest_fee=model.interest_fee,
            commission=model.commission,
            net_disbursement=model.net_disbursement,
            advance_rate=model.advance_rate,
            monthly_rate=model.monthly_rate,
            status=model.status,
            invoices=invoices,
            created_at=model.created_at,
        )
