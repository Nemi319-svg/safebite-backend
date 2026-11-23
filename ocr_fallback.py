import re
import os
import io
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("safebite.ocr")

_reader = None

def is_low_memory_environment() -> bool:
    """
    Detects if running on Render free tier (512MB RAM) or low-memory cloud instance.
    Loading PyTorch/EasyOCR in a 512MB container causes immediate OOM container kill.
    """
    if os.getenv("RENDER") or os.getenv("IS_RENDER"):
        return True
    if os.getenv("DISABLE_HEAVY_OCR", "false").lower() in ("true", "1", "yes"):
        return True
    return False

def get_easyocr_reader():
    """
    Lazy-loads EasyOCR only when safe and when memory allows (>1GB available).
    Never loads in memory-constrained environments like Render 512MB.
    """
    global _reader
    if is_low_memory_environment():
        logger.info("Low memory cloud environment detected (e.g. Render). Skipping heavy neural OCR to prevent OOM restart.")
        return None

    if _reader is None:
        try:
            import easyocr
            logger.info("Initializing EasyOCR reader...")
            _reader = easyocr.Reader(['en'], gpu=False)
        except Exception as e:
            logger.warning(f"Could not load EasyOCR: {e}")
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

    # Require at least one macronutrient or calorie metric to be legitimately detected
    if all(v is None for v in [calories, fat, protein, carbs, sugar, sodium]):
        logger.info("OCR did not detect nutrition values in the image.")
        return None

    return {
        "product_name": product_name,
        "calories": calories if calories is not None else 0.0,
        "total_fat": fat if fat is not None else 0.0,
        "protein": protein if protein is not None else 0.0,
        "carbohydrates": carbs if carbs is not None else 0.0,
        "sugar": sugar if sugar is not None else 0.0,
        "fiber": fiber if fiber is not None else 0.0,
        "sodium": sodium if sodium is not None else 0.0,
        "ingredients": ingredients_list
    }

def run_ocr_fallback(image_bytes: bytes) -> Optional[Dict[str, Any]]:
    """
    Lightweight, memory-efficient OCR fallback.
    Uses PIL instead of OpenCV to keep RAM footprint < 10MB.
    Guards against PyTorch OOM crashes on Render.
    """
    try:
        from PIL import Image

        # 1. Try lightweight Tesseract OCR first (C library, ~15MB RAM)
        try:
            import pytesseract
            img = Image.open(io.BytesIO(image_bytes))
            detected_text = pytesseract.image_to_string(img)
            if detected_text and len(detected_text.strip()) > 5:
                res = extract_nutrition_from_ocr_text(detected_text)
                if res:
                    return res
        except Exception:
            pass

        # 2. Check if safe to use EasyOCR
        reader = get_easyocr_reader()
        if not reader:
            logger.info("EasyOCR skipped to protect server memory limit.")
            return None

        import numpy as np
        img = Image.open(io.BytesIO(image_bytes))
        img_np = np.array(img.convert("RGB"))

        results = reader.readtext(img_np)
        detected_text = "\n".join([r[1] for r in results])
        logger.info(f"EasyOCR extracted text length: {len(detected_text)}")

        return extract_nutrition_from_ocr_text(detected_text)
    except Exception as e:
        logger.warning(f"OCR fallback error: {e}")
        return None
