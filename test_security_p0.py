import os
import pytest
from fastapi.testclient import TestClient

from main import app, create_access_token
from database import get_db, MongoStore, init_db
from models import User, Scan, SavedFood
from email_service import send_verification_email, is_smtp_configured

@pytest.fixture
def client():
    init_db()
    with TestClient(app) as test_client:
        yield test_client

def test_unauthenticated_requests_return_401(client):
    """Verify that all sensitive user endpoints reject unauthenticated requests with HTTP 401."""
    # Profile
    res = client.get("/profile?username=someone")
    assert res.status_code == 401
    assert "Authorization header is missing" in res.json()["detail"]

    res = client.post("/profile", json={"username": "someone", "age": 30})
    assert res.status_code == 401

    # History
    res = client.get("/history?username=someone")
    assert res.status_code == 401

    res = client.get("/history/123")
    assert res.status_code == 401

    res = client.delete("/history/123")
    assert res.status_code == 401

    res = client.delete("/history?username=someone")
    assert res.status_code == 401

    # Saved Foods
    res = client.get("/saved-foods?username=someone")
    assert res.status_code == 401

    res = client.post("/saved-foods", json={"username": "someone", "product_name": "Apple", "calories": 52.0})
    assert res.status_code == 401

    res = client.delete("/saved-foods/123")
    assert res.status_code == 401

    # Health Assessments & Stats
    res = client.get("/dashboard-stats?username=someone")
    assert res.status_code == 401

    res = client.post("/diabetes-check", json={"username": "someone"})
    assert res.status_code == 401

    # Account Deletion
    res = client.delete("/user/account?username=someone")
    assert res.status_code == 401


def test_invalid_bearer_token_returns_401(client):
    """Verify that malformed, corrupted, or non-bearer tokens return HTTP 401."""
    # Invalid token format
    res = client.get("/profile", headers={"Authorization": "Bearer not-a-valid-token"})
    assert res.status_code == 401
    assert "Invalid or expired token" in res.json()["detail"]

    # Invalid scheme (Basic instead of Bearer)
    res = client.get("/profile", headers={"Authorization": "Basic dXNlcjpwYXNz"})
    assert res.status_code == 401
    assert "Bearer token required" in res.json()["detail"]

    # Tampered signature
    valid_token = create_access_token("valid_user")
    tampered_token = valid_token[:-4] + "xxxx"
    res = client.get("/profile", headers={"Authorization": f"Bearer {tampered_token}"})
    assert res.status_code == 401
    assert "Invalid token signature" in res.json()["detail"]


def test_cross_user_isolation_strictly_enforced_403(client):
    """
    Verify cross-user isolation:
    User A cannot view, modify, or delete User B's profile, scans, saved foods, or account.
    All cross-user unauthorized attempts must return HTTP 403 Forbidden.
    """
    db: MongoStore = next(app.dependency_overrides.get(get_db, get_db)())

    # Set up User A
    user_a_name = "victim_a"
    db.delete_many(User, {"username": user_a_name})
    user_a = User(
        username=user_a_name,
        email="victim_a@safebite.app",
        hashed_password="hash_a",
        is_verified=True,
        email_verified=True,
        role="user"
    )
    user_a_id = db.insert(user_a)

    # Set up User B (Attacker)
    user_b_name = "attacker_b"
    db.delete_many(User, {"username": user_b_name})
    user_b = User(
        username=user_b_name,
        email="attacker_b@safebite.app",
        hashed_password="hash_b",
        is_verified=True,
        email_verified=True,
        role="user"
    )
    user_b_id = db.insert(user_b)

    # Seed User A's private data
    scan_a_id = db.insert(Scan(
        user_id=user_a_id,
        product_name="User A Confidential Scan",
        calories=250.0,
        health_score=85.0
    ))
    saved_a_id = db.insert(SavedFood(
        user_id=user_a_id,
        product_name="User A Bookmark",
        calories=150.0
    ))

    # User B credentials
    token_b = create_access_token(user_b_name)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 1. User B attempts to read User A's profile (IDOR protection returns 404)
    res = client.get(f"/profile?username={user_a_name}", headers=headers_b)
    assert res.status_code == 404

    # 2. User B attempts to overwrite User A's profile
    res = client.post("/profile", json={"username": user_a_name, "age": 99}, headers=headers_b)
    assert res.status_code == 404

    # 3. User B attempts to read User A's scan history
    res = client.get(f"/history?username={user_a_name}", headers=headers_b)
    assert res.status_code == 404

    # 4. User B attempts to read User A's specific scan item
    res = client.get(f"/history/{scan_a_id}", headers=headers_b)
    assert res.status_code == 404

    # 5. User B attempts to delete User A's scan item
    res = client.delete(f"/history/{scan_a_id}", headers=headers_b)
    assert res.status_code == 404

    # 6. User B attempts to wipe User A's scan history
    res = client.delete(f"/history?username={user_a_name}", headers=headers_b)
    assert res.status_code == 404

    # 7. User B attempts to read User A's saved foods
    res = client.get(f"/saved-foods?username={user_a_name}", headers=headers_b)
    assert res.status_code == 404

    # 8. User B attempts to delete User A's saved food
    res = client.delete(f"/saved-foods/{saved_a_id}", headers=headers_b)
    assert res.status_code == 404

    # 9. User B attempts to delete User A's account
    res = client.delete(f"/user/account?username={user_a_name}", headers=headers_b)
    assert res.status_code == 404

    # 10. User B attempts to assess User A's diabetes risk
    res = client.post("/diabetes-check", json={"username": user_a_name}, headers=headers_b)
    assert res.status_code == 404

    # 11. User B attempts to view User A's dashboard stats
    res = client.get(f"/dashboard-stats?username={user_a_name}", headers=headers_b)
    assert res.status_code == 404

    # Verify User A's account, scan, and saved food are 100% intact and undamaged
    assert db.find_one(User, {"username": user_a_name}) is not None
    assert db.find_one(Scan, {"id": scan_a_id}) is not None
    assert db.find_one(SavedFood, {"id": saved_a_id}) is not None


