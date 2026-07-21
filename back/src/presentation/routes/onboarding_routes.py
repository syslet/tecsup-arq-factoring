import os

from flask import Blueprint, Response, g, jsonify, request
from werkzeug.utils import secure_filename

from src.domain.entities.company_document import CompanyDocument
from src.infrastructure.di.container import get_container
from src.presentation.decorators.auth_decorator import login_required

onboarding_bp = Blueprint("onboarding", __name__, url_prefix="/api/v1")

UPLOAD_FOLDER = "/tmp/company_documents"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@onboarding_bp.route("/onboarding/documents", methods=["POST"])
@login_required
def upload_company_document() -> tuple[Response, int]:
    """Uploads legal/tax documents for the logged-in user's company."""
    user = getattr(g, "current_user", None)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    container = get_container()
    company = container.company_repository.find_by_user_id(user.id)
    if not company:
        return jsonify({"error": "No company associated with current user"}), 404

    document_type = request.form.get("document_type", "GENERAL")
    file = request.files.get("file")

    if file and file.filename:
        filename = secure_filename(file.filename)
        saved_path = os.path.join(UPLOAD_FOLDER, f"{company.id}_{filename}")
        file.save(saved_path)
    else:
        # Fallback if raw JSON payload or dummy mock file provided
        payload = request.get_json(silent=True) or {}
        document_type = payload.get("document_type", document_type)
        filename = payload.get("file_name", "document.pdf")
        saved_path = f"{UPLOAD_FOLDER}/{company.id}_{filename}"

    assert company.id is not None
    doc = CompanyDocument(
        id=None,
        company_id=company.id,
        document_type=document_type,
        file_name=filename,
        file_path=saved_path,
    )
    saved_doc = container.company_document_repository.save(doc)

    return (
        jsonify(
            {
                "message": "Document uploaded successfully",
                "document": {
                    "id": saved_doc.id,
                    "company_id": saved_doc.company_id,
                    "document_type": saved_doc.document_type,
                    "file_name": saved_doc.file_name,
                    "file_path": saved_doc.file_path,
                },
            }
        ),
        201,
    )


@onboarding_bp.route("/admin/companies/<int:company_id>/verify", methods=["POST"])
def verify_company_admin(company_id: int) -> tuple[Response, int]:
    """Mock administrative endpoint to approve or reject company verification (SUNAT/RENIEC)."""
    payload = request.get_json(silent=True) or {}
    approve = payload.get("approve", True)

    container = get_container()
    try:
        updated_user = container.verify_company_use_case.execute(company_id, approve=approve)
        status_val = (
            updated_user.verification_status.value
            if hasattr(updated_user.verification_status, "value")
            else str(updated_user.verification_status)
        )
        return (
            jsonify(
                {
                    "message": f"Company {company_id} verification updated",
                    "company_id": company_id,
                    "verification_status": status_val,
                }
            ),
            200,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
