from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.domain.entities.user import User
from src.domain.repositories.user_repository import IUserRepository
from src.domain.value_objects.dni import Dni
from src.domain.value_objects.user_role import UserRole
from src.domain.value_objects.verification_status import VerificationStatus
from src.infrastructure.db.models import UserModel


class SqlAlchemyUserRepository(IUserRepository):
    """SQLAlchemy implementation of IUserRepository."""

    def __init__(self, db_session: Session) -> None:
        self._db = db_session

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            full_name=model.full_name,
            dni=Dni(model.dni),
            phone=model.phone,
            role=UserRole(model.role),
            verification_status=VerificationStatus(model.verification_status),
            is_active=model.is_active,
            failed_login_attempts=model.failed_login_attempts,
            is_locked=model.is_locked,
            locked_until=model.locked_until,
            last_login_at=model.last_login_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, user: User) -> User:
        dni_str = user.dni.value
        role_str = user.role.value
        status_str = user.verification_status.value
        if user.id is None:
            model = UserModel(
                email=user.email,
                password_hash=user.password_hash,
                full_name=user.full_name,
                dni=dni_str,
                phone=user.phone,
                role=role_str,
                verification_status=status_str,
                is_active=user.is_active,
                failed_login_attempts=user.failed_login_attempts,
                is_locked=user.is_locked,
                locked_until=user.locked_until,
                last_login_at=user.last_login_at,
            )
            self._db.add(model)
        else:
            model = self._db.query(UserModel).filter(UserModel.id == user.id).first()
            if not model:
                model = UserModel(
                    id=user.id,
                    email=user.email,
                    password_hash=user.password_hash,
                    full_name=user.full_name,
                    dni=dni_str,
                    phone=user.phone,
                    role=role_str,
                    verification_status=status_str,
                    is_active=user.is_active,
                    failed_login_attempts=user.failed_login_attempts,
                    is_locked=user.is_locked,
                    locked_until=user.locked_until,
                    last_login_at=user.last_login_at,
                )
                self._db.add(model)
            else:
                model.email = user.email
                model.password_hash = user.password_hash
                model.full_name = user.full_name
                model.dni = dni_str
                model.phone = user.phone
                model.role = user.role.value
                model.verification_status = user.verification_status.value
                model.is_active = user.is_active
                model.failed_login_attempts = user.failed_login_attempts
                model.is_locked = user.is_locked
                model.locked_until = user.locked_until
                model.last_login_at = user.last_login_at

        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, user_id: int) -> User | None:
        model = self._db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(model) if model else None

    def find_by_email(self, email: str) -> User | None:
        model = self._db.query(UserModel).filter(UserModel.email == email.lower().strip()).first()
        return self._to_entity(model) if model else None

    def find_by_dni(self, dni: str) -> User | None:
        model = self._db.query(UserModel).filter(UserModel.dni == dni.strip()).first()
        return self._to_entity(model) if model else None

    def find_by_identifier(self, identifier: str) -> User | None:
        clean_identifier = identifier.strip().lower()
        model = (
            self._db.query(UserModel)
            .filter(
                or_(
                    UserModel.email == clean_identifier,
                    UserModel.dni == identifier.strip(),
                )
            )
            .first()
        )
        return self._to_entity(model) if model else None

    def find_all(self) -> list[User]:
        models = self._db.query(UserModel).all()
        return [self._to_entity(m) for m in models]
