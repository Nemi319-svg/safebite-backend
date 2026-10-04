import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from database import Base

# ============================================================================
# SQLAlchemy ORM Models
# ============================================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user") # 'user' or 'admin'
    age = Column(Integer, nullable=True)
    height = Column(Float, nullable=True) # cm
    weight = Column(Float, nullable=True) # kg
    gender = Column(String(20), nullable=True)
    is_diabetic = Column(Boolean, default=False)
    email = Column(String(150), unique=True, index=True, nullable=True)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    scans = relationship("Scan", back_populates="user", cascade="all, delete-orphan")
    saved_foods = relationship("SavedFood", back_populates="user", cascade="all, delete-orphan")


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String(200), default="Food Product")
    calories = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)
    carbs = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    sugar = Column(Float, nullable=True)
    fiber = Column(Float, nullable=True)
    sodium = Column(Float, nullable=True)
    saturated_fat = Column(Float, nullable=True)
    trans_fat = Column(Float, nullable=True)
    ingredients = Column(Text, nullable=True)
    health_score = Column(Float, default=70.0)
    classification = Column(String(50), default="Moderate") # Healthy, Moderate, Unhealthy
    analysis = Column(Text, nullable=True)
    healthier_alternatives = Column(Text, nullable=True) # JSON or comma-separated string
    benefits = Column(Text, nullable=True)
    concerns = Column(Text, nullable=True)
    image_path = Column(String(300), nullable=True)
    scan_date = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="scans")


class SavedFood(Base):
    __tablename__ = "saved_foods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String(200), default="Saved Food")
    calories = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)
    carbs = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    sugar = Column(Float, nullable=True)
    fiber = Column(Float, nullable=True)
    sodium = Column(Float, nullable=True)
    ingredients = Column(Text, nullable=True)
    health_score = Column(Float, nullable=True)
    analysis = Column(Text, nullable=True)
    image_path = Column(String(300), nullable=True)
    saved_date = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="saved_foods")


# ============================================================================
# Pydantic Schemas for Requests and Responses
# ============================================================================

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    verification_code: Optional[str] = None

class SendVerificationRequest(BaseModel):
    email: str

class SendVerificationResponse(BaseModel):
    status: str
    message: str
    demo_code: Optional[str] = None

class VerifyCodeRequest(BaseModel):
    email: str
    code: str

class VerifyCodeResponse(BaseModel):
    status: str
    message: str
    is_valid: bool

class LoginRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    status: str
    message: str
    username: Optional[str] = None
    role: Optional[str] = "user"

class UserProfileRequest(BaseModel):
    username: str
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    gender: Optional[str] = None
    is_diabetic: bool = False

class UserProfileResponse(BaseModel):
    status: str
    username: str
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    gender: Optional[str] = None
    is_diabetic: bool = False
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

class NutritionData(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float
    sugar: Optional[float] = 0.0
    fiber: Optional[float] = 0.0
    sodium: Optional[float] = 0.0

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

class BarcodeResponse(BaseModel):
    status: str
    product_name: str
    nutrition: NutritionData
    health_score: float
    classification: str
    category: str
    recommendation: str
    healthier_alternatives: List[str] = []

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

class ChatMessageResponse(BaseModel):
    status: str
    response: str
    model: Optional[str] = None

class HealthCheckResponse(BaseModel):
    status: str
    message: str
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
