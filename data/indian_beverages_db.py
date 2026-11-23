"""
SafeBite Indian Beverages, Liquid Sugar & Electrolyte Database
==============================================================
Author: Vaibhav112027 <vaibhavv1239@gmail.com>

Provides detailed nutrition, added sugar, caffeine, sodium, potassium,
glycemic spike potential, and hydration efficiency factor for popular Indian drinks:
- Traditional Homemade Drinks (Masala Chai, Filter Coffee, Nimbu Pani, Chaas, Sattu)
- Summer Street Coolers (Sugarcane Juice, Aam Panna, Kokum Sharbat, Jaljeera, Lassi)
- Natural Electrolytes (Tender Coconut Water, Barley Water)
- Packaged & Cafe Beverages (Cold Coffee, Energy Drinks, Mango Drinks, Flavored Milk)
"""

from typing import Dict, List, Optional, Any


INDIAN_BEVERAGES_DB: Dict[str, Dict[str, Any]] = {
    "tender_coconut_water": {
        "drink_id": "tender_coconut_water",
        "name": "Tender Coconut Water (Nariyal Pani)",
        "category": "Natural Electrolyte",
        "serving_ml": 250.0,
        "calories": 48.0,
        "sugar_g": 6.5,
        "added_sugar_g": 0.0,
        "sodium_mg": 250.0,
        "potassium_mg": 600.0,
        "magnesium_mg": 60.0,
        "caffeine_mg": 0.0,
        "hydration_efficiency_index": 1.15,
        "glycemic_index": 54,
        "health_score": 96,
        "traffic_light": "GREEN",
        "benefits": [
            "Rich in bioavailable potassium (600mg) and natural electrolytes",
            "Zero added sugar, zero preservatives, isotonic cellular hydration"
        ],
        "cautions": [
            "CKD Stage 3-5 kidney patients should monitor potassium load"
        ]
    },
    "spiced_buttermilk_chaas": {
        "drink_id": "spiced_buttermilk_chaas",
        "name": "Traditional Spiced Buttermilk (Masala Chaas)",
        "category": "Probiotic Cooler",
        "serving_ml": 250.0,
        "calories": 65.0,
        "sugar_g": 4.2,
        "added_sugar_g": 0.0,
        "sodium_mg": 340.0,
        "potassium_mg": 240.0,
        "magnesium_mg": 22.0,
        "caffeine_mg": 0.0,
        "hydration_efficiency_index": 1.12,
        "glycemic_index": 30,
        "health_score": 92,
        "traffic_light": "GREEN",
        "benefits": [
            "Live Lactobacillus probiotics support gut health and digestion",
            "Cumin (jeera) and ginger soothe post-meal bloating",
            "Extremely low glycemic index (30)"
        ],
        "cautions": [
            "Hypertensive patients should ask for less black salt (kala namak)"
        ]
    },
    "sattu_namkeen_cooler": {
        "drink_id": "sattu_namkeen_cooler",
        "name": "Bihari Roasted Gram Drink (Namkeen Sattu Sharbat)",
        "category": "Protein Cooler",
        "serving_ml": 250.0,
        "calories": 145.0,
        "sugar_g": 1.2,
        "added_sugar_g": 0.0,
        "sodium_mg": 290.0,
        "potassium_mg": 320.0,
        "magnesium_mg": 55.0,
        "caffeine_mg": 0.0,
        "hydration_efficiency_index": 1.05,
        "glycemic_index": 28,
        "health_score": 94,
        "traffic_light": "GREEN",
        "benefits": [
            "Provides 9.5g plant protein and insoluble dietary fiber",
            "Prevents summer heatstroke (loo) while keeping blood sugar completely steady"
        ],
        "cautions": []
    },
    "masala_chai_with_sugar": {
        "drink_id": "masala_chai_with_sugar",
        "name": "Indian Masala Chai (Milk + 2 tsp Sugar)",
        "category": "Hot Beverage",
        "serving_ml": 150.0,
        "calories": 105.0,
        "sugar_g": 13.5,
        "added_sugar_g": 10.0,
        "sodium_mg": 35.0,
        "potassium_mg": 145.0,
        "magnesium_mg": 12.0,
        "caffeine_mg": 42.0,
        "hydration_efficiency_index": 0.85,
        "glycemic_index": 62,
        "health_score": 56,
        "traffic_light": "YELLOW",
        "benefits": [
            "Cardamom, ginger, and black tea polyphenols provide mild antioxidants"
        ],
        "cautions": [
            "Drinking 3-4 cups/day adds 30-40g hidden refined white sugar",
            "Tannins in tea inhibit iron absorption if taken immediately with meals"
        ]
    },
    "masala_chai_unsweetened": {
        "drink_id": "masala_chai_unsweetened",
        "name": "Indian Masala Chai (No Added Sugar)",
        "category": "Hot Beverage",
        "serving_ml": 150.0,
        "calories": 62.0,
        "sugar_g": 3.5,
        "added_sugar_g": 0.0,
        "sodium_mg": 35.0,
        "potassium_mg": 145.0,
        "magnesium_mg": 12.0,
        "caffeine_mg": 42.0,
        "hydration_efficiency_index": 0.88,
        "glycemic_index": 34,
        "health_score": 82,
        "traffic_light": "GREEN",
        "benefits": [
            "Eliminates empty sucrose calories while preserving spice anti-inflammatories"
        ],
        "cautions": [
            "Wait 45 minutes after iron-rich meals before drinking tea"
        ]
    },
    "south_indian_filter_coffee": {
        "drink_id": "south_indian_filter_coffee",
        "name": "South Indian Filter Coffee (Full Milk + 2 tsp Sugar)",
        "category": "Hot Beverage",
        "serving_ml": 150.0,
        "calories": 122.0,
        "sugar_g": 14.5,
        "added_sugar_g": 10.0,
        "sodium_mg": 45.0,
        "potassium_mg": 190.0,
        "magnesium_mg": 18.0,
        "caffeine_mg": 85.0,
        "hydration_efficiency_index": 0.80,
        "glycemic_index": 60,
        "health_score": 54,
        "traffic_light": "YELLOW",
        "benefits": [
            "Chicory root provides gentle prebiotic inulin fiber",
            "Boosts alertness and metabolic rate"
        ],
        "cautions": [
            "High caffeine (85mg) + full cream milk + 10g added sugar"
        ]
    },
    "sweet_punjabi_lassi": {
        "drink_id": "sweet_punjabi_lassi",
        "name": "Sweet Punjabi Malai Lassi",
        "category": "Dairy Cooler",
        "serving_ml": 300.0,
        "calories": 340.0,
        "sugar_g": 36.0,
        "added_sugar_g": 28.0,
        "sodium_mg": 95.0,
        "potassium_mg": 310.0,
        "magnesium_mg": 28.0,
        "caffeine_mg": 0.0,
        "hydration_efficiency_index": 0.90,
        "glycemic_index": 68,
        "health_score": 44,
        "traffic_light": "RED",
        "benefits": [
            "Good calcium and probiotic curd base"
        ],
        "cautions": [
            "Contains ~7 teaspoons of added sugar (28g) + heavy malai fat",
            "High glycemic load; unsafe for diabetic or weight-loss goals"
        ]
    },
    "fresh_sugarcane_juice": {
        "drink_id": "fresh_sugarcane_juice",
        "name": "Fresh Sugarcane Juice (Ganne Ka Ras with Lemon & Mint)",
        "category": "Street Cooler",
        "serving_ml": 250.0,
        "calories": 185.0,
        "sugar_g": 42.0,
        "added_sugar_g": 0.0,
        "sodium_mg": 25.0,
        "potassium_mg": 180.0,
        "magnesium_mg": 20.0,
        "caffeine_mg": 0.0,
        "hydration_efficiency_index": 0.95,
        "glycemic_index": 64,
        "health_score": 58,
        "traffic_light": "YELLOW",
        "benefits": [
            "Rich in natural iron, calcium, and fast-acting glucose for outdoor physical exertion"
        ],
        "cautions": [
            "42g liquid sugar (~10.5 teaspoons equivalent) spikes blood sugar rapidly if sedentary",
            "Verify street vendor cleans cane and avoids unhygienic commercial ice blocks"
        ]
    },
    "nimbu_pani_salt_lemon": {
        "drink_id": "nimbu_pani_salt_lemon",
        "name": "Salted Nimbu Shikanji (No Sugar, With Black Salt & Jeera)",
        "category": "Homemade Electrolyte",
        "serving_ml": 250.0,
        "calories": 14.0,
        "sugar_g": 0.8,
        "added_sugar_g": 0.0,
        "sodium_mg": 320.0,
        "potassium_mg": 85.0,
        "magnesium_mg": 8.0,
        "caffeine_mg": 0.0,
        "hydration_efficiency_index": 1.10,
        "glycemic_index": 15,
        "health_score": 95,
        "traffic_light": "GREEN",
        "benefits": [
            "High Vitamin C + natural citrate prevents kidney stones",
            "Zero added sugar, ideal for diabetes, weight loss, and dehydration recovery"
        ],
        "cautions": [
            "Keep salt moderate if hypertensive"
        ]
    },
    "aam_panna_sweetened": {
        "drink_id": "aam_panna_sweetened",
        "name": "Raw Mango Aam Panna (Standard Sweetened)",
        "category": "Summer Cooler",
        "serving_ml": 250.0,
        "calories": 155.0,
        "sugar_g": 34.0,
        "added_sugar_g": 28.0,
        "sodium_mg": 260.0,
        "potassium_mg": 140.0,
        "magnesium_mg": 15.0,
        "caffeine_mg": 0.0,
        "hydration_efficiency_index": 0.95,
        "glycemic_index": 66,
        "health_score": 52,
        "traffic_light": "YELLOW",
        "benefits": [
            "Traditional remedy against heat exhaustion with roasted cumin and mint"
        ],
        "cautions": [
            "Commercial/restaurant versions load 28g+ refined sugar syrup"
        ]
    },
    "packaged_mango_drink_frooti": {
        "drink_id": "packaged_mango_drink_frooti",
        "name": "Packaged Mango Fruit Drink (Tetra Pack / Bottle)",
        "category": "Packaged Sugar Drink",
        "serving_ml": 250.0,
        "calories": 145.0,
        "sugar_g": 34.5,
        "added_sugar_g": 30.0,
        "sodium_mg": 45.0,
        "potassium_mg": 35.0,
        "magnesium_mg": 3.0,
        "caffeine_mg": 0.0,
        "hydration_efficiency_index": 0.65,
        "glycemic_index": 74,
        "health_score": 26,
        "traffic_light": "RED",
        "benefits": [],
        "cautions": [
            "Only 15-18% mango pulp; rest is water, high sugar syrup, citric acid, and synthetic flavor",
            "34.5g sugar (~8.5 teaspoons) spikes insulin and promotes fatty liver"
        ]
    },
    "packaged_energy_drink_sting": {
        "drink_id": "packaged_energy_drink_sting",
        "name": "Carbonated Caffeinated Energy Drink (250ml)",
        "category": "Energy Drink",
        "serving_ml": 250.0,
        "calories": 115.0,
        "sugar_g": 27.5,
        "added_sugar_g": 27.5,
        "sodium_mg": 160.0,
        "potassium_mg": 10.0,
        "magnesium_mg": 0.0,
        "caffeine_mg": 72.0,
        "hydration_efficiency_index": 0.55,
        "glycemic_index": 78,
        "health_score": 18,
        "traffic_light": "RED",
        "benefits": [],
        "cautions": [
            "Combines 72mg caffeine + 27.5g sugar + synthetic Red 40 / Allura Red dye (E129)",
            "Dehydrating effect; triggers tachycardia and insulin resistance"
        ]
    },
    "cafe_cold_coffee_ice_cream": {
        "drink_id": "cafe_cold_coffee_ice_cream",
        "name": "Cafe Style Cold Coffee with Chocolate Syrup & Ice Cream",
        "category": "Cafe Beverage",
        "serving_ml": 300.0,
        "calories": 385.0,
        "sugar_g": 44.0,
        "added_sugar_g": 35.0,
        "sodium_mg": 140.0,
        "potassium_mg": 280.0,
        "magnesium_mg": 24.0,
        "caffeine_mg": 95.0,
        "hydration_efficiency_index": 0.70,
        "glycemic_index": 70,
        "health_score": 30,
        "traffic_light": "RED",
        "benefits": [],
        "cautions": [
            "Equivalent in calories and sugar to eating 2 chocolate pastries",
            "44g liquid sugar (~11 teaspoons)"
        ]
    }
}


def get_beverage_profile(drink_id: str) -> Optional[Dict[str, Any]]:
    """Fetches nutritional and hydration efficiency metrics for an Indian beverage."""
    return INDIAN_BEVERAGES_DB.get(drink_id.lower().strip())


def search_beverages(query: str) -> List[Dict[str, Any]]:
    """Searches beverages by name or category."""
    q = query.lower().strip()
    return [
        b for b in INDIAN_BEVERAGES_DB.values()
        if q in b["name"].lower() or q in b["category"].lower()
    ]