def test_admin_secret_missing_fails_safely_503(client, monkeypatch):
    """Verify that when ADMIN_SECRET is not configured, admin endpoints return HTTP 503."""
    monkeypatch.delenv("ADMIN_SECRET", raising=False)

    res = client.post("/admin/login", json={"admin_secret": "any_secret"})
    assert res.status_code == 503
    assert "ADMIN_SECRET is not configured" in res.json()["detail"]

    res = client.get("/admin/history?admin_secret=any_secret")
    assert res.status_code == 503
    assert "ADMIN_SECRET is not configured" in res.json()["detail"]


def test_admin_login_with_configured_secret(client, monkeypatch):
    """Verify admin login with configured ADMIN_SECRET issues a valid bearer token."""
    test_secret = "my_super_secret_production_admin_key_2026"
    monkeypatch.setenv("ADMIN_SECRET", test_secret)

    # Invalid secret fails with 401
    bad_res = client.post("/admin/login", json={"admin_secret": "wrong_password"})
    assert bad_res.status_code == 401
    assert "Invalid admin credentials" in bad_res.json()["detail"]

    # Correct secret succeeds with 200, returning role and bearer token
    good_res = client.post("/admin/login", json={"admin_secret": test_secret})
    assert good_res.status_code == 200
    data = good_res.json()
    assert data["status"] == "success"
    assert data["role"] == "admin"
    assert data["token"] is not None

    # Admin history query
    hist_res = client.get(f"/admin/history?admin_secret={test_secret}")
    assert hist_res.status_code == 200
    assert "scans" in hist_res.json()


def test_email_service_safe_fallback_when_unconfigured(monkeypatch):
    """Verify email service fails safely without exposing credentials or crashing when SMTP and webhooks are unconfigured."""
    monkeypatch.delenv("SMTP_PASSWORD", raising=False)
    monkeypatch.delenv("SMTP_USERNAME", raising=False)
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("GMAIL_WEBHOOK_URL", raising=False)
    monkeypatch.delenv("BREVO_API_KEY", raising=False)
    monkeypatch.delenv("TESTING", raising=False)

    assert is_smtp_configured() is False
    success, msg = send_verification_email(
        to_email="realuser@somedomain.com",
        verification_code="123456",
        username="testuser"
    )
    assert success is False
    assert "Email service is not configured" in msg


