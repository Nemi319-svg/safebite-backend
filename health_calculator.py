from typing import Dict, List, Tuple, Any

def calculate_health_score(
    calories: float,
    protein: float,
    carbs: float,
    fat: float,
    sugar: float = 0.0,
    fiber: float = 0.0,
    sodium: float = 0.0,
    is_diabetic: bool = False
) -> Tuple[float, str, List[str], List[str], List[str]]:
    """
    Computes a transparent health score (0-100) based on nutritional values.
    Returns:
        (final_score, classification, reasons, benefits, concerns)
    """
    score = 70.0 # Starting baseline score
    reasons: List[str] = []
    benefits: List[str] = []
    concerns: List[str] = []

    # 1. Calories Evaluation
    if calories > 500:
        score -= 20
        reasons.append("High calorie density (>500 kcal) [-20 pts]")
        concerns.append("Very high calorie density per serving")
    elif calories > 300:
        score -= 10
        reasons.append("Moderate to high calories (>300 kcal) [-10 pts]")
        concerns.append("Moderate calorie load")
    elif 0 <= calories <= 200:
        score += 5
        reasons.append("Low calorie profile (<=200 kcal) [+5 pts]")
        benefits.append("Light and low in calories")

    # 2. Total Fat Evaluation
    if fat > 20:
        score -= 20
        reasons.append("High total fat content (>20g) [-20 pts]")
        concerns.append("Elevated total fat content")
    elif fat > 15:
        score -= 10
        reasons.append("Moderate fat content (>15g) [-10 pts]")
        concerns.append("Moderate fat levels")
    elif 0 <= fat <= 10:
        score += 5
        reasons.append("Low fat formulation (<=10g) [+5 pts]")
        benefits.append("Low in fat")

    # 3. Protein Evaluation
    if protein >= 10:
        score += 10
        reasons.append("Rich in protein (>=10g) [+10 pts]")
        benefits.append("Excellent source of dietary protein for muscle repair")
    elif protein >= 5:
        score += 5
        reasons.append("Adequate protein source (>=5g) [+5 pts]")
        benefits.append("Good source of protein")

    # 4. Carbohydrates Evaluation
    if carbs > 60:
        score -= 15
        reasons.append("High carbohydrate content (>60g) [-15 pts]")
        concerns.append("High carbohydrate load")
    elif carbs > 40:
        score -= 8
        reasons.append("Moderate carbohydrate content (>40g) [-8 pts]")

    # 5. Sugar Evaluation
    if sugar > 20:
        score -= 20
        reasons.append("High added sugars (>20g) [-20 pts]")
        concerns.append("Excessive sugar content")
    elif sugar > 10:
        score -= 10
        reasons.append("Elevated sugar (>10g) [-10 pts]")
        concerns.append("Contains noticeable sugar")
    elif sugar > 0 and sugar <= 3:
        score += 5
        reasons.append("Minimal sugar (<=3g) [+5 pts]")
        benefits.append("Very low in sugar")

    # 6. Fiber Evaluation
    if fiber >= 5:
        score += 8
        reasons.append("High dietary fiber (>=5g) [+8 pts]")
        benefits.append("Rich in digestive fiber")
    elif fiber >= 2:
        score += 4
        reasons.append("Contains dietary fiber (>=2g) [+4 pts]")
        benefits.append("Provides dietary fiber")

    # 7. Sodium Evaluation (mg)
    if sodium > 500:
        score -= 15
        reasons.append("Very high sodium (>500mg) [-15 pts]")
        concerns.append("High sodium level, may affect blood pressure")
    elif sodium > 250:
        score -= 8
        reasons.append("Moderate sodium (>250mg) [-8 pts]")

    # 8. Diabetic Penalty Adjustment
    if is_diabetic:
        if carbs > 50:
            score -= 15
            reasons.append("Diabetic sensitivity: Carbs exceed 50g [-15 pts]")
            concerns.append("May cause notable blood glucose elevation")
        if sugar > 8:
            score -= 12
            reasons.append("Diabetic sensitivity: Sugar exceeds 8g [-12 pts]")
            concerns.append("High glycemic impact for diabetics")

    # Clamp final score between 0 and 100
    final_score = max(0.0, min(100.0, score))

    # Classification
    if final_score >= 70:
        classification = "Healthy"
    elif final_score >= 40:
        classification = "Moderate"
    else:
        classification = "Unhealthy"

    return final_score, classification, reasons, benefits, concerns


