import datetime
import uuid
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath("backend"))

from main import app, create_access_token
from database import store, init_db
from models import (
    User, Subscription, ReferralRecord, UserSyncBackup,
    FeedbackItem, ProductSubmission, ProductReport, Scan, SavedFood
)

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def create_fresh_user(prefix: str, role: str = "user", referral_code: str = None) -> User:
    unique_name = f"{prefix}_{uuid.uuid4().hex[:6]}"
    user = User(
        username=unique_name,
        hashed_password="hashed_test_password",
        email=f"{unique_name}@example.com",
        is_verified=True,
        email_verified=True,
        role=role,
        referral_code=referral_code
    )
    store.insert(user)
    return store.find_one(User, {"username": unique_name})

def test_referral_flow_and_limits():
    code = f"SB{uuid.uuid4().hex[:6].upper()}"
    referrer = create_fresh_user("ref_user_a", referral_code=code)
    referee = create_fresh_user("ref_user_b")

    token_a = create_access_token(referrer.username, "user")
    token_b = create_access_token(referee.username, "user")

    # Test get my referral code
    resp = client.get("/api/referrals/my-code", headers={"Authorization": f"Bearer {token_a}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["referral_code"] == code
    assert f"https://safebite.app/ref/{code}" in data["referral_link"]
    assert data["max_referrals"] == 20

    # Self-referral rejected
    resp_self = client.post(
        "/api/referrals/apply",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"referral_code": code}
    )
    assert resp_self.status_code == 400

    # Apply referral by referee
    resp_apply = client.post(
        "/api/referrals/apply",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"referral_code": code}
    )
    assert resp_apply.status_code == 200
    res_data = resp_apply.json()
    assert res_data["status"] == "success"
    assert res_data["days_granted"] == 7

    # Verify both got subscription
    sub_referee = store.find_one(Subscription, {"user_id": referee.id})
    assert sub_referee is not None
    assert sub_referee.status == "ACTIVE"

    sub_referrer = store.find_one(Subscription, {"user_id": referrer.id})
    assert sub_referrer is not None
    assert sub_referrer.status == "ACTIVE"

    # Duplicate referral by same referee rejected
    resp_dup = client.post(
        "/api/referrals/apply",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"referral_code": code}
    )
    assert resp_dup.status_code == 409


def test_cloud_sync_backup_and_restore():
    user = create_fresh_user("sync_user")
    token = create_access_token(user.username, "user")

    sample_history = [{"product_name": "Oats", "calories": 389.0}]
    sample_saved = [{"product_name": "Almonds", "protein": 21.0}]
    sample_profiles = [{"profile_name": "Dad", "allergens": "peanut"}]
    sample_settings = {"theme": "dark", "daily_calories": 2100}

    # Backup
    backup_resp = client.post(
        "/api/sync/backup",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "history": sample_history,
            "saved_foods": sample_saved,
            "profiles": sample_profiles,
            "settings": sample_settings,
            "device_id": "test_pixel_8"
        }
    )
    assert backup_resp.status_code == 200
    b_data = backup_resp.json()
    assert b_data["status"] == "success"
    assert b_data["history_count"] == 1
    assert b_data["saved_foods_count"] == 1

    # Restore
    restore_resp = client.get("/api/sync/restore", headers={"Authorization": f"Bearer {token}"})
    assert restore_resp.status_code == 200
    r_data = restore_resp.json()
    assert r_data["status"] == "success"
    assert len(r_data["history"]) == 1
    assert r_data["history"][0]["product_name"] == "Oats"
    assert r_data["settings"]["theme"] == "dark"


def test_help_and_feedback():
    resp = client.post(
        "/api/feedback",
        json={
            "feedback_type": "bug_report",
            "message": "OCR missed calcium value on label",
            "rating": 4,
            "app_version": "2.4.0",
            "os_version": "Android 14",
            "device_model": "Pixel 7"
        }
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"


def test_shared_product_database_sanity_checks_and_auto_approve():
    test_barcode = f"890{uuid.uuid4().int % 1000000000:09d}"

    # 1. Macro sum > 100g fails
    resp_fail_macro = client.post(
        "/api/products/submit-label",
        json={
            "barcode": test_barcode,
            "product_name": "Invalid Snack",
            "protein": 50.0,
            "carbohydrates": 40.0,
            "total_fat": 30.0  # Sum = 120g > 100g!
        }
    )
    assert resp_fail_macro.status_code == 400
    assert "exceeds 100g" in resp_fail_macro.json()["detail"]

    # 2. Calories grossly mismatched fails (macros sum <= 100g)
    resp_fail_cal = client.post(
        "/api/products/submit-label",
        json={
            "barcode": test_barcode,
            "product_name": "Mismatch Snack",
            "calories": 100.0,
            "protein": 10.0,
            "carbohydrates": 20.0,
            "total_fat": 20.0  # Expected: (10*4)+(20*4)+(20*9) = 40+80+180 = 300 kcal! 100 is 66% off!
        }
    )
    assert resp_fail_cal.status_code == 400
    assert "Calories" in resp_fail_cal.json()["detail"]

    # 3. Valid submission #1 -> not yet auto-approved
    resp_sub1 = client.post(
        "/api/products/submit-label",
        json={
            "barcode": test_barcode,
            "product_name": "Organic Roasted Chana",
            "calories": 390.0,
            "protein": 22.0,
            "carbohydrates": 58.0,
            "total_fat": 6.0,
            "fiber": 10.0
        }
    )
    assert resp_sub1.status_code == 200
    data1 = resp_sub1.json()
    assert data1["match_count"] == 1
    assert data1["is_approved"] is False

    # 4. Valid submission #2 with same barcode -> auto-approves!
    resp_sub2 = client.post(
        "/api/products/submit-label",
        json={
            "barcode": test_barcode,
            "product_name": "Organic Roasted Chana",
            "calories": 390.0,
            "protein": 22.0,
            "carbohydrates": 58.0,
            "total_fat": 6.0,
            "fiber": 10.0
        }
    )
    assert resp_sub2.status_code == 200
    data2 = resp_sub2.json()
    assert data2["match_count"] == 2
    assert data2["is_approved"] is True
    assert data2["community_verified"] is True

    # 5. Report product
    resp_rep = client.post(
        "/api/products/report",
        json={
            "barcode": test_barcode,
            "reason": "Ingredients list outdated"
        }
    )
    assert resp_rep.status_code == 200
    assert resp_rep.json()["status"] == "success"


def test_delete_user_account_cascades_all_data():
    user = create_fresh_user("del_user")
    token = create_access_token(user.username, "user")

    # Add scan, saved food, backup
    store.insert(Scan(user_id=user.id, product_name="Test Delete Scan"))
    store.insert(SavedFood(user_id=user.id, product_name="Test Delete Saved"))
    store.insert(UserSyncBackup(user_id=user.id, history_json="[]", saved_foods_json="[]"))

    assert store.find_one(Scan, {"user_id": user.id}) is not None

    # Delete account
    resp_del = client.delete("/user/account", headers={"Authorization": f"Bearer {token}"})
    assert resp_del.status_code == 200
    assert resp_del.json()["status"] == "success"

    # Verify everything wiped
    assert store.find_one(User, {"id": user.id}) is None
    assert store.find_one(Scan, {"user_id": user.id}) is None
    assert store.find_one(SavedFood, {"user_id": user.id}) is None
    assert store.find_one(UserSyncBackup, {"user_id": user.id}) is None
