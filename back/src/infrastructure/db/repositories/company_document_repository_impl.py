from sqlalchemy.orm import Session

from src.domain.entities.company_document import CompanyDocument
from src.domain.repositories.company_document_repository import ICompanyDocumentRepository
from src.infrastructure.db.models import CompanyDocumentModel


class SqlAlchemyCompanyDocumentRepository(ICompanyDocumentRepository):
    """SQLAlchemy implementation of ICompanyDocumentRepository."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, document: CompanyDocument) -> CompanyDocument:
        model = CompanyDocumentModel(
            company_id=document.company_id,
            document_type=document.document_type,
            file_name=document.file_name,
            file_path=document.file_path,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return CompanyDocument(
            id=model.id,
            company_id=model.company_id,
            document_type=model.document_type,
            file_name=model.file_name,
            file_path=model.file_path,
            uploaded_at=model.uploaded_at,
        )

    def find_by_company_id(self, company_id: int) -> list[CompanyDocument]:
        models = (
            self._db.query(CompanyDocumentModel)
            .filter(CompanyDocumentModel.company_id == company_id)
            .all()
        )
        return [
            CompanyDocument(
                id=m.id,
                company_id=m.company_id,
                document_type=m.document_type,
                file_name=m.file_name,
                file_path=m.file_path,
                uploaded_at=m.uploaded_at,
            )
            for m in models
        ]
