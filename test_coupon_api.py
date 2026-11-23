import datetime
import threading
import pytest
from fastapi.testclient import TestClient
from main import app, create_access_token
from database import get_db
from models import User, Subscription, Coupon, CouponRedemption
from coupon_service import reset_rate_limits

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_data():
    reset_rate_limits()
    db = next(get_db())

    # Ensure test users
    for i in range(1, 6):
        uname = f"coupon_user_{i}"
        user = db.find_one(User, {"username": uname})
        if not user:
            u = User(
                username=uname,
                email=f"coupon_{i}@test.com",
                hashed_password="dummy_hash",
                role="user",
                is_verified=True,
                email_verified=True
            )
            db.insert(u)
        else:
            user.is_verified = True
            user.email_verified = True
            db.update(user)

    # Guest user
    guest_user = db.find_one(User, {"username": "guest_coupon_user"})
    if not guest_user:
        g = User(
            username="guest_coupon_user",
            email="guest@safebite.local",
            hashed_password="dummy_hash",
            role="guest",
            is_verified=False
        )
        db.insert(g)

    # Clean existing redemptions for test users
    for i in range(1, 6):
        u = db.find_one(User, {"username": f"coupon_user_{i}"})
        if u:
            db.delete_many(CouponRedemption, {"user_id": u.id})
            db.delete_many(Subscription, {"user_id": u.id})

    # Ensure seeded test coupons
    now = datetime.datetime.utcnow()
    # Test active coupon
    c_active = db.find_one(Coupon, {"code": "TEST_ACTIVE_30"})
    if not c_active:
        db.insert(Coupon(code="TEST_ACTIVE_30", days_free=30, active=True, redeemed_count=0))

    # Test inactive coupon
    c_inactive = db.find_one(Coupon, {"code": "TEST_INACTIVE"})
    if not c_inactive:
        db.insert(Coupon(code="TEST_INACTIVE", days_free=30, active=False, redeemed_count=0))

    # Test expired coupon
    c_expired = db.find_one(Coupon, {"code": "TEST_EXPIRED"})
    if not c_expired:
        db.insert(Coupon(
            code="TEST_EXPIRED",
            days_free=30,
            active=True,
            expires_at=now - datetime.timedelta(days=1),
            redeemed_count=0
        ))

    # Test limit reached coupon
    c_limited = db.find_one(Coupon, {"code": "TEST_LIMIT_REACHED"})
    if not c_limited:
        db.insert(Coupon(
            code="TEST_LIMIT_REACHED",
            days_free=30,
            max_redemptions=2,
            active=True,
            redeemed_count=2
        ))

    yield


def test_redeem_requires_auth():
    resp = client.post("/api/coupons/redeem", json={"code": "NEMI100"})
    assert resp.status_code == 401


def test_redeem_guest_user_rejected():
    token = create_access_token("guest_coupon_user", "guest")
    resp = client.post(
        "/api/coupons/redeem",
        headers={"Authorization": f"Bearer {token}"},
        json={"code": "NEMI100"}
    )
    assert resp.status_code == 403
    data = resp.json()
    assert data["errorCode"] == "NOT_AUTHENTICATED"


