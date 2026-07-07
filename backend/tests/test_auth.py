import os
import pytest
from fastapi.testclient import TestClient

from backend.app.database.session import Base, SessionLocal, engine
from backend.app.models.user import User
from backend.main import app

client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./sql_app.db"):
        try:
            os.remove("./sql_app.db")
        except PermissionError:
            pass


def test_auth_and_user_endpoints_lifecycle():
    # 1. Register User
    reg_payload = {
        "email": "user@example.com",
        "password": "secretpassword",
        "name": "Alex Smith",
    }
    response = client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "user@example.com"
    assert data["name"] == "Alex Smith"
    assert "id" in data

    # 2. Register Duplicate Email (Asserts 400)
    dup_resp = client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_resp.status_code == 400

    # 3. Login
    login_payload = {"email": "user@example.com", "password": "secretpassword"}
    login_resp = client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data
    assert login_data["user"]["name"] == "Alex Smith"

    # Check HttpOnly Cookie headers exist in response
    cookies = login_resp.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies

    # 4. Get Current Profile
    headers = {"Authorization": f"Bearer {login_data['access_token']}"}
    me_resp = client.get("/api/v1/users/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "user@example.com"

    # 5. Update Profile
    update_payload = {"name": "Alex Updated", "language": "es"}
    up_resp = client.put(
        "/api/v1/users/me", json=update_payload, headers=headers
    )
    assert up_resp.status_code == 200
    assert up_resp.json()["name"] == "Alex Updated"
    assert up_resp.json()["language"] == "es"

    # 6. Logout
    logout_resp = client.post("/api/v1/auth/logout")
    assert logout_resp.status_code == 200


if __name__ == "__main__":
    # Setup test DB
    Base.metadata.create_all(bind=engine)
    try:
        test_auth_and_user_endpoints_lifecycle()
        print("ALL AUTHENTICATION TESTS PASSED SUCCESSFULLY!")
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
