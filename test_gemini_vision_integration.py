import io
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from PIL import Image

from main import app
from database import get_db, MongoStore
from models import User

client = TestClient(app)

def create_dummy_jpeg() -> bytes:
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_analyze_image_valid_gemini_vision_mock():
    """Tests successful image analysis via Gemini Vision with allergens, macros, and serving size."""
    image_bytes = create_dummy_jpeg()

    mock_gemini_data = {
        "product_name": "Organic Almond Milk",
        "serving_size": "240ml",
        "calories": 60.0,
        "total_fat": 2.5,
        "saturated_fat": 0.2,
        "trans_fat": 0.0,
        "carbohydrates": 8.0,
        "sugar": 7.0,
        "added_sugar": 5.0,
        "fiber": 1.0,
        "protein": 1.0,
        "sodium": 150.0,
        "ingredients": ["Almondmilk (Water, Almonds)", "Cane Sugar", "Sea Salt"],
        "allergens": ["Tree Nuts (Almonds)"]
    }

    with patch("main.analyze_food_image_with_gemini", return_value=mock_gemini_data):
        response = client.post(
            "/analyze/image",
            files={"image": ("almond_milk.jpg", image_bytes, "image/jpeg")}
        )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "success"
    assert data["product_name"] == "Organic Almond Milk"
    assert data["nutrition"]["calories"] == 60.0
    assert data["nutrition"]["protein"] == 1.0
    assert data["nutrition"]["carbs"] == 8.0
    assert data["nutrition"]["fat"] == 2.5
    assert data["nutrition"]["serving_size"] == "240ml"
    assert "Tree Nuts (Almonds)" in data["allergens"]
    assert any("Contains allergen: Tree Nuts (Almonds)" in c for c in data["concerns"])
    assert data["analysis_source"] == "Gemini Vision AI"
    assert data["health_score"] > 0

def test_analyze_image_atwater_calories_calculation():
    """Tests that missing calories are accurately calculated from Atwater factors."""
    image_bytes = create_dummy_jpeg()

    # protein=10g (40 kcal), carbs=20g (80 kcal), fat=5g (45 kcal) -> Total = 165 kcal
    mock_gemini_data = {
        "product_name": "High Protein Bar",
        "serving_size": "50g",
        "calories": None,
        "total_fat": 5.0,
        "saturated_fat": 1.0,
        "trans_fat": 0.0,
        "carbohydrates": 20.0,
        "sugar": 2.0,
        "added_sugar": 0.0,
        "fiber": 5.0,
        "protein": 10.0,
        "sodium": 100.0,
        "ingredients": ["Whey Protein", "Oats", "Cocoa"],
        "allergens": ["Milk"]
    }

    with patch("main.analyze_food_image_with_gemini", return_value=mock_gemini_data):
        response = client.post(
            "/analyze/image",
            files={"image": ("protein_bar.jpg", image_bytes, "image/jpeg")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["nutrition"]["calories"] == 165.0
    assert data["nutrition"]["protein"] == 10.0
    assert data["nutrition"]["carbs"] == 20.0
    assert data["nutrition"]["fat"] == 5.0

def test_analyze_image_invalid_corrupted_file_400():
    """Tests that corrupt non-image bytes are rejected with HTTP 400."""
    fake_bytes = b"This is plain text pretending to be an image."
    response = client.post(
        "/analyze/image",
        files={"image": ("fake.jpg", fake_bytes, "image/jpeg")}
    )
    assert response.status_code == 400
    assert "valid image format" in response.json()["detail"]

def test_analyze_image_empty_file_400():
    """Tests that an empty file is rejected with HTTP 400."""
    response = client.post(
        "/analyze/image",
        files={"image": ("empty.jpg", b"", "image/jpeg")}
    )
    assert response.status_code == 400
    assert "Empty image file" in response.json()["detail"]

def test_analyze_image_blank_non_food_image_422():
    """Tests that an unreadable/non-food image returning nulls is rejected with 422 without fabricating zeroes."""
    image_bytes = create_dummy_jpeg()

    empty_extracted = {
        "product_name": "Unknown Product",
        "serving_size": None,
        "calories": None,
        "total_fat": None,
        "saturated_fat": None,
        "trans_fat": None,
        "carbohydrates": None,
        "sugar": None,
        "fiber": None,
        "protein": None,
        "sodium": None,
        "ingredients": [],
        "allergens": []
    }

    with patch("main.analyze_food_image_with_gemini", return_value=empty_extracted), \
         patch("main.run_ocr_fallback", return_value=None):
        response = client.post(
            "/analyze/image",
            files={"image": ("cat_photo.jpg", image_bytes, "image/jpeg")}
        )

    assert response.status_code == 422
    assert "Could not detect nutrition information" in response.json()["detail"]

def test_analyze_image_ocr_fallback_when_gemini_unavailable():
    """Tests graceful fallback to OCR when Gemini returns None."""
    image_bytes = create_dummy_jpeg()

    ocr_extracted = {
        "product_name": "Rolled Oats",
        "calories": 150.0,
        "protein": 5.0,
        "carbohydrates": 27.0,
        "total_fat": 3.0,
        "sugar": 1.0,
        "fiber": 4.0,
        "sodium": 0.0,
        "ingredients": ["100% Whole Grain Rolled Oats"]
    }

    with patch("main.analyze_food_image_with_gemini", return_value=None), \
         patch("main.run_ocr_fallback", return_value=ocr_extracted):
        response = client.post(
            "/analyze/image",
            files={"image": ("oats.jpg", image_bytes, "image/jpeg")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["product_name"] == "Rolled Oats"
    assert data["nutrition"]["calories"] == 150.0
    assert data["analysis_source"] == "OCR Fallback"
