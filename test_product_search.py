"""
Unit and Integration Tests for Universal Food Product Search & Health Analyzer
=============================================================================
Tests:
1. Search Maggi (curated noodles).
2. Search Oreo (biscuits).
3. Search Amul Milk (dairy).
4. Search an unknown product.
5. Search with case differences / partial matches.
6. Search by brand.
7. Search by barcode.
8. Product with complete nutrition data (FSSAI alerts, macros, health score).
9. Product with incomplete nutrition data (graceful handling, confidence).
10. External API unavailable (mock timeout/failure without crash).
11. Multiple products with similar names (rank ordering).
12. Product comparison (side-by-side nutrition & score).
13. Personalized suitability (diabetic, low-sodium, vegetarian, allergens).
14. Admin addition of new products.
"""

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
import requests

from main import app
from product_search_service import product_search_service

client = TestClient(app)


def test_1_search_maggi():
    response = client.get("/products/search?query=maggi")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total"] >= 1
    names = [p["name"] for p in data["products"]]
    assert any("maggi" in n.lower() for n in names)
    first = data["products"][0]
    assert first["health_score"] is not None
    assert first["classification"] in ["Healthy", "Moderate", "Unhealthy"]


def test_2_search_oreo():
    response = client.get("/products/search?query=oreo")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["products"]) >= 1
    oreo = next((p for p in data["products"] if "oreo" in p["name"].lower()), None)
    assert oreo is not None
    assert oreo["brand"] == "Mondelez Oreo"
    assert oreo["sugar"] > 30.0  # High sugar detected


def test_3_search_amul_milk():
    response = client.get("/products/search?query=amul%20milk")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["products"]) >= 1
    amul = data["products"][0]
    assert "amul" in amul["brand"].lower()
    assert amul["protein"] >= 3.0


def test_4_search_unknown_product():
    # An obscure nonsense string that does not exist in local catalog or OFF
    with patch("product_search_service.query_openfoodfacts_search", return_value=[]):
        response = client.get("/products/search?query=xyznotarealfood123987")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["total"] == 0
        assert data["products"] == []
        assert len(data["suggestions"]) > 0


def test_5_search_case_insensitivity_and_partial():
    r1 = client.get("/products/search?query=KuRkUrE")
    r2 = client.get("/products/search?query=kurkure")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["total"] == r2.json()["total"]


def test_6_search_by_brand():
    response = client.get("/products/search?brand=Britannia")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    for p in data["products"]:
        assert "britannia" in p["brand"].lower()


def test_7_search_by_barcode():
    # Barcode for Kurkure Masala Munch
    response = client.get("/products/barcode/8901499008200")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "kurkure" in data["name"].lower()
    assert data["barcode"] == "8901499008200"
    assert len(data["fssai_warnings"]) > 0  # Sodium & Sat Fat alerts


def test_8_complete_nutrition_details():
    response = client.get("/products/maggi_2min_masala")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Maggi 2-Minute Masala Noodles"
    assert data["nutrition_per_100g"]["calories"] == 427.0
    assert data["nutrition_per_100g"]["sodium"] == 1020.0
    assert len(data["fssai_warnings"]) > 0
    assert any("sodium" in w.lower() for w in data["fssai_warnings"])
    assert len(data["additive_details"]) > 0
    assert len(data["healthier_alternatives"]) > 0
    assert data["is_data_insufficient"] is False


def test_9_incomplete_nutrition_handling():
    # Directly test get_detail with simulated incomplete record
    with patch.dict(product_search_service._curated, {
        "test_incomplete": {
            "id": "test_incomplete",
            "name": "Mystery Powder",
            "brand": "Unknown",
            "category": "General",
            "calories": None,
            "protein": None,
            "carbohydrates": None,
            "total_fat": None,
            "total_sugar": None,
            "sodium": None,
            "fiber": None,
            "ingredients": "Unknown spices"
        }
    }):
        detail = product_search_service.get_detail("test_incomplete")
        assert detail is not None
        assert detail.is_data_insufficient is True
        assert detail.health_score is None


def test_10_external_api_unavailable_graceful_fallback():
    # Simulate network timeout when calling OpenFoodFacts
    with patch("product_search_service.requests.get", side_effect=requests.exceptions.Timeout("Connection timed out")):
        response = client.get("/products/search?query=lays")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        # Should gracefully return local curated Lay's items without crashing
        assert any("lay" in p["name"].lower() for p in data["products"])


def test_11_multiple_products_similar_names_ranking():
    response = client.get("/products/search?query=coca")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    # Exact prefix starts first
    names = [p["name"] for p in data["products"]]
    assert names[0].lower().startswith("coca")


def test_12_product_comparison():
    payload = {
        "product_ids": ["maggi_2min_masala", "quaker_rolled_oats"]
    }
    response = client.post("/products/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["products"]) == 2
    # Oats should have significantly higher score than Maggi
    maggi = next(p for p in data["products"] if p["id"] == "maggi_2min_masala")
    oats = next(p for p in data["products"] if p["id"] == "quaker_rolled_oats")
    assert oats["health_score"] > maggi["health_score"]
    assert data["healthier_choice_id"] == "quaker_rolled_oats"
    assert len(data["key_differences"]) > 0


def test_13_personalized_health_analysis():
    # Test diabetic and low sodium suitability for Coca-Cola Original
    res_coke = client.get("/products/coca_cola_original/health?diabetic=true&low_sodium=false")
    assert res_coke.status_code == 200
    data_coke = res_coke.json()
    assert data_coke["personalized_suitability"]["flags"]["diabetic_friendly"] is False
    assert any("diabetic" in n.lower() for n in data_coke["personalized_suitability"]["notes"])

    # Test vegetarian check for item with gluten allergy
    res_oreo = client.get("/products/oreo_vanilla/health?vegetarian=true&allergens=gluten")
    assert res_oreo.status_code == 200
    data_oreo = res_oreo.json()
    assert data_oreo["personalized_suitability"]["flags"]["vegetarian_compatible"] is True
    assert data_oreo["personalized_suitability"]["flags"]["allergen_safe"] is False
    assert any("allergen" in n.lower() for n in data_oreo["personalized_suitability"]["notes"])


def test_14_admin_add_product():
    new_product_payload = {
        "admin_secret": "safebite_admin_secret_2026",
        "name": "Organic Roasted Makhana Herbs",
        "brand": "SafeBite Organics",
        "category": "Snacks",
        "barcode": "8909999888877",
        "calories": 180.0,
        "protein": 9.5,
        "carbohydrates": 26.0,
        "total_sugar": 0.5,
        "total_fat": 3.0,
        "saturated_fat": 0.5,
        "trans_fat": 0.0,
        "sodium": 120.0,
        "fiber": 6.5,
        "ingredients": "Foxnuts (Makhana), Olive Oil, Himalayan Pink Salt, Oregano, Thyme."
    }
    response = client.post("/products/admin/add", json=new_product_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Organic Roasted Makhana Herbs"
    assert data["health_score"] >= 80.0
    assert data["classification"] == "Healthy"

    # Search for this newly ingested product
    search_res = client.get("/products/search?query=makhana")
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert any("makhana" in p["name"].lower() for p in search_data["products"])
