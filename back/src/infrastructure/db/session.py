import os
from collections.abc import Generator
from typing import TYPE_CHECKING

from flask import Flask, g
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

if TYPE_CHECKING:
    pass


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


def init_app_db(app: Flask) -> None:
    """Registers database session and container initialization on Flask lifecycle hooks."""
    from src.infrastructure.di.container import Container

    @app.before_request
    def create_request_session_and_container() -> None:
        g.db = SessionLocal()
        g.container = Container(g.db)

    @app.teardown_appcontext
    def close_request_session(_exception: BaseException | None = None) -> None:
        db = getattr(g, "db", None)
        if db is not None:
            db.close()


def get_db_session() -> Generator[Session, None, None]:
    """Provides a database session generator."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
