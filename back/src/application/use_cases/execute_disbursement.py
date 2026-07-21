from src.domain.entities.disbursement import Disbursement
from src.domain.entities.invoice_sheet import InvoiceSheet
from src.domain.repositories.company_repository import ICompanyRepository
from src.domain.repositories.disbursement_repository import IDisbursementRepository
from src.domain.repositories.invoice_sheet_repository import IInvoiceSheetRepository
from src.infrastructure.services.account_annotation_service import AccountAnnotationService


class ExecuteDisbursementUseCase:
    """Use case to accept a factoring quote, execute CAVALI account annotation and register bank disbursement."""

    def __init__(
        self,
        sheet_repository: IInvoiceSheetRepository,
        company_repository: ICompanyRepository,
        disbursement_repository: IDisbursementRepository,
        annotation_service: AccountAnnotationService | None = None,
    ) -> None:
        self._sheet_repository = sheet_repository
        self._company_repository = company_repository
        self._disbursement_repository = disbursement_repository
        self._annotation_service = annotation_service or AccountAnnotationService()

    def execute(self, sheet_id: int) -> tuple[InvoiceSheet, Disbursement]:
        sheet = self._sheet_repository.find_by_id(sheet_id)
        if not sheet:
            raise ValueError(f"Planilla con ID {sheet_id} no encontrada")

        if sheet.status == "DISBURSED":
            existing = self._disbursement_repository.find_by_sheet_id(sheet_id)
            if existing:
                return sheet, existing

        company = self._company_repository.find_by_id(sheet.company_id)
        if not company:
            raise ValueError(f"Empresa con ID {sheet.company_id} no encontrada")

        # 1. Register Account Annotation with CAVALI/RADIAN
        annotation_code = self._annotation_service.register_account_annotation(
            sheet.sheet_code, len(sheet.invoices)
        )

        assert sheet.id is not None

        # 2. Create Disbursement record
        disbursement = Disbursement(
            id=None,
            sheet_id=sheet.id,
            annotation_code=annotation_code,
            amount=sheet.net_disbursement,
            currency=sheet.currency,
            bank_name=company.bank_name,
            bank_account_number=company.bank_account_number,
            cci=company.cci,
            status="DISBURSED",
        )
        saved_disbursement = self._disbursement_repository.save(disbursement)

        # 3. Update sheet status -> DISBURSED
        sheet.status = "DISBURSED"
        updated_sheet = self._sheet_repository.save(sheet)

        return updated_sheet, saved_disbursement