def get_healthier_alternatives(product_name: str, classification: str) -> List[str]:
    """
    Returns curated, realistic healthier food alternatives based on product category.
    """
    p_lower = (product_name or "").lower()

    if any(k in p_lower for k in ["chip", "crisp", "wafer", "nacho", "dorito", "lays", "kurkure", "snack"]):
        return [
            "Roasted makhana (fox nuts) with olive oil & turmeric",
            "Air-popped popcorn (unsalted/light pink salt)",
            "Baked ragi & beetroot crisps",
            "Roasted salted chana (chickpeas)"
        ]
    elif any(k in p_lower for k in ["noodle", "maggi", "ramen", "pasta", "yippee"]):
        return [
            "Whole wheat millet noodles with fresh veggies",
            "Steamed vegetable vermicelli (seviyan upma)",
            "Vegetable oats khichdi",
            "Zucchini noodles (zoodles) with stir-fry veggies"
        ]
    elif any(k in p_lower for k in ["biscuit", "cookie", "oreo", "parle", "rusk", "cream"]):
        return [
            "Ragi (finger millet) whole grain cookies",
            "Oatmeal banana seed bake bites",
            "Almond flour & flaxseed crackers",
            "Roasted pumpkin & sunflower seed mix"
        ]
    elif any(k in p_lower for k in ["soda", "coke", "pepsi", "fanta", "sprite", "energy", "drink", "juice", "frooti", "maaza"]):
        return [
            "Fresh tender coconut water (natural electrolytes)",
            "Spiced probiotic buttermilk (chaas) with roasted cumin",
            "Infused lemon mint cucumber cooler",
            "Fresh unsweetened seasonal lime water"
        ]
    elif any(k in p_lower for k in ["chocolate", "candy", "sweet", "bar", "mithai", "cake", "pastry", "donut"]):
        return [
            "Dark chocolate (>=75% cacao - antioxidant rich)",
            "Medjool dates stuffed with roasted walnuts",
            "Anjeer (figs) & unsalted nut trail mix",
            "Greek yogurt topped with fresh berries & chia seeds"
        ]
    elif any(k in p_lower for k in ["burger", "pizza", "fries", "frankie", "roll"]):
        return [
            "Whole wheat grilled vegetable & paneer wrap",
            "Air-fried sweet potato wedges with rosemary",
            "Cauliflower / millet crust vegetable pizza",
            "Sprouted rajma & oats vegetable patty"
        ]
    elif any(k in p_lower for k in ["namkeen", "bhujia", "sev", "samosa", "pakora", "kachori", "fried"]):
        return [
            "Roasted puffed rice (jhalmuri / roasted bhel)",
            "Baked moong dal & peanut mixture",
            "Air-fried vegetable cutlets (zero trans fat)",
            "Sprouted chana chaat with lemon & pomegranate"
        ]
    else:
        if classification == "Unhealthy":
            return [
                "Fresh seasonal whole fruits (apple, papaya, guava)",
                "Handful of roasted unsalted almonds & walnuts",
                "Sprouted moong & corn salad with lemon dressing",
                "Roasted makhana or chana snack"
            ]
        elif classification == "Moderate":
            return [
                "Pair with fresh cucumber/carrot salad for added fiber",
                "Switch to whole grain or less processed version",
                "Control portion size and drink plenty of water"
            ]
        else:
            return [
                "Keep up the clean eating habits!",
                "Pair with fresh water for maximum nutrient absorption",
                "Include a handful of soaked almonds or walnuts"
            ]
