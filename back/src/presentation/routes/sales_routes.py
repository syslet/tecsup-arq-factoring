from datetime import datetime

from flask import Blueprint, Response, g, jsonify, request, send_from_directory

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


@sales_bp.route("/sheets/upload-batch", methods=["POST"])
@require_verified_company
def upload_batch_invoice_sheet() -> tuple[Response, int]:
    """Uploads a CSV or JSON batch file of invoices and processes the sheet."""
    user = getattr(g, "current_user", None)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    container = get_container()
    company = container.company_repository.find_by_user_id(user.id)
    if not company or not company.id:
        return jsonify({"error": "No company record associated with current user"}), 404

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded in form data under 'file' key"}), 400

    uploaded_file = request.files["file"]
    if not uploaded_file.filename:
        return jsonify({"error": "Selected file has no filename"}), 400

    try:
        file_bytes = uploaded_file.read()
        currency = request.form.get("currency", company.currency.value)

        sheet = container.parse_and_process_batch_use_case.execute(
            file_bytes=file_bytes,
            filename=uploaded_file.filename,
            company_id=company.id,
            drawer_ruc=company.ruc,
            currency=currency,
        )

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
                    "message": "Planilla masiva procesada con éxito",
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
    except Exception as e:
        return jsonify({"error": f"Error al procesar archivo masivo: {e}"}), 500


@sales_bp.route("/files/<file_type>/<filename>", methods=["GET", "HEAD"])
@require_verified_company
def serve_uploaded_file(file_type: str, filename: str):
    """Secure endpoint to retrieve uploaded files from storage volume."""
    container = get_container()
    file_path = container.storage_service.get_file_path(filename=filename, subfolder=file_type)
    import os
    if not os.path.exists(file_path):
        return jsonify({"error": "Archivo no encontrado"}), 404
    
    directory = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    return send_from_directory(directory, base_name)


@sales_bp.route("/sheets/<int:sheet_id>/negotiate", methods=["POST"])
@require_verified_company
def negotiate_quote(sheet_id: int) -> tuple[Response, int]:
    """Allows client to submit a rate negotiation request."""
    user = getattr(g, "current_user", None)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    requested_rate = payload.get("requested_rate")
    notes = payload.get("notes")

    if requested_rate is None:
        return jsonify({"error": "El campo 'requested_rate' es obligatorio"}), 400

    try:
        container = get_container()
        negotiation, sheet = container.negotiate_quote_use_case.execute(
            sheet_id=sheet_id,
            user_id=user.id,
            requested_rate=float(requested_rate),
            notes=notes,
        )

        return (
            jsonify(
                {
                    "message": "Solicitud de negociación procesada",
                    "status": sheet.status,
                    "negotiation": {
                        "id": negotiation.id,
                        "sheet_id": negotiation.sheet_id,
                        "requested_rate": negotiation.requested_rate,
                        "offered_rate": negotiation.offered_rate,
                        "status": negotiation.status,
                        "notes": negotiation.notes,
                    },
                    "sheet": {
                        "id": sheet.id,
                        "monthly_rate": sheet.monthly_rate,
                        "interest_fee": sheet.interest_fee,
                        "net_disbursement": sheet.net_disbursement,
                        "status": sheet.status,
                    },
                }
            ),
            200,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error al negociar tasa: {e}"}), 500


@sales_bp.route("/sheets/<int:sheet_id>/respond-negotiation", methods=["POST"])
@require_verified_company
def respond_negotiation(sheet_id: int) -> tuple[Response, int]:
    """Allows admin/executive to accept, counter offer, or reject rate negotiation."""
    payload = request.get_json(silent=True) or {}
    accepted = payload.get("accepted")
    counter_rate = payload.get("counter_rate")
    notes = payload.get("notes")

    if accepted is None:
        return jsonify({"error": "El campo 'accepted' es obligatorio"}), 400

    try:
        container = get_container()
        sheet = container.respond_negotiation_use_case.execute(
            sheet_id=sheet_id,
            accepted=bool(accepted),
            counter_rate=float(counter_rate) if counter_rate is not None else None,
            notes=notes,
        )

        return (
            jsonify(
                {
                    "message": "Negociación resuelta con éxito",
                    "sheet": {
                        "id": sheet.id,
                        "monthly_rate": sheet.monthly_rate,
                        "interest_fee": sheet.interest_fee,
                        "net_disbursement": sheet.net_disbursement,
                        "status": sheet.status,
                    },
                }
            ),
            200,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error al responder negociación: {e}"}), 500