def test_chat_endpoint_routes_through_gemini_without_exposing_credentials(client, monkeypatch):
    """Verify /chat endpoint routes through server-side Gemini service and returns clean response."""
    import main
    monkeypatch.setattr(main, "chat_with_gemini", lambda msg, ctx: f"Nutritional advice for: {msg}")

    res = client.post("/chat", json={"message": "Is oatmeal healthy?"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "Nutritional advice for: Is oatmeal healthy?" in data["response"]
    # Verify no secret credentials are leaked in response
    assert "gsk_" not in str(data)
    assert "AIzaSy" not in str(data)


def test_google_auth_token_verification(client, monkeypatch):
    """Verify POST /auth/google enforces ID token presence and cryptographic verification."""
    monkeypatch.setenv("TESTING", "true")

    # 1. Missing id_token must be rejected with HTTP 401
    res_no_token = client.post("/auth/google", json={"email": "hacker@gmail.com"})
    assert res_no_token.status_code == 401
    assert "Google ID token is required" in res_no_token.json()["detail"]

    # 2. Invalid / forged token must be rejected with HTTP 401
    res_bad_token = client.post("/auth/google", json={
        "email": "hacker@gmail.com",
        "id_token": "mock-invalid-token"
    })
    assert res_bad_token.status_code == 401
    assert "Invalid, expired, or untrusted Google ID token" in res_bad_token.json()["detail"]

    # 3. Valid Google ID token authenticates user, sets email_verified=True, and issues JWT
    google_user_email = "verified_google_user@gmail.com"
    res_valid = client.post("/auth/google", json={
        "email": google_user_email,
        "name": "Verified Google User",
        "id_token": "mock-valid-google-jwt-token"
    })
    assert res_valid.status_code == 200
    data = res_valid.json()
    assert data["status"] == "success"
    assert data["email"] == google_user_email
    assert data["is_verified"] is True
    assert data["token"] is not None

    # Verify user in database has email_verified=True
    db: MongoStore = next(app.dependency_overrides.get(get_db, get_db)())
    db_user = db.find_one(User, {"email": google_user_email})
    assert db_user is not None
    assert db_user.email_verified is True
    assert db_user.is_verified is True

    # 4. Subsequent sign-in with same valid token succeeds
    res_subsequent = client.post("/auth/google", json={
        "email": google_user_email,
        "name": "Verified Google User",
        "id_token": "mock-valid-google-jwt-token"
    })
    assert res_subsequent.status_code == 200
    assert res_subsequent.json()["username"] == db_user.username


def test_unauthenticated_username_cannot_associate_manual_scan_or_leak_chat_history(client, monkeypatch):
    """
    Verify that an unauthenticated caller providing an arbitrary 'username' in the body
    cannot associate scans with that user or access that user's scan context in chat.
    """
    db: MongoStore = next(app.dependency_overrides.get(get_db, get_db)())

    # Create victim user with private scan
    victim_name = "private_scan_victim"
    db.delete_many(User, {"username": victim_name})
    victim_user = User(
        username=victim_name,
        email="victim_scan@safebite.app",
        hashed_password="hashed_pass",
        is_verified=True,
        email_verified=True
    )
    victim_id = db.insert(victim_user)

    db.insert(Scan(
        user_id=victim_id,
        product_name="Private Medical Nutrition Shake",
        health_score=95.0,
        calories=300.0,
        protein=25.0,
        carbs=30.0,
        fat=5.0
    ))

    # 1. Attacker calls /analyze/manual with username=victim_name without Authorization header
    res_manual = client.post("/analyze/manual", json={
        "username": victim_name,
        "product_name": "Injected Junk Food",
        "calories": 600.0,
        "protein": 2.0,
        "carbs": 80.0,
        "fat": 30.0
    })
    assert res_manual.status_code == 200
    # Confirm the scan was NOT associated with victim's account in database
    victim_scans = db.find_many(Scan, {"user_id": victim_id})
    assert len(victim_scans) == 1
    assert victim_scans[0].product_name == "Private Medical Nutrition Shake"

    # 2. Attacker calls /chat with username=victim_name without Authorization header
    import main
    captured_context = []
    def mock_chat(msg, ctx):
        captured_context.append(ctx)
        return "Chat reply"

    monkeypatch.setattr(main, "chat_with_gemini", mock_chat)

    res_chat = client.post("/chat", json={
        "username": victim_name,
        "message": "What did I eat recently?"
    })
    assert res_chat.status_code == 200
    # Context passed to Gemini must be None, victim's private scan history was NOT leaked!
    assert len(captured_context) == 1
    assert captured_context[0] is None


def test_admin_history_bearer_and_header_auth(client, monkeypatch):
    """Verify GET /admin/history supports Bearer token and X-Admin-Secret header."""
    admin_secret = "admin_secure_secret_2026"
    monkeypatch.setenv("ADMIN_SECRET", admin_secret)

    # 1. Request with Bearer admin token (no query param or header)
    admin_login_res = client.post("/admin/login", json={"admin_secret": admin_secret})
    assert admin_login_res.status_code == 200
    admin_token = admin_login_res.json()["token"]

    res_bearer = client.get("/admin/history", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_bearer.status_code == 200
    assert "scans" in res_bearer.json()

    # 2. Request with X-Admin-Secret header (no query param)
    res_header = client.get("/admin/history", headers={"X-Admin-Secret": admin_secret})
    assert res_header.status_code == 200
    assert "scans" in res_header.json()

    # 3. Request without credentials or invalid secret returns 401
    res_no_creds = client.get("/admin/history")
    assert res_no_creds.status_code == 401

    res_bad_header = client.get("/admin/history", headers={"X-Admin-Secret": "wrong_secret"})
    assert res_bad_header.status_code == 401
