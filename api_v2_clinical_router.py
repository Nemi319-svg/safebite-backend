"""
SafeBite Clinical & Regional Intelligence API v2 Router
=======================================================
FastAPI endpoints exposing regional nutrition analytics, additive toxicology scanning,
biophysical continuous glucose curve simulation, personalized weekly meal planning,
and Atwater nutrition label normalization.
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from backend.data.regional_indian_nutrition_db import regional_food_db
from backend.regional_nutrition_engine import regional_nutrition_engine
from backend.additive_safety_engine import additive_safety_engine
from backend.glycemic_clinical_engine import glycemic_clinical_engine
from backend.meal_planner_engine import smart_meal_planner_engine, UserBiometricProfile
from backend.label_normalization_service import label_normalization_service
from backend.allergen_detection_engine import allergen_detection_engine

router = APIRouter(prefix="/api/v2", tags=["Clinical & Regional Nutrition v2"])


# -------------------------------------------------------------
# Request & Response Schemas
# -------------------------------------------------------------

class ThaliAnalysisRequest(BaseModel):
    meal_name: str = "Regional Meal"
    food_ids: List[str]


class AdditiveScanRequest(BaseModel):
    ingredients_text: str


class GlycemicSimRequest(BaseModel):
    carbs_g: float
    sugar_g: float = 0.0
    fiber_g: float = 0.0
    protein_g: float = 0.0
    fat_g: float = 0.0
    glycemic_index: Optional[int] = None
    fasting_glucose_mg_dl: float = 95.0
    is_diabetic: bool = False


class MealPlanRequest(BaseModel):
    age: int
    gender: str = "male"
    height_cm: float
    weight_kg: float
    activity_level: str = "moderate"
    dietary_goal: str = "maintenance"
    is_diabetic: bool = False
    is_hypertensive: bool = False
    is_vegetarian: bool = True
    is_vegan: bool = False
    is_gluten_free: bool = False


class LabelNormalizationRequest(BaseModel):
    product_name: str = "Food Product"
    raw_calories: Optional[float] = None
    raw_energy_kj: Optional[float] = None
    raw_protein_g: Optional[float] = None
    raw_carbs_g: Optional[float] = None
    raw_fiber_g: Optional[float] = None
    raw_sugar_g: Optional[float] = None
    raw_added_sugar_g: Optional[float] = None
    raw_fat_g: Optional[float] = None
    raw_sat_fat_g: Optional[float] = None
    raw_trans_fat_g: Optional[float] = None
    raw_sodium_mg: Optional[float] = None
    raw_salt_g: Optional[float] = None
    serving_size_g: Optional[float] = 100.0


class AllergenScanRequest(BaseModel):
    ingredients_text: str
    user_declared_allergens: Optional[List[str]] = None


# -------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------

@router.get("/regional-foods")
def list_regional_foods(
    query: Optional[str] = Query(None, description="Search term across name, state, or ingredients"),
    region: Optional[str] = Query(None, description="North, South, West, East"),
    state: Optional[str] = Query(None, description="Specific Indian state"),
    diabetic_only: bool = Query(False, description="Filter only diabetic safe items"),
    gluten_free_only: bool = Query(False, description="Filter only gluten-free items"),
    min_health_score: int = Query(0, ge=0, le=100)
):
    """Retrieves regional Indian foods matching query filters."""
    query_str = query if isinstance(query, str) else None
    region_str = region if isinstance(region, str) else None
    state_str = state if isinstance(state, str) else None
    is_diabetic = diabetic_only if isinstance(diabetic_only, bool) else False
    is_gluten_free = gluten_free_only if isinstance(gluten_free_only, bool) else False
    min_score = min_health_score if isinstance(min_health_score, (int, float)) else 0

    if query_str:
        items = regional_food_db.search_by_name(query_str)
    else:
        items = regional_food_db.get_all()

    filtered = []
    for f in items:
        if region_str and f.region.lower() != region_str.lower():
            continue
        if state_str and f.state.lower() != state_str.lower():
            continue
        if is_diabetic and not f.is_diabetic_safe:
            continue
        if is_gluten_free and not f.is_gluten_free:
            continue
        if f.health_score < min_score:
            continue
        filtered.append(f)
    return {"total_count": len(filtered), "foods": filtered}


@router.get("/regional-foods/{food_id}")
def get_regional_food_detail(food_id: str):
    """Returns detailed nutrition and clinical density report for a single regional dish."""
    food = regional_food_db.get_by_id(food_id)
    if not food:
        raise HTTPException(status_code=404, detail="Regional food item not found.")
    density = regional_nutrition_engine.calculate_nutrient_density(food)
    swaps = regional_nutrition_engine.suggest_healthier_swaps(food_id)
    return {
        "food": food,
        "density_report": density,
        "healthier_swaps": swaps
    }


@router.post("/regional-thali/analyze")
def analyze_thali(req: ThaliAnalysisRequest):
    """Analyzes a multi-item authentic Indian regional meal combination."""
    result = regional_nutrition_engine.analyze_regional_thali(req.meal_name, req.food_ids)
    return result


@router.get("/regional-thalis/curated")
def get_curated_thalis():
    """Provides canonical pre-configured regional thalis (Rajasthani, Punjabi, Maharashtrian, South Indian)."""
    return regional_nutrition_engine.get_curated_thalis()


@router.post("/additive-toxicology/scan")
def scan_additives(req: AdditiveScanRequest):
    """Scans raw OCR ingredient statements for INS/E-numbers and evaluates chemical toxicity."""
    result = additive_safety_engine.scan_ingredients_text(req.ingredients_text)
    return result


@router.post("/glycemic-cgm/simulate")
def simulate_cgm_curve(req: GlycemicSimRequest):
    """Simulates 180-minute Continuous Glucose Monitor trajectory, iAUC, and peak excursions."""
    result = glycemic_clinical_engine.simulate_glucose_curve(
        carbs_g=req.carbs_g,
        sugar_g=req.sugar_g,
        fiber_g=req.fiber_g,
        protein_g=req.protein_g,
        fat_g=req.fat_g,
        glycemic_index=req.glycemic_index,
        fasting_glucose_mg_dl=req.fasting_glucose_mg_dl,
        is_diabetic=req.is_diabetic
    )
    return result


@router.post("/meal-plans/generate")
def generate_meal_plan(req: MealPlanRequest):
    """Calculates BMR/TDEE and generates a tailored 7-day meal plan with organized grocery list."""
    profile = UserBiometricProfile(
        age=req.age,
        gender=req.gender,
        height_cm=req.height_cm,
        weight_kg=req.weight_kg,
        activity_level=req.activity_level,
        dietary_goal=req.dietary_goal,
        is_diabetic=req.is_diabetic,
        is_hypertensive=req.is_hypertensive,
        is_vegetarian=req.is_vegetarian,
        is_vegan=req.is_vegan,
        is_gluten_free=req.is_gluten_free
    )
    plan = smart_meal_planner_engine.generate_weekly_plan(profile)
    return plan


@router.post("/normalize-label")
def normalize_nutrition_label(req: LabelNormalizationRequest):
    """Cleans OCR text, standardizes units, and performs Atwater caloric integrity validation."""
    result = label_normalization_service.normalize_facts(
        raw_calories=req.raw_calories,
        raw_energy_kj=req.raw_energy_kj,
        raw_protein_g=req.raw_protein_g,
        raw_carbs_g=req.raw_carbs_g,
        raw_fiber_g=req.raw_fiber_g,
        raw_sugar_g=req.raw_sugar_g,
        raw_added_sugar_g=req.raw_added_sugar_g,
        raw_fat_g=req.raw_fat_g,
        raw_sat_fat_g=req.raw_sat_fat_g,
        raw_trans_fat_g=req.raw_trans_fat_g,
        raw_sodium_mg=req.raw_sodium_mg,
        raw_salt_g=req.raw_salt_g,
        serving_size_g=req.serving_size_g,
        product_name=req.product_name
    )
    return result


@router.post("/allergens/scan")
def scan_allergens(req: AllergenScanRequest):
    """Screens packaging statements for 14 global allergens and patient-specific medical conflicts."""
    result = allergen_detection_engine.scan_ingredients(
        ingredients_text=req.ingredients_text,
        user_declared_allergens=req.user_declared_allergens
    )
    return result
