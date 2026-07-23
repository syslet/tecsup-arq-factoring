from flask import Blueprint, Response, g, jsonify

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
                        "cci": str(disbursement.cci),
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
                    "cci": str(disbursement.cci),
                    "status": disbursement.status,
                    "executed_at": disbursement.executed_at.isoformat()
                    if disbursement.executed_at
                    else None,
                }
            }
        ),
        200,
    )


@disbursement_bp.route("/disbursements", methods=["GET"])
@require_verified_company
def list_disbursements() -> tuple[Response, int]:
    """Retrieves all disbursements for the logged in user's company."""
    user = getattr(g, "current_user", None)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    container = get_container()
    company = container.company_repository.find_by_user_id(user.id)
    if not company or not company.id:
        return jsonify({"error": "No company record associated with current user"}), 404

    disbursements = container.list_disbursements_use_case.execute(company.id)
    result = [
        {
            "id": d.id,
            "sheet_id": d.sheet_id,
            "annotation_code": d.annotation_code,
            "amount": d.amount,
            "currency": d.currency.value,
            "bank_name": d.bank_name,
            "bank_account_number": d.bank_account_number,
            "cci": str(d.cci),
            "status": d.status,
            "executed_at": d.executed_at.isoformat() if d.executed_at else None,
        }
        for d in disbursements
    ]
    return jsonify({"disbursements": result}), 200