def test_redeem_valid_coupon_success_and_case_insensitive():
    token = create_access_token("coupon_user_1", "user")
    headers = {"Authorization": f"Bearer {token}"}

    # Test lowercase and leading/trailing whitespace
    resp = client.post(
        "/api/coupons/redeem",
        headers=headers,
        json={"code": "  nemi100  "}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "premiumUntil" in data
    assert "30 days" in data["message"]

    # Verify Subscription status API reflects coupon entitlement
    status_resp = client.get("/api/subscription/status", headers=headers)
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["is_premium"] is True
    assert status_data["source"] == "coupon"
    assert status_data["status"] == "ACTIVE"
    assert status_data["premium_until"] is not None


def test_redeem_invalid_code():
    token = create_access_token("coupon_user_2", "user")
    resp = client.post(
        "/api/coupons/redeem",
        headers={"Authorization": f"Bearer {token}"},
        json={"code": "NON_EXISTENT_CODE_XYZ"}
    )
    assert resp.status_code == 400
    data = resp.json()
    assert data["errorCode"] == "INVALID_CODE"


def test_redeem_inactive_code():
    token = create_access_token("coupon_user_2", "user")
    resp = client.post(
        "/api/coupons/redeem",
        headers={"Authorization": f"Bearer {token}"},
        json={"code": "TEST_INACTIVE"}
    )
    assert resp.status_code == 400
    data = resp.json()
    assert data["errorCode"] == "INVALID_CODE"


def test_redeem_expired_code():
    token = create_access_token("coupon_user_2", "user")
    resp = client.post(
        "/api/coupons/redeem",
        headers={"Authorization": f"Bearer {token}"},
        json={"code": "TEST_EXPIRED"}
    )
    assert resp.status_code == 400
    data = resp.json()
    assert data["errorCode"] == "EXPIRED"


def test_redeem_limit_reached():
    token = create_access_token("coupon_user_2", "user")
    resp = client.post(
        "/api/coupons/redeem",
        headers={"Authorization": f"Bearer {token}"},
        json={"code": "TEST_LIMIT_REACHED"}
    )
    assert resp.status_code == 400
    data = resp.json()
    assert data["errorCode"] == "LIMIT_REACHED"


def test_duplicate_redemption_by_same_user_rejected():
    token = create_access_token("coupon_user_3", "user")
    headers = {"Authorization": f"Bearer {token}"}

    # First redemption succeeds
    resp1 = client.post(
        "/api/coupons/redeem",
        headers=headers,
        json={"code": "NEMI100"}
    )
    assert resp1.status_code == 200

    # Second redemption attempt (even with different code) is rejected!
    resp2 = client.post(
        "/api/coupons/redeem",
        headers=headers,
        json={"code": "GUDDU100"}
    )
    assert resp2.status_code == 409
    data = resp2.json()
    assert data["errorCode"] == "ALREADY_REDEEMED"


def test_dual_entitlement_uses_later_expiry():
    db = next(get_db())
    u = db.find_one(User, {"username": "coupon_user_4"})
    token = create_access_token("coupon_user_4", "user")
    headers = {"Authorization": f"Bearer {token}"}

    # Give user a Google Play subscription expiring in 60 days
    now = datetime.datetime.utcnow()
    play_expiry = now + datetime.timedelta(days=60)
    db.insert(Subscription(
        user_id=u.id,
        product_id="safebite_premium_monthly",
        purchase_token_hash="fake_play_token_hash_dual",
        order_id="GPA.DUAL-TEST-1234",
        status="ACTIVE",
        start_time=now,
        expiry_time=play_expiry,
        auto_renewing=True
    ))

    # Redeem coupon (adds 30 days to base, resulting in ~90 days)
    resp = client.post(
        "/api/coupons/redeem",
        headers=headers,
        json={"code": "GUDDU100"}
    )
    assert resp.status_code == 200

    status_resp = client.get("/api/subscription/status", headers=headers)
    assert status_resp.status_code == 200
    data = status_resp.json()
    assert data["is_premium"] is True
    # Precedence keeps Play info while extending expiry
    assert data["source"] == "play"
    returned_expiry = datetime.datetime.fromisoformat(data["expiry_time"])
    assert returned_expiry >= play_expiry


def test_rate_limiting_max_5_attempts_per_hour():
    token = create_access_token("coupon_user_5", "user")
    headers = {"Authorization": f"Bearer {token}"}

    # 5 failed attempts
    for _ in range(5):
        r = client.post("/api/coupons/redeem", headers=headers, json={"code": "BAD_CODE"})
        assert r.status_code == 400

    # 6th attempt hits rate limit
    r6 = client.post("/api/coupons/redeem", headers=headers, json={"code": "BAD_CODE"})
    assert r6.status_code == 429
    data = r6.json()
    assert data["errorCode"] == "LIMIT_REACHED"


def test_concurrent_redemptions_safety():
    token = create_access_token("coupon_user_2", "user")
    headers = {"Authorization": f"Bearer {token}"}

    results = []

    def attempt_redeem(code_str):
        r = client.post(
            "/api/coupons/redeem",
            headers=headers,
            json={"code": code_str}
        )
        results.append(r.status_code)

    threads = [
        threading.Thread(target=attempt_redeem, args=("NEMI100",)),
        threading.Thread(target=attempt_redeem, args=("GUDDU100",)),
        threading.Thread(target=attempt_redeem, args=("TEST_ACTIVE_30",))
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Exactly ONE thread can get 200, others must get 409
    successes = [code for code in results if code == 200]
    conflicts = [code for code in results if code == 409]
    assert len(successes) == 1, f"Expected 1 success, got {results}"
    assert len(conflicts) == 2, f"Expected 2 conflicts, got {results}"
