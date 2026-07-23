from flask import g
from sqlalchemy.orm import Session

from src.application.use_cases.execute_disbursement import ExecuteDisbursementUseCase
from src.application.use_cases.get_current_user import GetCurrentUserUseCase
from src.application.use_cases.list_disbursements import ListDisbursementsUseCase
from src.application.use_cases.login_user import LoginUserUseCase
from src.application.use_cases.logout_user import LogoutUserUseCase
from src.application.use_cases.negotiate_quote import NegotiateQuoteUseCase
from src.application.use_cases.parse_and_process_batch import ParseAndProcessBatchUseCase
from src.application.use_cases.process_invoice_sheet import ProcessInvoiceSheetUseCase
from src.application.use_cases.register_user import RegisterUserUseCase
from src.application.use_cases.respond_negotiation import RespondNegotiationUseCase
from src.application.use_cases.verify_company import VerifyCompanyUseCase
from src.infrastructure.db.repositories.company_document_repository_impl import (
    SqlAlchemyCompanyDocumentRepository,
)
from src.infrastructure.db.repositories.company_repository_impl import SqlAlchemyCompanyRepository
from src.infrastructure.db.repositories.disbursement_repository_impl import (
    SqlAlchemyDisbursementRepository,
)
from src.infrastructure.db.repositories.invoice_sheet_repository_impl import (
    SqlAlchemyInvoiceSheetRepository,
)
from src.infrastructure.db.repositories.negotiation_repository_impl import (
    SqlAlchemyNegotiationRepository,
)
from src.infrastructure.db.repositories.session_repository_impl import SqlAlchemySessionRepository
from src.infrastructure.db.repositories.user_repository_impl import SqlAlchemyUserRepository
from src.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from src.infrastructure.services.jwt_token_service import PyJwtTokenService
from src.infrastructure.services.local_storage_service import LocalStorageService
from src.infrastructure.services.mock_identity_verification_service import (
    MockIdentityVerificationService,
)
from src.infrastructure.services.pricing_service_impl import StandardPricingService


class Container:
    """Dependency injection container for wiring repositories and use cases."""

    def __init__(self, db_session: Session) -> None:
        self.db = db_session
        self.user_repository = SqlAlchemyUserRepository(db_session)
        self.company_repository = SqlAlchemyCompanyRepository(db_session)
        self.company_document_repository = SqlAlchemyCompanyDocumentRepository(db_session)
        self.invoice_sheet_repository = SqlAlchemyInvoiceSheetRepository(db_session)
        self.disbursement_repository = SqlAlchemyDisbursementRepository(db_session)
        self.session_repository = SqlAlchemySessionRepository(db_session)
        self.negotiation_repository = SqlAlchemyNegotiationRepository(db_session)
        self.password_hasher = BcryptPasswordHasher()
        self.token_service = PyJwtTokenService()
        self.verification_service = MockIdentityVerificationService()
        self.storage_service = LocalStorageService()
        self.pricing_service = StandardPricingService()

    @property
    def negotiate_quote_use_case(self) -> NegotiateQuoteUseCase:
        return NegotiateQuoteUseCase(
            sheet_repository=self.invoice_sheet_repository,
            negotiation_repository=self.negotiation_repository,
        )

    @property
    def respond_negotiation_use_case(self) -> RespondNegotiationUseCase:
        return RespondNegotiationUseCase(
            sheet_repository=self.invoice_sheet_repository,
            negotiation_repository=self.negotiation_repository,
        )

    @property
    def parse_and_process_batch_use_case(self) -> ParseAndProcessBatchUseCase:
        return ParseAndProcessBatchUseCase(
            process_sheet_use_case=self.process_invoice_sheet_use_case,
            storage_service=self.storage_service,
        )

    @property
    def execute_disbursement_use_case(self) -> ExecuteDisbursementUseCase:
        return ExecuteDisbursementUseCase(
            sheet_repository=self.invoice_sheet_repository,
            company_repository=self.company_repository,
            disbursement_repository=self.disbursement_repository,
        )

    @property
    def list_disbursements_use_case(self) -> ListDisbursementsUseCase:
        return ListDisbursementsUseCase(
            disbursement_repository=self.disbursement_repository,
        )

    @property
    def process_invoice_sheet_use_case(self) -> ProcessInvoiceSheetUseCase:
        return ProcessInvoiceSheetUseCase(
            sheet_repository=self.invoice_sheet_repository,
            pricing_service=self.pricing_service,
        )

    @property
    def verify_company_use_case(self) -> VerifyCompanyUseCase:
        return VerifyCompanyUseCase(
            user_repository=self.user_repository,
            company_repository=self.company_repository,
        )

    @property
    def register_user_use_case(self) -> RegisterUserUseCase:
        return RegisterUserUseCase(
            user_repository=self.user_repository,
            company_repository=self.company_repository,
            password_hasher=self.password_hasher,
            verification_service=self.verification_service,
        )

    @property
    def login_user_use_case(self) -> LoginUserUseCase:
        return LoginUserUseCase(
            user_repository=self.user_repository,
            session_repository=self.session_repository,
            password_hasher=self.password_hasher,
            token_service=self.token_service,
        )

    @property
    def logout_user_use_case(self) -> LogoutUserUseCase:
        return LogoutUserUseCase(
            session_repository=self.session_repository,
        )

    @property
    def get_current_user_use_case(self) -> GetCurrentUserUseCase:
        return GetCurrentUserUseCase(
            token_service=self.token_service,
            user_repository=self.user_repository,
            session_repository=self.session_repository,
        )


def get_container() -> Container:
    """Retrieves the request-scoped Container instance from Flask g object.

    Raises:
        RuntimeError: If called outside request context or before Container init.
    """
    container: Container | None = getattr(g, "container", None)
    if container is None:
        raise RuntimeError("Container is not initialized in the request context.")
    return container
