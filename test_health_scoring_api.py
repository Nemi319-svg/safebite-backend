import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_score_endpoint_returns_score_and_explanation():
    response = client.post(
        "/health-score",
        json={
            "product_name": "Fresh Red Apple",
            "calories": 52,
            "protein": 0.3,
            "carbs": 13.8,
            "fat": 0.2,
            "sugar": 10.4,
            "fiber": 2.4,
            "sodium": 1,
            "ingredients": "100% raw apple",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["product_name"] == "Fresh Red Apple"
    assert 0 <= data["health_score"] <= 100
    assert data["classification"] == "Healthy"
    assert isinstance(data["reasons"], list)
    assert isinstance(data["benefits"], list)
    assert isinstance(data["concerns"], list)
    assert isinstance(data["healthier_alternatives"], list)
    assert data["nutrition"]["calories"] == 52


def test_health_score_endpoint_rejects_negative_nutrition_values():
    response = client.post(
        "/health-score",
        json={
            "product_name": "Example",
            "calories": -1,
            "protein": 1,
            "carbs": 1,
            "fat": 1,
        },
    )

    assert response.status_code == 422


def test_health_score_compare_endpoint_is_available():
    response = client.post(
        "/health-score/compare",
        json={
            "product_a_name": "Natural Peanut Butter",
            "product_a_calories": 625,
            "product_a_protein": 30,
            "product_a_carbs": 18,
            "product_a_fat": 50,
            "product_a_sugar": 4,
            "product_a_sodium": 10,
            "product_b_name": "Potato Chips",
            "product_b_calories": 536,
            "product_b_protein": 7,
            "product_b_carbs": 53,
            "product_b_fat": 34,
            "product_b_sugar": 0.5,
            "product_b_sodium": 550,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["product_a"]["health_score"] > data["product_b"]["health_score"]
    assert data["healthier_choice"].startswith("Natural Peanut Butter")
