import json
from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.application.use_cases.negotiate_quote import NegotiateQuoteUseCase
from src.application.use_cases.parse_and_process_batch import ParseAndProcessBatchUseCase
from src.application.use_cases.process_invoice_sheet import ProcessInvoiceSheetUseCase
from src.application.use_cases.respond_negotiation import RespondNegotiationUseCase
from src.domain.entities.company import Company
from src.domain.entities.user import User, UserRole, VerificationStatus
from src.domain.value_objects.currency import Currency
from src.infrastructure.db.models import Base
from src.infrastructure.db.repositories.company_repository_impl import SqlAlchemyCompanyRepository
from src.infrastructure.db.repositories.invoice_sheet_repository_impl import (
    SqlAlchemyInvoiceSheetRepository,
)
from src.infrastructure.db.repositories.negotiation_repository_impl import (
    SqlAlchemyNegotiationRepository,
)
from src.infrastructure.db.repositories.user_repository_impl import SqlAlchemyUserRepository
from src.infrastructure.services.local_storage_service import LocalStorageService


@pytest.fixture
def db_session():
    sqlite_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=sqlite_engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_parse_and_process_batch(db_session, tmp_path):
    storage_service = LocalStorageService(base_dir=str(tmp_path))
    sheet_repo = SqlAlchemyInvoiceSheetRepository(db_session)
    process_use_case = ProcessInvoiceSheetUseCase(sheet_repository=sheet_repo)
    batch_use_case = ParseAndProcessBatchUseCase(
        process_sheet_use_case=process_use_case,
        storage_service=storage_service,
    )

    user_repo = SqlAlchemyUserRepository(db_session)
    company_repo = SqlAlchemyCompanyRepository(db_session)

    user = user_repo.save(
        User(
            id=None,
            email="batch_user@test.com",
            password_hash="hashed_pw",
            full_name="Batch User",
            dni="88776655",
            role=UserRole.GIRADOR,
            verification_status=VerificationStatus.APPROVED,
        )
    )
    company = company_repo.save(
        Company(
            id=None,
            ruc="20987654321",
            business_name="Batch Test Corp SAC",
            legal_representative_user_id=user.id,
            bank_name="BCP",
            bank_account_number="123456789",
            cci="00212345678901234567",
            currency=Currency.PEN,
        )
    )

    today = date.today()
    due = today + timedelta(days=30)
    batch_json = [
        {
            "invoice_number": "F001-0001",
            "debtor_ruc": "20111111111",
            "debtor_name": "Debtor A SAC",
            "amount": 15000.0,
            "issue_date": today.isoformat(),
            "due_date": due.isoformat(),
        }
    ]
    file_bytes = json.dumps(batch_json).encode("utf-8")

    sheet = batch_use_case.execute(
        file_bytes=file_bytes,
        filename="invoices_batch.json",
        company_id=company.id,
        drawer_ruc=company.ruc,
        currency="PEN",
    )

    assert sheet.id is not None
    assert sheet.status == "QUOTED"
    assert sheet.total_amount == 15000.0
    assert len(sheet.invoices) == 1


def test_rate_negotiation_flow(db_session, tmp_path):
    storage_service = LocalStorageService(base_dir=str(tmp_path))
    sheet_repo = SqlAlchemyInvoiceSheetRepository(db_session)
    negotiation_repo = SqlAlchemyNegotiationRepository(db_session)
    user_repo = SqlAlchemyUserRepository(db_session)
    company_repo = SqlAlchemyCompanyRepository(db_session)

    user = user_repo.save(
        User(
            id=None,
            email="neg_user@test.com",
            password_hash="hashed_pw",
            full_name="Neg User",
            dni="11224455",
            role=UserRole.GIRADOR,
            verification_status=VerificationStatus.APPROVED,
        )
    )
    company = company_repo.save(
        Company(
            id=None,
            ruc="20999888777",
            business_name="Neg Corp SAC",
            legal_representative_user_id=user.id,
            bank_name="BBVA",
            bank_account_number="987654321",
            cci="01198765432109876543",
            currency=Currency.PEN,
        )
    )

    process_use_case = ProcessInvoiceSheetUseCase(sheet_repository=sheet_repo)
    batch_use_case = ParseAndProcessBatchUseCase(
        process_sheet_use_case=process_use_case,
        storage_service=storage_service,
    )

    today = date.today()
    due = today + timedelta(days=30)
    batch_json = [
        {
            "invoice_number": "F001-0002",
            "debtor_ruc": "20222222222",
            "debtor_name": "Debtor B SAC",
            "amount": 20000.0,
            "issue_date": today.isoformat(),
            "due_date": due.isoformat(),
        }
    ]
    sheet = batch_use_case.execute(
        file_bytes=json.dumps(batch_json).encode("utf-8"),
        filename="invoices_neg.json",
        company_id=company.id,
        drawer_ruc=company.ruc,
    )

    negotiate_use_case = NegotiateQuoteUseCase(
        sheet_repository=sheet_repo,
        negotiation_repository=negotiation_repo,
    )
    respond_use_case = RespondNegotiationUseCase(
        sheet_repository=sheet_repo,
        negotiation_repository=negotiation_repo,
    )

    # 1. Negotiate within tolerance (0.02 -> 0.018 = diff 0.002 <= 0.015)
    neg_entry, updated_sheet = negotiate_use_case.execute(
        sheet_id=sheet.id,
        user_id=user.id,
        requested_rate=0.018,
        notes="Tolerance test",
    )
    assert neg_entry.status == "ACCEPTED"
    assert updated_sheet.status == "COUNTER_OFFERED"
    assert updated_sheet.monthly_rate == 0.018

    # 2. Respond negotiation approval
    approved_sheet = respond_use_case.execute(
        sheet_id=sheet.id,
        accepted=True,
    )
    assert approved_sheet.status == "APPROVED"
