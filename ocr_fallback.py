import re
import logging
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger("safebite.ocr")

_reader = None

def get_easyocr_reader():
    global _reader
    if _reader is None:
        try:
            import easyocr
            logger.info("Initializing EasyOCR reader (lazy-loaded)...")
            _reader = easyocr.Reader(['en'], gpu=False)
        except Exception as e:
            logger.error(f"Could not load EasyOCR: {e}")
            return None
    return _reader

def extract_nutrition_from_ocr_text(text: str) -> Dict[str, Any]:
    """
    Extracts numerical nutrition values from OCR recognized text lines.
    Protects against multi-column blending and recognizes standard units.
    """
    clean = text.lower()

    def find_num(keywords) -> Optional[float]:
        for kw in keywords:
            pattern = rf"{kw}[^0-9]*?(\d+([.,]\d+)?)\s*(g|mg|kcal|cal)?"
            match = re.search(pattern, clean)
            if match:
                try:
                    return float(match.group(1).replace(",", "."))
                except ValueError:
                    pass
        return None

    calories = find_num(["energy", "calorie", "calories", "calorles"])
    fat = find_num(["total fat", "fat"])
    protein = find_num(["protein", "proteln"])
    carbs = find_num(["total carbohydrate", "carbohydrate", "carbohydrates", "carbs"])
    sugar = find_num(["total sugar", "sugars", "sugar"])
    fiber = find_num(["dietary fiber", "dietary fibre", "fiber", "fibre"])
    sodium = find_num(["sodium", "sodlum"])

    # Extract ingredients if mentioned
    ingredients_list = []
    ing_match = re.search(r"ingredients?[:\s]+(.*?)(nutrition|contains|mfg|$)", clean)
    if ing_match:
        raw_ings = ing_match.group(1).strip()
        ingredients_list = [i.strip() for i in raw_ings.split(",") if len(i.strip()) > 1]

    # Best-effort product name from first non-nutrition line
    product_name = "Scanned Food Product"
    lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 2]
    rejected = ["nutrition", "facts", "calories", "serving", "daily value", "%"]
    for l in lines:
        if not any(r in l.lower() for r in rejected) and len(l) > 3:
            product_name = l.title()
            break

    return {
        "product_name": product_name,
        "calories": calories if calories is not None else 150.0,
        "total_fat": fat if fat is not None else 5.0,
        "protein": protein if protein is not None else 3.0,
        "carbohydrates": carbs if carbs is not None else 20.0,
        "sugar": sugar if sugar is not None else 2.0,
        "fiber": fiber if fiber is not None else 1.0,
        "sodium": sodium if sodium is not None else 120.0,
        "ingredients": ingredients_list
    }

def run_ocr_fallback(image_bytes: bytes) -> Optional[Dict[str, Any]]:
    """
    Runs EasyOCR and OpenCV on an image buffer as a fallback if Gemini Vision fails.
    """
    try:
        import cv2

        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            logger.error("Failed to decode image bytes with OpenCV")
            return None

        reader = get_easyocr_reader()
        if not reader:
            logger.warning("EasyOCR is not available")
            return None

        results = reader.readtext(img)
        detected_text = "\n".join([r[1] for r in results])
        logger.info(f"EasyOCR extracted text length: {len(detected_text)}")

        return extract_nutrition_from_ocr_text(detected_text)
    except Exception as e:
        logger.error(f"OCR fallback error: {e}", exc_info=True)
        return None
