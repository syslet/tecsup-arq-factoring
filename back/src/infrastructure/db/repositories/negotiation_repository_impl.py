from sqlalchemy.orm import Session

from src.domain.entities.negotiation_history import NegotiationHistory
from src.domain.repositories.negotiation_repository import INegotiationRepository
from src.infrastructure.db.models import NegotiationHistoryModel


class SqlAlchemyNegotiationRepository(INegotiationRepository):
    """SQLAlchemy implementation of INegotiationRepository."""

    def __init__(self, db_session: Session) -> None:
        self._db = db_session

    def save(self, negotiation: NegotiationHistory) -> NegotiationHistory:
        if negotiation.id is not None:
            model = self._db.query(NegotiationHistoryModel).filter_by(id=negotiation.id).first()
            if model:
                model.status = negotiation.status
                model.offered_rate = negotiation.offered_rate
                model.notes = negotiation.notes
                self._db.flush()
                self._db.refresh(model)
                return NegotiationHistory(
                    id=model.id,
                    sheet_id=model.sheet_id,
                    requested_rate=model.requested_rate,
                    offered_rate=model.offered_rate,
                    requested_by_user_id=model.requested_by_user_id,
                    status=model.status,
                    notes=model.notes,
                    created_at=model.created_at,
                )

        model = NegotiationHistoryModel(
            sheet_id=negotiation.sheet_id,
            requested_rate=negotiation.requested_rate,
            offered_rate=negotiation.offered_rate,
            requested_by_user_id=negotiation.requested_by_user_id,
            status=negotiation.status,
            notes=negotiation.notes,
        )
        self._db.add(model)
        self._db.flush()
        self._db.refresh(model)

        return NegotiationHistory(
            id=model.id,
            sheet_id=model.sheet_id,
            requested_rate=model.requested_rate,
            offered_rate=model.offered_rate,
            requested_by_user_id=model.requested_by_user_id,
            status=model.status,
            notes=model.notes,
            created_at=model.created_at,
        )

    def find_by_sheet_id(self, sheet_id: int) -> list[NegotiationHistory]:
        models = (
            self._db.query(NegotiationHistoryModel)
            .filter(NegotiationHistoryModel.sheet_id == sheet_id)
            .order_by(NegotiationHistoryModel.created_at.desc())
            .all()
        )
        return [
            NegotiationHistory(
                id=m.id,
                sheet_id=m.sheet_id,
                requested_rate=m.requested_rate,
                offered_rate=m.offered_rate,
                requested_by_user_id=m.requested_by_user_id,
                status=m.status,
                notes=m.notes,
                created_at=m.created_at,
            )
            for m in models
        ]
