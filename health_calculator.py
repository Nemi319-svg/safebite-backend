from typing import Dict, List, Tuple, Any

def calculate_health_score(
    calories: float,
    protein: float,
    carbs: float,
    fat: float,
    sugar: float = 0.0,
    fiber: float = 0.0,
    sodium: float = 0.0,
    product_name: str = "",
    ingredients: str = "",
    is_diabetic: bool = False
) -> Tuple[float, str, List[str], List[str], List[str]]:
    """
    Computes a transparent health score (0-100) based on nutritional values,
    beverage vs solid classification, and ingredient warning indicators.
    Returns:
        (final_score, classification, reasons, benefits, concerns)
    """
    p_lower = (product_name or "").lower()
    i_lower = (ingredients or "").lower()
    full_text = f"{p_lower} {i_lower}"

    sug = sugar or 0.0
    fib = fiber or 0.0
    sod = sodium or 0.0

    reasons: List[str] = []
    benefits: List[str] = []
    concerns: List[str] = []

    # Detection of Carbonated Drinks, Sodas, Colas & Energy Drinks
    is_carbonated_or_soda = any(k in full_text for k in [
        "cola", "coke", "pepsi", "thums up", "sprite", "fanta", "limca",
        "mountain dew", "7up", "mirinda", "soda", "carbonated", "soft drink",
        "cold drink", "fizzy", "appy fizz", "energy drink", "red bull",
        "monster", "sting"
    ])

    # Detection of General Beverages (Juices, Packaged Drinks, Syrups)
    is_general_beverage = is_carbonated_or_soda or any(k in full_text for k in [
        "juice", "drink", "beverage", "sharbat", "squash", "nectar",
        "syrup", "frooti", "maaza", "slice"
    ]) or (fat <= 0.5 and protein <= 0.5 and fib <= 0.5 and (carbs > 5.0 or sug > 0.0) and 10.0 <= calories <= 80.0)

    # =========================================================================
    # CASE A: CARBONATED SODAS, COLAS & ENERGY DRINKS (Coca-Cola, Pepsi, etc.)
    # =========================================================================
    if is_carbonated_or_soda:
        is_zero_or_diet = (sug <= 0.5 and carbs <= 0.5 and calories <= 5.0)
        is_pure_club_soda_or_water = (calories == 0.0 and sug == 0.0 and carbs == 0.0 and "sweetener" not in full_text)

        if is_pure_club_soda_or_water:
            score = 96.0
            classification = "Healthy"
            reasons.append("Calorie-free pure hydration (+96 pts)")
            benefits.append("100% calorie-free and sugar-free pure hydration")
            benefits.append("Zero artificial sweeteners, zero synthetic preservatives")
        elif is_zero_or_diet:
            score = 42.0
            classification = "Moderate"
            reasons.append("Zero-sugar formulation avoids glucose spike (+42 pts)")
            reasons.append("Contains synthetic artificial sweeteners")
            benefits.append("Zero calories and zero sugar — avoids immediate blood glucose spikes")
            concerns.append("Contains synthetic high-potency artificial sweeteners (Aspartame / Acesulfame-K / Sucralose)")
            concerns.append("Artificial sweeteners can alter gut microbiota and sustain intense sweet cravings")
            if "338" in full_text or "phosphoric" in full_text:
                concerns.append("Contains Phosphoric Acid (INS 338) which can weaken tooth enamel and bone calcium")
            if "150d" in full_text or "caramel" in full_text:
                concerns.append("Contains Caramel IV (INS 150d) coloring with 4-MEI contaminant concerns")
        else:
            # SUGARY SODA / COLD DRINK (Coca-Cola Original, Thums Up, Sprite, Fanta, Sting, etc.)
            # Standard 300ml bottle/can has ~32g of sugar (8 teaspoons)!
            calc_score = 22.0 - (sug - 6.0) * 1.5
            score = max(12.0, min(26.0, calc_score))
            classification = "Unhealthy"

            reasons.append(f"Excessive liquid sugar ({sug:.1f}g/100ml) [-50 pts]")
            reasons.append("Zero nutritional value / empty calories [-25 pts]")
            concerns.append(f"Extremely high liquid sugar ({sug:.1f}g / 100ml) — A standard 300ml can contains ~32g (8 teaspoons) of sugar")
            concerns.append("100% empty calories — Provides zero dietary fiber, zero protein, and zero essential vitamins")
            concerns.append("Rapid liquid sugar absorption triggers sharp insulin surges, driving fatty liver and visceral weight gain")

            if "338" in full_text or "phosphoric" in full_text or any(k in p_lower for k in ["coca", "pepsi", "thums"]):
                concerns.append("Contains Phosphoric Acid (INS 338) linked to tooth enamel demineralization and bone calcium loss")
            if "150d" in full_text or "caramel" in full_text or any(k in p_lower for k in ["coca", "pepsi", "thums"]):
                concerns.append("Contains Caramel IV (INS 150d) chemical coloring containing trace 4-MEI")
            if "caffeine" in full_text or any(k in p_lower for k in ["coca", "pepsi", "thums", "sting", "red bull"]):
                concerns.append("Contains added caffeine paired with high sugar")
            if "110" in full_text or "sunset yellow" in full_text or any(k in p_lower for k in ["fanta", "mirinda"]):
                concerns.append("Contains Sunset Yellow FCF (INS 110) petroleum dye")

    # =========================================================================
    # CASE B: PACKAGED FRUIT DRINKS & JUICES (Frooti, Maaza, Slice, etc.)
    # =========================================================================
    elif is_general_beverage:
        if sug > 10.0:
            calc_score = 32.0 - (sug - 10.0) * 1.5
            score = max(16.0, min(32.0, calc_score))
            classification = "Unhealthy"
            reasons.append(f"High liquid sugar ({sug:.1f}g/100ml) with stripped fiber [-40 pts]")
            concerns.append(f"High added liquid sugar ({sug:.1f}g / 100ml) with stripped natural dietary fiber")
            concerns.append("Delivers concentrated fructose that directly stresses hepatic (liver) metabolism")
        elif sug > 5.0:
            score = 50.0
            classification = "Moderate"
            reasons.append("Moderate liquid sugar with low natural fiber")
            concerns.append("Moderate sugar content in liquid form")
        else:
            score = 88.0
            classification = "Healthy"
            reasons.append("Low-sugar natural hydration (+88 pts)")
            benefits.append("Naturally low sugar hydration")

    # =========================================================================
    # CASE C: SOLID FOODS & GENERAL SNACKS
    # =========================================================================
    else:
        solid_score = 55.0 # Realistic neutral baseline

        # Positive factors (Protein & Fiber)
        if protein >= 15.0:
            solid_score += 16.0
            reasons.append("High protein (>=15g) [+16 pts]")
            benefits.append("High protein content (>=15g) — supports muscle synthesis & satiety")
        elif protein >= 8.0:
            solid_score += 10.0
            reasons.append("Good protein (>=8g) [+10 pts]")
            benefits.append("Good source of dietary protein (>=8g)")
        elif protein >= 4.0:
            solid_score += 5.0
            reasons.append("Adequate protein (>=4g) [+5 pts]")
            benefits.append("Source of protein (>=4g)")

        if fib >= 6.0:
            solid_score += 16.0
            reasons.append("High fiber (>=6g) [+16 pts]")
            benefits.append("High dietary fiber (>=6g) — slows digestion & promotes gut health")
        elif fib >= 3.0:
            solid_score += 10.0
            reasons.append("Good fiber (>=3g) [+10 pts]")
            benefits.append("Good source of dietary fiber (>=3g)")
        elif fib >= 1.5:
            solid_score += 5.0
            reasons.append("Contains fiber (>=1.5g) [+5 pts]")
            benefits.append("Contains dietary fiber (>=1.5g)")

        if fib >= 3.0 and protein >= 6.0 and sug <= 5.0 and fat <= 8.0:
            solid_score += 8.0
            reasons.append("Balanced whole food profile [+8 pts]")
            benefits.append("Balanced whole food nutritional profile")

        if 0.1 <= sod <= 140.0 and calories > 50.0:
            solid_score += 4.0
            reasons.append("Naturally low sodium [+4 pts]")
            benefits.append("Naturally low in sodium (<=140mg)")

        # Negative factors (Sugar, Fat, Calories, Sodium, Palm Oil)
        if sug > 35.0:
            solid_score -= 32.0
            reasons.append("Extremely high sugar (>35g) [-32 pts]")
            concerns.append("Very high added sugar (>35g) — acute glycemic spike")
        elif sug > 20.0:
            solid_score -= 22.0
            reasons.append("High sugar (>20g) [-22 pts]")
            concerns.append("High sugar content (>20g) — risk of insulin spikes")
        elif sug > 12.0:
            solid_score -= 14.0
            reasons.append("Elevated sugar (>12g) [-14 pts]")
            concerns.append("Elevated sugar content (>12g)")
        elif sug > 6.0:
            solid_score -= 7.0
            reasons.append("Contains added sugar (>6g) [-7 pts]")
            concerns.append("Contains added sugar (>6g)")

        if calories > 500.0:
            solid_score -= 18.0
            reasons.append("Very high calorie density (>500 kcal) [-18 pts]")
            concerns.append("Very high calorie density (>500 kcal per 100g)")
        elif calories > 400.0:
            solid_score -= 12.0
            reasons.append("High calories (>400 kcal) [-12 pts]")
            concerns.append("High calorie load (>400 kcal)")
        elif calories > 300.0:
            solid_score -= 6.0
            reasons.append("Moderate-high calories (>300 kcal) [-6 pts]")
            concerns.append("Moderate to high calories (>300 kcal)")

        if fat > 30.0:
            solid_score -= 22.0
            reasons.append("Very high fat (>30g) [-22 pts]")
            concerns.append("Very high total fat content (>30g per 100g)")
        elif fat > 20.0:
            solid_score -= 15.0
            reasons.append("High fat (>20g) [-15 pts]")
            concerns.append("High fat formulation (>20g)")
        elif fat > 12.0:
            solid_score -= 8.0
            reasons.append("Moderate fat (>12g) [-8 pts]")
            concerns.append("Moderate to high fat content (>12g)")

        if sod > 800.0:
            solid_score -= 22.0
            reasons.append("Very high sodium (>800mg) [-22 pts]")
            concerns.append("Very high sodium (>800mg) — exceeds blood pressure thresholds")
        elif sod > 500.0:
            solid_score -= 15.0
            reasons.append("High sodium (>500mg) [-15 pts]")
            concerns.append("High sodium level (>500mg)")
        elif sod > 250.0:
            solid_score -= 8.0
            reasons.append("Moderate sodium (>250mg) [-8 pts]")
            concerns.append("Moderate sodium content (>250mg)")

        # Palm oil & Trans-fat penalty
        if any(k in full_text for k in ["palm oil", "palmolein", "vanaspati", "hydrogenated"]):
            solid_score -= 12.0
            reasons.append("Contains Palm Oil / Hydrogenated Fats [-12 pts]")
            concerns.append("Contains Palm Oil / Hydrogenated Fats high in atherogenic saturated and trans-fatty acids")

        # Empty calorie junk penalty
        if (sug > 15.0 or fat > 18.0) and protein < 2.0 and fib < 1.0:
            solid_score -= 10.0
            reasons.append("Empty calorie ultra-processed junk [-10 pts]")
            concerns.append("Empty calories — high in sugars/fats with negligible protein or fiber")

        score = max(8.0, min(96.0, solid_score))

        # Guardrails: A food CANNOT be called Healthy if high in sugar, sodium, or palm oil
        is_unhealthy_override = (
            (sug > 25.0) or
            (fat > 25.0 and sod > 600.0) or
            (calories > 450.0 and sug > 20.0) or
            (score < 42.0)
        )

        is_healthy_eligible = (
            (score >= 68.0) and
            (sug <= 8.0) and
            (fat <= 18.0) and
            (sod <= 450.0) and
            ("palm oil" not in full_text) and
            ("palmolein" not in full_text)
        )

        if is_unhealthy_override:
            classification = "Unhealthy"
        elif is_healthy_eligible:
            classification = "Healthy"
        else:
            classification = "Moderate"

    # Diabetic Adjustment
    if is_diabetic:
        if is_carbonated_or_soda or is_general_beverage:
            if sug > 2.0:
                score = max(5.0, score - 15.0)
                reasons.append("Diabetic sensitivity: Liquid sugars rapidly spike blood glucose [-15 pts]")
                concerns.append("Extremely high glycemic impact for diabetics")
        else:
            if carbs > 50:
                score = max(5.0, score - 15.0)
                reasons.append("Diabetic sensitivity: Carbs exceed 50g [-15 pts]")
                concerns.append("May cause notable blood glucose elevation")
            if sug > 8:
                score = max(5.0, score - 12.0)
                reasons.append("Diabetic sensitivity: Sugar exceeds 8g [-12 pts]")
                concerns.append("High glycemic impact for diabetics")

    final_score = round(max(5.0, min(98.0, score)), 1)
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
