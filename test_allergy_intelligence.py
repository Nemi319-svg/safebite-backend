import pytest
from fastapi.testclient import TestClient
from main import app, create_access_token
from database import get_db, MongoStore, SQLiteStore, init_db
from models import User
from allergy_service import (
    assess_allergies_and_ingredients,
    determine_ingredient_completeness,
    ALLERGEN_FREE_DISCLAIMER
)

@pytest.fixture
def client():
    init_db()
    with TestClient(app) as test_client:
        yield test_client


def test_confirmed_peanut_and_tree_nut_detection():
    # Test Indian terms like moongphali, badam, kaju
    ingredients = "Refined wheat flour, moongphali (peanuts), badam (almonds), kaju, sugar, vegetable oil"
    alerts, completeness, disclaimer = assess_allergies_and_ingredients(
        ingredients_text=ingredients,
        analysis_mode="packaged"
    )

    names = {a.name for a in alerts}
    assert "Peanuts" in names
    assert "Tree Nuts" in names
    assert completeness == "complete"
    assert "not guarantee a product is 100% allergen-free" in disclaimer


def test_hidden_dairy_and_gluten_derivatives():
    ingredients = "Whey protein concentrate, calcium caseinate, milk solids, maida, sooji, malt extract"
    alerts, completeness, _ = assess_allergies_and_ingredients(
        ingredients_text=ingredients,
        analysis_mode="packaged"
    )

    dairy_alerts = [a for a in alerts if a.name == "Dairy"]
    gluten_alerts = [a for a in alerts if a.name == "Gluten / Wheat"]

    assert len(dairy_alerts) > 0
    assert "whey protein" in dairy_alerts[0].matched_term or "casein" in dairy_alerts[0].matched_term or "milk solids" in dairy_alerts[0].matched_term
    assert dairy_alerts[0].match_type == "confirmed"

    assert len(gluten_alerts) > 0
    assert "maida" in gluten_alerts[0].matched_term or "sooji" in gluten_alerts[0].matched_term
    assert gluten_alerts[0].match_type == "confirmed"


def test_user_profile_allergy_critical_matching():
    ingredients = "Sugar, peanut butter, cocoa solids, palm oil"
    alerts, _, _ = assess_allergies_and_ingredients(
        ingredients_text=ingredients,
        user_allergens="peanut allergy",
        user_exclusions=""
    )

    critical_peanut = [a for a in alerts if a.name == "Peanuts"]
    assert len(critical_peanut) > 0
    assert critical_peanut[0].is_user_allergy is True
    assert critical_peanut[0].severity == "critical"
    assert "violates your Peanuts allergy profile" in critical_peanut[0].message


def test_user_profile_ingredient_exclusions():
    ingredients = "Edible vegetable oil (palmolein), sugar, monosodium glutamate (ins 621), iodized salt"
    alerts, _, _ = assess_allergies_and_ingredients(
        ingredients_text=ingredients,
        user_allergens="",
        user_exclusions="palm oil, msg"
    )

    palm_alerts = [a for a in alerts if a.name == "Palm Oil"]
    msg_alerts = [a for a in alerts if a.name == "Monosodium Glutamate"]

    assert len(palm_alerts) > 0
    assert palm_alerts[0].is_user_allergy is True
    assert palm_alerts[0].severity == "critical"
    assert "palmolein" in palm_alerts[0].matched_term

    assert len(msg_alerts) > 0
    assert msg_alerts[0].is_user_allergy is True
    assert msg_alerts[0].severity == "critical"


def test_precautionary_possible_allergen_matching():
    ingredients = (
        "Wheat flour, sugar, cocoa butter. "
        "Manufactured in a facility that also processes tree nuts, eggs, and soy."
    )
    alerts, _, _ = assess_allergies_and_ingredients(
        ingredients_text=ingredients,
        user_allergens="eggs",
        analysis_mode="packaged"
    )

    egg_alerts = [a for a in alerts if a.name == "Eggs"]
    assert len(egg_alerts) > 0
    assert egg_alerts[0].match_type == "possible"
    assert egg_alerts[0].is_user_allergy is True
    assert egg_alerts[0].severity == "critical"
    assert "May contain traces of" in egg_alerts[0].message


def test_incomplete_unreadable_ingredient_list_detection():
    # 1. Truncated with ellipsis
    c1 = determine_ingredient_completeness("Wheat flour, sugar, palm oil, salt, ...")
    assert c1 == "partial"

    # 2. Too short / cut off
    c2 = determine_ingredient_completeness("Wheat flour, ")
    assert c2 == "partial"

    # 3. Explicit unreadable marker
    c3 = determine_ingredient_completeness("unreadable")
    assert c3 == "unreadable"

    # 4. Unavailable
    c4 = determine_ingredient_completeness("")
    assert c4 == "unavailable"

    # 5. Food object mode defaults to complete
    c5 = determine_ingredient_completeness(None, analysis_mode="food_object")
    assert c5 == "complete"


def test_profile_endpoint_persists_ingredient_exclusions(client):
    db: MongoStore = next(get_db())
    username = f"allergy_test_user_{id(test_profile_endpoint_persists_ingredient_exclusions)}"
    
    existing = db.find_one(User, {"username": username})
    if existing:
        db.delete(existing)
        
    user = User(
        username=username,
        email=f"{username}@example.com",
        hashed_password="hashed_pwd",
        role="user"
    )
    db.insert(user)
    
    token = create_access_token(username)
    headers = {"Authorization": f"Bearer {token}"}

    # Update profile with allergens and exclusions
    put_resp = client.post(
        "/profile",
        headers=headers,
        json={
            "username": username,
            "age": 28,
            "allergens": "peanuts, lactose",
            "ingredient_exclusions": "palm oil, tartrazine, hfcs"
        }
    )
    assert put_resp.status_code == 200
    put_data = put_resp.json()
    assert put_data["allergens"] == "peanuts, lactose"
    assert put_data["ingredient_exclusions"] == "palm oil, tartrazine, hfcs"

    # Verify GET profile returns persisted values
    get_resp = client.get("/profile", headers=headers)
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["allergens"] == "peanuts, lactose"
    assert get_data["ingredient_exclusions"] == "palm oil, tartrazine, hfcs"


def test_manual_analysis_returns_structured_alerts_and_disclaimer(client):
    resp = client.post(
        "/analyze/manual",
        json={
            "product_name": "Peanut Chikki Bar",
            "calories": 480.0,
            "protein": 12.0,
            "carbs": 55.0,
            "fat": 24.0,
            "sugar": 35.0,
            "fiber": 4.0,
            "sodium": 120.0,
            "ingredients": "Moongphali (peanuts), jaggery, liquid glucose, ghee"
        }
    )
    assert resp.status_code == 200
    data = resp.json()

    assert "allergy_alerts" in data
    assert len(data["allergy_alerts"]) > 0
    names = [a["name"] for a in data["allergy_alerts"]]
    assert "Peanuts" in names
    assert "Dairy" in names  # ghee is recognized as Dairy!

    assert data["ingredient_completeness"] == "complete"
    assert "allergen_free_disclaimer" in data
    assert "not guarantee a product is 100% allergen-free" in data["allergen_free_disclaimer"]
