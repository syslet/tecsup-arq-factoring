from sqlalchemy.orm import Session

from src.domain.entities.disbursement import Disbursement
from src.domain.repositories.disbursement_repository import IDisbursementRepository
from src.domain.value_objects.currency import Currency
from src.infrastructure.db.models import DisbursementModel


class SqlAlchemyDisbursementRepository(IDisbursementRepository):
    """SQLAlchemy implementation of IDisbursementRepository."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, disbursement: Disbursement) -> Disbursement:
        model = DisbursementModel(
            sheet_id=disbursement.sheet_id,
            annotation_code=disbursement.annotation_code,
            amount=disbursement.amount,
            currency=disbursement.currency.value,
            bank_name=disbursement.bank_name,
            bank_account_number=disbursement.bank_account_number,
            cci=disbursement.cci,
            status=disbursement.status,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def find_by_sheet_id(self, sheet_id: int) -> Disbursement | None:
        model = self._db.query(DisbursementModel).filter_by(sheet_id=sheet_id).first()
        return self._to_entity(model) if model else None

    def find_by_id(self, disbursement_id: int) -> Disbursement | None:
        model = self._db.query(DisbursementModel).filter_by(id=disbursement_id).first()
        return self._to_entity(model) if model else None

    def find_by_company_id(self, company_id: int) -> list[Disbursement]:
        from src.infrastructure.db.models import InvoiceSheetModel
        models = (
            self._db.query(DisbursementModel)
            .join(InvoiceSheetModel, DisbursementModel.sheet_id == InvoiceSheetModel.id)
            .filter(InvoiceSheetModel.company_id == company_id)
            .order_by(DisbursementModel.executed_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: DisbursementModel) -> Disbursement:
        return Disbursement(
            id=model.id,
            sheet_id=model.sheet_id,
            annotation_code=model.annotation_code,
            amount=model.amount,
            currency=Currency(model.currency),
            bank_name=model.bank_name,
            bank_account_number=model.bank_account_number,
            cci=model.cci,
            status=model.status,
            executed_at=model.executed_at,
        )
