from src.domain.entities.disbursement import Disbursement
from src.domain.repositories.disbursement_repository import IDisbursementRepository


class ListDisbursementsUseCase:
    """Use case for listing all executed disbursements of a company."""

    def __init__(self, disbursement_repository: IDisbursementRepository) -> None:
        self._disbursement_repository = disbursement_repository

    def execute(self, company_id: int) -> list[Disbursement]:
        return self._disbursement_repository.find_by_company_id(company_id)
