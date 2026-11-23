import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator

# ============================================================================
# MongoDB document models
# ============================================================================

@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    hashed_password: str = ""
    role: str = "user"
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    gender: Optional[str] = None
    is_diabetic: bool = False
    dietary_preference: Optional[str] = "None"
    allergens: Optional[str] = ""
    ingredient_exclusions: Optional[str] = ""
    email: Optional[str] = None
    is_verified: bool = False
    email_verified: bool = False
    verification_code_hash: Optional[str] = None
    verification_expires_at: Optional[datetime.datetime] = None
    verification_last_sent_at: Optional[datetime.datetime] = None
    failed_verification_attempts: int = 0
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    referral_code: Optional[str] = None


@dataclass
class Scan:
    id: Optional[int] = None
    user_id: int = 0
    product_name: str = "Food Product"
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    sugar: Optional[float] = None
    fiber: Optional[float] = None
    sodium: Optional[float] = None
    saturated_fat: Optional[float] = None
    trans_fat: Optional[float] = None
    ingredients: Optional[str] = None
    health_score: float = 70.0
    classification: str = "Moderate"
    analysis: Optional[str] = None
    healthier_alternatives: Optional[str] = None
    benefits: Optional[str] = None
    concerns: Optional[str] = None
    image_path: Optional[str] = None
    scan_date: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class SavedFood:
    id: Optional[int] = None
    user_id: int = 0
    product_name: str = "Saved Food"
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    sugar: Optional[float] = None
    fiber: Optional[float] = None
    sodium: Optional[float] = None
    ingredients: Optional[str] = None
    health_score: Optional[float] = None
    analysis: Optional[str] = None
    image_path: Optional[str] = None
    saved_date: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class Subscription:
    id: Optional[int] = None
    user_id: int = 0
    product_id: str = "safebite_premium_monthly"
    purchase_token_hash: str = ""
    order_id: Optional[str] = None
    status: str = "ACTIVE"  # ACTIVE, EXPIRED, CANCELLED, PENDING, REVOKED
    start_time: Optional[datetime.datetime] = None
    expiry_time: Optional[datetime.datetime] = None
    auto_renewing: bool = True
    verified_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    last_checked_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class Conversation:
    id: Optional[int] = None
    user_id: int = 0
    title: str = "New Conversation"
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class ChatMessage:
    id: Optional[int] = None
    conversation_id: int = 0
    user_id: int = 0
    sender: str = "user"  # "user" or "assistant"
    message: str = ""
    scan_context: Optional[str] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class Coupon:
    id: Optional[int] = None
    code: str = ""
    days_free: int = 30
    max_redemptions: Optional[int] = None
    expires_at: Optional[datetime.datetime] = None
    active: bool = True
    redeemed_count: int = 0
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class CouponRedemption:
    id: Optional[int] = None
    user_id: int = 0
    code: str = ""
    redeemed_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    premium_until: Optional[datetime.datetime] = None


# ============================================================================
# Pydantic Schemas for Requests and Responses
# ============================================================================

