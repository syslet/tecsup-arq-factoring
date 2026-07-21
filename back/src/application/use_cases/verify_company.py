from src.domain.entities.user import User
from src.domain.repositories.company_repository import ICompanyRepository
from src.domain.repositories.user_repository import IUserRepository
from src.domain.value_objects.verification_status import VerificationStatus


class VerifyCompanyUseCase:
    """Use case to mock administrative approval or rejection of company and legal rep verification."""

    def __init__(
        self,
        user_repository: IUserRepository,
        company_repository: ICompanyRepository,
    ) -> None:
        self._user_repository = user_repository
        self._company_repository = company_repository

    def execute(self, company_id: int, approve: bool = True) -> User:
        company = self._company_repository.find_by_id(company_id)
        if not company:
            raise ValueError(f"Company with id {company_id} not found")

        user = self._user_repository.find_by_id(company.legal_representative_user_id)
        if not user:
            raise ValueError(f"Legal representative user for company {company_id} not found")

        new_status = VerificationStatus.APPROVED if approve else VerificationStatus.REJECTED
        user.verification_status = new_status
        return self._user_repository.save(user)
