import pytest
from fastapi.testclient import TestClient
from main import app, create_access_token
from database import get_db, MongoStore
from models import User, Scan, Conversation, ChatMessage

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    db: MongoStore = next(app.dependency_overrides.get(get_db, get_db)())
    test_user = User(
        username="coach_user",
        hashed_password="pw",
        role="user",
        dietary_preference="Vegetarian",
        allergens="peanuts,gluten",
        is_diabetic=True
    )
    db.delete_many(User, {"username": "coach_user"})
    user_id = db.insert(test_user)
    test_user.id = user_id
    token = create_access_token("coach_user")
    return {"Authorization": f"Bearer {token}"}, test_user

@pytest.fixture
def victim_headers(client):
    db: MongoStore = next(app.dependency_overrides.get(get_db, get_db)())
    victim_user = User(
        username="victim_coach_user",
        hashed_password="pw",
        role="user"
    )
    db.delete_many(User, {"username": "victim_coach_user"})
    user_id = db.insert(victim_user)
    victim_user.id = user_id
    token = create_access_token("victim_coach_user")
    return {"Authorization": f"Bearer {token}"}, victim_user


def test_empty_message_validation(client):
    """Empty or whitespace-only messages should return 400 Bad Request."""
    res = client.post("/chat", json={"message": "   "})
    assert res.status_code == 400
    assert "cannot be empty" in res.json()["detail"]


def test_gajak_nutrition_inquiry(client):
    """Testing Gajak nutritional inquiry triggers detailed answer and suggestions."""
    res = client.post("/chat", json={"message": "Is gajak healthy?"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "gajak" in data["response"].lower()
    assert "sesame" in data["response"].lower() or "til" in data["response"].lower()
    assert len(data.get("follow_up_suggestions", [])) > 0


def test_samosa_vs_kachori_comparison(client):
    """Testing Samosa vs Kachori food comparison."""
    res = client.post("/chat", json={"message": "Compare samosa and kachori"})
    assert res.status_code == 200
    data = res.json()
    assert "samosa" in data["response"].lower()
    assert "kachori" in data["response"].lower()
    assert "calories" in data["response"].lower()


def test_chat_without_scan_context_does_not_invent_scan(client, auth_headers):
    """When user asks about 'my scan' but no scans exist, NutriCoach does not invent one."""
    headers, user = auth_headers
    db: MongoStore = next(app.dependency_overrides.get(get_db, get_db)())
    db.delete_many(Scan, {"user_id": user.id})

    res = client.post("/chat", json={"message": "Why did my scan receive this score?"}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "no recent food scan" in data["response"].lower() or "scan food" in data["response"].lower()


def test_chat_with_scan_context_evaluates_food(client, auth_headers):
    """When a scan context is provided, NutriCoach grounds advice in the real scan."""
    headers, user = auth_headers
    payload = {
        "message": "Why did this food receive this score?",
        "scan_context": {
            "product_name": "NutriChoice Digestive Biscuits",
            "health_score": 58.0,
            "classification": "Moderate",
            "calories": 440.0,
            "protein": 7.0,
            "carbs": 68.0,
            "fat": 16.0,
            "sugar": 18.0,
            "sodium": 320.0,
            "ingredients": "Whole wheat flour, sugar, edible vegetable oil, maltodextrin"
        }
    }
    res = client.post("/chat", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "NutriChoice Digestive Biscuits" in data["response"]
    assert "58" in data["response"]


def test_conversation_persistence_and_isolation(client, auth_headers, victim_headers):
    """Verify conversations are saved, isolated between users, and can be retrieved & deleted."""
    headers1, user1 = auth_headers
    headers2, user2 = victim_headers

    # 1. User 1 sends message -> conversation created
    res1 = client.post("/chat", json={"message": "Suggest a healthy Indian breakfast"}, headers=headers1)
    assert res1.status_code == 200
    conv_id = res1.json()["conversation_id"]
    assert conv_id is not None

    # 2. User 1 lists conversations -> sees the conversation
    res_list = client.get("/chat/conversations", headers=headers1)
    assert res_list.status_code == 200
    conv_ids = [c["id"] for c in res_list.json()]
    assert conv_id in conv_ids

    # 3. User 1 gets conversation details -> sees message history
    res_detail = client.get(f"/chat/conversations/{conv_id}", headers=headers1)
    assert res_detail.status_code == 200
    assert len(res_detail.json()["messages"]) >= 2  # user + assistant

    # 4. User 2 cannot access User 1's conversation (Cross-user isolation)
    res_unauth = client.get(f"/chat/conversations/{conv_id}", headers=headers2)
    assert res_unauth.status_code == 404

    # 5. User 2 cannot delete User 1's conversation
    res_del_unauth = client.delete(f"/chat/conversations/{conv_id}", headers=headers2)
    assert res_del_unauth.status_code == 404

    # 6. User 1 deletes their conversation
    res_del = client.delete(f"/chat/conversations/{conv_id}", headers=headers1)
    assert res_del.status_code == 200
    assert res_del.json()["status"] == "success"

    # 7. Verification: conversation is gone
    res_check = client.get(f"/chat/conversations/{conv_id}", headers=headers1)
    assert res_check.status_code == 404
