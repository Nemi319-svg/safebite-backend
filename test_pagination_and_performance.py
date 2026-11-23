import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from main import app, create_access_token
from database import get_db, MongoStore, init_db
from models import User, Scan, SavedFood

@pytest.fixture
def client():
    init_db()
    with TestClient(app) as test_client:
        yield test_client

def test_health_endpoint_and_timing_header(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database_connected"] is True
    # Verify timing middleware header
    assert "x-process-time-ms" in response.headers
    assert float(response.headers["x-process-time-ms"]) >= 0.0

def test_history_and_saved_foods_pagination(client):
    db: MongoStore = next(app.dependency_overrides.get(get_db, get_db)())
    test_username = "pagination_user"
    
    # Clean up any existing test data
    existing_user = db.find_one(User, {"username": test_username})
    if existing_user:
        db.delete_many(Scan, {"user_id": existing_user.id})
        db.delete_many(SavedFood, {"user_id": existing_user.id})
        db.delete(existing_user)
        
    user = User(
        username=test_username,
        email="pagination@safebite.app",
        hashed_password="test_hashed_pwd",
        role="user"
    )
    user_id = db.insert(user)
    token = create_access_token(test_username)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Insert 5 scans
    for i in range(5):
        db.insert(Scan(
            user_id=user_id,
            product_name=f"Food Item {i}",
            calories=100.0 * (i + 1),
            health_score=80.0
        ))
        db.insert(SavedFood(
            user_id=user_id,
            product_name=f"Saved Item {i}",
            calories=100.0 * (i + 1),
            health_score=80.0
        ))
        
    # Test pagination: limit=2, skip=0
    res1 = client.get(f"/history?username={test_username}&limit=2&skip=0", headers=headers)
    assert res1.status_code == 200
    scans1 = res1.json().get("scans", [])
    assert len(scans1) == 2
    
    # Test pagination: limit=2, skip=2
    res2 = client.get(f"/history?username={test_username}&limit=2&skip=2", headers=headers)
    assert res2.status_code == 200
    scans2 = res2.json().get("scans", [])
    assert len(scans2) == 2
    assert scans1[0]["id"] != scans2[0]["id"]
    
    # Test saved foods pagination
    res_saved = client.get(f"/saved-foods?username={test_username}&limit=3&skip=1", headers=headers)
    assert res_saved.status_code == 200
    assert len(res_saved.json().get("foods", [])) == 3

def test_blank_image_returns_422_without_fake_nutrition(client, monkeypatch):
    import main
    # Ensure neither Gemini nor OCR find nutrition facts in a blank image
    monkeypatch.setattr(main, "analyze_food_image_with_gemini", lambda b: None)
    monkeypatch.setattr(main, "run_ocr_fallback", lambda b: None)

    # Create a small blank image (no text, no nutrition facts)
    img = Image.new("RGB", (100, 100), color="white")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    
    response = client.post(
        "/analyze/image",
        files={"file": ("blank.jpg", buf, "image/jpeg")}
    )
    # Should not fabricate fake Oat & Grain Snack; should return 422 error
    assert response.status_code == 422
    assert "Could not detect nutrition information" in response.json()["detail"]

def test_user_profile_dietary_preferences_persistence(client):
    db: MongoStore = next(app.dependency_overrides.get(get_db, get_db)())
    test_user = "dietary_test_user"
    existing = db.find_one(User, {"username": test_user})
    if existing:
        db.delete(existing)

    user = User(
        username=test_user,
        email="dietary@safebite.app",
        hashed_password="pwd",
        role="user"
    )
    db.insert(user)

    token = create_access_token(test_user)
    headers = {"Authorization": f"Bearer {token}"}

    # Update profile with dietary preference and allergens
    payload = {
        "username": test_user,
        "age": 28,
        "height": 175.0,
        "weight": 70.0,
        "gender": "Female",
        "is_diabetic": True,
        "dietary_preference": "Strict Vegetarian",
        "allergens": "Peanuts, Soy, Gluten"
    }
    update_res = client.post("/profile", json=payload, headers=headers)
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["dietary_preference"] == "Strict Vegetarian"
    assert data["allergens"] == "Peanuts, Soy, Gluten"

    # Get profile
    get_res = client.get(f"/profile?username={test_user}", headers=headers)
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["dietary_preference"] == "Strict Vegetarian"
    assert get_data["allergens"] == "Peanuts, Soy, Gluten"
    assert get_data["is_diabetic"] is True

def test_google_play_account_deletion(client):
    db: MongoStore = next(app.dependency_overrides.get(get_db, get_db)())
    test_user = "delete_me_user"
    existing = db.find_one(User, {"username": test_user})
    if existing:
        db.delete_many(Scan, {"user_id": existing.id})
        db.delete_many(SavedFood, {"user_id": existing.id})
        db.delete(existing)

    user = User(
        username=test_user,
        email="deleteme@safebite.app",
        hashed_password="pwd",
        role="user"
    )
    user_id = db.insert(user)
    token = create_access_token(test_user)
    headers = {"Authorization": f"Bearer {token}"}

    # Create associated scans and saved foods
    db.insert(Scan(user_id=user_id, product_name="Item To Delete", calories=200.0))
    db.insert(SavedFood(user_id=user_id, product_name="Saved To Delete", calories=200.0))

    # Perform Google Play compliant account deletion
    del_res = client.delete(f"/user/account?username={test_user}", headers=headers)
    assert del_res.status_code == 200
    assert "permanently deleted" in del_res.json()["message"]

    # Verify user and all data purged from database
    assert db.find_one(User, {"username": test_user}) is None
    assert db.count(Scan, {"user_id": user_id}) == 0
    assert db.count(SavedFood, {"user_id": user_id}) == 0

