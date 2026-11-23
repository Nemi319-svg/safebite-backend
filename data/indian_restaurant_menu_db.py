"""
SafeBite Indian Restaurant & QSR Menu Nutrition, Allergen & Smart Ordering Database
===================================================================================
Author: Vaibhav112027 <vaibhavv1239@gmail.com>

Provides verified nutritional data, hidden allergen flags, sodium/sugar warnings,
and practical 'Order Smart' customization strategies for popular Indian dining chains
and restaurant dishes:
- Quick Service Restaurants (McDonald's India, Domino's India, Burger King, Subway)
- Traditional Indian Dining Chains (Haldiram's, Bikanervala, Saravana Bhavan, Sagar Ratna)
- Casual Indian Restaurant Classics (Butter Chicken, Dal Makhani, Paneer Tikka, Masala Dosa)
"""

from typing import Dict, List, Optional, Any


INDIAN_RESTAURANT_MENU_DB: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # 1. QSR CHAINS (McDonald's, Domino's, Burger King, Subway India)
    # =========================================================================
    "mcdonalds_mcaloo_tikki": {
        "dish_id": "mcdonalds_mcaloo_tikki",
        "restaurant": "McDonald's India",
        "dish_name": "McAloo Tikki Burger (Regular)",
        "category": "QSR Burger",
        "serving_size_g": 146.0,
        "calories": 334.0,
        "protein_g": 6.8,
        "carbs_g": 46.2,
        "fat_g": 13.5,
        "saturated_fat_g": 5.2,
        "sugar_g": 6.4,
        "fiber_g": 3.1,
        "sodium_mg": 612.0,
        "allergens": ["Gluten (Wheat)", "Soy", "Milk traces"],
        "health_score": 48,
        "traffic_light": "YELLOW",
        "risk_warnings": [
            "Deep-fried potato-pea patty absorbs refined frying oil",
            "Sweet tomato mayo sauce adds refined sugar and seed oils",
            "612mg sodium is ~27% of daily upper limit"
        ],
        "order_smart_tips": [
            "Request 'No Mayo' to save ~85 kcal and 8g fat",
            "Skip the combo French fries and sugary cola; pair with unsweetened iced tea or water",
            "Ask for extra lettuce, onion, and tomato slices for added fiber"
        ]
    },
    "mcdonalds_mcchicken": {
        "dish_id": "mcdonalds_mcchicken",
        "restaurant": "McDonald's India",
        "dish_name": "McChicken Burger",
        "category": "QSR Burger",
        "serving_size_g": 173.0,
        "calories": 400.0,
        "protein_g": 15.2,
        "carbs_g": 41.0,
        "fat_g": 19.5,
        "saturated_fat_g": 4.8,
        "sugar_g": 5.1,
        "fiber_g": 2.2,
        "sodium_mg": 768.0,
        "allergens": ["Gluten (Wheat)", "Egg (Mayo)", "Soy"],
        "health_score": 44,
        "traffic_light": "RED",
        "risk_warnings": [
            "Reconstituted breaded chicken patty fried in commercial vegetable oil",
            "High sodium (768mg) and mayonnaise-heavy dressing"
        ],
        "order_smart_tips": [
            "Opt for Grilled Chicken Wrap instead of fried patty burger to cut 140 kcal",
            "Ask for half sauce / light mayo"
        ]
    },
    "dominos_margherita_medium_2slices": {
        "dish_id": "dominos_margherita_medium_2slices",
        "restaurant": "Domino's India",
        "dish_name": "Classic Margherita Pizza (2 Medium Slices)",
        "category": "QSR Pizza",
        "serving_size_g": 190.0,
        "calories": 478.0,
        "protein_g": 18.0,
        "carbs_g": 62.0,
        "fat_g": 17.4,
        "saturated_fat_g": 9.8,
        "sugar_g": 5.8,
        "fiber_g": 2.4,
        "sodium_mg": 980.0,
        "allergens": ["Gluten (Wheat)", "Milk (Cheese)", "Soy traces"],
        "health_score": 40,
        "traffic_light": "RED",
        "risk_warnings": [
            "Refined white maida base causes steep blood sugar spikes",
            "Very high sodium (980mg in just 2 slices) from pizza sauce and processed cheese",
            "High saturated dairy fat"
        ],
        "order_smart_tips": [
            "Always switch crust to 'Thin Crust' or 'Wheat Thin Crust' to slash 130 kcal of refined dough",
            "Add high-fiber toppings like onions, capsicum, mushrooms, and jalapenos",
            "Limit to 2 slices and pair with a plain garden salad first"
        ]
    },
    "dominos_peppy_paneer_2slices": {
        "dish_id": "dominos_peppy_paneer_2slices",
        "restaurant": "Domino's India",
        "dish_name": "Peppy Paneer Pizza (2 Medium Slices)",
        "category": "QSR Pizza",
        "serving_size_g": 220.0,
        "calories": 556.0,
        "protein_g": 22.4,
        "carbs_g": 64.0,
        "fat_g": 23.2,
        "saturated_fat_g": 12.1,
        "sugar_g": 6.2,
        "fiber_g": 3.0,
        "sodium_mg": 1140.0,
        "allergens": ["Gluten (Wheat)", "Milk (Cheese & Paneer)", "Soy"],
        "health_score": 38,
        "traffic_light": "RED",
        "risk_warnings": [
            "Extreme sodium (1140mg per 2 slices)",
            "Double dairy fat load from mozzarella cheese + marinated paneer cubes"
        ],
        "order_smart_tips": [
            "Request 'Light Cheese' and choose Thin Crust",
            "Skip extra cheese burst option which adds 280+ calories per slice"
        ]
    },
    "subway_paneer_tikka_6inch": {
        "dish_id": "subway_paneer_tikka_6inch",
        "restaurant": "Subway India",
        "dish_name": "Paneer Tikka Sub (6-inch Multigrain with Standard Sauces)",
        "category": "QSR Sandwich",
        "serving_size_g": 260.0,
        "calories": 465.0,
        "protein_g": 19.8,
        "carbs_g": 54.0,
        "fat_g": 18.6,
        "saturated_fat_g": 7.4,
        "sugar_g": 7.2,
        "fiber_g": 5.8,
        "sodium_mg": 890.0,
        "allergens": ["Gluten (Wheat)", "Milk (Paneer)", "Soy", "Sesame (Multigrain bread)"],
        "health_score": 70,
        "traffic_light": "GREEN",
        "risk_warnings": [
            "Creamy sauces (Southwest Chipotle, Mayonnaise) contribute 130+ hidden fat calories",
            "Multigrain bread contains caramelized coloring and moderate sodium"
        ],
        "order_smart_tips": [
            "Choose 9-Grain Honey Oat or Multigrain toasted without butter",
            "Load up on all fresh veggies (spinach, cucumber, tomato, capsicum, olives)",
            "Pick ONLY 1 low-calorie sauce (Mint Mayonnaise or Mustard) + Vinegar instead of 3 creamy sauces"
        ]
    },
    "subway_roasted_chicken_salad": {
        "dish_id": "subway_roasted_chicken_salad",
        "restaurant": "Subway India",
        "dish_name": "Roasted Chicken Breast Signature Salad Bowl",
        "category": "QSR Salad",
        "serving_size_g": 310.0,
        "calories": 245.0,
        "protein_g": 24.5,
        "carbs_g": 16.0,
        "fat_g": 8.5,
        "saturated_fat_g": 2.1,
        "sugar_g": 5.2,
        "fiber_g": 6.4,
        "sodium_mg": 540.0,
        "allergens": ["Soy traces", "Mustard (if chosen)"],
        "health_score": 89,
        "traffic_light": "GREEN",
        "risk_warnings": [
            "Processed chicken strips contain moderate preservative sodium"
        ],
        "order_smart_tips": [
            "Use olive oil + red wine vinegar or lemon juice as dressing instead of creamy Ranch",
            "Excellent low-carb, high-protein QSR choice for diabetics and weight loss"
        ]
    },

    # =========================================================================
    # 2. INDIAN FAMILY DINING CHAINS (Haldiram's, Saravana Bhavan, Sagar Ratna)
    # =========================================================================
    "haldirams_special_thali": {
        "dish_id": "haldirams_special_thali",
        "restaurant": "Haldiram's",
        "dish_name": "Haldiram's Special North Indian Thali",
        "category": "Restaurant Thali",
        "serving_size_g": 680.0,
        "calories": 1120.0,
        "protein_g": 28.5,
        "carbs_g": 142.0,
        "fat_g": 48.0,
        "saturated_fat_g": 21.0,
        "sugar_g": 24.0,
        "fiber_g": 11.2,
        "sodium_mg": 1680.0,
        "allergens": ["Gluten (Naan/Roti)", "Milk (Paneer, Dal Makhani, Gulab Jamun, Raita)", "Cashew (Gravy)"],
        "health_score": 42,
        "traffic_light": "RED",
        "risk_warnings": [
            "Single thali exceeds 55% of daily calorie budget and 70% of sodium limit",
            "Dal Makhani and Shahi Paneer gravies are heavy in cream, butter, and cashew paste",
            "Includes sugar-soaked Gulab Jamun and buttered Naan"
        ],
        "order_smart_tips": [
            "Swap Butter Naan for plain Tandoori Roti (no butter) to cut 160 kcal",
            "Share the sweet (Gulab Jamun) or skip it completely for diabetic safety",
            "Consume the raita and fresh salad before touching the rich gravies"
        ]
    },
    "haldirams_raj_kachori": {
        "dish_id": "haldirams_raj_kachori",
        "restaurant": "Haldiram's / Bikanervala",
        "dish_name": "Raj Kachori Chaat (1 Large Plate)",
        "category": "Restaurant Chaat",
        "serving_size_g": 340.0,
        "calories": 640.0,
        "protein_g": 12.0,
        "carbs_g": 82.0,
        "fat_g": 29.0,
        "saturated_fat_g": 8.4,
        "sugar_g": 26.0,
        "fiber_g": 4.8,
        "sodium_mg": 980.0,
        "allergens": ["Gluten (Wheat crust)", "Milk (Sweetened Dahi)", "Peanut/Sev traces"],
        "health_score": 36,
        "traffic_light": "RED",
        "risk_warnings": [
            "Large deep-fried crispy shell filled with sweetened curd, sweet saunth, and deep-fried bhalla/sev",
            "26g simple sugars cause rapid glycemic spike"
        ],
        "order_smart_tips": [
            "Split 1 Raj Kachori between 2-3 people as a treat",
            "Ask for unsweetened curd and light sweet tamarind chutney"
        ]
    },
    "saravana_bhavan_mini_tiffin": {
        "dish_id": "saravana_bhavan_mini_tiffin",
        "restaurant": "Saravana Bhavan / Sagar Ratna",
        "dish_name": "South Indian Mini Tiffin (Idli, Vada, Pongal, Mini Dosa, Kesari)",
        "category": "South Indian Combo",
        "serving_size_g": 480.0,
        "calories": 760.0,
        "protein_g": 16.5,
        "carbs_g": 112.0,
        "fat_g": 27.5,
        "saturated_fat_g": 12.5,
        "sugar_g": 18.0,
        "fiber_g": 6.5,
        "sodium_mg": 1120.0,
        "allergens": ["Milk (Ghee in Pongal & Kesari)", "Cashew (Kesari/Pongal)", "Mustard"],
        "health_score": 52,
        "traffic_light": "YELLOW",
        "risk_warnings": [
            "Ghee Pongal and Rava Kesari pack heavy saturated ghee fat and sugar",
            "Deep-fried Medu Vada adds excess oil"
        ],
        "order_smart_tips": [
            "Order plain 'Plate Idli (2 pcs) + Sambar' instead of full Mini Tiffin for a 240 kcal breakfast",
            "Maximize vegetable sambar intake for lentil protein and fiber"
        ]
    },
    "saravana_bhavan_rava_dosa": {
        "dish_id": "saravana_bhavan_rava_dosa",
        "restaurant": "Saravana Bhavan / Sagar Ratna",
        "dish_name": "Onion Rava Masala Dosa",
        "category": "South Indian Dosa",
        "serving_size_g": 280.0,
        "calories": 490.0,
        "protein_g": 8.4,
        "carbs_g": 68.0,
        "fat_g": 20.5,
        "saturated_fat_g": 7.8,
        "sugar_g": 3.2,
        "fiber_g": 3.8,
        "sodium_mg": 780.0,
        "allergens": ["Gluten (Rava/Sooji & Maida)", "Cashew", "Milk (Ghee)"],
        "health_score": 54,
        "traffic_light": "YELLOW",
        "risk_warnings": [
            "Unlike regular fermented rice-dal dosa, Rava dosa uses semolina (gluten) and requires extra oil on tawa",
            "Not suitable for Celiac / Gluten-intolerant individuals"
        ],
        "order_smart_tips": [
            "Choose Regular Plain Sada Dosa or Pesarattu (Green Moong Dosa) which is naturally gluten-free and fermented"
        ]
    },

    # =========================================================================
    # 3. INDIAN RESTAURANT MAIN COURSES & GRAVIES
    # =========================================================================
    "restaurant_butter_chicken": {
        "dish_id": "restaurant_butter_chicken",
        "restaurant": "Casual North Indian Restaurant",
        "dish_name": "Butter Chicken (Murgh Makhani - 1 Bowl)",
        "category": "Non-Veg Curry",
        "serving_size_g": 300.0,
        "calories": 580.0,
        "protein_g": 31.0,
        "carbs_g": 18.0,
        "fat_g": 42.0,
        "saturated_fat_g": 22.0,
        "sugar_g": 7.5,
        "fiber_g": 2.1,
        "sodium_mg": 960.0,
        "allergens": ["Milk (Butter & Heavy Cream)", "Cashew (Makhani paste)"],
        "health_score": 48,
        "traffic_light": "YELLOW",
        "risk_warnings": [
            "Contains heavy dairy cream, salted butter, and sugar-sweetened tomato puree",
            "22g saturated fat in a single serving bowl"
        ],
        "order_smart_tips": [
            "Order Tandoori Chicken Tikka (dry roasted) with mint chutney instead — saves 300 kcal and 32g fat with higher protein!",
            "Pair with 1-2 plain tandoori rotis rather than butter naan"
        ]
    },
    "restaurant_paneer_tikka_dry": {
        "dish_id": "restaurant_paneer_tikka_dry",
        "restaurant": "Casual North Indian Restaurant",
        "dish_name": "Tandoori Paneer Tikka Starter (6 Pieces with Bell Peppers)",
        "category": "Veg Starter",
        "serving_size_g": 220.0,
        "calories": 340.0,
        "protein_g": 19.5,
        "carbs_g": 11.0,
        "fat_g": 24.0,
        "saturated_fat_g": 13.5,
        "sugar_g": 3.0,
        "fiber_g": 2.8,
        "sodium_mg": 620.0,
        "allergens": ["Milk (Paneer & Curd marinade)", "Mustard oil"],
        "health_score": 76,
        "traffic_light": "GREEN",
        "risk_warnings": [
            "Moderate saturated fat from paneer; watch out for excess chaat masala sodium"
        ],
        "order_smart_tips": [
            "One of the smartest restaurant vegetarian orders: rich in protein, low carb, and tandoor-grilled instead of deep-fried",
            "Request no extra melted butter brushing on top"
        ]
    },
    "restaurant_hyderabadi_veg_biryani": {
        "dish_id": "restaurant_hyderabadi_veg_biryani",
        "restaurant": "Biryani Specialty Chain",
        "dish_name": "Hyderabadi Dum Veg Biryani (1 Full Portion with Mirchi Ka Salan)",
        "category": "Rice & Biryani",
        "serving_size_g": 450.0,
        "calories": 720.0,
        "protein_g": 14.5,
        "carbs_g": 96.0,
        "fat_g": 30.0,
        "saturated_fat_g": 11.2,
        "sugar_g": 4.0,
        "fiber_g": 5.6,
        "sodium_mg": 1150.0,
        "allergens": ["Milk (Ghee/Curd)", "Cashew & Almond (Garnish)", "Peanut & Sesame (Mirchi Ka Salan)"],
        "health_score": 50,
        "traffic_light": "YELLOW",
        "risk_warnings": [
            "Mirchi Ka Salan gravy is traditionally thickened with peanuts and sesame seeds (critical hidden allergen!)",
            "Very large refined basmati rice portion (96g carbs)"
        ],
        "order_smart_tips": [
            "Eat only half the rice portion and fill up on vegetable raita and salad",
            "Avoid Mirchi Ka Salan if you have Peanut/Sesame allergies or are watching oil calories"
        ]
    }
}


def lookup_restaurant_dish(dish_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves detailed nutritional and allergen profile for a restaurant dish."""
    return INDIAN_RESTAURANT_MENU_DB.get(dish_id.lower().strip())


def search_restaurant_menu(query: str) -> List[Dict[str, Any]]:
    """Searches restaurant dishes by dish name, restaurant brand, or category."""
    q = query.lower().strip()
    return [
        dish for dish in INDIAN_RESTAURANT_MENU_DB.values()
        if (q in dish["dish_name"].lower() or
            q in dish["restaurant"].lower() or
            q in dish["category"].lower())
    ]


def filter_allergen_free_restaurant_dishes(excluded_allergen: str) -> List[Dict[str, Any]]:
    """Finds dishes that do not list the specified allergen."""
    ex = excluded_allergen.lower().strip()
    safe_list = []
    for dish in INDIAN_RESTAURANT_MENU_DB.values():
        allergens_str = " ".join(dish.get("allergens", [])).lower()
        if ex not in allergens_str:
            safe_list.append(dish)
    return safe_list
