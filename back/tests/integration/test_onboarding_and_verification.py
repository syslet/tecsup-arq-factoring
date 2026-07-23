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


def test_onboarding_documents_and_verification_flow(client):
    reg_payload = {
        "email": "onboarding_test@empresa.com",
        "password": "Password123!",
        "full_name": "Juan Perez",
        "dni": "77889900",
        "phone": "999888777",
        "company": {
            "ruc": "20601122334",
            "business_name": "Empresa Test SAC",
            "bank_name": "BCP",
            "bank_account_number": "193-1234567-0-12",
            "cci": "00219300123456701214",
            "currency": "PEN",
        },
    }
    resp = client.post("/api/auth/register", json=reg_payload)
    assert resp.status_code == 201, resp.get_json()
    user_data = resp.get_json()["user"]
    company_id = user_data["company"]["id"]
    assert user_data["verification_status"] in ("PENDING_VERIFICATION", "APPROVED")

    # Login to get JWT token
    login_resp = client.post(
        "/api/auth/login",
        json={"identifier": "onboarding_test@empresa.com", "password": "Password123!"},
    )
    assert login_resp.status_code == 200, login_resp.get_json()
    token = login_resp.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload Document
    doc_payload = {"document_type": "RUC_FICHA", "file_name": "ficha_ruc_test.pdf"}
    doc_resp = client.post("/api/v1/onboarding/documents", json=doc_payload, headers=headers)
    assert doc_resp.status_code == 201, doc_resp.get_json()
    assert doc_resp.get_json()["document"]["company_id"] == company_id

    # Admin endpoint verifying company approval
    verify_resp = client.post(
        f"/api/v1/admin/companies/{company_id}/verify", json={"approve": True}
    )
    assert verify_resp.status_code == 200, verify_resp.get_json()
    assert verify_resp.get_json()["verification_status"] == "APPROVED"

    # GET /api/auth/me shows APPROVED
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200, me_resp.get_json()
    assert me_resp.get_json()["user"]["verification_status"] == "APPROVED"
