from datetime import datetime

from flask import Blueprint, Response, g, jsonify, request

from src.application.use_cases.process_invoice_sheet import (
    InvoiceItemInput,
    ProcessSheetCommand,
)
from src.infrastructure.di.container import get_container
from src.presentation.decorators.verified_company_decorator import require_verified_company

sales_bp = Blueprint("sales", __name__, url_prefix="/api/v1/sales")


@sales_bp.route("/sheets", methods=["POST"])
@require_verified_company
def create_invoice_sheet() -> tuple[Response, int]:
    """Uploads a batch of invoices, validates rules, calculates pricing quote."""
    user = getattr(g, "current_user", None)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    container = get_container()
    company = container.company_repository.find_by_user_id(user.id)
    if not company or not company.id:
        return jsonify({"error": "No company record associated with current user"}), 404

    payload = request.get_json(silent=True) or {}
    raw_invoices = payload.get("invoices", [])

    if not isinstance(raw_invoices, list):
        return jsonify({"error": "invoices field must be a list"}), 400

    try:
        parsed_items: list[InvoiceItemInput] = []
        for item in raw_invoices:
            issue_d = datetime.strptime(item["issue_date"], "%Y-%m-%d").date()
            due_d = datetime.strptime(item["due_date"], "%Y-%m-%d").date()

            parsed_items.append(
                InvoiceItemInput(
                    invoice_number=str(item["invoice_number"]).strip(),
                    debtor_ruc=str(item["debtor_ruc"]).strip(),
                    debtor_name=str(item.get("debtor_name", "Empresa Aceptante S.A.C.")).strip(),
                    amount=float(item["amount"]),
                    issue_date=issue_d,
                    due_date=due_d,
                )
            )

        command = ProcessSheetCommand(
            company_id=company.id,
            drawer_ruc=company.ruc,
            currency=payload.get("currency", company.currency.value),
            invoices=parsed_items,
        )

        sheet = container.process_invoice_sheet_use_case.execute(command)

        invoices_response = [
            {
                "id": inv.id,
                "invoice_number": inv.invoice_number,
                "drawer_ruc": inv.drawer_ruc,
                "debtor_ruc": inv.debtor_ruc,
                "debtor_name": inv.debtor_name,
                "amount": inv.amount,
                "currency": inv.currency.value,
                "issue_date": inv.issue_date.isoformat(),
                "due_date": inv.due_date.isoformat(),
                "days_to_maturity": inv.days_to_maturity,
                "sunat_status": inv.sunat_status,
                "is_approved": inv.is_approved,
                "rejection_reason": inv.rejection_reason,
            }
            for inv in sheet.invoices
        ]

        return (
            jsonify(
                {
                    "message": "Planilla procesada y cotizada con éxito",
                    "sheet": {
                        "id": sheet.id,
                        "sheet_code": sheet.sheet_code,
                        "company_id": sheet.company_id,
                        "currency": sheet.currency.value,
                        "total_amount": sheet.total_amount,
                        "advance_amount": sheet.advance_amount,
                        "interest_fee": sheet.interest_fee,
                        "commission": sheet.commission,
                        "net_disbursement": sheet.net_disbursement,
                        "advance_rate": sheet.advance_rate,
                        "monthly_rate": sheet.monthly_rate,
                        "status": sheet.status,
                        "invoices": invoices_response,
                    },
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except KeyError as e:
        return jsonify({"error": f"Falta el campo requerido: {e}"}), 400
    except Exception as e:
        return jsonify({"error": f"Error al procesar planilla: {e}"}), 500


@sales_bp.route("/sheets/<int:sheet_id>", methods=["GET"])
@require_verified_company
def get_invoice_sheet(sheet_id: int) -> tuple[Response, int]:
    """Retrieves an invoice sheet by ID."""
    container = get_container()
    sheet = container.invoice_sheet_repository.find_by_id(sheet_id)
    if not sheet:
        return jsonify({"error": "Planilla no encontrada"}), 404

    invoices_response = [
        {
            "id": inv.id,
            "invoice_number": inv.invoice_number,
            "drawer_ruc": inv.drawer_ruc,
            "debtor_ruc": inv.debtor_ruc,
            "debtor_name": inv.debtor_name,
            "amount": inv.amount,
            "currency": inv.currency.value,
            "issue_date": inv.issue_date.isoformat(),
            "due_date": inv.due_date.isoformat(),
            "days_to_maturity": inv.days_to_maturity,
            "sunat_status": inv.sunat_status,
            "is_approved": inv.is_approved,
            "rejection_reason": inv.rejection_reason,
        }
        for inv in sheet.invoices
    ]

    return (
        jsonify(
            {
                "sheet": {
                    "id": sheet.id,
                    "sheet_code": sheet.sheet_code,
                    "company_id": sheet.company_id,
                    "currency": sheet.currency.value,
                    "total_amount": sheet.total_amount,
                    "advance_amount": sheet.advance_amount,
                    "interest_fee": sheet.interest_fee,
                    "commission": sheet.commission,
                    "net_disbursement": sheet.net_disbursement,
                    "advance_rate": sheet.advance_rate,
                    "monthly_rate": sheet.monthly_rate,
                    "status": sheet.status,
                    "invoices": invoices_response,
                }
            }
        ),
        200,
    )


@sales_bp.route("/sheets", methods=["GET"])
@require_verified_company
def list_invoice_sheets() -> tuple[Response, int]:
    """Lists all invoice sheets for the logged in user's company."""
    user = getattr(g, "current_user", None)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    container = get_container()
    company = container.company_repository.find_by_user_id(user.id)
    if not company or not company.id:
        return jsonify({"error": "No company record"}), 404

    sheets = container.invoice_sheet_repository.find_by_company_id(company.id)
    result = [
        {
            "id": s.id,
            "sheet_code": s.sheet_code,
            "company_id": s.company_id,
            "currency": s.currency.value,
            "total_amount": s.total_amount,
            "advance_amount": s.advance_amount,
            "net_disbursement": s.net_disbursement,
            "status": s.status,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "invoices_count": len(s.invoices),
        }
        for s in sheets
    ]
    return jsonify({"sheets": result}), 200
