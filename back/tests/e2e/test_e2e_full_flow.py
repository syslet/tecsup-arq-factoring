from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.db.session import Base
from src.presentation.app import create_app


@pytest.fixture
def client():
    sqlite_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=sqlite_engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)

    app = create_app()
    app.config["TESTING"] = True

    from src.infrastructure.di.container import Container

    @app.before_request
    def override_create_session():
        from flask import g

        g.db = TestingSessionLocal()
        g.container = Container(g.db)

    with app.test_client() as client:
        yield client


def test_full_e2e_client_journey(client):
    """Full End-to-End Client Journey Test:

    1. Register -> 2. Verification -> 3. Carga de Planilla -> 4. Visualización de Cotización -> 5. Aceptación y Desembolso
    """
    # ---------------------------------------------------------
    # PASO 1: Registro (Etapa 1 + Etapa 2)
    # ---------------------------------------------------------
    reg_payload = {
        "email": "e2e_ceo@empresa.com",
        "password": "Password123!",
        "full_name": "Roberto Diaz",
        "dni": "44332211",
        "phone": "987654321",
        "company": {
            "ruc": "20555444333",
            "business_name": "Industrias Peru SAC",
            "bank_name": "Interbank",
            "bank_account_number": "200-300400-0-11",
            "cci": "00320000300400011122",
            "currency": "PEN",
        },
    }
    reg_resp = client.post("/api/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201, reg_resp.get_json()
    company_id = reg_resp.get_json()["user"]["company"]["id"]

    # Authenticate to obtain JWT Bearer Token
    login_resp = client.post(
        "/api/auth/login",
        json={"identifier": "e2e_ceo@empresa.com", "password": "Password123!"},
    )
    assert login_resp.status_code == 200
    token = login_resp.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload verification document
    doc_resp = client.post(
        "/api/v1/onboarding/documents",
        json={"document_type": "VIGENCIA_PODER", "file_name": "vigencia_e2e.pdf"},
        headers=headers,
    )
    assert doc_resp.status_code == 201

    # ---------------------------------------------------------
    # PASO 2: Verificación (Admin mock approval)
    # ---------------------------------------------------------
    verify_resp = client.post(
        f"/api/v1/admin/companies/{company_id}/verify", json={"approve": True}
    )
    assert verify_resp.status_code == 200
    assert verify_resp.get_json()["verification_status"] == "APPROVED"

    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.get_json()["user"]["verification_status"] == "APPROVED"

    # ---------------------------------------------------------
    # PASO 3: Carga de Planilla & Motor de Pricing
    # ---------------------------------------------------------
    today = date.today()
    sheet_payload = {
        "currency": "PEN",
        "invoices": [
            {
                "invoice_number": "F001-000100",
                "debtor_ruc": "20987654321",
                "debtor_name": "Comercializadora Lima S.A.",
                "amount": 50000.00,
                "issue_date": today.isoformat(),
                "due_date": (today + timedelta(days=90)).isoformat(),
            },
            {
                "invoice_number": "F001-000101",
                "debtor_ruc": "20112233445",
                "debtor_name": "Supermercados Peru S.A.",
                "amount": 30000.00,
                "issue_date": today.isoformat(),
                "due_date": (today + timedelta(days=45)).isoformat(),
            },
        ],
    }
    sheet_resp = client.post("/api/v1/sales/sheets", json=sheet_payload, headers=headers)
    assert sheet_resp.status_code == 200, sheet_resp.get_json()
    sheet_data = sheet_resp.get_json()["sheet"]
    sheet_id = sheet_data["id"]

    assert sheet_data["total_amount"] == 80000.00
    assert sheet_data["advance_amount"] == 68000.00  # 85% of 80000
    assert sheet_data["net_disbursement"] > 0
    assert len(sheet_data["invoices"]) == 2

    # ---------------------------------------------------------
    # PASO 4: Visualización de Cotización (GET /sheets/{id})
    # ---------------------------------------------------------
    get_sheet_resp = client.get(f"/api/v1/sales/sheets/{sheet_id}", headers=headers)
    assert get_sheet_resp.status_code == 200
    fetched_sheet = get_sheet_resp.get_json()["sheet"]
    assert fetched_sheet["status"] == "QUOTED"

    # ---------------------------------------------------------
    # PASO 5: Aceptación y Desembolso Bancario
    # ---------------------------------------------------------
    accept_resp = client.post(f"/api/v1/sales/sheets/{sheet_id}/accept", headers=headers)
    assert accept_resp.status_code == 200, accept_resp.get_json()
    disb_data = accept_resp.get_json()

    assert disb_data["sheet"]["status"] == "DISBURSED"
    assert "CAVALI-" in disb_data["disbursement"]["annotation_code"]
    assert disb_data["disbursement"]["bank_name"] == "Interbank"
    assert disb_data["disbursement"]["cci"] == "00320000300400011122"
    disb_id = disb_data["disbursement"]["id"]

    # Verify final Disbursement receipt retrieval
    disb_get_resp = client.get(f"/api/v1/disbursements/{disb_id}", headers=headers)
    assert disb_get_resp.status_code == 200
    assert (
        disb_get_resp.get_json()["disbursement"]["annotation_code"]
        == disb_data["disbursement"]["annotation_code"]
    )
