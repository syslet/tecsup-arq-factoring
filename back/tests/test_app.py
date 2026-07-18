import pytest
from flask.testing import FlaskClient

from src.presentation.app import create_app


@pytest.fixture
def client() -> FlaskClient:
    app = create_app()
    app.config.update({"TESTING": True})
    with app.test_client() as client:
        yield client


def test_health_check(client: FlaskClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy", "service": "backend"}
