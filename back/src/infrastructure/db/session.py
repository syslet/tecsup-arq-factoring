import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Base class for SQLAlchemy declarative models."""

    pass


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://factoring_user:factoring_password@db:5432/factoring_core_db",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    """Provides a database session generator."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
