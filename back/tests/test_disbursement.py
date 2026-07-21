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


def test_disbursement_execution_flow(client):
    # 1. Register & verify user + company
    reg_payload = {
        "email": "disbursement_test@empresa.com",
        "password": "Password123!",
        "full_name": "Carlos Gomez",
        "dni": "55667788",
        "company": {
            "ruc": "20888888888",
            "business_name": "Factoring Client SAC",
            "bank_name": "BBVA",
            "bank_account_number": "0011-0123-456789",
            "cci": "01101230004567890123",
            "currency": "PEN",
        },
    }
    resp = client.post("/api/auth/register", json=reg_payload)
    assert resp.status_code == 201
    company_id = resp.get_json()["user"]["company"]["id"]

    # Verify company
    client.post(f"/api/v1/admin/companies/{company_id}/verify", json={"approve": True})

    # Login
    login_resp = client.post(
        "/api/auth/login",
        json={
            "identifier": "disbursement_test@empresa.com",
            "password": "Password123!",
        },
    )
    token = login_resp.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create sheet quote
    today = date.today()
    sheet_payload = {
        "currency": "PEN",
        "invoices": [
            {
                "invoice_number": "F001-998877",
                "debtor_ruc": "20777777777",
                "debtor_name": "Empresa Deudora S.A.C.",
                "amount": 15000.00,
                "issue_date": today.isoformat(),
                "due_date": (today + timedelta(days=60)).isoformat(),
            }
        ],
    }
    sheet_resp = client.post("/api/v1/sales/sheets", json=sheet_payload, headers=headers)
    assert sheet_resp.status_code == 200
    sheet_id = sheet_resp.get_json()["sheet"]["id"]

    # 3. Accept quote and trigger disbursement
    accept_resp = client.post(f"/api/v1/sales/sheets/{sheet_id}/accept", headers=headers)
    assert accept_resp.status_code == 200, accept_resp.get_json()
    data = accept_resp.get_json()

    assert data["sheet"]["status"] == "DISBURSED"
    assert "CAVALI-" in data["disbursement"]["annotation_code"]
    assert data["disbursement"]["amount"] > 0
    assert data["disbursement"]["bank_name"] == "BBVA"
    disbursement_id = data["disbursement"]["id"]

    # 4. Fetch disbursement detail
    get_disb_resp = client.get(f"/api/v1/disbursements/{disbursement_id}", headers=headers)
    assert get_disb_resp.status_code == 200
    assert get_disb_resp.get_json()["disbursement"]["sheet_id"] == sheet_id
