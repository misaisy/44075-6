import pytest
from fastapi.testclient import TestClient
from io import StringIO
from app.main import app
from app.database.session import get_db


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_upload_csv_success(client):
    csv_data = """company_name,region,industry,возбуждено производство по делу о несостоятельности (банкротстве)
Test 1,Region A,IT,Да
Test 2,Region B,Manufacturing,Нет"""

    response = client.post(
        "/api/upload-csv/",
        files={"file": ("test.csv", StringIO(csv_data))}
    )

    assert response.status_code == 201
    assert "Successfully uploaded 2 records" in response.json()["message"]


def test_upload_csv_invalid_file_type(client):
    response = client.post(
        "/api/upload-csv/",
        files={"file": ("test.txt", StringIO("invalid data"))}
    )
    assert response.status_code == 400