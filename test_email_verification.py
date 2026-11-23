import os
import sys

# Ensure testing mode is active so test suites do not trigger outbound SMTP emails
os.environ["TESTING"] = "true"

import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, store, ServerSelectionTimeoutError
from main import app, verification_codes
from models import User

client = TestClient(app)

def cleanup_test_user(email: str, username: str):
    user = store.find_one(User, {
        "$or": [{"email": email}, {"username": username}]
    })
    if user:
        store.delete(user)
    verification_codes.pop(email.lower(), None)

def test_full_email_verification_lifecycle():
    try:
        init_db()
    except ServerSelectionTimeoutError as exc:
        pytest.skip(f"MongoDB is unavailable for integration testing: {exc}")

    test_email = "testverifier@safebite.io"
    test_username = "testverifier"
    test_password = "SecurePassword123"

    cleanup_test_user(test_email, test_username)

    # 1. Register new user
    reg_resp = client.post("/register", json={
        "name": test_username,
        "email": test_email,
        "password": test_password
    })
    assert reg_resp.status_code == 200, f"Register failed: {reg_resp.text}"
    reg_data = reg_resp.json()
    assert reg_data["status"] == "success"
    assert reg_data["verification_required"] is True
    assert reg_data["is_verified"] is False
    # Verification code MUST NEVER be in response
    assert "verification_code" not in reg_data
    assert "code" not in reg_data

    # 2. Attempt login before verification -> MUST FAIL with 403 email_not_verified
    login_resp = client.post("/login", json={
        "username": test_username,
        "password": test_password
    })
    assert login_resp.status_code == 403, f"Unverified login should be rejected: {login_resp.text}"
    detail = login_resp.json()["detail"]
    assert detail.get("error") == "email_not_verified"

    # Also test login with email instead of username
    login_email_resp = client.post("/login", json={
        "email": test_email,
        "password": test_password
    })
    assert login_email_resp.status_code == 403

    # 3. Retrieve code from in-memory cache / DB for testing verification
    cached = verification_codes.get(test_email)
    assert cached is not None
    real_code = cached["code"]
    assert len(real_code) == 6

    # 4. Attempt verify with wrong code
    wrong_resp = client.post("/verify-email", json={
        "email": test_email,
        "code": "000000" if real_code != "000000" else "111111"
    })
    assert wrong_resp.status_code == 400
    assert "Incorrect verification code" in wrong_resp.json()["detail"]

    # 5. Resend verification immediately -> Should hit cooldown (429)
    cooldown_resp = client.post("/resend-verification", json={
        "email": test_email
    })
    assert cooldown_resp.status_code == 429
    assert "Please wait" in cooldown_resp.json()["detail"]

    # 6. Verify with correct code -> MUST SUCCEED
    verify_resp = client.post("/verify-email", json={
        "email": test_email,
        "code": real_code
    })
    assert verify_resp.status_code == 200, f"Verification failed: {verify_resp.text}"
    verify_data = verify_resp.json()
    assert verify_data["status"] == "success"
    assert verify_data["is_valid"] is True

    # 7. Attempt login after verification -> MUST SUCCEED with 200
    login_success = client.post("/login", json={
        "username": test_username,
        "password": test_password
    })
    assert login_success.status_code == 200, f"Login should succeed: {login_success.text}"
    success_data = login_success.json()
    assert success_data["status"] == "success"
    assert success_data["is_verified"] is True

    # Cleanup
    cleanup_test_user(test_email, test_username)

def test_welcome_email_content_and_preview_endpoints():
    from email_service import get_welcome_email_html, get_welcome_email_text, send_welcome_email

    # 1. Verify HTML template formatting and personalization
    html = get_welcome_email_html(username="Rupal")
    assert "Welcome to SafeBite, Rupal!" in html
    assert "SafeBite" in html
    assert "Gemini Vision" in html
    assert "safebitefoodanalyzer@gmail.com" in html
    assert "Health Score" in html

    # 2. Verify plain text template formatting
    text = get_welcome_email_text(username="Rupal")
    assert "Welcome to SafeBite – AI Food Health Analyzer!" in text
    assert "safebitefoodanalyzer@gmail.com" in text
    assert "3 Easy Steps to Get Started" in text

    # 3. Verify send_welcome_email executes safely with mock/dummy recipient
    success, err = send_welcome_email(to_email="testwelcome@safebite.io", username="Rupal")
    assert success is True
    assert err is None

    # 4. Test GET /welcome-preview endpoint returns HTML
    preview_res = client.get("/welcome-preview?username=Rupal")
    assert preview_res.status_code == 200
    assert "text/html" in preview_res.headers.get("content-type", "")
    assert "Welcome to SafeBite, Rupal!" in preview_res.text

    # 5. Test POST /auth/send-welcome endpoint
    send_res = client.post("/auth/send-welcome", json={
        "email": "testwelcome@safebite.io",
        "username": "Rupal"
    })
    assert send_res.status_code == 200
    assert send_res.json()["status"] == "success"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