class RegisterRequest(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    password: str
    email: Optional[str] = None
    verification_code: Optional[str] = None

class SendVerificationRequest(BaseModel):
    email: str

class SendVerificationResponse(BaseModel):
    status: str
    message: str
    demo_code: Optional[str] = None

class ResendVerificationRequest(BaseModel):
    email: str

class ResendVerificationResponse(BaseModel):
    status: str
    message: str

class VerifyCodeRequest(BaseModel):
    email: str
    code: str

class VerifyCodeResponse(BaseModel):
    status: str
    message: str
    is_valid: bool = True
    username: Optional[str] = None
    token: Optional[str] = None

class VerifyEmailRequest(BaseModel):
    email: str
    code: str

class VerifyEmailResponse(BaseModel):
    status: str
    message: str
    is_valid: bool = True
    username: Optional[str] = None
    token: Optional[str] = None

class LoginRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: str

class GoogleAuthRequest(BaseModel):
    email: str
    name: Optional[str] = None
    google_id: Optional[str] = None
    id_token: Optional[str] = None

class SendWelcomeRequest(BaseModel):
    email: str
    username: Optional[str] = None

class AuthResponse(BaseModel):
    status: str
    message: str
    username: Optional[str] = None
    role: Optional[str] = "user"
    email: Optional[str] = None
    verification_required: Optional[bool] = False
    is_verified: Optional[bool] = True
    token: Optional[str] = None

class UserProfileRequest(BaseModel):
    username: str
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    gender: Optional[str] = None
    is_diabetic: bool = False
    dietary_preference: Optional[str] = "None"
    allergens: Optional[str] = ""
    ingredient_exclusions: Optional[str] = ""

class UserProfileResponse(BaseModel):
    status: str
    username: str
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    gender: Optional[str] = None
    is_diabetic: bool = False
    dietary_preference: Optional[str] = "None"
    allergens: Optional[str] = ""
    ingredient_exclusions: Optional[str] = ""
    bmi: Optional[float] = None
    bmi_category: Optional[str] = None

class ManualAnalysisRequest(BaseModel):
    product_name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    sugar: Optional[float] = 0.0
    fiber: Optional[float] = 0.0
    sodium: Optional[float] = 0.0
    ingredients: Optional[str] = ""
    username: Optional[str] = None

class HealthScoreRequest(BaseModel):
    product_name: str = Field(min_length=1, max_length=200)
    calories: float = Field(ge=0)
    protein: float = Field(ge=0)
    carbs: float = Field(ge=0)
    fat: float = Field(ge=0)
    sugar: float = Field(default=0.0, ge=0)
    fiber: float = Field(default=0.0, ge=0)
    sodium: float = Field(default=0.0, ge=0)
    ingredients: Optional[str] = ""
    is_diabetic: bool = False

class NutritionData(BaseModel):
    calories: float
    protein: float
    carbs: float
    carbohydrates: Optional[float] = None
    fat: float
    sugar: Optional[float] = 0.0
    fiber: Optional[float] = 0.0
    sodium: Optional[float] = 0.0
    saturated_fat: Optional[float] = None
    trans_fat: Optional[float] = None
    added_sugar: Optional[float] = None
    serving_size: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def sync_carbs(cls, data):
        if isinstance(data, dict):
            if "carbohydrates" in data and data["carbohydrates"] is not None and "carbs" not in data:
                data["carbs"] = float(data["carbohydrates"])
            elif "carbs" in data and data["carbs"] is not None and ("carbohydrates" not in data or data["carbohydrates"] is None):
                data["carbohydrates"] = float(data["carbs"])
        return data

class AllergenAlertItem(BaseModel):
    name: str
    match_type: str = "confirmed"  # "confirmed" or "possible"
    matched_term: str = ""
    is_user_allergy: bool = False
    severity: str = "warning"  # "critical", "warning", "info"
    message: str = ""

class AnalysisResponse(BaseModel):
    status: str
    product_name: str
    nutrition: NutritionData
    health_score: float
    classification: str
    category: str # Backwards compatibility alias for classification
    ingredients: Optional[str] = None
    analysis: str
    recommendation: str # Backwards compatibility alias for analysis
    healthier_alternatives: List[str] = []
    benefits: List[str] = []
    concerns: List[str] = []
    image_url: Optional[str] = None
    serving_size: Optional[str] = None
    allergens: List[str] = []
    allergy_alerts: List[AllergenAlertItem] = []
    ingredient_completeness: Optional[str] = "complete"  # "complete", "partial", "unreadable", "unavailable"
    allergen_free_disclaimer: Optional[str] = (
        "The absence of an allergen alert does not guarantee a product is 100% allergen-free. "
        "Cross-contamination may occur during manufacturing. Always inspect original packaging."
    )
    analysis_source: Optional[str] = "Gemini Vision AI"
    analysis_mode: Optional[str] = "packaged"  # "packaged" or "food_object"
    confidence: Optional[float] = None
    food_category: Optional[str] = None
    portion_size_estimated: Optional[bool] = None
    serving_options: List[str] = []
    alternative_candidates: List[str] = []
    missing_fields: List[str] = []
    nutrition_source: Optional[str] = None
    is_estimate: Optional[bool] = False
    warnings: List[str] = []

    # Universal Food Image Recognition & Section 6 schema compatibility
    food_mode: Optional[str] = None  # "packaged" | "unpackaged"
    food_name: Optional[str] = None  # Canonical food title
    identification_confidence: Optional[float] = None  # 0.0 - 1.0
    serving_size_g: Optional[float] = None  # Gram weight
    nutrition_is_estimated: Optional[bool] = None  # True for unpackaged/visual estimates
    health_category: Optional[str] = None  # "Healthy" | "Moderate" | "Unhealthy"
    data_confidence: Optional[str] = "medium"  # "high" | "medium" | "low"
    explanation: Optional[str] = None  # Descriptive analysis text
    recommendations: List[str] = []  # Nutrition & dietary recommendations
    requires_user_confirmation: Optional[bool] = False  # Flag when low confidence or ambiguous

    @model_validator(mode="before")
    @classmethod
    def populate_mode_and_aliases(cls, data):
        if not isinstance(data, dict):
            return data

        # Food Mode
        a_mode = data.get("analysis_mode") or "packaged"
        f_mode = data.get("food_mode")
        if not f_mode:
            f_mode = "unpackaged" if a_mode == "food_object" else "packaged"
        data["food_mode"] = f_mode
        if not data.get("analysis_mode"):
            data["analysis_mode"] = "food_object" if f_mode == "unpackaged" else "packaged"

        # Food Name
        name = data.get("product_name") or data.get("food_name") or ("Food Item" if f_mode == "unpackaged" else "Packaged Food")
        data["product_name"] = name
        data["food_name"] = data.get("food_name") or name

        # Confidence
        conf = data.get("confidence")
        if conf is None:
            conf = data.get("identification_confidence")
        data["confidence"] = conf
        data["identification_confidence"] = conf if conf is not None else (0.90 if f_mode == "packaged" else 0.85)

        # Health Category / Classification
        cls_val = data.get("classification") or data.get("health_category") or data.get("category") or "Moderate"
        data["classification"] = cls_val
        data["category"] = cls_val
        data["health_category"] = cls_val

        # Explanation / Analysis
        expl = data.get("analysis") or data.get("explanation") or data.get("recommendation") or ""
        data["analysis"] = expl
        data["explanation"] = expl
        data["recommendation"] = expl

        # Recommendations / Healthier Alternatives
        recs = data.get("recommendations") or data.get("healthier_alternatives") or []
        data["recommendations"] = recs
        data["healthier_alternatives"] = recs

        # Estimate flag
        is_est = data.get("is_estimate")
        if is_est is None:
            is_est = data.get("nutrition_is_estimated")
        if is_est is None:
            is_est = (f_mode == "unpackaged")
        data["is_estimate"] = bool(is_est)
        data["nutrition_is_estimated"] = bool(is_est)

        # Grams from serving_size if missing
        if data.get("serving_size_g") is None and data.get("serving_size"):
            import re
            m = re.search(r"(\d+(?:\.\d+)?)\s*g", str(data["serving_size"]))
            if m:
                try:
                    data["serving_size_g"] = float(m.group(1))
                except ValueError:
                    pass

        # Data Confidence
        if not data.get("data_confidence"):
            if f_mode == "packaged":
                data["data_confidence"] = "high"
            else:
                c = data.get("identification_confidence") or 0.85
                data["data_confidence"] = "high" if c >= 0.88 else ("medium" if c >= 0.70 else "low")

        # Requires confirmation
        if "requires_user_confirmation" not in data or data.get("requires_user_confirmation") is None:
            c = data.get("identification_confidence") or 0.85
            data["requires_user_confirmation"] = bool(c < 0.70 or data.get("data_confidence") == "low")

        return data

class LookupFoodRequest(BaseModel):
    food_name: str = Field(min_length=1, max_length=200)
    serving_size_g: Optional[float] = None
    is_diabetic: Optional[bool] = False
    username: Optional[str] = None

class RecalculatePortionRequest(BaseModel):
    product_name: str
    base_calories: float
    base_protein: float
    base_carbs: float
    base_fat: float
    base_sugar: Optional[float] = 0.0
    base_fiber: Optional[float] = 0.0
    base_sodium: Optional[float] = 0.0
    base_saturated_fat: Optional[float] = None
    base_trans_fat: Optional[float] = None
    ingredients: Optional[str] = ""
    multiplier: float = 1.0
    serving_size: str = "100g"
    is_diabetic: Optional[bool] = False

class HealthScoreResponse(BaseModel):
    status: str
    product_name: str
    nutrition: NutritionData
    health_score: float
    classification: str
    reasons: List[str] = []
    benefits: List[str] = []
    concerns: List[str] = []
    healthier_alternatives: List[str] = []

class BarcodeResponse(BaseModel):
    status: str
    product_name: str
    nutrition: NutritionData
    health_score: float
    classification: str
    category: str
    recommendation: str
    healthier_alternatives: List[str] = []
    ingredients: Optional[str] = None

class IndianFoodItem(BaseModel):
    name: str
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    sodium: Optional[float] = None
    category: Optional[str] = None
    region: Optional[str] = None

class IndianFoodSearchResponse(BaseModel):
    status: str
    results: List[IndianFoodItem] = []

class ScanItem(BaseModel):
    id: int
    product_name: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    sugar: Optional[float] = None
    fiber: Optional[float] = None
    sodium: Optional[float] = None
    ingredients: Optional[str] = None
    health_score: Optional[float] = None
    classification: Optional[str] = None
    analysis: Optional[str] = None
    image_path: Optional[str] = None
    scan_date: Optional[str] = None

class HistoryResponse(BaseModel):
    status: str
    scans: List[ScanItem] = []

class SavedFoodRequest(BaseModel):
    username: str
    product_name: str = "Food"
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    sugar: Optional[float] = None
    fiber: Optional[float] = None
    sodium: Optional[float] = None
    ingredients: Optional[str] = ""
    health_score: Optional[float] = None
    analysis: Optional[str] = ""
    image_path: Optional[str] = None

class SavedFoodItem(BaseModel):
    id: int
    product_name: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    sugar: Optional[float] = None
    fiber: Optional[float] = None
    sodium: Optional[float] = None
    ingredients: Optional[str] = None
    health_score: Optional[float] = None
    analysis: Optional[str] = None
    image_path: Optional[str] = None
    saved_date: Optional[str] = None

class SavedFoodsResponse(BaseModel):
    status: str
    foods: List[SavedFoodItem] = []

class SimpleStatusResponse(BaseModel):
    status: str
    message: Optional[str] = None
    id: Optional[int] = None
    scan_id: Optional[int] = None
    deleted_count: Optional[int] = None

class DiabetesCheckRequest(BaseModel):
    username: str

class DiabetesCheckResponse(BaseModel):
    status: str
    risk_score: int
    risk_level: str
    recommendations: List[str] = []
    disclaimer: str = (
        "Disclaimer: This evaluation is for informational wellness purposes only and "
        "is not a medical diagnosis or treatment plan. Always consult a healthcare professional."
    )

class ChatMessageRequest(BaseModel):
    message: str
    username: Optional[str] = None
    conversation_id: Optional[int] = None
    scan_id: Optional[int] = None
    scan_context: Optional[Dict[str, Any]] = None

class ChatMessageResponse(BaseModel):
    status: str
    response: str
    model: Optional[str] = None
    conversation_id: Optional[int] = None
    title: Optional[str] = None
    follow_up_suggestions: Optional[List[str]] = None

class ConversationSummary(BaseModel):
    id: int
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0

class ConversationDetailResponse(BaseModel):
    id: int
    title: str
    created_at: str
    updated_at: str
    messages: List[Dict[str, Any]] = []

class HealthCheckResponse(BaseModel):
    status: str
    message: str
    database_connected: bool = False
    gemini_configured: bool = False
    groq_configured: bool = False # backwards compatibility
    ocr_ready: bool = True

class DashboardRecentScan(BaseModel):
    id: int
    product_name: str
    health_score: Optional[float] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    scan_date: Optional[str] = None

class DashboardStatsResponse(BaseModel):
    status: str
    total_scans: int = 0
    avg_health_score: float = 0.0
    bmi: Optional[float] = None
    bmi_category: Optional[str] = None
    is_diabetic: bool = False
    smart_insight: Optional[str] = None
    healthy_count: int = 0
    moderate_count: int = 0
    unhealthy_count: int = 0
    healthy_percentage: float = 0.0
    moderate_percentage: float = 0.0
    unhealthy_percentage: float = 0.0
    scan_streak: int = 0
    personalized_recommendations: List[str] = []
    recent_scans: List[DashboardRecentScan] = []

class ComparedProductData(BaseModel):
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    sugar: float = 0.0
    sodium: float = 0.0
    health_score: float
    classification: str

class CompareFoodRequest(BaseModel):
    product_a_name: str
    product_a_calories: float
    product_a_protein: float
    product_a_carbs: float
    product_a_fat: float
    product_a_sugar: Optional[float] = 0.0
    product_a_sodium: Optional[float] = 0.0

    product_b_name: str
    product_b_calories: float
    product_b_protein: float
    product_b_carbs: float
    product_b_fat: float
    product_b_sugar: Optional[float] = 0.0
    product_b_sodium: Optional[float] = 0.0

class CompareFoodResponse(BaseModel):
    status: str
    product_a: ComparedProductData
    product_b: ComparedProductData
    healthier_choice: str
    comparison_summary: str
    key_differences: List[str] = []

class AdminLoginRequest(BaseModel):
    admin_secret: str

class AdminHistoryResponse(BaseModel):
    status: str
    total_users: int
    total_scans: int
    scans: List[ScanItem] = []

class VerifySubscriptionRequest(BaseModel):
    purchase_token: str
    product_id: str = "safebite_premium_monthly"
    package_name: str = "com.example.safebite"
    order_id: Optional[str] = None

class SubscriptionStatusResponse(BaseModel):
    is_premium: bool
    status: str
    product_id: Optional[str] = None
    order_id: Optional[str] = None
    expiry_time: Optional[str] = None
    auto_renewing: bool = False
    message: str = ""
    source: Optional[str] = None  # "play", "coupon", or None
    premium_until: Optional[str] = None


class CouponRedeemRequest(BaseModel):
    code: str


class CouponRedeemResponse(BaseModel):
    success: bool
    premium_until: Optional[str] = None
    error_code: Optional[str] = None
    message: str


# ============================================================================
# Universal Food Product Search & Health Analyzer Models
# ============================================================================

class ProductNutritionValues(BaseModel):
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbohydrates: Optional[float] = None
    total_sugar: Optional[float] = None
    added_sugar: Optional[float] = None
    total_fat: Optional[float] = None
    saturated_fat: Optional[float] = None
    trans_fat: Optional[float] = None
    sodium: Optional[float] = None
    fiber: Optional[float] = None


class ProductSummaryItem(BaseModel):
    id: str
    name: str
    brand: str
    category: str = "General"
    barcode: Optional[str] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    health_score: Optional[float] = None
    classification: Optional[str] = None  # Healthy, Moderate, Unhealthy
    calories: Optional[float] = None
    sugar: Optional[float] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    sodium: Optional[float] = None
    data_source: str = "SafeBite Indian Food Database"


class ProductSearchResponse(BaseModel):
    status: str = "success"
    query: str
    total: int
    page: int = 1
    page_size: int = 20
    products: List[ProductSummaryItem] = []
    suggestions: List[str] = []


class ProductDetailResponse(BaseModel):
    status: str = "success"
    id: str
    name: str
    brand: str
    barcode: Optional[str] = None
    category: str = "General"
    image_url: Optional[str] = None
    ingredients: Optional[str] = None
    serving_size: Optional[str] = None
    nutrition_per_100g: ProductNutritionValues
    nutrition_per_serving: Optional[ProductNutritionValues] = None
    allergens: List[str] = []
    additives: List[str] = []
    additive_details: List[str] = []
    fssai_warnings: List[str] = []
    health_score: Optional[float] = None
    classification: Optional[str] = None  # Healthy, Moderate, Unhealthy
    positive_points: List[str] = []
    negative_points: List[str] = []
    healthier_alternatives: List[str] = []
    data_source: str = "SafeBite Indian Food Database"
    last_updated: Optional[str] = None
    is_data_insufficient: bool = False


class ProductHealthAnalysisResponse(BaseModel):
    status: str = "success"
    product_id: str
    product_name: str
    health_score: float
    classification: str  # Healthy, Moderate, Unhealthy
    positive_points: List[str] = []
    negative_points: List[str] = []
    fssai_warnings: List[str] = []
    additive_information: List[str] = []
    allergen_warnings: List[str] = []
    healthier_alternatives: List[str] = []
    personalized_suitability: Dict[str, Any] = {}
    medical_disclaimer: str = (
        "SafeBite provides nutritional education and transparent health scores based on FSSAI & international guidance. "
        "This evaluation is for informational purposes only and does not constitute medical advice."
    )


class ProductCompareItem(BaseModel):
    id: str
    name: str
    brand: str
    category: Optional[str] = None
    image_url: Optional[str] = None
    health_score: float
    classification: str
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbohydrates: Optional[float] = None
    total_sugar: Optional[float] = None
    total_fat: Optional[float] = None
    saturated_fat: Optional[float] = None
    sodium: Optional[float] = None
    fiber: Optional[float] = None
    favorable_points: List[str] = []


class ProductCompareIdsRequest(BaseModel):
    product_ids: List[str] = Field(..., min_length=1, max_length=5)


class ProductMultiCompareResponse(BaseModel):
    status: str = "success"
    products: List[ProductCompareItem]
    healthier_choice_id: Optional[str] = None
    healthier_choice_name: Optional[str] = None
    comparison_summary: str
    key_differences: List[str] = []


class AdminAddProductRequest(BaseModel):
    admin_secret: Optional[str] = None
    id: Optional[str] = None
    name: str
    brand: str
    barcode: Optional[str] = None
    category: str = "General"
    image_url: Optional[str] = None
    ingredients: Optional[str] = None
    serving_size: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbohydrates: Optional[float] = None
    total_sugar: Optional[float] = None
    added_sugar: Optional[float] = None
    total_fat: Optional[float] = None
    saturated_fat: Optional[float] = None
    trans_fat: Optional[float] = None
    sodium: Optional[float] = None
    fiber: Optional[float] = None
    allergens: Optional[List[str]] = None
    additives: Optional[List[str]] = None


# ============================================================================
# Referral, Sync, Feedback & Moderation Models
# ============================================================================

@dataclass
class ReferralRecord:
    id: Optional[int] = None
    referrer_user_id: int = 0
    referee_user_id: int = 0
    referral_code: str = ""
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class UserSyncBackup:
    id: Optional[int] = None
    user_id: int = 0
    history_json: str = "[]"
    saved_foods_json: str = "[]"
    profiles_json: str = "[]"
    settings_json: str = "{}"
    device_id: Optional[str] = None
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class FeedbackItem:
    id: Optional[int] = None
    user_id: Optional[int] = None
    feedback_type: str = "general"
    message: str = ""
    rating: Optional[int] = None
    screenshot_path: Optional[str] = None
    app_version: Optional[str] = None
    os_version: Optional[str] = None
    device_model: Optional[str] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class ProductSubmission:
    id: Optional[int] = None
    barcode: str = ""
    product_name: str = ""
    brand: Optional[str] = None
    category: Optional[str] = None
    serving_size: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbohydrates: Optional[float] = None
    total_sugar: Optional[float] = None
    total_fat: Optional[float] = None
    saturated_fat: Optional[float] = None
    sodium: Optional[float] = None
    fiber: Optional[float] = None
    ingredients: Optional[str] = None
    submitted_by_user_id: Optional[int] = None
    submission_count: int = 1
    is_approved: bool = False
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class ProductReport:
    id: Optional[int] = None
    barcode: str = ""
    user_id: Optional[int] = None
    reason: str = ""
    details: Optional[str] = None
    status: str = "pending"
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


class ReferralInfoResponse(BaseModel):
    referral_code: str
    referral_link: str
    total_referrals: int
    days_earned: int
    max_referrals: int = 20


class ApplyReferralRequest(BaseModel):
    referral_code: str


class ApplyReferralResponse(BaseModel):
    status: str = "success"
    message: str
    days_granted: int = 7
    premium_until: Optional[str] = None


class CloudSyncBackupRequest(BaseModel):
    history: List[Dict[str, Any]] = []
    saved_foods: List[Dict[str, Any]] = []
    profiles: Optional[List[Dict[str, Any]]] = None
    settings: Optional[Dict[str, Any]] = None
    device_id: Optional[str] = None


class CloudSyncBackupResponse(BaseModel):
    status: str = "success"
    message: str
    synced_at: str
    history_count: int
    saved_foods_count: int


class CloudSyncRestoreResponse(BaseModel):
    status: str = "success"
    synced_at: Optional[str] = None
    history: List[Dict[str, Any]] = []
    saved_foods: List[Dict[str, Any]] = []
    profiles: List[Dict[str, Any]] = []
    settings: Dict[str, Any] = {}


class SubmitFeedbackRequest(BaseModel):
    feedback_type: str = "general"
    message: str
    rating: Optional[int] = None
    screenshot_base64: Optional[str] = None
    app_version: Optional[str] = None
    os_version: Optional[str] = None
    device_model: Optional[str] = None


class SubmitFeedbackResponse(BaseModel):
    status: str = "success"
    message: str
    feedback_id: int


class SubmitProductLabelRequest(BaseModel):
    barcode: str
    product_name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    serving_size: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbohydrates: Optional[float] = None
    total_sugar: Optional[float] = None
    total_fat: Optional[float] = None
    saturated_fat: Optional[float] = None
    sodium: Optional[float] = None
    fiber: Optional[float] = None
    ingredients: Optional[str] = None
    label_image_base64: Optional[str] = None


class SubmitProductLabelResponse(BaseModel):
    status: str = "success"
    message: str
    submission_id: int
    is_approved: bool
    match_count: int
    community_verified: bool = False


class ReportProductRequest(BaseModel):
    barcode: str
    reason: str
    details: Optional[str] = None


class ReportProductResponse(BaseModel):
    status: str = "success"
    message: str
    report_id: int


class AdminModerationItem(BaseModel):
    id: int
    barcode: str
    product_name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    submission_count: int
    is_approved: bool
    created_at: str


class AdminModerationListResponse(BaseModel):
    status: str = "success"
    submissions: List[AdminModerationItem] = []
    total: int = 0
