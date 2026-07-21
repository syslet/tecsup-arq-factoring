from sqlalchemy.orm import Session

from src.domain.entities.company import Company
from src.domain.repositories.company_repository import ICompanyRepository
from src.domain.value_objects.currency import Currency
from src.infrastructure.db.models import CompanyModel


class SqlAlchemyCompanyRepository(ICompanyRepository):
    """SQLAlchemy implementation of ICompanyRepository."""

    def __init__(self, db_session: Session) -> None:
        self._db = db_session

    def _to_entity(self, model: CompanyModel) -> Company:
        return Company(
            id=model.id,
            ruc=model.ruc,
            business_name=model.business_name,
            legal_representative_user_id=model.legal_representative_user_id,
            bank_name=model.bank_name,
            bank_account_number=model.bank_account_number,
            cci=model.cci,
            currency=Currency(model.currency),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, company: Company) -> Company:
        if company.id is None:
            model = CompanyModel(
                ruc=company.ruc,
                business_name=company.business_name,
                legal_representative_user_id=company.legal_representative_user_id,
                bank_name=company.bank_name,
                bank_account_number=company.bank_account_number,
                cci=company.cci,
                currency=company.currency.value,
            )
            self._db.add(model)
        else:
            model = self._db.query(CompanyModel).filter(CompanyModel.id == company.id).first()
            if not model:
                model = CompanyModel(
                    id=company.id,
                    ruc=company.ruc,
                    business_name=company.business_name,
                    legal_representative_user_id=company.legal_representative_user_id,
                    bank_name=company.bank_name,
                    bank_account_number=company.bank_account_number,
                    cci=company.cci,
                    currency=company.currency.value,
                )
                self._db.add(model)
            else:
                model.ruc = company.ruc
                model.business_name = company.business_name
                model.legal_representative_user_id = company.legal_representative_user_id
                model.bank_name = company.bank_name
                model.bank_account_number = company.bank_account_number
                model.cci = company.cci
                model.currency = company.currency.value

        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, company_id: int) -> Company | None:
        model = self._db.query(CompanyModel).filter(CompanyModel.id == company_id).first()
        return self._to_entity(model) if model else None

    def find_by_ruc(self, ruc: str) -> Company | None:
        model = self._db.query(CompanyModel).filter(CompanyModel.ruc == ruc.strip()).first()
        return self._to_entity(model) if model else None

    def find_by_user_id(self, user_id: int) -> Company | None:
        model = (
            self._db.query(CompanyModel)
            .filter(CompanyModel.legal_representative_user_id == user_id)
            .first()
        )
        return self._to_entity(model) if model else None
