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


def test_sales_and_pricing_scenarios(client):
    # 1. Register & verify user + company
    reg_payload = {
        "email": "sales_test@empresa.com",
        "password": "Password123!",
        "full_name": "Maria Lopez",
        "dni": "11223344",
        "company": {
            "ruc": "20100000001",  # Part of GRUPO_ALFA
            "business_name": "Alfa Corp SAC",
            "bank_name": "BCP",
            "bank_account_number": "193-111111-0-12",
            "cci": "00219300111111012141",
            "currency": "PEN",
        },
    }
    resp = client.post("/api/auth/register", json=reg_payload)
    assert resp.status_code == 201
    user_id = resp.get_json()["user"]["id"]
    company_id = resp.get_json()["user"]["company"]["id"]

    # Verify company via admin endpoint
    client.post(f"/api/v1/admin/companies/{company_id}/verify", json={"approve": True})

    # Login to get bearer token
    login_resp = client.post(
        "/api/auth/login",
        json={"identifier": "sales_test@empresa.com", "password": "Password123!"},
    )
    token = login_resp.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    today = date.today()

    # Scenario A: Valid batch -> 200 OK
    valid_payload = {
        "currency": "PEN",
        "invoices": [
            {
                "invoice_number": "F001-000001",
                "debtor_ruc": "20999999999",  # Independent debtor
                "debtor_name": "Empresa Cliente S.A.",
                "amount": 10000.00,
                "issue_date": today.isoformat(),
                "due_date": (today + timedelta(days=30)).isoformat(),
            }
        ],
    }
    sheet_resp = client.post("/api/v1/sales/sheets", json=valid_payload, headers=headers)
    assert sheet_resp.status_code == 200, sheet_resp.get_json()
    sheet_data = sheet_resp.get_json()["sheet"]
    assert sheet_data["total_amount"] == 10000.00
    assert sheet_data["advance_amount"] == 8500.00
    assert sheet_data["net_disbursement"] > 0
    assert sheet_data["invoices"][0]["is_approved"] is True

    # Scenario B: Invoice > 180 days -> 400 Bad Request
    invalid_days_payload = {
        "currency": "PEN",
        "invoices": [
            {
                "invoice_number": "F001-000002",
                "debtor_ruc": "20999999999",
                "debtor_name": "Empresa Cliente S.A.",
                "amount": 5000.00,
                "issue_date": today.isoformat(),
                "due_date": (today + timedelta(days=200)).isoformat(),  # > 180 days
            }
        ],
    }
    invalid_resp = client.post("/api/v1/sales/sheets", json=invalid_days_payload, headers=headers)
    assert invalid_resp.status_code == 400
    assert "excede el plazo máximo de 180 días" in invalid_resp.get_json()["error"]

    # Scenario C: Same economic group (Girador = 20100000001, Aceptante = 20100000002, GRUPO_ALFA) -> Invoice rejected in breakdown
    economic_group_payload = {
        "currency": "PEN",
        "invoices": [
            {
                "invoice_number": "F001-000003",
                "debtor_ruc": "20100000002",  # Same Economic Group GRUPO_ALFA
                "debtor_name": "Alfa Filial S.A.C.",
                "amount": 20000.00,
                "issue_date": today.isoformat(),
                "due_date": (today + timedelta(days=45)).isoformat(),
            }
        ],
    }
    eg_resp = client.post("/api/v1/sales/sheets", json=economic_group_payload, headers=headers)
    assert eg_resp.status_code == 200, eg_resp.get_json()
    eg_sheet = eg_resp.get_json()["sheet"]
    assert eg_sheet["invoices"][0]["is_approved"] is False
    assert (
        "Grupo Económico" in eg_sheet["invoices"][0]["rejection_reason"]
        or "Autofacturación" in eg_sheet["invoices"][0]["rejection_reason"]
    )
