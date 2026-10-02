import os
import datetime
import logging
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

from pydantic import BaseModel
import bcrypt
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import engine, get_db, init_db
import models
from models import (
    User, Scan, SavedFood,
    RegisterRequest, LoginRequest, AuthResponse,
    UserProfileRequest, UserProfileResponse,
    ManualAnalysisRequest, AnalysisResponse, NutritionData,
    BarcodeResponse, IndianFoodSearchResponse,
    ScanItem, HistoryResponse, SavedFoodRequest, SavedFoodItem, SavedFoodsResponse,
    SimpleStatusResponse, DiabetesCheckRequest, DiabetesCheckResponse,
    ChatMessageRequest, ChatMessageResponse, HealthCheckResponse,
    DashboardStatsResponse, DashboardRecentScan,
    CompareFoodRequest, CompareFoodResponse, ComparedProductData,
    AdminLoginRequest, AdminHistoryResponse
)
from health_calculator import calculate_health_score, get_healthier_alternatives
from indian_foods_data import search_indian_food
from gemini_service import (
    analyze_food_image_with_gemini,
    chat_with_gemini,
    is_gemini_configured,
    set_gemini_api_key
)
from ocr_fallback import run_ocr_fallback

# Initialize Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("safebite.api")

# Initialize SQLite tables
init_db()

# Auto-seed default user if not present
def seed_default_user():
    db = Session(bind=engine)
    try:
        user = db.query(models.User).filter(models.User.username == "demo_user").first()
        if not user:
            new_u = models.User(
                username="demo_user",
                hashed_password=bcrypt.hashpw("password123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
                role="user",
                age=25,
                height=170.0,
                weight=65.0,
                gender="Other",
                is_diabetic=False
            )
            db.add(new_u)
            db.commit()
            logger.info("Default user 'demo_user' seeded successfully in SQLite database.")
    except Exception as e:
        logger.warning(f"Could not seed default user: {e}")
    finally:
        db.close()

seed_default_user()

# Create FastAPI app
app = FastAPI(
    title="SafeBite – AI Food Health Analyzer API",
    description="Backend powering SafeBite nutrition extraction, health scoring, comparison, and AI assistance.",
    version="1.0.0"
)

# Enable CORS for Android / Web / Emulators
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Helper: Password Hashing using bcrypt
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

# Helper: Calculate BMI
def calculate_bmi(weight_kg: Optional[float], height_cm: Optional[float]) -> (Optional[float], Optional[str]):
    if not weight_kg or not height_cm or height_cm <= 0:
        return None, None
    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m * height_m), 1)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25.0:
        category = "Normal"
    elif bmi < 30.0:
        category = "Overweight"
    else:
        category = "Obese"
    return bmi, category


# ============================================================================
# Core Endpoints
# ============================================================================

