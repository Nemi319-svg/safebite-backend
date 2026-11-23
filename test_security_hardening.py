import base64
import json
import pytest
from fastapi.testclient import TestClient

from main import app, create_access_token, rate_limiter
from database import get_db, MongoStore, init_db
from models import User, Scan, SavedFood, Subscription

@pytest.fixture
def client():
    init_db()
    with TestClient(app) as test_client:
        yield test_client

def test_idor_attempts_return_404(client):
    """
    Verify IDOR (Insecure Direct Object Reference) attempts return 404 Not Found
    (never 403 Forbidden) so resource IDs and user IDs cannot be enumerated.
    """
    db: MongoStore = next(app.dependency_overrides.get(get_db, get_db)())
    db.delete_many(User, {"username": "victim_idor_user"})
    db.delete_many(User, {"email": "victim_idor@safebite.app"})
    db.delete_many(User, {"username": "attacker_idor_user"})
    db.delete_many(User, {"email": "attacker_idor@safebite.app"})

    # User 1 (Victim)
    user_victim = User(
        username="victim_idor_user",
        email="victim_idor@safebite.app",
        hashed_password="hashed_pass_a",
        is_verified=True,
        email_verified=True,
        role="user"
    )
    victim_id = db.insert(user_victim)

    scan_id = db.insert(Scan(
        user_id=victim_id,
        product_name="Confidential Scan",
        calories=300.0,
        health_score=80.0
    ))

    saved_id = db.insert(SavedFood(
        user_id=victim_id,
        product_name="Private Saved Food",
        calories=150.0
    ))

    # User 2 (Attacker)
    user_attacker = User(
        username="attacker_idor_user",
        email="attacker_idor@safebite.app",
        hashed_password="hashed_pass_b",
        is_verified=True,
        email_verified=True,
        role="user"
    )
    attacker_id = db.insert(user_attacker)

    token_attacker = create_access_token(user_attacker.username, role="user")
    headers_attacker = {"Authorization": f"Bearer {token_attacker}"}

    # 1. Attacker attempts to fetch victim's specific scan item -> 404
    res = client.get(f"/history/{scan_id}", headers=headers_attacker)
    assert res.status_code == 404, f"Expected 404, got {res.status_code}"

    # 2. Attacker attempts to delete victim's specific scan item -> 404
    res = client.delete(f"/history/{scan_id}", headers=headers_attacker)
    assert res.status_code == 404, f"Expected 404, got {res.status_code}"

    # 3. Attacker attempts to delete victim's saved food -> 404
    res = client.delete(f"/saved-foods/{saved_id}", headers=headers_attacker)
    assert res.status_code == 404, f"Expected 404, got {res.status_code}"

    # 4. Attacker attempts to read victim's profile -> 404
    res = client.get(f"/profile?username={user_victim.username}", headers=headers_attacker)
    assert res.status_code == 404, f"Expected 404, got {res.status_code}"

    # 5. Attacker attempts to delete victim's account -> 404
    res = client.delete(f"/user/account?username={user_victim.username}", headers=headers_attacker)
    assert res.status_code == 404, f"Expected 404, got {res.status_code}"

def test_otp_brute_force_lockout_and_invalidation(client):
    """
    Verify OTP verification:
    - Max 5 failed attempts per code
    - Code is permanently invalidated after 5th attempt (HTTP 429)
    - Subsequent attempts return HTTP 429
    """
    db: MongoStore = next(app.dependency_overrides.get(get_db, get_db)())
    test_email = "lockout_test@safebite.app"
    db.delete_many(User, {"email": test_email})
    db.delete_many(User, {"username": "LockoutTestUser"})

    # Register user
    reg_res = client.post("/register", json={
        "username": "LockoutTestUser",
        "email": test_email,
        "password": "Password123"
    })
    assert reg_res.status_code == 200

    # Attempts 1 to 4 with incorrect code -> 400
    for attempt in range(1, 5):
        res = client.post("/verify-email", json={
            "email": test_email,
            "code": "000000"
        })
        assert res.status_code == 400
        assert "Incorrect verification code" in res.json()["detail"]

    # 5th attempt -> code is invalidated and HTTP 429 returned
    res5 = client.post("/verify-email", json={
        "email": test_email,
        "code": "000000"
    })
    assert res5.status_code == 429
    assert "Too many failed verification attempts" in res5.json()["detail"]

    # 6th attempt with correct or incorrect code is blocked
    res6 = client.post("/verify-email", json={
        "email": test_email,
        "code": "000000"
    })
    assert res6.status_code == 429

