import datetime
import pytest
from fastapi.testclient import TestClient
from main import app, create_access_token
from database import get_db, SQLiteStore
from models import User, Subscription
from subscription_service import hash_purchase_token

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    db = next(get_db())
    # Ensure fresh test users
    user1 = db.find_one(User, {"username": "sub_test_user1"})
    if not user1:
        u = User(username="sub_test_user1", email="sub1@test.com", hashed_password="dummy_hash", role="user")
        db.insert(u)
    
    user2 = db.find_one(User, {"username": "sub_test_user2"})
    if not user2:
        u = User(username="sub_test_user2", email="sub2@test.com", hashed_password="dummy_hash", role="user")
        db.insert(u)
    
    yield

def test_verify_subscription_requires_auth():
    response = client.post(
        "/api/subscription/verify",
        json={
            "purchase_token": "test_token_123",
            "product_id": "safebite_premium_monthly",
            "package_name": "com.example.safebite"
        }
    )
    assert response.status_code == 401

def test_verify_and_get_subscription_status_success():
    token = create_access_token("sub_test_user1", "user")
    headers = {"Authorization": f"Bearer {token}"}

    # Verify purchase
    verify_resp = client.post(
        "/api/subscription/verify",
        headers=headers,
        json={
            "purchase_token": "token_user1_valid_abc",
            "product_id": "safebite_premium_monthly",
            "package_name": "com.example.safebite",
            "order_id": "GPA.1234-5678-9012"
        }
    )
    assert verify_resp.status_code == 200
    data = verify_resp.json()
    assert data["is_premium"] is True
    assert data["status"] == "ACTIVE"
    assert data["product_id"] == "safebite_premium_monthly"
    assert data["order_id"] == "GPA.1234-5678-9012"

    # Query status
    status_resp = client.get("/api/subscription/status", headers=headers)
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["is_premium"] is True
    assert status_data["status"] == "ACTIVE"
    assert status_data["order_id"] == "GPA.1234-5678-9012"

def test_anti_fraud_duplicate_token_rejected():
    token1 = create_access_token("sub_test_user1", "user")
    token2 = create_access_token("sub_test_user2", "user")

    shared_token = "unique_fraud_test_token_999"

    # User 1 claims token
    resp1 = client.post(
        "/api/subscription/verify",
        headers={"Authorization": f"Bearer {token1}"},
        json={
            "purchase_token": shared_token,
            "product_id": "safebite_premium_monthly",
            "package_name": "com.example.safebite",
            "order_id": "GPA.USER1-ORDER"
        }
    )
    assert resp1.status_code == 200

    # User 2 attempts to claim the same token
    resp2 = client.post(
        "/api/subscription/verify",
        headers={"Authorization": f"Bearer {token2}"},
        json={
            "purchase_token": shared_token,
            "product_id": "safebite_premium_monthly",
            "package_name": "com.example.safebite",
            "order_id": "GPA.FRAUDULENT-ATTEMPT"
        }
    )
    assert resp2.status_code == 409
    assert "already associated" in resp2.json()["detail"]

def test_verify_subscription_invalid_package():
    token = create_access_token("sub_test_user1", "user")
    response = client.post(
        "/api/subscription/verify",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "purchase_token": "some_token",
            "product_id": "safebite_premium_monthly",
            "package_name": "com.hacker.fakeapp"
        }
    )
    assert response.status_code == 400
    assert "INVALID_PACKAGE" in response.json()["detail"]
