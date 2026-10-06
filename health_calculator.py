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


def get_healthier_alternatives(
    product_name: str,
    classification: str,
    ingredients: str = "",
    calories: float = 0.0,
    fat: float = 0.0,
    carbs: float = 0.0
) -> List[str]:
    """
    Returns curated, realistic healthier food alternatives strictly tailored to the product's category.
    """
    p_lower = (product_name or "").lower()
    i_lower = (ingredients or "").lower()
    text = f"{p_lower} {i_lower}"

    # 1. Carbonated Soft Drinks & Energy Drinks (Cold Drinks)
    if any(k in text for k in [
        "cola", "coca", "pepsi", "sprite", "fanta", "limca", "thums up", "mountain dew",
        "7up", "mirinda", "sting", "red bull", "monster", "energy drink", "cold drink",
        "soda", "carbonated", "soft drink", "appy fizz", "fizzy", "tonic water", "ginger ale"
    ]) or (fat <= 0.5 and carbs > 6.0 and 20.0 <= calories <= 75.0 and "drink" in text):
        return [
            "🥥 Fresh Tender Coconut Water (Nariyal Pani) — 100% natural electrolytes, zero added sugar",
            "🥛 Spiced Masala Buttermilk (Chaas) with roasted jeera & mint — gut probiotics",
            "🍋 Fresh Mint Nimbu Pani (Lime Soda) with rock salt & soaked chia seeds",
            "🌾 Chilled Sattu Sharbat (roasted gram drink) — high natural plant protein & cooling energy",
            "🍃 Unsweetened Iced Green Tea with lemon slices & mint leaves — antioxidant rich",
            "🥭 Natural Bel Sharbat or Raw Mango Aam Panna (prepared with jaggery)"
        ]

    # 2. Packaged Juices & Nectars
    elif any(k in text for k in [
        "frooti", "maaza", "slice", "fruit juice", "real juice", "tropicana", "nectar",
        "squash", "sharbat", "fruit drink", "pulp", "mango drink", "guava juice", "orange juice"
    ]):
        return [
            "🍊 Fresh Whole Seasonal Fruits (Orange, Mosambi, Guava) — preserves essential dietary fiber",
            "🥤 Freshly Squeezed Cold-Pressed Orange or Pomegranate Juice (with pulp, zero sugar)",
            "🥥 Tender Coconut Water with a splash of fresh lime",
            "🍉 Fresh Watermelon & Mint Infused Cooler (hydrating & naturally sweet)"
        ]

    # 3. Commercial Milk & Beverage Powders / Teas
    elif any(k in text for k in [
        "horlicks", "bournvita", "boost", "complan", "nescafe", "bru", "chai", "tea",
        "coffee", "latte", "frappe", "cappuccino", "amul kool", "milkshake", "shake"
    ]):
        return [
            "☕ Freshly brewed Filter Coffee or Black Americano without refined white sugar",
            "☕ Traditional Spiced Masala Chai brewed with crushed ginger, cardamom & clove",
            "🥛 Golden Turmeric Milk (Haldi Doodh) with a pinch of black pepper & cinnamon",
            "🌰 Homemade Badam Milk prepared with crushed almonds & natural jaggery"
        ]

    # 4. Chips & Extruded Snacks
    elif any(k in text for k in [
        "chip", "crisp", "wafer", "nacho", "dorito", "lays", "kurkure", "bingo", "pringles", "cheetos"
    ]):
        return [
            "🍿 Roasted Makhana (Fox Nuts) with cold-pressed olive oil & pink rock salt",
            "🌾 Baked Jowar / Ragi chips or air-dried beetroot crisps (low oil)",
            "🥜 Roasted Salted Chana (chickpeas) & roasted peanuts mix",
            "🥗 Sprouted Moong & Boiled Sweet Corn Chaat with lemon dressing"
        ]

    # 5. Namkeen & Fried Savories
    elif any(k in text for k in [
        "namkeen", "bhujia", "sev", "samosa", "pakora", "kachori", "fried", "dal biji",
        "chivda", "mathri", "mixture", "haldiram", "bikaji", "balaji"
    ]):
        return [
            "🌾 Roasted Puffed Rice (Jhalmuri / murmura bhel) with chopped tomatoes & lime",
            "🫘 Steamed Sprouted Kala Chana with fresh coriander & chaat masala",
            "🫓 Baked Methi / Palak whole wheat mathri (zero trans fat)",
            "🌰 Roasted Masala Edamame or spiced lotus seeds"
        ]

    # 6. Biscuits, Cookies & Bakery
    elif any(k in text for k in [
        "biscuit", "cookie", "oreo", "parle", "rusk", "cream biscuit", "good day", "bourbon",
        "marie", "dark fantasy", "monaco", "krackjack", "hide & seek", "cracker", "cake"
    ]):
        return [
            "🍪 Homemade Rolled Oats & Mashed Banana Cookies (zero maida, zero white sugar)",
            "🌾 Ragi (Finger Millet) & Jaggery whole grain digestive biscuits",
            "🌰 Medjool Dates stuffed with raw walnuts & California almonds",
            "🥣 Roasted Pumpkin, Flax & Sunflower seed trail mix"
        ]

    # 7. Instant Noodles & Pasta
    elif any(k in text for k in [
        "noodle", "maggi", "ramen", "pasta", "yippee", "macaroni", "spaghetti", "hakka", "chowmein", "wai wai"
    ]):
        return [
            "🍜 100% Foxtail Millet or Whole Wheat Noodles with sauteed vegetables",
            "🥕 Steamed Vegetable Vermicelli (Seviyan Upma) with mustard seeds & curry leaves",
            "🥣 Vegetable Rolled Oats Khichdi cooked with fresh peas & carrots",
            "🥒 Zucchini Ribbon Noodles (Zoodles) with homemade fresh tomato basil sauce"
        ]

    # 8. Chocolates, Candies & Sweets
    elif any(k in text for k in [
        "chocolate", "candy", "sweet", "bar", "mithai", "cake", "pastry", "donut", "dairy milk",
        "kitkat", "5 star", "munch", "perk", "snickers", "milkybar", "gems", "toffee"
    ]):
        return [
            "🍫 Dark Chocolate (>=70% Cacao) — rich in heart-healthy flavonoids",
            "🌴 Soft Khajoor (Dates) & roasted almond/walnut energy bites",
            "🍯 Anjeer (Dried Figs) & raw cashew nut trail mix",
            "🥥 Homemade Dry Fruit & Jaggery Besan/Atta Laddu (no refined white sugar)"
        ]

    # 9. Ice Creams & Frozen Desserts
    elif any(k in text for k in ["ice cream", "icecream", "kulfi", "sundae", "gelato", "dessert"]):
        return [
            "🍧 Frozen Banana 'Nice Cream' blended with raw cocoa powder & almond milk",
            "🥣 Creamy Greek Yogurt or Hung Curd topped with fresh berries & chia seeds",
            "🥭 Homemade Mango & Chia Seed Pudding made with coconut milk",
            "🥛 Chilled Badam Kheer sweetened naturally with crushed dates"
        ]

    # 10. Fast Food & Burgers / Pizzas
    elif any(k in text for k in ["burger", "pizza", "fries", "frankie", "roll", "sandwich", "patty"]):
        return [
            "🌯 Whole Wheat Grilled Paneer & Capsicum Wrap with mint curd spread",
            "🍟 Air-Fried Sweet Potato Wedges tossed with herbs & olive oil",
            "🍕 Thin-Crust Millet / Ragi base vegetable pizza with homemade cottage cheese",
            "🧆 Sprouted Rajma & Oats vegetable cutlets with coriander-mint chutney"
        ]

    # 11. Sauces & Spreads
    elif any(k in text for k in ["ketchup", "sauce", "mayonnaise", "mayo", "spread", "jam", "nutella", "dip"]):
        return [
            "🌿 Fresh homemade Dhania-Pudina (Coriander-Mint) Chutney",
            "🫒 Homemade Creamy Hummus drizzled with extra virgin olive oil",
            "🥣 Hung Curd Garlic & Herb Dip (high protein, zero trans fat)",
            "🍅 Fresh Homemade Tomato & Jalapeno Salsa (zero corn syrup)"
        ]

    # 12. General Fallback
    else:
        if classification == "Healthy":
            return [
                "🌟 Keep up the clean eating habits!",
                "💧 Pair with ample water throughout the day for optimal digestion",
                "🥜 Add a handful of soaked almonds or walnuts for essential omega-3s"
            ]
        else:
            return [
                "🥗 Fresh seasonal whole fruits (Apple, Papaya, Guava, Orange) for dietary fiber",
                "🥜 Handful of soaked almonds, walnuts, and pumpkin seeds",
                "🥗 Sprouted Moong & Paneer Salad with lemon dressing & rock salt",
                "🍿 Lightly roasted Makhana with turmeric and black pepper"
            ]