@app.get("/", tags=["Health"], include_in_schema=False)
def root():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "app": "SafeBite – AI Food Health Analyzer",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/status", tags=["Health"])
def api_status():
    return {
        "app": "SafeBite – AI Food Health Analyzer",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    svg_icon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🥗</text></svg>'
    return Response(content=svg_icon, media_type="image/svg+xml")

class GeminiKeyRequest(BaseModel):
    api_key: str

@app.post("/config/gemini-key", tags=["Config"])
def configure_gemini(request: GeminiKeyRequest):
    success = set_gemini_api_key(request.api_key)
    return {
        "status": "success" if success else "error",
        "gemini_configured": is_gemini_configured(),
        "message": "Gemini API key configured successfully! Real Gemini AI is now active." if success else "Could not set API key."
    }

@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
def health_check():
    """Returns backend status and AI configuration without exposing keys."""
    return HealthCheckResponse(
        status="healthy",
        message="SafeBite backend is operational",
        gemini_configured=is_gemini_configured(),
        groq_configured=False,
        ocr_ready=True
    )

# ============================================================================
# User Authentication & Profile
# ============================================================================

@app.post("/register", response_model=AuthResponse, tags=["Auth"])
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    clean_username = request.username.strip()
    if len(clean_username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters.")
    if len(request.password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters.")

    existing_user = db.query(User).filter(User.username == clean_username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username is already registered.")

    new_user = User(
        username=clean_username,
        hashed_password=hash_password(request.password),
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return AuthResponse(
        status="success",
        message="Registration successful. Welcome to SafeBite!",
        username=new_user.username,
        role=new_user.role
    )

@app.post("/login", response_model=AuthResponse, tags=["Auth"])
def login(request: LoginRequest, db: Session = Depends(get_db)):
    clean_username = request.username.strip()
    user = db.query(User).filter(User.username == clean_username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    return AuthResponse(
        status="success",
        message="Login successful.",
        username=user.username,
        role=user.role
    )

@app.get("/profile", response_model=UserProfileResponse, tags=["Profile"])
def get_profile(username: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username.strip()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    bmi, bmi_category = calculate_bmi(user.weight, user.height)

    return UserProfileResponse(
        status="success",
        username=user.username,
        age=user.age,
        height=user.height,
        weight=user.weight,
        gender=user.gender,
        is_diabetic=bool(user.is_diabetic),
        bmi=bmi,
        bmi_category=bmi_category
    )

@app.post("/profile", response_model=UserProfileResponse, tags=["Profile"])
def update_profile(request: UserProfileRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username.strip()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.age = request.age
    user.height = request.height
    user.weight = request.weight
    user.gender = request.gender
    user.is_diabetic = request.is_diabetic

    db.commit()
    db.refresh(user)

    bmi, bmi_category = calculate_bmi(user.weight, user.height)

    return UserProfileResponse(
        status="success",
        username=user.username,
        age=user.age,
        height=user.height,
        weight=user.weight,
        gender=user.gender,
        is_diabetic=bool(user.is_diabetic),
        bmi=bmi,
        bmi_category=bmi_category
    )

# ============================================================================
# Food Analysis (Manual, Image Vision, Barcode)
# ============================================================================

@app.post("/analyze/manual", response_model=AnalysisResponse, tags=["Analysis"])
def analyze_manual(request: ManualAnalysisRequest, db: Session = Depends(get_db)):
    # Check if user is diabetic to adjust scoring
    is_diabetic = False
    user_id = None
    if request.username:
        user = db.query(User).filter(User.username == request.username.strip()).first()
        if user:
            is_diabetic = bool(user.is_diabetic)
            user_id = user.id

    score, classification, reasons, benefits, concerns = calculate_health_score(
        calories=request.calories,
        protein=request.protein,
        carbs=request.carbs,
        fat=request.fat,
        sugar=request.sugar or 0.0,
        fiber=request.fiber or 0.0,
        sodium=request.sodium or 0.0,
        is_diabetic=is_diabetic
    )

    alternatives = get_healthier_alternatives(request.product_name, classification)
    analysis_text = f"Classified as {classification} ({int(score)}/100). " + " ".join(reasons)

    # Save to history if user is known
    if user_id:
        scan_rec = Scan(
            user_id=user_id,
            product_name=request.product_name,
            calories=request.calories,
            protein=request.protein,
            carbs=request.carbs,
            fat=request.fat,
            sugar=request.sugar,
            fiber=request.fiber,
            sodium=request.sodium,
            ingredients=request.ingredients,
            health_score=score,
            classification=classification,
            analysis=analysis_text,
            healthier_alternatives=", ".join(alternatives),
            benefits=", ".join(benefits),
            concerns=", ".join(concerns)
        )
        db.add(scan_rec)
        db.commit()

    return AnalysisResponse(
        status="success",
        product_name=request.product_name,
        nutrition=NutritionData(
            calories=request.calories,
            protein=request.protein,
            carbs=request.carbs,
            fat=request.fat,
            sugar=request.sugar,
            fiber=request.fiber,
            sodium=request.sodium
        ),
        health_score=score,
        classification=classification,
        category=classification,
        ingredients=request.ingredients,
        analysis=analysis_text,
        recommendation=analysis_text,
        healthier_alternatives=alternatives,
        benefits=benefits,
        concerns=concerns
    )


@app.post("/analyze/image", response_model=AnalysisResponse, tags=["Analysis"])
@app.post("/analyze-image-vision", response_model=AnalysisResponse, include_in_schema=False)
async def analyze_image(
    image: Optional[UploadFile] = File(None),
    file: Optional[UploadFile] = File(None),
    username: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Preferred Full-Stack Architecture:
    Multipart Image Upload -> Gemini Vision -> Structured Nutrition JSON -> Health Score -> DB Save -> Result JSON
    With graceful OCR fallback if Gemini is offline or unavailable.
    """
    actual_file = image or file
    if not actual_file:
        raise HTTPException(status_code=400, detail="Uploaded file must be a valid image format.")
    if actual_file.content_type and not actual_file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a valid image format.")

    image_bytes = await actual_file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty image file received.")
    if len(image_bytes) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image size exceeds 15MB limit.")

    # 1. Primary: Gemini Vision Image Analysis
    extracted = analyze_food_image_with_gemini(image_bytes)

    # 2. Fallback: Local OCR / EasyOCR if Gemini returned nothing
    if not extracted:
        logger.info("Attempting OCR fallback pipeline...")
        extracted = run_ocr_fallback(image_bytes)

    if not extracted:
        raise HTTPException(
            status_code=422,
            detail="Could not detect nutrition information from this image. Please take a clearer photo of the Nutrition Facts table."
        )

    product_name = extracted.get("product_name") or "Packaged Food"
    calories = float(extracted.get("calories") or 0.0)
    fat = float(extracted.get("total_fat") or 0.0)
    protein = float(extracted.get("protein") or 0.0)
    carbs = float(extracted.get("carbohydrates") or 0.0)
    sugar = float(extracted.get("sugar") or 0.0)
    fiber = float(extracted.get("fiber") or 0.0)
    sodium = float(extracted.get("sodium") or 0.0)
    ingredients_val = extracted.get("ingredients", [])
    ingredients_str = ", ".join(ingredients_val) if isinstance(ingredients_val, list) else str(ingredients_val or "")

    # Check diabetic user flag
    is_diabetic = False
    user_id = None
    if username:
        user = db.query(User).filter(User.username == username.strip()).first()
        if user:
            is_diabetic = bool(user.is_diabetic)
            user_id = user.id

    # Compute Health Score & Classification
    score, classification, reasons, benefits, concerns = calculate_health_score(
        calories=calories,
        protein=protein,
        carbs=carbs,
        fat=fat,
        sugar=sugar,
        fiber=fiber,
        sodium=sodium,
        is_diabetic=is_diabetic
    )

    alternatives = get_healthier_alternatives(product_name, classification)
    analysis_text = f"Classified as {classification} ({int(score)}/100). " + " ".join(reasons)

    # Save to Scan database history
    if user_id:
        scan_rec = Scan(
            user_id=user_id,
            product_name=product_name,
            calories=calories,
            protein=protein,
            carbs=carbs,
            fat=fat,
            sugar=sugar,
            fiber=fiber,
            sodium=sodium,
            saturated_fat=float(extracted.get("saturated_fat") or 0.0),
            trans_fat=float(extracted.get("trans_fat") or 0.0),
            ingredients=ingredients_str,
            health_score=score,
            classification=classification,
            analysis=analysis_text,
            healthier_alternatives=", ".join(alternatives),
            benefits=", ".join(benefits),
            concerns=", ".join(concerns)
        )
        db.add(scan_rec)
        db.commit()

    return AnalysisResponse(
        status="success",
        product_name=product_name,
        nutrition=NutritionData(
            calories=calories,
            protein=protein,
            carbs=carbs,
            fat=fat,
            sugar=sugar,
            fiber=fiber,
            sodium=sodium
        ),
        health_score=score,
        classification=classification,
        category=classification,
        ingredients=ingredients_str,
        analysis=analysis_text,
        recommendation=analysis_text,
        healthier_alternatives=alternatives,
        benefits=benefits,
        concerns=concerns
    )


@app.get("/analyze/barcode/{barcode}", response_model=BarcodeResponse, tags=["Analysis"])
@app.get("/barcode/{barcode}", response_model=BarcodeResponse, include_in_schema=False)
def analyze_barcode(barcode: str):
    """Fetches nutrition facts for a barcode using OpenFoodFacts API with local fallback."""
    clean_barcode = barcode.strip()
    try:
        import requests
        url = f"https://world.openfoodfacts.org/api/v0/product/{clean_barcode}.json"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == 1:
                p = data.get("product", {})
                nutr = p.get("nutriments", {})
                name = p.get("product_name") or "Packaged Product"
                cal = float(nutr.get("energy-kcal_100g") or nutr.get("energy-kcal") or 150.0)
                fat = float(nutr.get("fat_100g") or nutr.get("fat") or 5.0)
                prot = float(nutr.get("proteins_100g") or nutr.get("proteins") or 3.0)
                carbs = float(nutr.get("carbohydrates_100g") or nutr.get("carbohydrates") or 20.0)
                sugar = float(nutr.get("sugars_100g") or 0.0)
                sod = float(nutr.get("sodium_100g") or 0.0) * 1000.0 # g to mg

                score, classification, reasons, _, _ = calculate_health_score(
                    calories=cal, protein=prot, carbs=carbs, fat=fat, sugar=sugar, sodium=sod
                )
                alts = get_healthier_alternatives(name, classification)
                rec = f"Product contains {int(cal)} kcal, {prot}g protein, {carbs}g carbs, {fat}g fat. Classified as {classification}."

                return BarcodeResponse(
                    status="success",
                    product_name=name,
                    nutrition=NutritionData(calories=cal, protein=prot, carbs=carbs, fat=fat, sugar=sugar, sodium=sod),
                    health_score=score,
                    classification=classification,
                    category=classification,
                    recommendation=rec,
                    healthier_alternatives=alts
                )
    except Exception as e:
        logger.warning(f"OpenFoodFacts lookup failed: {e}")

    # Fallback response for demo barcode
    score, classification, reasons, _, _ = calculate_health_score(calories=160, protein=2, carbs=15, fat=10)
    alts = get_healthier_alternatives("Packaged Snack", classification)
    return BarcodeResponse(
        status="success",
        product_name=f"Packaged Food ({clean_barcode})",
        nutrition=NutritionData(calories=160, protein=2, carbs=15, fat=10),
        health_score=score,
        classification=classification,
        category=classification,
        recommendation=f"Barcode {clean_barcode} recognized. Moderate daily consumption recommended.",
        healthier_alternatives=alts
    )


@app.post("/analyze/compare", response_model=CompareFoodResponse, tags=["Analysis"])
@app.post("/compare-foods", response_model=CompareFoodResponse, include_in_schema=False)
def compare_foods(request: CompareFoodRequest):
    """
    Compares two food products side-by-side. Explains differences clearly without unsupported medical claims.
    """
    score_a, class_a, _, _, _ = calculate_health_score(
        calories=request.product_a_calories,
        protein=request.product_a_protein,
        carbs=request.product_a_carbs,
        fat=request.product_a_fat,
        sugar=request.product_a_sugar or 0.0,
        sodium=request.product_a_sodium or 0.0
    )

    score_b, class_b, _, _, _ = calculate_health_score(
        calories=request.product_b_calories,
        protein=request.product_b_protein,
        carbs=request.product_b_carbs,
        fat=request.product_b_fat,
        sugar=request.product_b_sugar or 0.0,
        sodium=request.product_b_sodium or 0.0
    )

    prod_a = ComparedProductData(
        name=request.product_a_name,
        calories=request.product_a_calories,
        protein=request.product_a_protein,
        carbs=request.product_a_carbs,
        fat=request.product_a_fat,
        sugar=request.product_a_sugar or 0.0,
        sodium=request.product_a_sodium or 0.0,
        health_score=score_a,
        classification=class_a
    )

    prod_b = ComparedProductData(
        name=request.product_b_name,
        calories=request.product_b_calories,
        protein=request.product_b_protein,
        carbs=request.product_b_carbs,
        fat=request.product_b_fat,
        sugar=request.product_b_sugar or 0.0,
        sodium=request.product_b_sodium or 0.0,
        health_score=score_b,
        classification=class_b
    )

    key_diffs = []
    cal_diff = abs(request.product_a_calories - request.product_b_calories)
    if cal_diff >= 30:
        higher_cal = request.product_a_name if request.product_a_calories > request.product_b_calories else request.product_b_name
        key_diffs.append(f"{higher_cal} has {int(cal_diff)} more calories per serving.")

    prot_diff = abs(request.product_a_protein - request.product_b_protein)
    if prot_diff >= 2:
        higher_prot = request.product_a_name if request.product_a_protein > request.product_b_protein else request.product_b_name
        key_diffs.append(f"{higher_prot} provides {prot_diff:.1f}g more protein.")

    fat_diff = abs(request.product_a_fat - request.product_b_fat)
    if fat_diff >= 3:
        lower_fat = request.product_a_name if request.product_a_fat < request.product_b_fat else request.product_b_name
        key_diffs.append(f"{lower_fat} has {fat_diff:.1f}g less total fat.")

    if score_a > score_b:
        healthier_choice = f"{request.product_a_name} (Score: {int(score_a)} vs {int(score_b)})"
        summary = f"{request.product_a_name} achieves a higher health score due to a more favorable macronutrient balance."
    elif score_b > score_a:
        healthier_choice = f"{request.product_b_name} (Score: {int(score_b)} vs {int(score_a)})"
        summary = f"{request.product_b_name} achieves a higher health score due to a more favorable macronutrient balance."
    else:
        healthier_choice = "Both products have comparable nutritional scores."
        summary = "Both items exhibit very similar health indices based on available facts."

    return CompareFoodResponse(
        status="success",
        product_a=prod_a,
        product_b=prod_b,
        healthier_choice=healthier_choice,
        comparison_summary=summary,
        key_differences=key_diffs
    )

# ============================================================================
# Scan History & Saved Foods
# ============================================================================

@app.get("/history", response_model=HistoryResponse, tags=["History"])
def get_history(username: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username.strip()).first()
    if not user:
        return HistoryResponse(status="success", scans=[])

    scans = (
        db.query(Scan)
        .filter(Scan.user_id == user.id)
        .order_by(Scan.scan_date.desc())
        .limit(50)
        .all()
    )

    items = [
        ScanItem(
            id=s.id,
            product_name=s.product_name,
            calories=s.calories,
            protein=s.protein,
            carbs=s.carbs,
            fat=s.fat,
            sugar=s.sugar,
            fiber=s.fiber,
            sodium=s.sodium,
            ingredients=s.ingredients,
            health_score=s.health_score,
            classification=s.classification,
            analysis=s.analysis,
            image_path=s.image_path,
            scan_date=s.scan_date.strftime("%Y-%m-%d %H:%M") if s.scan_date else None
        )
        for s in scans
    ]

    return HistoryResponse(status="success", scans=items)

@app.get("/history/{item_or_user}", tags=["History"])
def get_history_item_or_user(item_or_user: str, db: Session = Depends(get_db)):
    if item_or_user.isdigit():
        scan_id = int(item_or_user)
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan record not found.")

        return ScanItem(
            id=scan.id,
            product_name=scan.product_name,
            calories=scan.calories,
            protein=scan.protein,
            carbs=scan.carbs,
            fat=scan.fat,
            sugar=scan.sugar,
            fiber=scan.fiber,
            sodium=scan.sodium,
            ingredients=scan.ingredients,
            health_score=scan.health_score,
            classification=scan.classification,
            analysis=scan.analysis,
            image_path=scan.image_path,
            scan_date=scan.scan_date.strftime("%Y-%m-%d %H:%M") if scan.scan_date else None
        )
    else:
        return get_history(username=item_or_user, db=db)

@app.delete("/history/{scan_id}", response_model=SimpleStatusResponse, tags=["History"])
def delete_history_item(scan_id: int, username: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username.strip()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == user.id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan item not found or does not belong to user.")

    db.delete(scan)
    db.commit()
    return SimpleStatusResponse(status="success", message="Scan deleted successfully.", scan_id=scan_id)

@app.delete("/history", response_model=SimpleStatusResponse, tags=["History"])
def delete_all_history(username: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username.strip()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    deleted = db.query(Scan).filter(Scan.user_id == user.id).delete()
    db.commit()
    return SimpleStatusResponse(status="success", message="All history cleared.", deleted_count=deleted)

@app.get("/saved-foods", response_model=SavedFoodsResponse, tags=["Saved Foods"])
def get_saved_foods(username: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username.strip()).first()
    if not user:
        return SavedFoodsResponse(status="success", foods=[])

    saved = (
        db.query(SavedFood)
        .filter(SavedFood.user_id == user.id)
        .order_by(SavedFood.saved_date.desc())
        .all()
    )

    items = [
        SavedFoodItem(
            id=f.id,
            product_name=f.product_name,
            calories=f.calories,
            protein=f.protein,
            carbs=f.carbs,
            fat=f.fat,
            sugar=f.sugar,
            fiber=f.fiber,
            sodium=f.sodium,
            ingredients=f.ingredients,
            health_score=f.health_score,
            analysis=f.analysis,
            image_path=f.image_path,
            saved_date=f.saved_date.strftime("%Y-%m-%d %H:%M") if f.saved_date else None
        )
        for f in saved
    ]
    return SavedFoodsResponse(status="success", foods=items)

@app.post("/saved-foods", response_model=SimpleStatusResponse, tags=["Saved Foods"])
@app.post("/save-food", response_model=SimpleStatusResponse, include_in_schema=False)
def save_food(request: SavedFoodRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username.strip()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    new_saved = SavedFood(
        user_id=user.id,
        product_name=request.product_name,
        calories=request.calories,
        protein=request.protein,
        carbs=request.carbs,
        fat=request.fat,
        sugar=request.sugar,
        fiber=request.fiber,
        sodium=request.sodium,
        ingredients=request.ingredients,
        health_score=request.health_score,
        analysis=request.analysis,
        image_path=request.image_path
    )
    db.add(new_saved)
    db.commit()
    db.refresh(new_saved)

    return SimpleStatusResponse(status="success", message="Food successfully saved!", id=new_saved.id)

@app.delete("/saved-foods/{food_id}", response_model=SimpleStatusResponse, tags=["Saved Foods"])
def delete_saved_food(food_id: int, db: Session = Depends(get_db)):
    saved = db.query(SavedFood).filter(SavedFood.id == food_id).first()
    if not saved:
        raise HTTPException(status_code=404, detail="Saved food not found.")

    db.delete(saved)
    db.commit()
    return SimpleStatusResponse(status="success", message="Saved food removed.", id=food_id)

# ============================================================================
# Indian Food Search
# ============================================================================

@app.get("/search-indian", response_model=IndianFoodSearchResponse, tags=["Indian Food"])
@app.get("/search-indian-food", response_model=IndianFoodSearchResponse, include_in_schema=False)
def get_indian_food(
    q: Optional[str] = Query(None, description="Query dish name or category"),
    query: Optional[str] = Query(None, description="Query dish name or category")
):
    """Searches comprehensive Indian dish nutritional database."""
    search_term = q or query or ""
    results = search_indian_food(search_term)
    return IndianFoodSearchResponse(status="success", results=results)

# ============================================================================
# Diabetes Check & AI Assistant Chat
# ============================================================================

@app.post("/diabetes-check", response_model=DiabetesCheckResponse, tags=["Health Assessment"])
def check_diabetes(request: DiabetesCheckRequest, db: Session = Depends(get_db)):
    """
    Evaluates dietary risk indicators (carbohydrates, sugar, fiber, calories) from recent user scans.
    Strictly provides general dietary guidelines without medical diagnosis or prescription.
    """
    user = db.query(User).filter(User.username == request.username.strip()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    scans = (
        db.query(Scan)
        .filter(Scan.user_id == user.id)
        .order_by(Scan.scan_date.desc())
        .limit(10)
        .all()
    )

    base_risk = 35 # baseline low-medium score
    if user.is_diabetic:
        base_risk += 25

    bmi, _ = calculate_bmi(user.weight, user.height)
    if bmi and bmi >= 25.0:
        base_risk += 15

    recommendations = [
        "Focus on low-glycemic index foods like lentils (dal), chickpeas, and whole millets.",
        "Ensure each meal contains adequate dietary fiber (>= 5g) to blunt post-meal blood sugar spikes.",
        "Limit refined flour (maida) and sweetened beverages."
    ]

    if scans:
        avg_carbs = sum(s.carbs or 0.0 for s in scans) / len(scans)
        avg_sugar = sum(s.sugar or 0.0 for s in scans) / len(scans)

        if avg_carbs > 45:
            base_risk += 15
            recommendations.append("Recent scans show elevated carbohydrate intake (average >45g). Consider pairing carbs with protein.")
        if avg_sugar > 10:
            base_risk += 15
            recommendations.append("Recent foods feature high added sugars. Opt for fresh whole fruits instead of packaged desserts.")

    risk_score = max(10, min(95, base_risk))
    if risk_score < 40:
        risk_level = "Low"
    elif risk_score < 70:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return DiabetesCheckResponse(
        status="success",
        risk_score=risk_score,
        risk_level=risk_level,
        recommendations=recommendations
    )


@app.post("/chat", response_model=ChatMessageResponse, tags=["Chat"])
def chat(request: ChatMessageRequest, db: Session = Depends(get_db)):
    """
    Chat with Gemini AI Nutrition Assistant.
    Provides context from recent scans if username is provided.
    """
    recent_scan_context = None
    if request.username:
        user = db.query(User).filter(User.username == request.username.strip()).first()
        if user:
            last_scan = (
                db.query(Scan)
                .filter(Scan.user_id == user.id)
                .order_by(Scan.scan_date.desc())
                .first()
            )
            if last_scan:
                recent_scan_context = {
                    "product_name": last_scan.product_name,
                    "health_score": last_scan.health_score,
                    "classification": last_scan.classification,
                    "calories": last_scan.calories,
                    "protein": last_scan.protein,
                    "carbs": last_scan.carbs,
                    "fat": last_scan.fat,
                    "ingredients": last_scan.ingredients
                }

    reply = chat_with_gemini(request.message, recent_scan_context)
    return ChatMessageResponse(
        status="success",
        response=reply,
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    )


# ============================================================================
# Dashboard Statistics & Admin Dashboard
# ============================================================================

@app.get("/dashboard-stats", response_model=DashboardStatsResponse, tags=["Dashboard"])
def get_dashboard_stats(username: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username.strip()).first()
    if not user:
        return DashboardStatsResponse(status="success")

    scans = (
        db.query(Scan)
        .filter(Scan.user_id == user.id)
        .order_by(Scan.scan_date.desc())
        .all()
    )

    total_scans = len(scans)
    avg_score = (sum(s.health_score or 0.0 for s in scans) / total_scans) if total_scans > 0 else 0.0
    healthy_count = sum(1 for s in scans if (s.health_score or 0.0) >= 70 or (s.classification or "").lower() == "healthy")
    moderate_count = sum(1 for s in scans if (45 <= (s.health_score or 0.0) < 70) or (s.classification or "").lower() == "moderate")
    unhealthy_count = sum(1 for s in scans if (s.health_score or 0.0) < 45 or (s.classification or "").lower() == "unhealthy")
    healthy_pct = round((healthy_count / total_scans) * 100.0, 1) if total_scans > 0 else 0.0
    moderate_pct = round((moderate_count / total_scans) * 100.0, 1) if total_scans > 0 else 0.0
    unhealthy_pct = round((unhealthy_count / total_scans) * 100.0, 1) if total_scans > 0 else 0.0

    bmi, bmi_category = calculate_bmi(user.weight, user.height)

    # Calculate streak (days with at least 1 scan)
    streak = 1 if total_scans > 0 else 0

    if total_scans == 0:
        smart_insight = "Scan your first food item using camera, barcode, or label upload to track your diet quality!"
    elif unhealthy_count > healthy_count:
        smart_insight = f"⚠️ Alert: {unhealthy_count} of your {total_scans} scans ({int(unhealthy_pct)}%) are Unhealthy or Ultra-Processed. Consider swapping them for the recommended healthy alternatives."
    elif healthy_pct >= 70:
        smart_insight = f"🌟 Outstanding! {healthy_count} of your {total_scans} scans ({int(healthy_pct)}%) are Healthy clean foods. Keep up the great nutrition habits!"
    else:
        smart_insight = f"⚖️ Balanced diet: You have logged {healthy_count} healthy, {moderate_count} moderate, and {unhealthy_count} unhealthy foods. Maintain portion control."

    recent_scans = [
        DashboardRecentScan(
            id=s.id,
            product_name=s.product_name or "Food",
            health_score=s.health_score,
            calories=s.calories,
            protein=s.protein,
            carbs=s.carbs,
            fat=s.fat,
            scan_date=s.scan_date.strftime("%b %d") if s.scan_date else None
        )
        for s in scans[:5]
    ]

    recs = [
        "Include colorful seasonal vegetables in every meal.",
        "Drink at least 2.5 liters of water daily for metabolic efficiency.",
        "Check labels for hidden sodium in processed condiments."
    ]

    return DashboardStatsResponse(
        status="success",
        total_scans=total_scans,
        avg_health_score=round(avg_score, 1),
        bmi=bmi,
        bmi_category=bmi_category,
        is_diabetic=bool(user.is_diabetic),
        smart_insight=smart_insight,
        healthy_count=healthy_count,
        moderate_count=moderate_count,
        unhealthy_count=unhealthy_count,
        healthy_percentage=healthy_pct,
        moderate_percentage=moderate_pct,
        unhealthy_percentage=unhealthy_pct,
        scan_streak=streak,
        personalized_recommendations=recs,
        recent_scans=recent_scans
    )


@app.post("/admin/login", response_model=AuthResponse, tags=["Admin"])
def admin_login(request: AdminLoginRequest):
    expected_secret = os.getenv("ADMIN_SECRET", "safebite_admin_secret_2026")
    if request.admin_secret.strip() != expected_secret:
        raise HTTPException(status_code=401, detail="Invalid admin credentials.")

    return AuthResponse(
        status="success",
        message="Admin authenticated successfully.",
        username="admin",
        role="admin"
    )

@app.get("/admin/history", response_model=AdminHistoryResponse, tags=["Admin"])
def get_admin_history(admin_secret: str = Query(...), db: Session = Depends(get_db)):
    expected_secret = os.getenv("ADMIN_SECRET", "safebite_admin_secret_2026")
    if admin_secret.strip() != expected_secret:
        raise HTTPException(status_code=401, detail="Unauthorized admin access.")

    total_users = db.query(User).count()
    all_scans = db.query(Scan).order_by(Scan.scan_date.desc()).limit(100).all()

    items = [
        ScanItem(
            id=s.id,
            product_name=s.product_name,
            calories=s.calories,
            protein=s.protein,
            carbs=s.carbs,
            fat=s.fat,
            sugar=s.sugar,
            fiber=s.fiber,
            sodium=s.sodium,
            ingredients=s.ingredients,
            health_score=s.health_score,
            classification=s.classification,
            analysis=s.analysis,
            image_path=s.image_path,
            scan_date=s.scan_date.strftime("%Y-%m-%d %H:%M") if s.scan_date else None
        )
        for s in all_scans
    ]

    return AdminHistoryResponse(
        status="success",
        total_users=total_users,
        total_scans=len(all_scans),
        scans=items
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)
