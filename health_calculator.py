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
    Computes a transparent, scientifically calibrated health score (0-100) based on nutritional values,
    food category intelligence (Nut Butters, Nuts/Seeds, Beverages, Dairy, Solids), and ingredient quality.
    
    Returns:
        (final_score, classification, reasons, benefits, concerns)
    """
    p_lower = (product_name or "").lower().strip()
    i_lower = (ingredients or "").lower().strip()
    full_text = f"{p_lower} {i_lower}"

    cal = max(0.0, float(calories or 0.0))
    prot = max(0.0, float(protein or 0.0))
    carb = max(0.0, float(carbs or 0.0))
    f_total = max(0.0, float(fat or 0.0))
    sug = max(0.0, float(sugar or 0.0))
    fib = max(0.0, float(fiber or 0.0))
    sod = max(0.0, float(sodium or 0.0))

    reasons: List[str] = []
    benefits: List[str] = []
    concerns: List[str] = []

    # =========================================================================
    # CATEGORY DETECTION
    # =========================================================================

    # 1. Detection of Nut Butters & Plant Spreads (Peanut Butter, Almond Butter, Tahini)
    is_nut_butter_text = any(k in full_text for k in [
        "peanut butter", "almond butter", "cashew butter", "walnut butter",
        "nut butter", "seed butter", "tahini", "sunflower butter", "pintola",
        "myfitness", "alpino", "disano peanut", "sundrop peanut"
    ]) or (
        ("butter" in p_lower or "spread" in p_lower or "paste" in p_lower) and
        any(n in full_text for n in ["peanut", "almond", "cashew", "walnut", "sesame", "hazelnut"])
    )
    is_nut_butter_profile = (
        cal >= 480.0 and f_total >= 35.0 and prot >= 18.0 and sug <= 25.0 and
        any(n in full_text for n in ["butter", "spread", "paste", "tahini"])
    )
    is_nut_butter = is_nut_butter_text or is_nut_butter_profile

    # 2. Detection of Whole Nuts, Seeds & Dry Fruits
    is_nuts_seeds_text = any(k in full_text for k in [
        "almond", "badam", "walnut", "akhrot", "cashew", "kaju", "pistachio", "pista",
        "chia seed", "flax seed", "flaxseed", "alasi", "pumpkin seed", "sunflower seed",
        "sesame seed", "til", "makhana", "fox nut", "lotus seed", "trail mix", "mixed nuts",
        "roasted peanut", "roasted chana", "peanuts"
    ]) and not is_nut_butter
    is_nuts_seeds_profile = (
        cal >= 450.0 and f_total >= 35.0 and prot >= 12.0 and sug <= 15.0 and sod <= 400.0 and
        not is_nut_butter
    )
    is_nuts_seeds = (is_nuts_seeds_text and f_total >= 15.0 and cal >= 320.0) or is_nuts_seeds_profile

    # 3. Detection of Liquid Beverages (Juices, Packaged Drinks, Sodas, Colas, Syrups)
    is_beverage_by_profile = (f_total <= 0.8 and prot <= 0.8 and fib <= 0.8 and (carb > 4.0 or sug > 4.0) and 10.0 <= cal <= 95.0)
    is_beverage_by_text = any(k in full_text for k in [
        "cola", "coke", "pepsi", "thums up", "sprite", "fanta", "limca",
        "mountain dew", "7up", "mirinda", "soda", "carbonated", "soft drink",
        "cold drink", "fizzy", "appy fizz", "energy drink", "red bull",
        "monster", "sting", "juice", "drink", "beverage", "sharbat", "squash",
        "nectar", "syrup", "frooti", "maaza", "slice"
    ])
    is_liquid_beverage = (is_beverage_by_profile or is_beverage_by_text) and not is_nut_butter and not is_nuts_seeds

    # 4. Detection of Fresh Whole Fruits & Raw Produce (Apples, Bananas, Oranges, Cucumbers, etc.)
    is_fresh_fruit_veg_text = any(k in full_text for k in [
        "apple", "seb", "banana", "kela", "orange", "santra", "mosambi", "citrus",
        "guava", "amrood", "papaya", "papita", "watermelon", "tarbooz", "muskmelon",
        "mango", "aam", "pomegranate", "anar", "grapes", "angoor", "pear", "nashpati",
        "strawberry", "blueberry", "cucumber", "khira", "kakdi", "tomato", "tamatar",
        "carrot", "gajar", "radish", "mooli", "spinach", "palak", "broccoli",
        "fresh fruit", "whole fruit", "raw fruit", "fresh vegetable", "raw vegetable"
    ]) and not any(p in full_text for p in [
        "juice", "syrup", "jam", "jelly", "squash", "candy", "pie", "cake", "chip", "chips", "wafer", "snack", "fried", "powder", "seasoning"
    ])
    is_fresh_fruit_or_veg = is_fresh_fruit_veg_text and not is_nut_butter and not is_nuts_seeds and not is_liquid_beverage and cal <= 130.0 and f_total <= 4.0

    # =========================================================================
    # CASE A: NUT BUTTERS & SEED SPREADS (PEANUT BUTTER, ALMOND BUTTER, TAHINI)
    # =========================================================================
    if is_nut_butter:
        # Nut butters are nutrient-dense superfoods packed with healthy monounsaturated
        # and polyunsaturated fats, plant protein, magnesium, and dietary fiber.
        # They must NEVER be penalized for natural caloric density or natural unsaturated fat!
        nut_score = 88.0

        # Protein Evaluation
        if prot >= 25.0:
            nut_score += 6.0
            reasons.append(f"Exceptional plant protein ({prot:.1f}g/100g) [+6 pts]")
            benefits.append(f"Outstanding plant protein ({prot:.1f}g/100g) — fuels muscle synthesis, tissue repair & prolonged satiety")
        elif prot >= 18.0:
            nut_score += 3.0
            reasons.append(f"Rich in dietary protein ({prot:.1f}g/100g) [+3 pts]")
            benefits.append(f"Rich in dietary plant protein ({prot:.1f}g/100g)")

        # Dietary Fiber Evaluation
        if fib >= 6.0:
            nut_score += 4.0
            reasons.append(f"High prebiotic dietary fiber ({fib:.1f}g/100g) [+4 pts]")
            benefits.append(f"High natural dietary fiber ({fib:.1f}g/100g) — nourishes gut microbiome and slows carbohydrate absorption")
        elif fib >= 3.0:
            nut_score += 2.0
            reasons.append(f"Good dietary fiber ({fib:.1f}g/100g) [+2 pts]")
            benefits.append(f"Good source of dietary fiber ({fib:.1f}g/100g)")

        # Cardioprotective Monounsaturated Fatty Acids
        benefits.append("Rich in heart-healthy Monounsaturated Fatty Acids (MUFA, Oleic Acid) that support healthy HDL/LDL cholesterol balance")
        benefits.append("Naturally low glycemic index (GI ~14), preventing sharp insulin spikes and supporting steady metabolic energy")

        # Check for Industrial Emulsifiers / Hydrogenated Oils
        has_hydrogenated = any(k in full_text for k in ["hydrogenated", "partially hydrogenated", "vanaspati", "trans fat"])
        has_palm_oil = any(k in full_text for k in ["palm oil", "palmolein", "fractionated palm"])

        if has_hydrogenated:
            nut_score -= 26.0
            reasons.append("Contains Hydrogenated Vegetable Oils / Industrial Trans Fats [-26 pts]")
            concerns.append("Contains Hydrogenated Vegetable Oils used to prevent oil separation; introduces harmful trans-fatty acids")
        elif has_palm_oil:
            nut_score -= 18.0
            reasons.append("Contains Added Palm Oil / Palmolein [-18 pts]")
            concerns.append("Contains Added Palm Oil / Palmolein high in saturated palmitic acid; choose 100% All-Natural peanut butter")

        # Added Sugar Evaluation
        if sug > 25.0:
            nut_score -= 32.0
            reasons.append(f"Excessive added sugar ({sug:.1f}g/100g) [-32 pts]")
            concerns.append(f"Excessive added sugar ({sug:.1f}g/100g) — converts healthy nut butter into a high-sugar dessert spread")
        elif sug > 15.0:
            nut_score -= 18.0
            reasons.append(f"High added sugar ({sug:.1f}g/100g) [-18 pts]")
            concerns.append(f"High added sugar ({sug:.1f}g/100g) — counteracts cardiometabolic benefits")
        elif sug > 8.0:
            nut_score -= 8.0
            reasons.append(f"Contains added sugar ({sug:.1f}g/100g) [-8 pts]")
            concerns.append(f"Contains added cane sugar / sweetener ({sug:.1f}g/100g)")
        elif sug <= 6.0:
            nut_score += 3.0
            reasons.append("Clean low-sugar profile (<=6g natural sugars) [+3 pts]")
            benefits.append("Naturally low sugar profile (<=6g) — excellent for keto, low-carb, and diabetic diets")

        # Sodium Evaluation
        if sod > 450.0:
            nut_score -= 12.0
            reasons.append(f"Elevated sodium ({sod:.0f}mg) [-12 pts]")
            concerns.append(f"Elevated sodium ({sod:.0f}mg/100g)")
        elif sod > 250.0:
            nut_score -= 6.0
            reasons.append(f"Noticeable added salt ({sod:.0f}mg) [-6 pts]")
        elif sod <= 150.0:
            nut_score += 2.0
            reasons.append("Low sodium / unsalted [+2 pts]")
            benefits.append("Naturally low sodium (<150mg)")

        score = max(18.0, min(96.0, nut_score))

        if has_hydrogenated or sug > 25.0 or score < 45.0:
            classification = "Unhealthy"
        elif score >= 70.0 and sug <= 10.0 and not has_palm_oil and not has_hydrogenated:
            classification = "Healthy"
        else:
            classification = "Moderate"

    # =========================================================================
    # CASE B: WHOLE NUTS, SEEDS & DRY FRUITS (ALMONDS, WALNUTS, SEEDS, MAKHANA)
    # =========================================================================
    elif is_nuts_seeds:
        seed_score = 88.0

        if prot >= 18.0:
            seed_score += 5.0
            reasons.append(f"High natural plant protein ({prot:.1f}g/100g) [+5 pts]")
            benefits.append(f"High plant protein ({prot:.1f}g/100g) — supports muscle health and prolonged satiety")
        elif prot >= 10.0:
            seed_score += 3.0
            benefits.append(f"Good source of dietary protein ({prot:.1f}g/100g)")

        if fib >= 6.0:
            seed_score += 5.0
            reasons.append(f"High dietary fiber ({fib:.1f}g/100g) [+5 pts]")
            benefits.append(f"High natural dietary fiber ({fib:.1f}g/100g) — supports digestion and slows glucose absorption")
        elif fib >= 3.0:
            seed_score += 2.0
            benefits.append(f"Contains natural dietary fiber ({fib:.1f}g/100g)")

        benefits.append("Rich in essential healthy fats (Omega-3 ALA, Monounsaturated Fatty Acids), Vitamin E & Magnesium")

        # Penalties for sugar coatings, heavy frying, or sodium
        has_palm = any(k in full_text for k in ["palm oil", "palmolein", "hydrogenated", "vanaspati"])
        if has_palm:
            seed_score -= 18.0
            reasons.append("Fried in Palm Oil / Refined industrial fat [-18 pts]")
            concerns.append("Fried in Palm Oil / Palmolein instead of dry roasted; increases saturated fat load")

        if sug > 20.0:
            seed_score -= 25.0
            reasons.append(f"Heavily sugar-glazed ({sug:.1f}g/100g) [-25 pts]")
            concerns.append(f"Heavily sugar-coated ({sug:.1f}g/100g) — high added sugar content")
        elif sug > 10.0:
            seed_score -= 12.0
            reasons.append(f"Contains added sugar/honey coating ({sug:.1f}g) [-12 pts]")

        if sod > 500.0:
            seed_score -= 14.0
            reasons.append(f"Heavily salted ({sod:.0f}mg) [-14 pts]")
            concerns.append(f"Excessive sodium ({sod:.0f}mg/100g) — choose unsalted or lightly salted varieties")
        elif sod <= 150.0:
            seed_score += 2.0
            reasons.append("Low sodium / unseasoned [+2 pts]")

        score = max(20.0, min(96.0, seed_score))
        if has_palm or sug > 25.0 or score < 45.0:
            classification = "Unhealthy"
        elif score >= 70.0 and sug <= 10.0 and not has_palm:
            classification = "Healthy"
        else:
            classification = "Moderate"

    # =========================================================================
    # CASE C: LIQUID BEVERAGES (COLD DRINKS, COLAS, SODAS, JUICES & ENERGY DRINKS)
    # =========================================================================
    elif is_liquid_beverage:
        effective_beverage_sugar = max(sug, carb)
        is_zero_or_diet = (effective_beverage_sugar <= 0.5 and cal <= 5.0 and any(k in full_text for k in ["sweetener", "diet", "zero", "black", "light", "aspartame", "sucralose"]))
        is_pure_club_soda_or_water = (cal == 0.0 and effective_beverage_sugar == 0.0 and carb == 0.0 and "sweetener" not in full_text)

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
        elif effective_beverage_sugar > 6.0:
            calc_score = 22.0 - (effective_beverage_sugar - 6.0) * 1.5
            score = max(12.0, min(26.0, calc_score))
            classification = "Unhealthy"

            reasons.append(f"Excessive liquid sugar ({effective_beverage_sugar:.1f}g/100ml) [-50 pts]")
            reasons.append("Zero nutritional value / empty calories [-25 pts]")
            concerns.append(f"Extremely high liquid sugar ({effective_beverage_sugar:.1f}g / 100ml) — A standard 300ml can contains ~{effective_beverage_sugar * 3.0:.0f}g ({(effective_beverage_sugar * 3.0) / 4.0:.0f} teaspoons) of sugar")
            concerns.append("100% empty calories — Provides zero dietary fiber, zero protein, and zero essential vitamins")
            concerns.append("Rapid liquid sugar absorption triggers sharp insulin surges, driving fatty liver and visceral weight gain")

            if "338" in full_text or "phosphoric" in full_text or any(k in full_text for k in ["coca", "pepsi", "thums"]):
                concerns.append("Contains Phosphoric Acid (INS 338) linked to tooth enamel demineralization and bone calcium loss")
            if "150d" in full_text or "caramel" in full_text or any(k in full_text for k in ["coca", "pepsi", "thums"]):
                concerns.append("Contains Caramel IV (INS 150d) chemical coloring containing trace 4-MEI")
            if "caffeine" in full_text or any(k in full_text for k in ["coca", "pepsi", "thums", "sting", "red bull"]):
                concerns.append("Contains added caffeine paired with high sugar")
            if "110" in full_text or "sunset yellow" in full_text or any(k in full_text for k in ["fanta", "mirinda"]):
                concerns.append("Contains Sunset Yellow FCF (INS 110) petroleum dye")
        elif effective_beverage_sugar > 2.5:
            calc_score = 50.0 - (effective_beverage_sugar - 2.5) * 6.0
            score = max(30.0, min(50.0, calc_score))
            classification = "Moderate"
            reasons.append(f"Contains noticeable liquid sugar ({effective_beverage_sugar:.1f}g/100ml)")
            concerns.append(f"Contains noticeable liquid sugar ({effective_beverage_sugar:.1f}g / 100ml)")
        else:
            score = 88.0
            classification = "Healthy"
            reasons.append(f"Naturally low sugar hydration ({effective_beverage_sugar:.1f}g/100ml) [+88 pts]")
            benefits.append(f"Naturally low sugar hydration ({effective_beverage_sugar:.1f}g / 100ml)")

    # =========================================================================
    # CASE D: FRESH WHOLE FRUITS & RAW PRODUCE (APPLES, BANANAS, CUCUMBERS, ORANGES)
    # =========================================================================
    elif is_fresh_fruit_or_veg:
        fruit_score = 92.0

        if fib >= 2.0:
            fruit_score += 4.0
            reasons.append(f"High natural dietary fiber (pectin/cellulose) ({fib:.1f}g) [+4 pts]")
            benefits.append(f"Rich in natural dietary fiber ({fib:.1f}g/100g) — nourishes gut microbiome and slows glucose absorption")
        elif fib >= 1.0:
            fruit_score += 2.0

        if cal <= 65.0:
            fruit_score += 2.0
            reasons.append(f"Naturally light caloric density ({cal:.0f} kcal) [+2 pts]")

        benefits.append("100% whole fresh plant food — rich in vitamins (Vitamin C), cellular hydration, and polyphenol antioxidants")
        benefits.append("Zero added refined sugars — intrinsic fructose is bound within cellular plant fiber, preventing insulin surges")
        benefits.append("Naturally zero cholesterol, zero saturated fat, and virtually zero sodium")

        score = max(88.0, min(98.0, fruit_score))
        classification = "Healthy"

    # =========================================================================
    # CASE E: SOLID FOODS & GENERAL SNACKS
    # =========================================================================
    else:
        solid_score = 55.0

        # Positive factors (Protein & Fiber)
        if prot >= 15.0:
            solid_score += 16.0
            reasons.append("High protein (>=15g) [+16 pts]")
            benefits.append("High protein content (>=15g) — supports muscle synthesis & satiety")
        elif prot >= 8.0:
            solid_score += 10.0
            reasons.append("Good protein (>=8g) [+10 pts]")
            benefits.append("Good source of dietary protein (>=8g)")
        elif prot >= 4.0:
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

        if fib >= 3.0 and prot >= 6.0 and sug <= 5.0 and f_total <= 10.0:
            solid_score += 8.0
            reasons.append("Balanced whole food profile [+8 pts]")
            benefits.append("Balanced whole food nutritional profile")

        if 0.1 <= sod <= 140.0 and cal > 50.0:
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

        if cal > 500.0:
            solid_score -= 18.0
            reasons.append("Very high calorie density (>500 kcal) [-18 pts]")
            concerns.append("Very high calorie density (>500 kcal per 100g)")
        elif cal > 400.0:
            solid_score -= 12.0
            reasons.append("High calories (>400 kcal) [-12 pts]")
            concerns.append("High calorie load (>400 kcal)")
        elif cal > 300.0:
            solid_score -= 6.0
            reasons.append("Moderate-high calories (>300 kcal) [-6 pts]")
            concerns.append("Moderate to high calories (>300 kcal)")

        if f_total > 30.0:
            solid_score -= 22.0
            reasons.append("Very high fat (>30g) [-22 pts]")
            concerns.append("Very high total fat content (>30g per 100g)")
        elif f_total > 20.0:
            solid_score -= 15.0
            reasons.append("High fat (>20g) [-15 pts]")
            concerns.append("High fat formulation (>20g)")
        elif f_total > 12.0:
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
            solid_score -= 14.0
            reasons.append("Contains Palm Oil / Hydrogenated Fats [-14 pts]")
            concerns.append("Contains Palm Oil / Hydrogenated Fats high in atherogenic saturated and trans-fatty acids")

        # Empty calorie junk penalty
        if (sug > 15.0 or f_total > 18.0) and prot < 2.0 and fib < 1.0:
            solid_score -= 10.0
            reasons.append("Empty calorie ultra-processed junk [-10 pts]")
            concerns.append("Empty calories — high in sugars/fats with negligible protein or fiber")

        score = max(8.0, min(96.0, solid_score))

        # Guardrails: A food CANNOT be called Healthy if high in sugar, sodium, or palm oil
        is_unhealthy_override = (
            (sug > 25.0) or
            (f_total > 25.0 and sod > 600.0) or
            (cal > 450.0 and sug > 20.0) or
            (score < 42.0)
        )

        is_healthy_eligible = (
            (score >= 68.0) and
            (sug <= 8.0) and
            (f_total <= 20.0) and
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

        # Authentic Indian Cuisine Detection & Calibration
        indian_dishes = [
            "jalebi", "gulab jamun", "samosa", "chole bhature", "butter naan", "vada pav",
            "dal baati churma", "kachori", "medu vada", "malai kofta", "rasgulla", "ladoo",
            "halwa", "kheer", "kaju katli", "pakora", "bhatura", "bhature", "sprout", "makhana",
            "chaas", "buttermilk", "coconut water", "dal tadka", "palak paneer", "idli",
            "chilla", "bhuna chana", "roasted chana", "tandoori chicken", "cucumber raita",
            "dhokla", "dosa", "upma", "poha", "roti", "rajma", "biryani", "paneer butter masala",
            "kadai paneer", "matar paneer", "shahi paneer", "pav bhaji", "gajak", "chikki", "til patti"
        ]
        is_traditional_seed_sweet = any(s in p_lower for s in ["gajak", "chikki", "til patti", "tilpatti", "til kut", "tilkut", "sesame brittle"])
        is_indian = any(d in p_lower for d in indian_dishes) or "traditional indian" in full_text or "indian cuisine" in full_text
        if is_traditional_seed_sweet:
            # Traditional seed/nut jaggery sweet (Gajak, Chikki): Sesame seeds or peanuts provide natural plant protein,
            # healthy unsaturated fats, calcium, iron, and fiber, while jaggery provides natural unrefined sweetness.
            # Calibrated as Moderate (~50-58/100) with portion control advice.
            base_sweet_score = 56.0 + (prot * 0.4) + (fib * 0.8) - (sug * 0.2)
            score = max(46.0, min(62.0, base_sweet_score))
            classification = "Moderate"
            benefits.append("Rich in natural minerals (Calcium, Iron, Magnesium) and healthy plant unsaturated fats from sesame/peanuts")
            concerns.append("Contains concentrated jaggery sugar (~45% by weight) — enjoy in moderation (1-2 pieces / 25-50g)")
        elif is_indian and not is_nut_butter and not is_fresh_fruit_or_veg and not is_nuts_seeds:
            if any(u in p_lower for u in [
                "jalebi", "gulab jamun", "samosa", "chole bhature", "bhatura", "bhature",
                "butter naan", "vada pav", "dal baati churma", "kachori", "medu vada",
                "malai kofta", "rasgulla", "ladoo", "halwa", "kheer", "kaju katli", "pakora"
            ]) or (f_total >= 18.0 and carb >= 45.0 and fib <= 2.0):
                score = max(18.0, min(44.0, 40.0 - (f_total * 0.8) - (cal * 0.02)))
                classification = "Unhealthy"
            elif any(h in p_lower for h in [
                "sprout", "makhana", "chaas", "buttermilk", "coconut water", "dal tadka",
                "palak paneer", "idli", "chilla", "bhuna chana", "roasted chana", "tandoori chicken",
                "cucumber raita", "dhokla"
            ]) or (prot >= 10.0 and fib >= 5.0 and f_total <= 8.0):
                score = max(75.0, min(96.0, 72.0 + (prot * 0.6) + (fib * 1.5) - (f_total * 0.3)))
                classification = "Healthy"
            else:
                score = max(48.0, min(74.0, 68.0 + (prot * 0.4) + (fib * 0.8) - (f_total * 0.6) - (cal * 0.02)))
                classification = "Moderate"

    # Diabetic Adjustment
    if is_diabetic:
        if is_liquid_beverage:
            if sug > 2.0:
                score = max(5.0, score - 15.0)
                reasons.append("Diabetic sensitivity: Liquid sugars rapidly spike blood glucose [-15 pts]")
                concerns.append("Extremely high glycemic impact for diabetics")
        else:
            if sug > 12.0:
                score = max(5.0, score - 12.0)
                reasons.append("Diabetic sensitivity: Elevated sugar content [-12 pts]")
                concerns.append("High sugar content poses blood glucose elevation risk for diabetics")
            if carb > 55.0 and fib < 3.0:
                score = max(5.0, score - 8.0)
                reasons.append("Diabetic sensitivity: High refined carbohydrates with low fiber [-8 pts]")
                concerns.append("High glycemic carbohydrate load without sufficient dietary fiber")

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
    p_lower = (product_name or "").lower().strip()
    i_lower = (ingredients or "").lower().strip()
    text = f"{p_lower} {i_lower}"

    # 1. Nut Butters & Plant Spreads (Peanut Butter, Almond Butter, Tahini)
    if any(k in text for k in [
        "peanut butter", "almond butter", "cashew butter", "walnut butter",
        "nut butter", "seed butter", "tahini", "sunflower butter", "pintola",
        "myfitness", "alpino", "disano peanut", "sundrop peanut"
    ]) or (
        ("butter" in p_lower or "spread" in p_lower or "paste" in p_lower) and
        any(n in text for n in ["peanut", "almond", "cashew", "walnut", "sesame", "hazelnut"])
    ) or (fat >= 35.0 and calories >= 480.0 and any(n in text for n in ["peanut", "nut", "almond"])):
        if classification == "Healthy":
            return [
                "🥜 Excellent clean choice! 100% roasted peanut butter provides ~8g protein and 16g healthy unsaturated fats per 2 tbsp serving",
                "💡 Ideal Portion Tip: 2 tablespoons (32g) is the recommended daily portion — perfect on whole grain toast, apple slices, or morning oats",
                "🌰 Alternate with Raw Stone-Ground Almond Butter for a rich natural boost of Vitamin E and magnesium",
                "🌱 Sprinkle soaked chia seeds or flax seeds on top for plant-based Omega-3 (ALA) fatty acids",
                "🍌 Pair with sliced bananas and warm rolled oats for sustained workout energy"
            ]
        else:
            return [
                "🥜 Switch to 100% All-Natural Unsweetened Peanut Butter (Ingredients: Only 100% Roasted Peanuts — Zero Palm Oil, Zero Added Sugar)",
                "🌰 Pure Raw Stone-Ground Almond Butter (Rich in Vitamin E, Magnesium, and heart-healthy Monounsaturated Oleic Acid)",
                "🥣 Rolled Oats topped with Crushed Roasted Peanuts & Chia Seeds (Clean high-protein breakfast crunch)",
                "🥑 Fresh Mashed Avocado on Toasted Multigrain Sourdough Bread (Creamy 100% whole-food healthy fats with zero sodium)",
                "🫘 Traditional Roasted Salted Chana & Peanuts Mix (Authentic Indian clean plant-based protein snack)"
            ]

    # 2. Whole Nuts, Seeds & Dry Fruits
    elif any(k in text for k in [
        "almond", "badam", "walnut", "akhrot", "cashew", "kaju", "pistachio", "pista",
        "chia seed", "flax seed", "flaxseed", "alasi", "pumpkin seed", "sunflower seed",
        "makhana", "fox nut", "lotus seed", "trail mix", "mixed nuts", "roasted peanut", "roasted chana"
    ]):
        if classification == "Healthy":
            return [
                "🌰 Excellent choice! Raw nuts and seeds provide essential monounsaturated fats, Vitamin E, and dietary fiber",
                "💡 Recommended Portion: A closed handful (25–30g daily) provides maximum cardioprotective benefits",
                "🍿 Lightly Roasted Phool Makhana (Fox Nuts) toasted with A2 Desi Ghee & pink rock salt",
                "🌱 Blend chia and flax seeds into morning smoothies for optimal Omega-3 absorption"
            ]
        else:
            return [
                "🌰 Switch to Raw or Dry-Roasted California Almonds & Kashmiri Walnuts (Zero added oils, zero refined sugar coating)",
                "🍿 Roasted Phool Makhana (Fox Nuts) with a pinch of turmeric and rock salt (Ultra-low calorie, high crunch)",
                "🌱 Roasted 5-Seed Mix (Pumpkin, Sunflower, Chia, Flax, Watermelon seeds) — zinc & magnesium powerhouse",
                "🌴 Soft Medjool Dates stuffed with raw walnut halves (Natural wholesome sweet energy without refined sugar)"
            ]

    # 3. Whole Fresh Fruits & Raw Produce (Apples, Bananas, Oranges, Cucumbers)
    elif any(k in text for k in [
        "apple", "seb", "banana", "kela", "orange", "santra", "mosambi", "citrus",
        "guava", "amrood", "papaya", "papita", "watermelon", "tarbooz", "muskmelon",
        "mango", "aam", "pomegranate", "anar", "grapes", "angoor", "pear", "nashpati",
        "strawberry", "blueberry", "cucumber", "khira", "kakdi", "tomato", "tamatar",
        "fresh fruit", "whole fruit", "raw fruit"
    ]) and not any(p in text for p in ["juice", "syrup", "jam", "jelly", "squash", "candy", "pie", "cake", "chip", "chips"]):
        return [
            "🍎 Outstanding whole-food choice! 100% natural fiber, vitamins, and antioxidants",
            "🥜 Balanced Snack Pairing: Dip fresh apple slices in 1-2 spoons of 100% All-Natural Peanut Butter or Almond Butter",
            "🌱 Superfood Crunch: Sprinkle soaked chia seeds or hemp seeds over fruit bowl for essential Omega-3 fatty acids",
            "🍊 Try seasonal Indian Guava (Amrood) or Papaya for even higher natural Vitamin C and prebiotic gut fiber",
            "🌰 Pair with a handful of raw Kashmiri walnuts or almonds to stabilize glycemic response"
        ]

    # 4. Carbonated Soft Drinks & Energy Drinks (Cold Drinks)
    elif any(k in text for k in [
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

    # 4. Packaged Juices & Nectars
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

    # 5. Commercial Milk & Beverage Powders / Teas
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

    # 6. Breakfast Cereals & Oats
    elif any(k in text for k in ["oat", "muesli", "granola", "corn flakes", "cornflakes", "chocos", "cereal"]):
        return [
            "🥣 100% Whole Rolled Oats or Steel Cut Oats cooked with milk, cinnamon & fresh berries",
            "🌾 Homemade Roasted Muesli (Rolled oats, crushed almonds, walnuts, seeds, zero added sugar)",
            "🌾 Ragi (Finger Millet) Flakes or Jowar Flakes with warm spiced milk & crushed nuts",
            "🥣 Savory Vegetable Oats Khichdi cooked with moong dal, carrots, and cumin"
        ]

    # 7. Chips & Extruded Snacks
    elif any(k in text for k in [
        "chip", "crisp", "wafer", "nacho", "dorito", "lays", "kurkure", "bingo", "pringles", "cheetos"
    ]):
        return [
            "🍿 Roasted Makhana (Fox Nuts) with cold-pressed olive oil & pink rock salt",
            "🌾 Baked Jowar / Ragi chips or air-dried beetroot crisps (low oil)",
            "🥜 Roasted Salted Chana (chickpeas) & roasted peanuts mix",
            "🥗 Sprouted Moong & Boiled Sweet Corn Chaat with lemon dressing"
        ]

    # 8. Namkeen & Fried Savories
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

    # 9. Biscuits, Cookies & Bakery
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

    # 10. Instant Noodles & Pasta
    elif any(k in text for k in [
        "noodle", "maggi", "ramen", "pasta", "yippee", "macaroni", "spaghetti", "hakka", "chowmein", "wai wai"
    ]):
        return [
            "🍜 100% Foxtail Millet or Whole Wheat Noodles with sauteed vegetables",
            "🥕 Steamed Vegetable Vermicelli (Seviyan Upma) with mustard seeds & curry leaves",
            "🥣 Vegetable Rolled Oats Khichdi cooked with fresh peas & carrots",
            "🥒 Zucchini Ribbon Noodles (Zoodles) with homemade fresh tomato basil sauce"
        ]

    # 11. Chocolates, Candies & Sweets
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

    # 12. Ice Creams & Frozen Desserts
    elif any(k in text for k in ["ice cream", "icecream", "kulfi", "sundae", "gelato", "dessert"]):
        return [
            "🍧 Frozen Banana 'Nice Cream' blended with raw cocoa powder & almond milk",
            "🥣 Creamy Greek Yogurt or Hung Curd topped with fresh berries & chia seeds",
            "🥭 Homemade Mango & Chia Seed Pudding made with coconut milk",
            "🥛 Chilled Badam Kheer sweetened naturally with crushed dates"
        ]

    # 13. Fast Food & Burgers / Pizzas
    elif any(k in text for k in ["burger", "pizza", "fries", "frankie", "roll", "sandwich", "patty"]):
        return [
            "🌯 Whole Wheat Grilled Paneer & Capsicum Wrap with mint curd spread",
            "🍟 Air-Fried Sweet Potato Wedges tossed with herbs & olive oil",
            "🍕 Thin-Crust Millet / Ragi base vegetable pizza with homemade cottage cheese",
            "🧆 Sprouted Rajma & Oats vegetable cutlets with coriander-mint chutney"
        ]

    # 14. Sauces, Ketchup & Dips (excludes nut butters)
    elif any(k in text for k in ["ketchup", "mayonnaise", "mayo", "jam", "nutella", "dip", "dressing"]):
        return [
            "🌿 Fresh homemade Dhania-Pudina (Coriander-Mint) Chutney",
            "🫒 Homemade Creamy Hummus drizzled with extra virgin olive oil",
            "🥣 Hung Curd Garlic & Herb Dip (high protein, zero trans fat)",
            "🍅 Fresh Homemade Tomato & Jalapeno Salsa (zero corn syrup)"
        ]

    # 15. General Fallback
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
