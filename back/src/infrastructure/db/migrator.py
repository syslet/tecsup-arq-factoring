import logging
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.application.use_cases.seed_admin_user import SeedAdminUserUseCase
from src.infrastructure.db.models import Base
from src.infrastructure.db.repositories.user_repository_impl import SqlAlchemyUserRepository
from src.infrastructure.db.session import SessionLocal, engine
from src.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher

logger = logging.getLogger(__name__)


def init_db_and_seed() -> None:
    """Executes database DDL SQL scripts, creates missing tables/columns, and runs initial admin seeding."""
    # Ensure all tables defined in models.py exist
    Base.metadata.create_all(bind=engine)

    # Safely apply missing column migrations on existing tables if necessary
    with engine.connect() as connection:
        connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS dni VARCHAR(20);"))
        connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(30);"))
        connection.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_status VARCHAR(50) DEFAULT 'PENDING_VERIFICATION';"
            )
        )
        connection.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0;"
            )
        )
        connection.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_locked BOOLEAN DEFAULT FALSE;")
        )
        connection.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP WITH TIME ZONE;"
            )
        )
        connection.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;"
            )
        )
        connection.execute(text("UPDATE users SET dni = '00000000' WHERE dni IS NULL;"))
        connection.commit()

    # Search in db/ddl relative to root project if present
    possible_dirs = [
        Path(__file__).resolve().parent.parent.parent.parent.parent / "db" / "ddl",
        Path(__file__).resolve().parent.parent.parent.parent / "db" / "ddl",
        Path("/app/db/ddl"),
    ]
    for ddl_dir in possible_dirs:
        if ddl_dir.exists():
            sql_files = sorted(ddl_dir.glob("*.sql"))
            with engine.connect() as connection:
                for sql_file in sql_files:
                    logger.info("Executing DDL script: %s", sql_file.name)
                    with open(sql_file, encoding="utf-8") as f:
                        sql_content = f.read()
                    connection.execute(text(sql_content))
                connection.commit()
            break

    # Seed Admin User
    db: Session = SessionLocal()
    try:
        user_repo = SqlAlchemyUserRepository(db)
        password_hasher = BcryptPasswordHasher()
        seeder = SeedAdminUserUseCase(
            user_repository=user_repo,
            password_hasher=password_hasher,
        )
        seeder.execute()
    except Exception as e:
        logger.error("Failed to seed default admin user: %s", e)
        db.rollback()
    finally:
        db.close()