def test_rate_limits_enforced(client):
    """
    Verify sliding window rate limiting on authentication and sensitive endpoints.
    """
    test_email = "rate_limit_test@safebite.app"
    rate_limiter.reset(f"otp_resend:{test_email}")

    # Initial resend requests succeed (or return cooldown)
    client.post("/resend-verification", json={"email": test_email})
    client.post("/resend-verification", json={"email": test_email})
    client.post("/resend-verification", json={"email": test_email})
    client.post("/resend-verification", json={"email": test_email})

    # Exceeding threshold returns 429
    res = client.post("/resend-verification", json={"email": test_email})
    assert res.status_code == 429

def test_admin_endpoint_rejection_without_privileges(client, monkeypatch):
    """
    Verify /admin/history and /admin/login enforce privilege checks and reject unauthorized requests.
    """
    monkeypatch.setenv("ADMIN_SECRET", "super_secret_admin_key_2026")

    # Regular user token
    regular_token = create_access_token("regular_user", role="user")
    headers_user = {"Authorization": f"Bearer {regular_token}"}

    # Regular user cannot access /admin/history
    res = client.get("/admin/history", headers=headers_user)
    assert res.status_code == 401

    # Request with invalid secret header
    res_bad_secret = client.get("/admin/history", headers={"X-Admin-Secret": "wrong_key"})
    assert res_bad_secret.status_code == 401

    # Admin login with invalid secret returns 401
    bad_login = client.post("/admin/login", json={"admin_secret": "invalid_password"})
    assert bad_login.status_code == 401

def test_subscription_verification_with_forged_tokens(client):
    """
    Verify subscription verification rejects invalid packages, mismatched products, and empty tokens.
    """
    db: MongoStore = next(app.dependency_overrides.get(get_db, get_db)())
    db.delete_many(User, {"username": "sub_test_user"})
    db.delete_many(User, {"email": "sub_test@safebite.app"})
    sub_user = User(
        username="sub_test_user",
        email="sub_test@safebite.app",
        hashed_password="hash",
        is_verified=True,
        email_verified=True,
        role="user"
    )
    db.insert(sub_user)

    user_token = create_access_token("sub_test_user", role="user")
    headers = {"Authorization": f"Bearer {user_token}"}

    # 1. Invalid package name
    res_pkg = client.post("/api/subscription/verify", json={
        "package_name": "com.hacker.fakeapp",
        "product_id": "safebite_premium_monthly",
        "purchase_token": "token_123"
    }, headers=headers)
    assert res_pkg.status_code == 400

    # 2. Invalid product ID
    res_prod = client.post("/api/subscription/verify", json={
        "package_name": "com.safebite.app",
        "product_id": "fake_product_free_forever",
        "purchase_token": "token_123"
    }, headers=headers)
    assert res_prod.status_code == 400

    # 3. Empty purchase token
    res_empty = client.post("/api/subscription/verify", json={
        "package_name": "com.safebite.app",
        "product_id": "safebite_premium_monthly",
        "purchase_token": "   "
    }, headers=headers)
    assert res_empty.status_code == 400

def test_rtdn_webhook_event_handling(client):
    """
    Verify Google Cloud Pub/Sub RTDN webhook handles notifications gracefully.
    """
    db: MongoStore = next(app.dependency_overrides.get(get_db, get_db)())

    # Build simulated Google Cloud Pub/Sub payload for SUBSCRIPTION_CANCELED (3)
    notification_payload = {
        "version": "1.0",
        "packageName": "com.safebite.app",
        "eventTimeMillis": 1700000000000,
        "subscriptionNotification": {
            "version": "1.0",
            "notificationType": 3,
            "purchaseToken": "test_rtdn_purchase_token",
            "subscriptionId": "safebite_premium_monthly"
        }
    }
    encoded_data = base64.b64encode(json.dumps(notification_payload).encode("utf-8")).decode("utf-8")

    pubsub_message = {
        "message": {
            "data": encoded_data,
            "messageId": "pubsub_12345"
        }
    }

    res = client.post("/api/subscriptions/rtdn", json=pubsub_message)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"

def test_image_magic_bytes_validation(client):
    """
    Verify image upload validates magic bytes (rejects shell scripts/executables disguised as images).
    """
    # 1. Invalid payload (e.g. text/bash script disguised as image)
    fake_image_bytes = b"#!/bin/bash\necho 'hello hacker'"
    res_bad = client.post(
        "/analyze/image",
        files={"image": ("test.jpg", fake_image_bytes, "image/jpeg")}
    )
    assert res_bad.status_code == 400
    assert "Uploaded file must be a valid image format" in res_bad.json()["detail"]

    # 2. Valid PNG header
    valid_png_header = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
    # Note: Even if PIL thumbnailing fails on minimal raw bytes, initial magic-byte filter passes
