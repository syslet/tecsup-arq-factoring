from dataclasses import dataclass

from src.domain.entities.company import Company
from src.domain.entities.user import User
from src.domain.exceptions.auth_exceptions import (
    CompanyAlreadyExistsException,
    UserAlreadyExistsException,
)
from src.domain.repositories.company_repository import ICompanyRepository
from src.domain.repositories.user_repository import IUserRepository
from src.domain.services.identity_verification_service import IIdentityVerificationService
from src.domain.services.password_hasher import IPasswordHasher
from src.domain.value_objects.cci_account import CciAccount
from src.domain.value_objects.currency import Currency
from src.domain.value_objects.dni import Dni
from src.domain.value_objects.password import Password
from src.domain.value_objects.ruc import Ruc
from src.domain.value_objects.user_role import UserRole
from src.domain.value_objects.verification_status import VerificationStatus


@dataclass
class CompanyRegisterData:
    """Input payload for registering corporate details during onboarding."""

    ruc: str
    business_name: str
    bank_name: str
    bank_account_number: str
    cci: str
    currency: str = "PEN"


@dataclass
class RegisterUserCommand:
    """Input payload for registering a legal representative and their company."""

    email: str
    password: str
    full_name: str
    dni: str
    phone: str | None = None
    company: CompanyRegisterData | None = None
    role: UserRole = UserRole.GIRADOR


class RegisterUserUseCase:
    """Use case for full user and company onboarding in Factoring B2B."""

    def __init__(
        self,
        user_repository: IUserRepository,
        company_repository: ICompanyRepository,
        password_hasher: IPasswordHasher,
        verification_service: IIdentityVerificationService | None = None,
    ) -> None:
        self._user_repository = user_repository
        self._company_repository = company_repository
        self._password_hasher = password_hasher
        self._verification_service = verification_service

    def execute(self, command: RegisterUserCommand) -> tuple[User, Company | None]:
        """Executes full onboarding workflow.

        Validates all Value Objects (DNI, Password, RUC, CCI), ensures uniqueness
        of Email, DNI and RUC, creates User and Company in PENDING_VERIFICATION state,
        and triggers identity verification.
        """
        # Validate Value Objects
        dni_vo = Dni(command.dni)
        password_vo = Password(command.password)

        clean_email = command.email.lower().strip()
        clean_full_name = command.full_name.strip()

        # Check existing user by email or DNI
        if self._user_repository.find_by_email(clean_email):
            raise UserAlreadyExistsException(clean_email)
        if self._user_repository.find_by_dni(dni_vo.value):
            raise UserAlreadyExistsException(dni_vo.value)

        # Validate Company if provided
        company_vo_ruc: Ruc | None = None
        company_vo_cci: CciAccount | None = None
        if command.company:
            company_vo_ruc = Ruc(command.company.ruc)
            company_vo_cci = CciAccount(command.company.cci)
            if self._company_repository.find_by_ruc(company_vo_ruc.value):
                raise CompanyAlreadyExistsException(company_vo_ruc.value)

        hashed_password = self._password_hasher.hash(password_vo.value)
        new_user = User(
            id=None,
            email=clean_email,
            password_hash=hashed_password,
            full_name=clean_full_name,
            dni=dni_vo,
            phone=command.phone.strip() if command.phone else None,
            role=command.role,
            verification_status=VerificationStatus.PENDING_VERIFICATION,
            is_active=True,
        )

        saved_user = self._user_repository.save(new_user)
        assert saved_user.id is not None

        saved_company: Company | None = None
        if command.company and company_vo_ruc and company_vo_cci:
            currency_enum = Currency(command.company.currency)
            company_entity = Company(
                id=None,
                ruc=company_vo_ruc,
                business_name=command.company.business_name.strip(),
                legal_representative_user_id=saved_user.id,
                bank_name=command.company.bank_name.strip(),
                bank_account_number=command.company.bank_account_number.strip(),
                cci=company_vo_cci,
                currency=currency_enum,
            )
            saved_company = self._company_repository.save(company_entity)

        # Execute mock legal verification (RENIEC/SUNAT). A successful check does NOT
        # auto-approve: it leaves the user PENDING_VERIFICATION for manual admin review.
        # Only a verification failure short-circuits straight to REJECTED.
        if self._verification_service and company_vo_ruc:
            try:
                self._verification_service.verify_legal_representative_and_company(
                    user_id=saved_user.id,
                    dni=saved_user.dni,
                    ruc=company_vo_ruc.value,
                )
            except Exception:
                saved_user.verification_status = VerificationStatus.REJECTED
                saved_user = self._user_repository.save(saved_user)

        return saved_user, saved_company
