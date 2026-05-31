import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.test_client() as c:
        yield c


def test_metrics_endpoint(client):
    r = client.get("/api/metrics")
    assert r.status_code == 200
    data = r.get_json()
    assert "headcount" in data


def test_jobs_endpoint(client):
    r = client.get("/api/jobs")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)
