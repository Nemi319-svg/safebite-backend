"""
SafeBite Indian Street Food Nutrition, Hygiene & Reused Oil Safety Database
==========================================================================
Author: Vaibhav112027 <vaibhavv1239@gmail.com>

Comprehensive clinical and nutritional repository for popular Indian street foods:
- North India: Samosa, Chole Bhature, Aloo Tikki, Golgappe / Pani Puri, Momos, Bedmi Puri
- West India: Vada Pav, Pav Bhaji, Sev Puri, Dabeli, Misal Pav, Bhel Puri
- South India: Medu Vada, Masala Dosa, Bajji / Pakora, Idli Sambhar, Egg Puff
- East India: Puchka, Kathi Roll, Jhalmuri, Litti Chokha, Singara

Evaluates:
1. Calorie and macronutrient density per standard street portion.
2. Glycemic spike risk based on refined maida and potato starch loads.
3. FSSAI Total Polar Compounds (TPC) frying oil degradation risk (>25% TPC limit).
4. Street water/chutney hygiene vulnerability and bacterial contamination risk.
5. Actionable ordering modifications to reduce calories, glycemic load, and trans-fats.
"""

from typing import Dict, List, Optional, Any


INDIAN_STREET_FOOD_DATABASE: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # 1. NORTH INDIAN STREET FOOD (उत्तर भारतीय स्ट्रीट फूड)
    # =========================================================================
    "samosa_aloo": {
        "food_id": "samosa_aloo",
        "name": "Aloo Samosa (Standard Deep-Fried)",
        "hindi_name": "आलू समोसा",
        "region": "North India",
        "serving_size_g": 120.0,
        "standard_portion": "1 large piece (120g)",
        "calories": 308.0,
        "protein_g": 4.5,
        "carbs_g": 32.8,
        "fat_g": 17.5,
        "saturated_fat_g": 6.8,
        "trans_fat_g": 0.6,
        "sugar_g": 1.5,
        "fiber_g": 2.2,
        "sodium_mg": 460.0,
        "glycemic_index": 72,
        "glycemic_load": 23.6,
        "is_deep_fried": True,
        "tpc_oil_risk_level": "high",
        "hygiene_vulnerability": "low",  # Cooked at high heat
        "health_score": 38,
        "traffic_light": "RED",
        "safety_concerns": [
            "Commercial street vendors frequently reuse frying oil for 3-5 days, forming carcinogenic Total Polar Compounds (TPC)",
            "High trans-fats from hydrogenated vanaspati",
            "Refined flour (maida) crust causes steep postprandial glucose spike"
        ],
        "smart_customization_tips": [
            "Opt for baked or air-fried samosa if available",
            "Discard outer maida thick corners to cut 70 calories and 4g fat",
            "Eat with green mint-coriander chutney instead of high-sugar sweet tamarind saunth",
            "Pair with a handful of roasted chana to blunt glycemic response"
        ]
    },
    "chole_bhature": {
        "food_id": "chole_bhature",
        "name": "Chole Bhature (2 Bhature with Chana Masala)",
        "hindi_name": "छोले भटूरे",
        "region": "North India",
        "serving_size_g": 380.0,
        "standard_portion": "2 Bhature + 1 cup Chole + Pickle & Onion",
        "calories": 780.0,
        "protein_g": 18.5,
        "carbs_g": 88.0,
        "fat_g": 38.0,
        "saturated_fat_g": 14.5,
        "trans_fat_g": 1.2,
        "sugar_g": 4.5,
        "fiber_g": 8.5,
        "sodium_mg": 1180.0,
        "glycemic_index": 76,
        "glycemic_load": 66.8,
        "is_deep_fried": True,
        "tpc_oil_risk_level": "extreme",
        "hygiene_vulnerability": "low",
        "health_score": 32,
        "traffic_light": "RED",
        "safety_concerns": [
            "Single meal provides nearly 40% of daily calories and 80% of daily fat limit",
            "Bhatura dough fermented with baking soda and deep-fried absorbs ~18g oil per piece",
            "Extreme sodium (1180mg) triggers arterial stiffness and fluid retention"
        ],
        "smart_customization_tips": [
            "Ask for 1 Bhatura instead of 2, or substitute with tandoori roti / kulcha",
            "Request chole without the floating oil 'tari' layer on top",
            "Eat raw onion salad with lemon juice before starting to slow carbohydrate absorption"
        ]
    },
    "pani_puri_golgappa": {
        "food_id": "pani_puri_golgappa",
        "name": "Pani Puri / Golgappa (6 puris with spicy mint water)",
        "hindi_name": "पानी पूरी / गोलगप्पा",
        "region": "Pan-India",
        "serving_size_g": 180.0,
        "standard_portion": "6 pieces with teekha pani & boiled potato-chana filling",
        "calories": 210.0,
        "protein_g": 3.8,
        "carbs_g": 34.0,
        "fat_g": 6.8,
        "saturated_fat_g": 2.2,
        "trans_fat_g": 0.1,
        "sugar_g": 3.2,
        "fiber_g": 2.8,
        "sodium_mg": 740.0,
        "glycemic_index": 65,
        "glycemic_load": 22.1,
        "is_deep_fried": True,
        "tpc_oil_risk_level": "low",
        "hygiene_vulnerability": "high",  # Unboiled water and raw mint
        "health_score": 58,
        "traffic_light": "YELLOW",
        "safety_concerns": [
            "Major source of water-borne pathogens (E. coli, Salmonella) if vendor uses unfiltered ice/water",
            "High sodium from black salt and jaljeera spices (740mg for 6 pieces)"
        ],
        "smart_customization_tips": [
            "Ensure the vendor uses verified RO/bottled drinking water and wears gloves",
            "Choose sprouted moong / boiled chana filling rather than mashed potato",
            "Skip sweet meetha chutney (concentrated sugar syrup) to avoid insulin spike"
        ]
    },
    "aloo_tikki_chaat": {
        "food_id": "aloo_tikki_chaat",
        "name": "Aloo Tikki Chaat with Dahi & Chutneys",
        "hindi_name": "आलू टिक्की चाट",
        "region": "North India",
        "serving_size_g": 200.0,
        "standard_portion": "2 Tikkis with 50g curd & chutneys",
        "calories": 365.0,
        "protein_g": 6.2,
        "carbs_g": 48.0,
        "fat_g": 16.5,
        "saturated_fat_g": 5.2,
        "trans_fat_g": 0.4,
        "sugar_g": 8.5,
        "fiber_g": 3.4,
        "sodium_mg": 680.0,
        "glycemic_index": 75,
        "glycemic_load": 36.0,
        "is_deep_fried": True,
        "tpc_oil_risk_level": "high",
        "hygiene_vulnerability": "moderate",
        "health_score": 45,
        "traffic_light": "YELLOW",
        "safety_concerns": [
            "Tawa shallow-frying continually oxidizes oil over 8+ hours of service",
            "Sweet tamarind chutney adds 8-10g of simple sucrose"
        ],
        "smart_customization_tips": [
            "Request extra plain dahi (yogurt) and green chutney, skip sweet tamarind saunth",
            "Ask for non-fried grilled sweet potato (shakarkandi) chaat as a nutritious alternative"
        ]
    },
    "steamed_veg_momos": {
        "food_id": "steamed_veg_momos",
        "name": "Steamed Vegetable Momos (6 pieces with red chili chutney)",
        "hindi_name": "वेज स्टीम्ड मोमोज़",
        "region": "North / Northeast India",
        "serving_size_g": 150.0,
        "standard_portion": "6 steamed dumplings with red spicy dip",
        "calories": 215.0,
        "protein_g": 5.8,
        "carbs_g": 38.0,
        "fat_g": 4.5,
        "saturated_fat_g": 1.1,
        "trans_fat_g": 0.0,
        "sugar_g": 1.8,
        "fiber_g": 2.6,
        "sodium_mg": 520.0,
        "glycemic_index": 62,
        "glycemic_load": 23.5,
        "is_deep_fried": False,
        "tpc_oil_risk_level": "none",
        "hygiene_vulnerability": "low",
        "health_score": 74,
        "traffic_light": "GREEN",
        "safety_concerns": [
            "Casing is made of refined maida",
            "Red garlic-chili dip can trigger gastritis or acid reflux in sensitive stomachs",
            "Occasional usage of Monosodium Glutamate (MSG E621) in filling"
        ],
        "smart_customization_tips": [
            "Always choose steamed over fried or tandoori afghani momos (saves 180 kcal and 14g fat)",
            "Ask for whole wheat momos where available",
            "Use red chili dip sparingly to prevent mucosal lining irritation"
        ]
    },

    # =========================================================================
    # 2. WEST INDIAN STREET FOOD (पश्चिम भारतीय स्ट्रीट फूड)
    # =========================================================================
    "mumbai_vada_pav": {
        "food_id": "mumbai_vada_pav",
        "name": "Mumbai Vada Pav with Lasun Chutney",
        "hindi_name": "मुंबई वड़ा पाव",
        "region": "West India (Maharashtra)",
        "serving_size_g": 140.0,
        "standard_portion": "1 Batata Vada in Pav with dry garlic & green chutney",
        "calories": 340.0,
        "protein_g": 6.8,
        "carbs_g": 46.0,
        "fat_g": 14.5,
        "saturated_fat_g": 5.4,
        "trans_fat_g": 0.5,
        "sugar_g": 2.8,
        "fiber_g": 3.2,
        "sodium_mg": 580.0,
        "glycemic_index": 78,
        "glycemic_load": 35.8,
        "is_deep_fried": True,
        "tpc_oil_risk_level": "high",
        "hygiene_vulnerability": "low",
        "health_score": 42,
        "traffic_light": "RED",
        "safety_concerns": [
            "Double carbohydrate loading: mashed potato ball encased in besan inside white flour pav",
            "Repeated frying of batata vada in large kadhai generates oxidized lipid hydroperoxides",
            "High glycemic index (78)"
        ],
        "smart_customization_tips": [
            "Eat only the batata vada without the white bread pav to eliminate 160 calories of empty refined starch",
            "Ask for non-buttered pav",
            "Avoid fried green chilies if prone to acidity"
        ]
    },
    "mumbai_pav_bhaji": {
        "food_id": "mumbai_pav_bhaji",
        "name": "Mumbai Butter Pav Bhaji (2 Buttered Pav + Bhaji)",
        "hindi_name": "पाव भाजी",
        "region": "West India (Maharashtra)",
        "serving_size_g": 300.0,
        "standard_portion": "2 Pav toasted in butter with 1 bowl mixed veg bhaji",
        "calories": 590.0,
        "protein_g": 10.2,
        "carbs_g": 68.0,
        "fat_g": 31.0,
        "saturated_fat_g": 16.8,
        "trans_fat_g": 0.8,
        "sugar_g": 6.5,
        "fiber_g": 6.4,
        "sodium_mg": 920.0,
        "glycemic_index": 70,
        "glycemic_load": 47.6,
        "is_deep_fried": False,
        "tpc_oil_risk_level": "moderate",
        "hygiene_vulnerability": "low",
        "health_score": 48,
        "traffic_light": "YELLOW",
        "safety_concerns": [
            "Heavy application of commercial salted butter (often 40-50g per plate)",
            "Yellow food coloring (Tartrazine E102) commonly added by vendors to give vibrant red/orange hue",
            "High sodium content (920mg)"
        ],
        "smart_customization_tips": [
            "Request 'sukha pav' (plain toasted pav without butter) or specify 'half butter'",
            "Ask vendor not to add artificial red food color to the bhaji",
            "Squeeze fresh lemon generously (citric acid aids digestion and antioxidant protection)"
        ]
    },
    "bhel_puri_mumbai": {
        "food_id": "bhel_puri_mumbai",
        "name": "Bhel Puri (Puffed rice, sev, onions & chutneys)",
        "hindi_name": "भेल पूरी",
        "region": "West India",
        "serving_size_g": 150.0,
        "standard_portion": "1 paper cone / plate (150g)",
        "calories": 240.0,
        "protein_g": 5.2,
        "carbs_g": 42.0,
        "fat_g": 6.2,
        "saturated_fat_g": 1.8,
        "trans_fat_g": 0.2,
        "sugar_g": 4.8,
        "fiber_g": 3.8,
        "sodium_mg": 460.0,
        "glycemic_index": 68,
        "glycemic_load": 28.5,
        "is_deep_fried": False,
        "tpc_oil_risk_level": "low",
        "hygiene_vulnerability": "moderate",
        "health_score": 72,
        "traffic_light": "GREEN",
        "safety_concerns": [
            "Sev and papdi are deep fried",
            "Raw unwashed coriander and onions carry surface contamination risk during monsoons"
        ],
        "smart_customization_tips": [
            "Request 'sukha bhel' (dry bhel without sweet tamarind syrup) to reduce simple sugars",
            "Ask for extra roasted peanuts and boiled chana for more protein and lower glycemic load",
            "Request minimal sev"
        ]
    },

    # =========================================================================
    # 3. SOUTH INDIAN STREET FOOD (दक्षिण भारतीय स्ट्रीट फूड)
    # =========================================================================
    "medu_vada_sambar": {
        "food_id": "medu_vada_sambar",
        "name": "Medu Vada (2 pieces with Sambar & Coconut Chutney)",
        "hindi_name": "मेदू वड़ा सांभर",
        "region": "South India",
        "serving_size_g": 220.0,
        "standard_portion": "2 crispy urad dal vadas with 1 cup sambar & chutney",
        "calories": 420.0,
        "protein_g": 12.4,
        "carbs_g": 42.0,
        "fat_g": 23.0,
        "saturated_fat_g": 9.2,
        "trans_fat_g": 0.4,
        "sugar_g": 2.2,
        "fiber_g": 5.8,
        "sodium_mg": 710.0,
        "glycemic_index": 60,
        "glycemic_load": 25.2,
        "is_deep_fried": True,
        "tpc_oil_risk_level": "high",
        "hygiene_vulnerability": "low",
        "health_score": 52,
        "traffic_light": "YELLOW",
        "safety_concerns": [
            "Porous urad dal batter absorbs substantial frying oil (~11g fat per vada)",
            "Coconut chutney made with raw scraped coconut and curd spoils quickly in warm temperatures"
        ],
        "smart_customization_tips": [
            "Order 1 Idli + 1 Vada combo instead of 2 vadas to instantly slash 150 calories and 10g fat",
            "Eat more vegetable-packed sambar (rich in lentils, drumsticks, and spices) instead of dense coconut chutney"
        ]
    },
    "masala_dosa_street": {
        "food_id": "masala_dosa_street",
        "name": "Street-Style Masala Dosa with Butter/Ghee",
        "hindi_name": "मसाला डोसा",
        "region": "South India",
        "serving_size_g": 240.0,
        "standard_portion": "1 large crispy fermented rice-dal crepe with potato filling",
        "calories": 385.0,
        "protein_g": 7.5,
        "carbs_g": 55.0,
        "fat_g": 15.0,
        "saturated_fat_g": 6.5,
        "trans_fat_g": 0.3,
        "sugar_g": 2.0,
        "fiber_g": 4.2,
        "sodium_mg": 620.0,
        "glycemic_index": 64,
        "glycemic_load": 35.2,
        "is_deep_fried": False,
        "tpc_oil_risk_level": "low",
        "hygiene_vulnerability": "low",
        "health_score": 68,
        "traffic_light": "YELLOW",
        "safety_concerns": [
            "Street vendors often pour 20-30g melted butter or dalda ghee on the tawa for crispiness",
            "Potato palya filling is high in starchy carbohydrates"
        ],
        "smart_customization_tips": [
            "Request 'Plain Dosa' or 'Dosa with minimal oil/ghee'",
            "Opt for 'Set Dosa' or 'Ragi Dosa' if offered by vendor",
            "Consume with piping hot tomato or lentil sambar"
        ]
    },

    # =========================================================================
    # 4. EAST INDIAN STREET FOOD (पूर्वी भारतीय स्ट्रीट फूड)
    # =========================================================================
    "kolkata_kathi_roll_paneer": {
        "food_id": "kolkata_kathi_roll_paneer",
        "name": "Kolkata Paneer Kathi Roll (Paratha wrap)",
        "hindi_name": "कोलकाता पनीर काठी रोल",
        "region": "East India (Bengal)",
        "serving_size_g": 220.0,
        "standard_portion": "1 flaky maida paratha rolled with spiced paneer & salad",
        "calories": 480.0,
        "protein_g": 15.5,
        "carbs_g": 52.0,
        "fat_g": 24.0,
        "saturated_fat_g": 9.5,
        "trans_fat_g": 0.6,
        "sugar_g": 3.8,
        "fiber_g": 3.5,
        "sodium_mg": 740.0,
        "glycemic_index": 71,
        "glycemic_load": 36.9,
        "is_deep_fried": False,
        "tpc_oil_risk_level": "moderate",
        "hygiene_vulnerability": "low",
        "health_score": 54,
        "traffic_light": "YELLOW",
        "safety_concerns": [
            "Flaky layered paratha fried with generous vegetable oil / dalda",
            "High sodium sauces and refined white flour base"
        ],
        "smart_customization_tips": [
            "Request the wrap to be made on a dry tawa roti rather than oil-soaked paratha",
            "Ask to skip mayonnaise or high-sodium cheese spreads",
            "Request extra raw onions, capsicum, and cucumber filling"
        ]
    },
    "litti_chokha_bihar": {
        "food_id": "litti_chokha_bihar",
        "name": "Bihari Litti Chokha (2 Littis roasted with Baingan Chokha)",
        "hindi_name": "लिट्टी चोखा",
        "region": "East India (Bihar)",
        "serving_size_g": 280.0,
        "standard_portion": "2 whole wheat littis stuffed with sattu, served with roasted eggplant chokha",
        "calories": 410.0,
        "protein_g": 16.8,
        "carbs_g": 64.0,
        "fat_g": 10.2,
        "saturated_fat_g": 4.8,
        "trans_fat_g": 0.0,
        "sugar_g": 3.2,
        "fiber_g": 9.8,
        "sodium_mg": 520.0,
        "glycemic_index": 52,
        "glycemic_load": 33.2,
        "is_deep_fried": False,
        "tpc_oil_risk_level": "none",
        "hygiene_vulnerability": "low",
        "health_score": 86,
        "traffic_light": "GREEN",
        "safety_concerns": [
            "Vendors occasionally submerge hot littis in deep bowls of commercial ghee/dalda",
            "Ensure mustard oil used in chokha is food-grade"
        ],
        "smart_customization_tips": [
            "Request 'dry roasted litti' with a light brush of ghee rather than complete soaking",
            "Sattu (roasted gram flour) is one of India's richest plant proteins and low-GI foods; superior street food choice"
        ]
    }
}


def get_street_food_profile(food_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves street food safety and nutrition data by ID."""
    return INDIAN_STREET_FOOD_DATABASE.get(food_id.lower().strip())


def search_street_foods(query: str) -> List[Dict[str, Any]]:
    """Searches street foods by Hindi or English name or region."""
    q = query.lower().strip()
    return [
        item for item in INDIAN_STREET_FOOD_DATABASE.values()
        if q in item["name"].lower() or q in item["hindi_name"] or q in item["region"].lower()
    ]


def filter_street_foods_by_traffic_light(traffic_light: str) -> List[Dict[str, Any]]:
    """Filters street food items by GREEN, YELLOW, or RED rating."""
    target = traffic_light.upper().strip()
    return [item for item in INDIAN_STREET_FOOD_DATABASE.values() if item["traffic_light"] == target]
