from unittest.mock import MagicMock

import pytest

from src.application.use_cases.login_user import LoginCommand, LoginUserUseCase
from src.application.use_cases.register_user import (
    CompanyRegisterData,
    RegisterUserCommand,
    RegisterUserUseCase,
)
from src.domain.entities.user import User
from src.domain.exceptions.auth_exceptions import (
    AccountLockedException,
    InvalidCredentialsException,
    UserAlreadyExistsException,
)
from src.domain.value_objects.user_role import UserRole
from src.domain.value_objects.verification_status import VerificationStatus


def test_register_user_success() -> None:
    user_repo_mock = MagicMock()
    user_repo_mock.find_by_email.return_value = None
    user_repo_mock.find_by_dni.return_value = None
    user_repo_mock.save.side_effect = lambda u: User(
        id=1,
        email=u.email,
        password_hash=u.password_hash,
        full_name=u.full_name,
        dni=u.dni,
        role=u.role,
        verification_status=VerificationStatus.APPROVED,
        is_active=True,
    )

    company_repo_mock = MagicMock()
    company_repo_mock.find_by_ruc.return_value = None

    hasher_mock = MagicMock()
    hasher_mock.hash.return_value = "hashed_secret"

    verification_mock = MagicMock()
    verification_mock.verify_legal_representative_and_company.return_value = (
        VerificationStatus.APPROVED
    )

    use_case = RegisterUserUseCase(
        user_repository=user_repo_mock,
        company_repository=company_repo_mock,
        password_hasher=hasher_mock,
        verification_service=verification_mock,
    )

    command = RegisterUserCommand(
        email="test@factoring.com",
        password="SecretPassword123!",
        full_name="Test User",
        dni="12345678",
        company=CompanyRegisterData(
            ruc="20123456789",
            business_name="Empresa Test S.A.C.",
            bank_name="BCP",
            bank_account_number="191-12345678-0-12",
            cci="00219100123456780123",
        ),
    )

    user, _company = use_case.execute(command)

    assert user.id == 1
    assert user.email == "test@factoring.com"
    assert user.dni == "12345678"
    assert user.role == UserRole.GIRADOR
    assert user.verification_status == VerificationStatus.APPROVED
    hasher_mock.hash.assert_called_once_with("SecretPassword123!")


def test_register_user_duplicate_email() -> None:
    user_repo_mock = MagicMock()
    user_repo_mock.find_by_email.return_value = User(
        id=1,
        email="existing@factoring.com",
        password_hash="hash",
        full_name="Existing",
        dni="87654321",
        role=UserRole.GIRADOR,
    )

    company_repo_mock = MagicMock()
    hasher_mock = MagicMock()

    use_case = RegisterUserUseCase(
        user_repository=user_repo_mock,
        company_repository=company_repo_mock,
        password_hasher=hasher_mock,
    )

    command = RegisterUserCommand(
        email="existing@factoring.com",
        password="Password123!",
        full_name="Duplicate",
        dni="12345678",
    )

    with pytest.raises(UserAlreadyExistsException):
        use_case.execute(command)


def test_login_user_invalid_credentials() -> None:
    user_repo_mock = MagicMock()
    user_repo_mock.find_by_identifier.return_value = None
    session_repo_mock = MagicMock()
    hasher_mock = MagicMock()
    token_service_mock = MagicMock()

    use_case = LoginUserUseCase(
        user_repository=user_repo_mock,
        session_repository=session_repo_mock,
        password_hasher=hasher_mock,
        token_service=token_service_mock,
    )

    command = LoginCommand(identifier="unknown@factoring.com", password="Password123!")

    with pytest.raises(InvalidCredentialsException):
        use_case.execute(command)


def test_login_user_lockout_on_5_failed_attempts() -> None:
    existing_user = User(
        id=1,
        email="target@factoring.com",
        password_hash="correct_hash",
        full_name="Target",
        dni="12345678",
        role=UserRole.GIRADOR,
        failed_login_attempts=4,
        is_locked=False,
    )
    user_repo_mock = MagicMock()
    user_repo_mock.find_by_identifier.return_value = existing_user
    session_repo_mock = MagicMock()
    hasher_mock = MagicMock()
    hasher_mock.verify.return_value = False
    token_service_mock = MagicMock()

    use_case = LoginUserUseCase(
        user_repository=user_repo_mock,
        session_repository=session_repo_mock,
        password_hasher=hasher_mock,
        token_service=token_service_mock,
        max_failed_attempts=5,
    )

    command = LoginCommand(identifier="12345678", password="WrongPassword123!")

    with pytest.raises(AccountLockedException):
        use_case.execute(command)

    assert existing_user.failed_login_attempts == 5
    assert existing_user.is_locked is True
