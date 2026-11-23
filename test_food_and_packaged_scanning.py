import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from main import app, analyze_food_image_with_gemini
from gemini_service import (
    analyze_food_object_image_with_gemini,
    analyze_packaged_food_image_with_gemini,
    smart_local_food_object_analyzer
)

def create_test_image(width=100, height=100, color="green"):
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf

@pytest.fixture
def client():
    return TestClient(app)

# 1. Recognizable fruit / vegetable photos
def test_recognizable_fruit_food_object_mode(client, monkeypatch):
    mock_apple_response = {
        "is_food": True,
        "product_name": "Fresh Red Apple",
        "food_category": "Whole Fresh Fruit",
        "confidence": 0.95,
        "likely_ingredients": ["100% Fresh Apple"],
        "serving_size": "1 medium (~150g)",
        "serving_weight_grams": 150.0,
        "portion_estimated_with_visual_cues": True,
        "serving_options": ["1 small (100g)", "1 medium (150g)", "1 large (200g)"],
        "calories": 78.0,
        "total_fat": 0.3,
        "saturated_fat": 0.0,
        "trans_fat": 0.0,
        "carbohydrates": 20.7,
        "fiber": 3.6,
        "sugar": 15.6,
        "protein": 0.5,
        "sodium": 1.5,
        "allergens": [],
        "warnings": ["Values are visual estimates for a medium apple."],
        "analysis_mode": "food_object"
    }

    monkeypatch.setattr(
        "main.analyze_food_image_with_gemini",
        lambda img, mode=None: mock_apple_response
    )

    buf = create_test_image(color="red")
    response = client.post(
        "/analyze/image?mode=food_object",
        files={"image": ("apple.jpg", buf, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["product_name"] == "Fresh Red Apple"
    assert data["analysis_mode"] == "food_object"
    assert data["is_estimate"] is True
    assert data["confidence"] == 0.95
    assert data["nutrition"]["calories"] == 78.0
    assert data["health_score"] >= 80.0  # Whole fruit receives healthy rating
    assert data["classification"] == "Healthy"
    assert len(data["serving_options"]) == 3
    assert any("estimate" in w.lower() for w in data["warnings"])

# 2. Cooked mixed meals with uncertain ingredients (must not give reassuring score)
def test_cooked_mixed_meal_uncertain_ingredients_not_reassuring(client, monkeypatch):
    mock_uncertain_curry = {
        "is_food": True,
        "product_name": "Mixed Creamy Gravy Dish",
        "food_category": "Cooked Meal",
        "confidence": 0.42,  # Low confidence due to concealed ingredients
        "likely_ingredients": ["Gravy base", "Unknown cooking oil / butter", "Spices"],
        "serving_size": "1 bowl (~200g)",
        "serving_weight_grams": 200.0,
        "portion_estimated_with_visual_cues": False,
        "serving_options": ["1 small bowl (120g)", "1 medium bowl (200g)"],
        "calories": 380.0,
        "total_fat": 24.0,
        "saturated_fat": 8.0,
        "trans_fat": 0.5,
        "carbohydrates": 22.0,
        "fiber": 2.0,
        "sugar": 5.0,
        "protein": 7.0,
        "sodium": 650.0,
        "allergens": ["Dairy"],
        "warnings": ["Cooking oils, sodium, and hidden dairy cannot be accurately determined from visual appearance alone."],
        "analysis_mode": "food_object"
    }

    monkeypatch.setattr(
        "main.analyze_food_image_with_gemini",
        lambda img, mode=None: mock_uncertain_curry
    )

    buf = create_test_image(color="orange")
    response = client.post(
        "/analyze/food-object",
        files={"image": ("curry.jpg", buf, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["product_name"] == "Mixed Creamy Gravy Dish"
    assert data["confidence"] == 0.42
    # Ensure health score is conservative and NOT high/reassuring
    assert data["health_score"] <= 60.0
    assert data["classification"] != "Healthy"
    assert any("uncertain" in c.lower() for c in data["concerns"])

# 3. Packaged biscuits with readable nutrition label
def test_packaged_biscuits_nutrition_label(client, monkeypatch):
    mock_biscuit_label = {
        "product_name": "Parle Glucose Biscuits",
        "serving_size": "Per 100g",
        "calories": 454.0,
        "total_fat": 13.0,
        "saturated_fat": 6.5,
        "trans_fat": 0.0,
        "carbohydrates": 78.0,
        "sugar": 25.5,
        "added_sugar": 24.0,
        "fiber": 1.2,
        "protein": 6.5,
        "sodium": 280.0,
        "ingredients": ["Wheat Flour (Maida)", "Sugar", "Refined Palm Oil", "Invert Sugar Syrup", "Raising Agents"],
        "allergens": ["Wheat", "Gluten"],
        "analysis_mode": "packaged"
    }

    monkeypatch.setattr(
        "main.analyze_food_image_with_gemini",
        lambda img, mode=None: mock_biscuit_label
    )

    buf = create_test_image(color="yellow")
    response = client.post(
        "/analyze/packaged",
        files={"image": ("biscuit_label.jpg", buf, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["product_name"] == "Parle Glucose Biscuits"
    assert data["analysis_mode"] == "packaged"
    assert data["is_estimate"] is False
    assert data["nutrition"]["sugar"] == 25.5
    assert data["nutrition"]["added_sugar"] == 24.0
    assert data["nutrition"]["saturated_fat"] == 6.5
    assert "Wheat" in data["allergens"]
    assert data["classification"] in ["Unhealthy", "Moderate"]

# 4. Images with no recognizable food (must return 422)
def test_no_recognizable_food_rejected_422(client, monkeypatch):
    mock_no_food = {
        "is_food": False,
        "error": "No recognizable food items detected in the image."
    }

    monkeypatch.setattr(
        "main.analyze_food_image_with_gemini",
        lambda img, mode=None: mock_no_food
    )

    buf = create_test_image(color="gray")
    response = client.post(
        "/analyze/image?mode=food_object",
        files={"image": ("keyboard.jpg", buf, "image/jpeg")}
    )

    assert response.status_code == 422
    assert "No recognizable food" in response.json()["detail"]

# 5. Blurry unidentifiable images (must return 422)
def test_blurry_unidentifiable_image_rejected_422(client, monkeypatch):
    mock_blurry = {
        "is_food": False,
        "error": "Image is too blurry to identify food or nutrition label."
    }

    monkeypatch.setattr(
        "main.analyze_food_image_with_gemini",
        lambda img, mode=None: mock_blurry
    )

    buf = create_test_image(color="black")
    response = client.post(
        "/analyze/image",
        files={"image": ("blur.jpg", buf, "image/jpeg")}
    )

    assert response.status_code == 422

# 6. Unknown portion sizes with serving options
def test_unknown_portion_size_provides_options(client, monkeypatch):
    mock_dish = {
        "is_food": True,
        "product_name": "Cooked Dal",
        "food_category": "Cooked Meal",
        "confidence": 0.88,
        "likely_ingredients": ["Yellow lentils", "Turmeric", "Cumin", "Salt"],
        "serving_size": "1 standard bowl (~150g)",
        "serving_weight_grams": 150.0,
        "portion_estimated_with_visual_cues": False,  # Unknown plate scale
        "serving_options": ["1 small katori (100g)", "1 medium bowl (150g)", "1 large bowl (250g)"],
        "calories": 160.0,
        "total_fat": 4.0,
        "carbohydrates": 24.0,
        "fiber": 6.0,
        "sugar": 1.5,
        "protein": 8.5,
        "sodium": 320.0,
        "allergens": [],
        "warnings": ["Portion scale could not be visually confirmed. Standard katori weight applied."],
        "analysis_mode": "food_object"
    }

    monkeypatch.setattr(
        "main.analyze_food_image_with_gemini",
        lambda img, mode=None: mock_dish
    )

    buf = create_test_image(color="yellow")
    response = client.post(
        "/analyze/image?mode=food_object",
        files={"image": ("dal.jpg", buf, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["portion_size_estimated"] is False
    assert len(data["serving_options"]) == 3
    assert data["serving_options"][0] == "1 small katori (100g)"

# 7. Invalid uploads: empty file, non-image format
def test_invalid_uploads_validation(client):
    # Empty file
    response_empty = client.post(
        "/analyze/image",
        files={"image": ("empty.jpg", b"", "image/jpeg")}
    )
    assert response_empty.status_code == 400

    # Non-image mime type
    response_txt = client.post(
        "/analyze/image",
        files={"image": ("document.txt", b"Hello world", "text/plain")}
    )
    assert response_txt.status_code == 400

# 8. Gemini failure with local reference database fallback
def test_gemini_failure_local_reference_fallback(client, monkeypatch):
    # Simulate Gemini failing with exception
    def mock_failing_gemini(img, mode=None):
        raise RuntimeError("Gemini API connection timeout")

    monkeypatch.setattr("main.analyze_food_image_with_gemini", mock_failing_gemini)
    # OCR finds word "apple"
    monkeypatch.setattr(
        "main.run_ocr_fallback",
        lambda img: {"product_name": "Apple", "ingredients": ["Fresh Apple"]}
    )

    buf = create_test_image(color="red")
    response = client.post(
        "/analyze/image?mode=food_object",
        files={"image": ("apple_fallback.jpg", buf, "image/jpeg")}
    )

    # Either falls back cleanly or returns appropriate error without 500 crash
    assert response.status_code in [200, 422]
    if response.status_code == 200:
        data = response.json()
        assert "Apple" in data["product_name"]
        assert data["is_estimate"] is True


# 9. Apple and Banana identification with alternative candidates
def test_apple_and_banana_identification_with_alternatives(client, monkeypatch):
    # Test Banana with alternatives
    mock_banana = {
        "is_food": True,
        "product_name": "Fresh Banana",
        "food_category": "Whole Fresh Fruit",
        "confidence": 0.94,
        "likely_ingredients": ["100% Fresh Banana"],
        "serving_size": "1 medium (~120g)",
        "serving_weight_grams": 120.0,
        "portion_estimated_with_visual_cues": True,
        "serving_options": ["1 piece (120g)", "100g standard", "1 small (80g)"],
        "alternative_candidates": ["Raw Plantain", "Sweet Potato", "Corn on Cob"],
        "calories": 105.0,
        "total_fat": 0.4,
        "carbohydrates": 27.0,
        "fiber": 3.1,
        "sugar": 14.4,
        "protein": 1.3,
        "sodium": 1.2,
        "allergens": [],
        "warnings": ["Values are visual estimates."],
        "analysis_mode": "food_object"
    }

    monkeypatch.setattr(
        "main.analyze_food_image_with_gemini",
        lambda img, mode=None: mock_banana
    )

    buf = create_test_image(color="yellow")
    response = client.post(
        "/analyze/food-object",
        files={"image": ("banana.jpg", buf, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["product_name"] == "Fresh Banana"
    assert data["confidence"] == 0.94
    assert data["is_estimate"] is True
    assert "alternative_candidates" in data
    assert "Raw Plantain" in data["alternative_candidates"]
    assert len(data["serving_options"]) >= 3


# 10. Packaged food missing nutrition fields explicitly identified
def test_packaged_food_missing_fields_explicitly_identified(client, monkeypatch):
    # Only calories, fat, carbs, and protein printed on packet
    mock_sparse_label = {
        "product_name": "Traditional Rice Puffed Snacks",
        "serving_size": "Per 100g",
        "calories": 380.0,
        "total_fat": 2.0,
        "saturated_fat": None,
        "trans_fat": None,
        "carbohydrates": 82.0,
        "sugar": None,
        "added_sugar": None,
        "fiber": None,
        "protein": 7.0,
        "sodium": None,
        "ingredients": ["Puffed Rice, Salt"],
        "allergens": [],
        "analysis_mode": "packaged"
    }

    monkeypatch.setattr(
        "main.analyze_food_image_with_gemini",
        lambda img, mode=None: mock_sparse_label
    )

    buf = create_test_image(color="white")
    response = client.post(
        "/analyze/packaged",
        files={"image": ("puffed_rice.jpg", buf, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["analysis_mode"] == "packaged"
    assert "missing_fields" in data
    assert "Sodium" in data["missing_fields"]
    assert "Dietary Fiber" in data["missing_fields"]
    assert "Total Sugar" in data["missing_fields"]
    assert "Saturated Fat" in data["missing_fields"]
    assert data["is_estimate"] is False


# 11. Recalculate portion endpoint test
def test_recalculate_portion_endpoint(client):
    req_body = {
        "product_name": "Steamed White Rice",
        "base_calories": 195.0,
        "base_protein": 4.1,
        "base_carbs": 42.0,
        "base_fat": 0.4,
        "base_sugar": 0.1,
        "base_fiber": 0.6,
        "base_sodium": 2.0,
        "ingredients": "White Rice, Water",
        "multiplier": 1.5,
        "serving_size": "1.5 katori / large bowl (~225g)"
    }

    response = client.post("/analyze/recalculate", json=req_body)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["product_name"] == "Steamed White Rice"
    assert data["serving_size"] == "1.5 katori / large bowl (~225g)"
    # 195.0 * 1.5 = 292.5
    assert data["nutrition"]["calories"] == 292.5
    # 42.0 * 1.5 = 63.0
    assert data["nutrition"]["carbs"] == 63.0
    # Deterministic health score computed for the portion
    assert data["health_score"] > 0
    assert data["classification"] in ["Healthy", "Moderate", "Unhealthy"]


# 12. Specific Gajak recognition and health calibration test (Section 5)
def test_gajak_traditional_sweet_recognition(client, monkeypatch):
    """
    Tests recognition of Til-Gud Gajak:
    - Default serving ~25g (1 piece)
    - Nutrition: ~125 kcal, 3.2g protein, 6.5g fat, 14.5g carbs, 11.2g sugar, 1.6g fiber, 8mg sodium
    - Health score Moderate (~50-58)
    - Highlights sesame minerals and unsaturated fats vs jaggery sugar
    - Section 6 schema compatibility fields
    """
    def mock_gemini_gajak(img, mode=None):
        return {
            "is_food": True,
            "product_name": "Traditional Til-Gud Gajak",
            "food_category": "Traditional Indian Sweet",
            "confidence": 0.92,
            "calories": 125.0,
            "protein": 3.2,
            "carbohydrates": 14.5,
            "total_fat": 6.5,
            "sugar": 11.2,
            "fiber": 1.6,
            "sodium": 8.0,
            "serving_size": "1 piece (~25g)",
            "serving_weight_grams": 25.0,
            "portion_estimated_with_visual_cues": True,
            "serving_options": ["1 piece (25g)", "2 pieces (50g)", "100g standard"],
            "alternative_candidates": ["Peanut Chikki", "Til Ladoo", "Khasta Revdi"],
            "likely_ingredients": ["Roasted Sesame Seeds (Til)", "Jaggery (Gud)", "Cardamom", "Clarified Butter (Ghee)"],
            "analysis_mode": "food_object",
            "warnings": [
                "Visual estimate for traditional Til-Gud Gajak.",
                "High in concentrated jaggery sugar. Sesame seeds provide natural calcium, iron, and healthy unsaturated fats."
            ]
        }

    monkeypatch.setattr("main.analyze_food_image_with_gemini", mock_gemini_gajak)

    buf = create_test_image(color="yellow")
    response = client.post(
        "/analyze/food-object",
        files={"image": ("gajak.jpg", buf, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()

    # Core identities
    assert "Gajak" in data["food_name"] or "Gajak" in data["product_name"]
    assert data["food_mode"] == "unpackaged"
    assert data["nutrition_is_estimated"] is True

    # Portion & Nutrition
    assert data["serving_size_g"] == 25.0
    nutr = data["nutrition"]
    assert nutr["calories"] == 125.0
    assert nutr["protein"] == 3.2
    assert nutr["fat"] == 6.5
    assert nutr["carbohydrates"] == 14.5 or nutr["carbs"] == 14.5
    assert nutr["sugar"] == 11.2
    assert nutr["fiber"] == 1.6
    assert nutr["sodium"] == 8.0

    # Moderate score & classification (~50-58)
    assert 48.0 <= data["health_score"] <= 60.0
    assert data["health_category"] == "Moderate"
    assert data["classification"] == "Moderate"

    # Explanation and benefits highlight sesame seed minerals
    all_text = " ".join(data.get("benefits", []) + data.get("concerns", []) + [data.get("explanation", "")])
    assert "sesame" in all_text.lower() or "mineral" in all_text.lower() or "jaggery" in all_text.lower()

    # Alternative candidates
    assert "Peanut Chikki" in data["alternative_candidates"]

    # All Section 6 schema fields are present
    expected_fields = [
        "food_mode", "food_name", "food_category", "identification_confidence",
        "serving_size_g", "nutrition", "nutrition_source", "nutrition_is_estimated",
        "health_score", "health_category", "data_confidence", "missing_fields",
        "explanation", "recommendations", "requires_user_confirmation",
        "alternative_candidates", "serving_options"
    ]
    for field in expected_fields:
        assert field in data, f"Missing required Section 6 field: {field}"


# 13. Test Lookup Food Endpoint (/analyze/lookup-food)
def test_lookup_food_endpoint(client):
    # Lookup Gajak
    res = client.post("/analyze/lookup-food", json={"food_name": "Gajak"})
    assert res.status_code == 200
    data = res.json()
    assert "Gajak" in data["food_name"]
    assert data["serving_size_g"] == 25.0
    assert data["nutrition"]["calories"] == 125.0
    assert data["health_category"] == "Moderate"
    assert data["requires_user_confirmation"] is False

    # Lookup with custom portion grams (e.g. 50g -> 2 pieces)
    res50 = client.post("/analyze/lookup-food", json={"food_name": "Gajak", "serving_size_g": 50.0})
    assert res50.status_code == 200
    data50 = res50.json()
    assert data50["serving_size_g"] == 50.0
    assert data50["nutrition"]["calories"] == 250.0

    # Lookup Apple
    res_apple = client.post("/analyze/lookup-food", json={"food_name": "Apple"})
    assert res_apple.status_code == 200
    data_apple = res_apple.json()
    assert "Apple" in data_apple["food_name"]
    assert data_apple["health_category"] == "Healthy"

    # Nonexistent food 404
    res_none = client.post("/analyze/lookup-food", json={"food_name": "NonExistentExtraterrestrialFoodXYZ123"})
    assert res_none.status_code == 404


# 14. Low confidence image triggers requires_user_confirmation
def test_low_confidence_requires_user_confirmation(client, monkeypatch):
    def mock_low_confidence_food(img, mode=None):
        return {
            "is_food": True,
            "product_name": "Mysterious Golden Crisp",
            "food_category": "Snack",
            "confidence": 0.55,  # Low confidence
            "calories": 250.0,
            "protein": 3.0,
            "carbohydrates": 30.0,
            "total_fat": 13.0,
            "sugar": 5.0,
            "fiber": 1.0,
            "sodium": 200.0,
            "serving_size": "1 piece (~50g)",
            "alternative_candidates": ["Mathri", "Namak Pare", "Khakhra"],
            "analysis_mode": "food_object"
        }

    monkeypatch.setattr("main.analyze_food_image_with_gemini", mock_low_confidence_food)

    buf = create_test_image(color="yellow")
    response = client.post(
        "/analyze/food-object",
        files={"image": ("low_conf.jpg", buf, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["requires_user_confirmation"] is True
    assert data["data_confidence"] in ["low", "medium"]
    assert len(data["alternative_candidates"]) > 0

