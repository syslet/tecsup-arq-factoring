from flask import Blueprint, Response, jsonify

from src.infrastructure.di.container import get_container
from src.presentation.decorators.verified_company_decorator import require_verified_company

disbursement_bp = Blueprint("disbursement", __name__, url_prefix="/api/v1")


@disbursement_bp.route("/sales/sheets/<int:sheet_id>/accept", methods=["POST"])
@require_verified_company
def accept_sheet_and_disburse(sheet_id: int) -> tuple[Response, int]:
    """Accepts the factoring quote for an invoice sheet, registers CAVALI account annotation, and executes disbursement."""
    container = get_container()
    try:
        updated_sheet, disbursement = container.execute_disbursement_use_case.execute(sheet_id)
        return (
            jsonify(
                {
                    "message": "Planilla aceptada y desembolso ejecutado con éxito",
                    "sheet": {
                        "id": updated_sheet.id,
                        "sheet_code": updated_sheet.sheet_code,
                        "status": updated_sheet.status,
                        "net_disbursement": updated_sheet.net_disbursement,
                    },
                    "disbursement": {
                        "id": disbursement.id,
                        "sheet_id": disbursement.sheet_id,
                        "annotation_code": disbursement.annotation_code,
                        "amount": disbursement.amount,
                        "currency": disbursement.currency.value,
                        "bank_name": disbursement.bank_name,
                        "bank_account_number": disbursement.bank_account_number,
                        "cci": disbursement.cci,
                        "status": disbursement.status,
                        "executed_at": disbursement.executed_at.isoformat()
                        if disbursement.executed_at
                        else None,
                    },
                }
            ),
            200,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error al ejecutar desembolso: {e}"}), 500


@disbursement_bp.route("/disbursements/<int:disbursement_id>", methods=["GET"])
@require_verified_company
def get_disbursement_by_id(disbursement_id: int) -> tuple[Response, int]:
    """Retrieves disbursement details by ID."""
    container = get_container()
    disbursement = container.disbursement_repository.find_by_id(disbursement_id)
    if not disbursement:
        return jsonify({"error": "Desembolso no encontrado"}), 404

    return (
        jsonify(
            {
                "disbursement": {
                    "id": disbursement.id,
                    "sheet_id": disbursement.sheet_id,
                    "annotation_code": disbursement.annotation_code,
                    "amount": disbursement.amount,
                    "currency": disbursement.currency.value,
                    "bank_name": disbursement.bank_name,
                    "bank_account_number": disbursement.bank_account_number,
                    "cci": disbursement.cci,
                    "status": disbursement.status,
                    "executed_at": disbursement.executed_at.isoformat()
                    if disbursement.executed_at
                    else None,
                }
            }
        ),
        200,
    )
