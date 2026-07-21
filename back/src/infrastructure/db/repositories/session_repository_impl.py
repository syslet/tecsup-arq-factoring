from sqlalchemy.orm import Session

from src.domain.entities.session import UserSession
from src.domain.repositories.session_repository import ISessionRepository
from src.infrastructure.db.models import SessionModel


class SqlAlchemySessionRepository(ISessionRepository):
    """SQLAlchemy implementation of ISessionRepository."""

    def __init__(self, db_session: Session) -> None:
        self._db = db_session

    def _to_entity(self, model: SessionModel) -> UserSession:
        return UserSession(
            id=model.id,
            user_id=model.user_id,
            token_jti=model.token_jti,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            is_revoked=model.is_revoked,
            created_at=model.created_at,
            expires_at=model.expires_at,
        )

    def save(self, session: UserSession) -> UserSession:
        if session.id is None:
            model = SessionModel(
                user_id=session.user_id,
                token_jti=session.token_jti,
                ip_address=session.ip_address,
                user_agent=session.user_agent,
                is_revoked=session.is_revoked,
                expires_at=session.expires_at,
            )
            self._db.add(model)
        else:
            model = self._db.query(SessionModel).filter(SessionModel.id == session.id).first()
            if model:
                model.is_revoked = session.is_revoked
                model.expires_at = session.expires_at

        self._db.commit()
        if model:
            self._db.refresh(model)
            return self._to_entity(model)
        raise ValueError("Could not save session")

    def find_by_jti(self, token_jti: str) -> UserSession | None:
        model = self._db.query(SessionModel).filter(SessionModel.token_jti == token_jti).first()
        return self._to_entity(model) if model else None

    def revoke_by_jti(self, token_jti: str) -> bool:
        model = self._db.query(SessionModel).filter(SessionModel.token_jti == token_jti).first()
        if model:
            model.is_revoked = True
            self._db.commit()
            return True
        return False

    def revoke_all_user_sessions(self, user_id: int) -> int:
        count = (
            self._db.query(SessionModel)
            .filter(SessionModel.user_id == user_id, SessionModel.is_revoked == False)  # noqa: E712
            .update({SessionModel.is_revoked: True})
        )
        self._db.commit()
        return int(count)
