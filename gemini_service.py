import os
import json
import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from PIL import Image
import io

logger = logging.getLogger("safebite.gemini")

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize Google GenAI Client: {e}")
        return None

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from groq import Groq
        return Groq(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize Groq Client: {e}")
        return None

def is_groq_configured() -> bool:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    return bool(api_key and len(api_key) > 5)

def is_gemini_configured() -> bool:
    api_key = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
    return bool(api_key and len(api_key) > 5)

def set_gemini_api_key(api_key: str) -> bool:
    """Updates the Gemini API key in memory and persists to .env file."""
    clean_key = api_key.strip()
    if not clean_key:
        return False
    os.environ["GEMINI_API_KEY"] = clean_key
    try:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        
        key_found = False
        new_lines = []
        for line in lines:
            if line.startswith("GEMINI_API_KEY="):
                new_lines.append(f"GEMINI_API_KEY={clean_key}\n")
                key_found = True
            else:
                new_lines.append(line)
        if not key_found:
            new_lines.append(f"GEMINI_API_KEY={clean_key}\n")
            
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        logger.info("Successfully persisted GEMINI_API_KEY to .env")
        return True
    except Exception as e:
        logger.error(f"Could not persist .env file: {e}")
        return True # in-memory still set

STANDARD_FOOD_OBJECTS = [
    {
        "id": "apple",
        "name": "Fresh Whole Apple",
        "category": "Whole Fresh Fruit",
        "keywords": ["apple", "seb", "red apple", "green apple", "fuji", "gala"],
        "serving_size": "1 medium (~150g)",
        "serving_weight_grams": 150.0,
        "calories": 78.0,
        "protein": 0.45,
        "carbs": 20.7,
        "fat": 0.3,
        "fiber": 3.6,
        "sugar": 15.6,
        "sodium": 1.5,
        "serving_options": ["1 piece (150g)", "100g standard", "1 cup chopped (125g)", "1 large (200g)"],
        "alternative_candidates": ["Fresh Pear", "Peach", "Plum"],
        "ingredients": ["100% Fresh Raw Apple"],
        "warnings": ["Values are visual estimates for a standard medium apple. Natural sugar content can vary by ripeness."]
    },
    {
        "id": "banana",
        "name": "Fresh Banana",
        "category": "Whole Fresh Fruit",
        "keywords": ["banana", "kela", "cavendish", "robusta"],
        "serving_size": "1 medium (~120g)",
        "serving_weight_grams": 120.0,
        "calories": 105.0,
        "protein": 1.3,
        "carbs": 27.0,
        "fat": 0.4,
        "fiber": 3.1,
        "sugar": 14.4,
        "sodium": 1.2,
        "serving_options": ["1 piece (120g)", "100g standard", "1 small (80g)", "1 large (150g)"],
        "alternative_candidates": ["Raw Plantain", "Sweet Potato", "Corn on Cob"],
        "ingredients": ["100% Fresh Raw Banana"],
        "warnings": ["Values are visual estimates. Riper bananas contain slightly higher free sugars."]
    },
    {
        "id": "orange",
        "name": "Fresh Orange / Citrus",
        "category": "Whole Fresh Fruit",
        "keywords": ["orange", "santra", "mosambi", "citrus", "tangerine"],
        "serving_size": "1 medium (~130g)",
        "serving_weight_grams": 130.0,
        "calories": 62.0,
        "protein": 1.2,
        "carbs": 15.4,
        "fat": 0.2,
        "fiber": 3.1,
        "sugar": 12.2,
        "sodium": 0.0,
        "serving_options": ["1 piece (130g)", "100g standard", "1 cup segments (180g)"],
        "alternative_candidates": ["Sweet Lime (Mosambi)", "Tangerine", "Grapefruit"],
        "ingredients": ["100% Fresh Raw Orange"],
        "warnings": ["Visual estimate. Fiber is preserved in whole fruit unlike strained juice."]
    },
    {
        "id": "boiled_egg",
        "name": "Whole Boiled Egg",
        "category": "High Protein Food",
        "keywords": ["boiled egg", "egg", "anda", "boiled", "hard boiled"],
        "serving_size": "1 large egg (~50g)",
        "serving_weight_grams": 50.0,
        "calories": 78.0,
        "protein": 6.3,
        "carbs": 0.6,
        "fat": 5.3,
        "fiber": 0.0,
        "sugar": 0.6,
        "sodium": 62.0,
        "serving_options": ["1 egg (50g)", "2 eggs (100g)", "100g standard"],
        "alternative_candidates": ["Poached Egg", "Tofu Cube", "Paneer Cube"],
        "ingredients": ["100% Whole Hen Egg"],
        "warnings": ["Visual estimate for 1 large boiled egg."]
    },
    {
        "id": "steamed_rice",
        "name": "Steamed White Rice",
        "category": "Grains & Cereals",
        "keywords": ["rice", "chawal", "white rice", "steamed rice", "boiled rice"],
        "serving_size": "1 katori / bowl (~150g cooked)",
        "serving_weight_grams": 150.0,
        "calories": 195.0,
        "protein": 4.1,
        "carbs": 42.0,
        "fat": 0.4,
        "fiber": 0.6,
        "sugar": 0.1,
        "sodium": 2.0,
        "serving_options": ["1 katori / bowl (150g)", "100g standard", "1 cup cooked (180g)", "1 large bowl (250g)"],
        "alternative_candidates": ["Jeera Rice", "Poha", "Brown Rice"],
        "ingredients": ["White Rice, Water"],
        "warnings": ["Visual estimate for cooked plain rice. Does not account for added ghee or oil if cooked as pilaf."]
    },
    {
        "id": "roti",
        "name": "Whole Wheat Roti / Chapati",
        "category": "Breads & Grains",
        "keywords": ["roti", "chapati", "fulka", "phulka", "whole wheat flatbread"],
        "serving_size": "1 piece (~40g)",
        "serving_weight_grams": 40.0,
        "calories": 104.0,
        "protein": 3.1,
        "carbs": 20.0,
        "fat": 1.5,
        "fiber": 3.2,
        "sugar": 0.4,
        "sodium": 40.0,
        "serving_options": ["1 piece (40g)", "2 pieces (80g)", "100g standard"],
        "alternative_candidates": ["Whole Wheat Paratha", "Tandoori Naan", "Puri", "Bhakri"],
        "ingredients": ["Whole Wheat Flour (Atta), Water, Salt"],
        "warnings": ["Visual estimate for 1 plain chapati without excess ghee."]
    },
    {
        "id": "dal",
        "name": "Cooked Yellow Dal (Tadka)",
        "category": "Cooked Meal",
        "keywords": ["dal", "daal", "lentil", "tadka dal", "yellow dal", "moong dal"],
        "serving_size": "1 katori / bowl (~150g)",
        "serving_weight_grams": 150.0,
        "calories": 160.0,
        "protein": 8.5,
        "carbs": 24.0,
        "fat": 4.0,
        "fiber": 6.0,
        "sugar": 1.5,
        "sodium": 320.0,
        "serving_options": ["1 katori / bowl (150g)", "100g standard", "1 small cup (100g)", "1 large bowl (250g)"],
        "alternative_candidates": ["Sambar", "Kadhi", "Khichdi"],
        "ingredients": ["Yellow lentils, water, cumin, turmeric, spices, salt"],
        "warnings": ["Visual estimate. Tadka ghee or oil quantity cannot be verified visually."]
    },
    {
        "id": "pizza",
        "name": "Margherita Pizza Slice",
        "category": "Fast Food",
        "keywords": ["pizza", "pizza slice", "margherita", "cheese pizza"],
        "serving_size": "1 slice (~100g)",
        "serving_weight_grams": 100.0,
        "calories": 266.0,
        "protein": 11.0,
        "carbs": 33.0,
        "fat": 10.0,
        "fiber": 2.3,
        "sugar": 3.6,
        "sodium": 598.0,
        "serving_options": ["1 slice (100g)", "100g standard", "2 slices (200g)", "1 personal pizza (300g)"],
        "alternative_candidates": ["Cheese Flatbread", "Bruschetta", "Open Cheese Sandwich"],
        "ingredients": ["Refined flour crust, mozzarella cheese, tomato sauce, oil, salt"],
        "warnings": ["Visual estimate. Saturated fat and sodium vary significantly by pizzeria and cheese thickness."]
    },
    {
        "id": "salad",
        "name": "Fresh Mixed Green Salad",
        "category": "Vegetables & Salads",
        "keywords": ["salad", "green salad", "cucumber", "tomato salad", "lettuce", "mixed salad"],
        "serving_size": "1 bowl (~150g)",
        "serving_weight_grams": 150.0,
        "calories": 35.0,
        "protein": 1.8,
        "carbs": 6.5,
        "fat": 0.4,
        "fiber": 2.8,
        "sugar": 3.2,
        "sodium": 45.0,
        "serving_options": ["1 cup / katori (100g)", "100g standard", "1 medium bowl (150g)", "1 large bowl (250g)"],
        "alternative_candidates": ["Sprouts Salad", "Fruit Chaat", "Cucumber Tomato Salad"],
        "ingredients": ["Cucumber, Tomato, Greens, Lemon"],
        "warnings": ["Visual estimate for raw salad without creamy dressings or oil."]
    },
    {
        "id": "samosa",
        "name": "Fried Aloo Samosa",
        "category": "Snacks & Savories",
        "keywords": ["samosa", "samose", "aloo samosa"],
        "serving_size": "1 piece (~100g)",
        "serving_weight_grams": 100.0,
        "calories": 262.0,
        "protein": 4.0,
        "carbs": 24.0,
        "fat": 17.0,
        "fiber": 2.0,
        "sugar": 2.0,
        "sodium": 420.0,
        "serving_options": ["1 piece (100g)", "100g standard", "1 small piece (70g)", "2 pieces (200g)"],
        "alternative_candidates": ["Aloo Kachori", "Spring Roll", "Bread Pakora"],
        "ingredients": ["Refined flour, potatoes, vegetable oil, spices, salt"],
        "warnings": ["Visual estimate. Commercial deep-frying oil uptake and sodium vary widely."]
    },
    {
        "id": "gajak",
        "name": "Traditional Til-Gud Gajak",
        "category": "Traditional Indian Sweet",
        "keywords": ["gajak", "til gajak", "gud gajak", "khasta gajak", "tilpatti", "til patti", "sesame brittle", "tilkut", "til"],
        "serving_size": "1 piece (~25g)",
        "serving_weight_grams": 25.0,
        "calories": 125.0,
        "protein": 3.2,
        "carbs": 14.5,
        "fat": 6.5,
        "fiber": 1.6,
        "sugar": 11.2,
        "sodium": 8.0,
        "serving_options": ["1 piece (25g)", "2 pieces (50g)", "100g standard"],
        "alternative_candidates": ["Peanut Chikki", "Til Ladoo", "Khasta Revdi", "Sesame Brittle"],
        "ingredients": ["Roasted Sesame Seeds (Til)", "Jaggery (Gud)", "Cardamom", "Clarified Butter (Ghee)"],
        "warnings": [
            "Visual estimate for traditional Til-Gud Gajak. Exact recipe varies: peanut-blended, khasta, and sugar-syrup variants have different fat/sugar ratios.",
            "High in concentrated jaggery sugar. Sesame seeds provide natural calcium, iron, and healthy unsaturated fats."
        ]
    },
    {
        "id": "chikki",
        "name": "Peanut Chikki (Groundnut Brittle)",
        "category": "Traditional Indian Sweet",
        "keywords": ["chikki", "peanut chikki", "moongfali chikki", "groundnut brittle", "sing chikki", "patti"],
        "serving_size": "1 bar / piece (~30g)",
        "serving_weight_grams": 30.0,
        "calories": 153.0,
        "protein": 4.5,
        "carbs": 16.2,
        "fat": 8.1,
        "fiber": 1.5,
        "sugar": 12.0,
        "sodium": 15.0,
        "serving_options": ["1 bar (30g)", "2 bars (60g)", "100g standard"],
        "alternative_candidates": ["Til-Gud Gajak", "Roasted Peanuts with Jaggery", "Nut Brittle"],
        "ingredients": ["Roasted Peanuts, Jaggery (Gud)"],
        "warnings": ["Visual estimate. Recipe varies between pure jaggery and commercial glucose syrup formulations."]
    },
    {
        "id": "kachori",
        "name": "Khasta Dal Kachori",
        "category": "Fried Savories & Namkeen",
        "keywords": ["kachori", "dal kachori", "khasta kachori", "pyaaz kachori", "kachodi"],
        "serving_size": "1 piece (~75g)",
        "serving_weight_grams": 75.0,
        "calories": 285.0,
        "protein": 5.2,
        "carbs": 31.0,
        "fat": 16.0,
        "fiber": 2.4,
        "sugar": 1.5,
        "sodium": 380.0,
        "serving_options": ["1 piece (75g)", "2 pieces (150g)", "100g standard"],
        "alternative_candidates": ["Fried Samosa", "Aloo Bonda", "Mathri"],
        "ingredients": ["Refined wheat flour, spiced moong/urad dal, vegetable oil, spices, salt"],
        "warnings": ["Visual estimate. Deep-frying oil uptake and sodium vary by confectioner."]
    },
    {
        "id": "pakora",
        "name": "Mixed Vegetable Pakora / Bhajia",
        "category": "Fried Savories & Namkeen",
        "keywords": ["pakora", "pakoda", "bhajiya", "bhajia", "onion pakoda", "paneer pakora"],
        "serving_size": "4 pieces (~100g)",
        "serving_weight_grams": 100.0,
        "calories": 275.0,
        "protein": 6.0,
        "carbs": 26.0,
        "fat": 16.5,
        "fiber": 3.5,
        "sugar": 2.0,
        "sodium": 410.0,
        "serving_options": ["1 small plate (100g)", "2 pieces (50g)", "1 large plate (200g)"],
        "alternative_candidates": ["Onion Bhaji", "Bread Pakora", "Aloo Vada"],
        "ingredients": ["Gram flour (Besan), mixed vegetables (onion, potato, spinach), oil, spices, salt"],
        "warnings": ["Visual estimate. Batter thickness and oil absorption vary widely."]
    },
    {
        "id": "jalebi",
        "name": "Crispy Sugar Jalebi",
        "category": "Traditional Indian Sweet",
        "keywords": ["jalebi", "jilapi", "crispy jalebi", "kesar jalebi"],
        "serving_size": "2 pieces (~50g)",
        "serving_weight_grams": 50.0,
        "calories": 225.0,
        "protein": 1.5,
        "carbs": 38.0,
        "fat": 7.5,
        "fiber": 0.4,
        "sugar": 32.0,
        "sodium": 25.0,
        "serving_options": ["2 pieces (50g)", "4 pieces (100g)", "100g standard"],
        "alternative_candidates": ["Imarti", "Gulab Jamun", "Jaleba"],
        "ingredients": ["Fermented refined flour batter, deep-fried in ghee/oil, soaked in sugar syrup"],
        "warnings": ["Visual estimate. Sugar syrup absorption varies between 55% to 70% of total product weight. High glycemic impact."]
    },
    {
        "id": "gulab_jamun",
        "name": "Gulab Jamun in Sugar Syrup",
        "category": "Traditional Indian Sweet",
        "keywords": ["gulab jamun", "jamun", "kala jamun"],
        "serving_size": "2 pieces (~80g)",
        "serving_weight_grams": 80.0,
        "calories": 290.0,
        "protein": 4.0,
        "carbs": 44.0,
        "fat": 11.0,
        "fiber": 0.8,
        "sugar": 36.0,
        "sodium": 60.0,
        "serving_options": ["1 piece (40g)", "2 pieces (80g)", "100g standard"],
        "alternative_candidates": ["Rasgulla", "Kala Jamun", "Pantua"],
        "ingredients": ["Khoya (milk solids), chenna, flour, ghee/oil, sugar syrup, rose water"],
        "warnings": ["Visual estimate. Drained vs syrup-soaked serving weights differ significantly."]
    },
    {
        "id": "laddu",
        "name": "Besan / Motichoor Laddu",
        "category": "Traditional Indian Sweet",
        "keywords": ["laddu", "ladoo", "besan laddu", "motichoor laddu", "boondi laddu"],
        "serving_size": "1 piece (~45g)",
        "serving_weight_grams": 45.0,
        "calories": 210.0,
        "protein": 3.5,
        "carbs": 28.0,
        "fat": 9.5,
        "fiber": 1.2,
        "sugar": 22.0,
        "sodium": 15.0,
        "serving_options": ["1 piece (45g)", "2 pieces (90g)", "100g standard"],
        "alternative_candidates": ["Atta Ladoo", "Pinni", "Mysore Pak"],
        "ingredients": ["Gram flour (Besan), sugar, clarified butter (desi ghee), cardamom, nuts"],
        "warnings": ["Visual estimate. Desi ghee and sugar ratios vary by confectioner."]
    },
    {
        "id": "barfi",
        "name": "Kaju Katli / Milk Barfi",
        "category": "Traditional Indian Sweet",
        "keywords": ["barfi", "burfi", "kaju katli", "kaju barfi", "besan barfi", "milk barfi"],
        "serving_size": "2 pieces (~40g)",
        "serving_weight_grams": 40.0,
        "calories": 185.0,
        "protein": 4.0,
        "carbs": 22.0,
        "fat": 9.0,
        "fiber": 0.8,
        "sugar": 18.0,
        "sodium": 12.0,
        "serving_options": ["1 piece (20g)", "2 pieces (40g)", "100g standard"],
        "alternative_candidates": ["Kaju Peda", "Kalakand", "Milk Cake"],
        "ingredients": ["Cashew nuts / milk solids, sugar, ghee, silver foil (vark)"],
        "warnings": ["Visual estimate. Kaju katli has more unsaturated fats from cashews; milk barfi has more saturated dairy fat."]
    },
    {
        "id": "mango",
        "name": "Fresh Ripe Mango",
        "category": "Whole Fresh Fruit",
        "keywords": ["mango", "aam", "alphonso", "kesar", "dasheri", "langra"],
        "serving_size": "1 medium (~140g edible)",
        "serving_weight_grams": 140.0,
        "calories": 84.0,
        "protein": 1.1,
        "carbs": 21.0,
        "fat": 0.5,
        "fiber": 2.2,
        "sugar": 18.0,
        "sodium": 1.5,
        "serving_options": ["1 cup diced (165g)", "1 whole mango (140g edible)", "100g standard"],
        "alternative_candidates": ["Papaya", "Peach", "Melon"],
        "ingredients": ["100% Fresh Raw Mango"],
        "warnings": ["Visual estimate for ripe mango. Natural sweetness varies by ripeness."]
    },
    {
        "id": "grapes",
        "name": "Fresh Grapes (Green / Black)",
        "category": "Whole Fresh Fruit",
        "keywords": ["grapes", "angoor", "green grapes", "black grapes"],
        "serving_size": "1 cup (~150g)",
        "serving_weight_grams": 150.0,
        "calories": 104.0,
        "protein": 1.1,
        "carbs": 27.0,
        "fat": 0.2,
        "fiber": 1.4,
        "sugar": 23.0,
        "sodium": 3.0,
        "serving_options": ["1 cup (150g)", "1 small bowl (100g)", "100g standard"],
        "alternative_candidates": ["Berries", "Cherries", "Plums"],
        "ingredients": ["100% Fresh Raw Grapes"],
        "warnings": ["Visual estimate for fresh whole grapes. High in natural fruit sugars."]
    },
    {
        "id": "guava",
        "name": "Fresh Guava (Amrood)",
        "category": "Whole Fresh Fruit",
        "keywords": ["guava", "amrood", "peru", "safeda"],
        "serving_size": "1 medium (~100g)",
        "serving_weight_grams": 100.0,
        "calories": 68.0,
        "protein": 2.6,
        "carbs": 14.3,
        "fat": 1.0,
        "fiber": 5.4,
        "sugar": 8.9,
        "sodium": 2.0,
        "serving_options": ["1 medium (100g)", "1 cup slices (165g)", "100g standard"],
        "alternative_candidates": ["Fresh Apple", "Pear"],
        "ingredients": ["100% Fresh Raw Guava"],
        "warnings": ["Visual estimate. Outstanding natural dietary fiber and Vitamin C content."]
    },
    {
        "id": "papaya",
        "name": "Fresh Ripe Papaya",
        "category": "Whole Fresh Fruit",
        "keywords": ["papaya", "papita", "pawpaw"],
        "serving_size": "1 cup cubes (~140g)",
        "serving_weight_grams": 140.0,
        "calories": 60.0,
        "protein": 0.7,
        "carbs": 15.0,
        "fat": 0.4,
        "fiber": 2.5,
        "sugar": 11.0,
        "sodium": 4.0,
        "serving_options": ["1 cup cubes (140g)", "1 medium wedge (100g)", "100g standard"],
        "alternative_candidates": ["Cantaloupe", "Watermelon", "Mango"],
        "ingredients": ["100% Fresh Raw Papaya"],
        "warnings": ["Visual estimate. Rich in digestive papain enzymes and Vitamin A."]
    },
    {
        "id": "idli",
        "name": "Steamed Rice & Dal Idli",
        "category": "Cooked Meal",
        "keywords": ["idli", "idly", "steamed idli"],
        "serving_size": "2 pieces (~100g)",
        "serving_weight_grams": 100.0,
        "calories": 130.0,
        "protein": 4.5,
        "carbs": 26.0,
        "fat": 0.6,
        "fiber": 2.2,
        "sugar": 0.3,
        "sodium": 180.0,
        "serving_options": ["2 pieces (100g)", "4 pieces (200g)", "100g standard"],
        "alternative_candidates": ["Rava Idli", "Plain Dosa", "Appam"],
        "ingredients": ["Fermented rice and urad dal batter, salt, steamed"],
        "warnings": ["Visual estimate for plain steamed idli without coconut chutney or ghee."]
    },
    {
        "id": "dosa",
        "name": "Plain / Masala Dosa",
        "category": "Cooked Meal",
        "keywords": ["dosa", "dhosa", "masala dosa", "plain dosa", "crispy dosa"],
        "serving_size": "1 medium dosa (~150g)",
        "serving_weight_grams": 150.0,
        "calories": 240.0,
        "protein": 5.5,
        "carbs": 38.0,
        "fat": 7.5,
        "fiber": 2.8,
        "sugar": 0.8,
        "sodium": 320.0,
        "serving_options": ["1 medium dosa (150g)", "1 large paper dosa (220g)", "100g standard"],
        "alternative_candidates": ["Rava Dosa", "Uttapam", "Set Dosa"],
        "ingredients": ["Fermented rice and lentils batter, spiced potato filling, oil/ghee, salt"],
        "warnings": ["Visual estimate. Oil/ghee used for crisping and potato filling volume vary."]
    },
    {
        "id": "poha",
        "name": "Kanda Batata Poha",
        "category": "Cooked Meal",
        "keywords": ["poha", "pohe", "kanda poha", "flattened rice"],
        "serving_size": "1 medium plate (~150g)",
        "serving_weight_grams": 150.0,
        "calories": 220.0,
        "protein": 4.5,
        "carbs": 36.0,
        "fat": 6.5,
        "fiber": 2.6,
        "sugar": 2.0,
        "sodium": 280.0,
        "serving_options": ["1 medium plate (150g)", "1 small bowl (100g)", "100g standard"],
        "alternative_candidates": ["Upma", "Sabudana Khichdi", "Dalia"],
        "ingredients": ["Flattened rice (poha), onions, peanuts, mustard seeds, turmeric, green chillies, oil, salt"],
        "warnings": ["Visual estimate. Peanuts and oil quantity vary by household."]
    },
    {
        "id": "chole",
        "name": "Punjabi Chole (Spiced Chickpea Curry)",
        "category": "Cooked Meal",
        "keywords": ["chole", "chana masala", "kabuli chana", "amritsari chole"],
        "serving_size": "1 katori / bowl (~150g)",
        "serving_weight_grams": 150.0,
        "calories": 210.0,
        "protein": 9.0,
        "carbs": 32.0,
        "fat": 5.5,
        "fiber": 7.5,
        "sugar": 3.0,
        "sodium": 440.0,
        "serving_options": ["1 katori (150g)", "1 cup (200g)", "100g standard"],
        "alternative_candidates": ["Rajma Curry", "Dal Makhani", "Black Chana"],
        "ingredients": ["White chickpeas, onion-tomato gravy, ginger, garlic, spices, oil, salt"],
        "warnings": ["Visual estimate. High in soluble dietary fiber and plant protein."]
    },
    {
        "id": "rajma",
        "name": "Rajma Masala (Red Kidney Bean Curry)",
        "category": "Cooked Meal",
        "keywords": ["rajma", "rajma chawal", "kidney bean curry"],
        "serving_size": "1 katori / bowl (~150g)",
        "serving_weight_grams": 150.0,
        "calories": 195.0,
        "protein": 8.5,
        "carbs": 29.0,
        "fat": 4.8,
        "fiber": 6.8,
        "sugar": 2.5,
        "sodium": 410.0,
        "serving_options": ["1 katori (150g)", "1 cup (200g)", "100g standard"],
        "alternative_candidates": ["Chole Curry", "Dal Tadka", "Lobia"],
        "ingredients": ["Red kidney beans, onion, tomato, spices, oil, salt"],
        "warnings": ["Visual estimate. High in iron, potassium, and slow-digesting resistant starch."]
    }
]

def smart_local_image_analyzer(image_bytes: bytes) -> Optional[Dict[str, Any]]:
    """
    Local optical nutrition extraction fallback when Gemini API is unconfigured or unavailable.
    Delegates to local OCR parser to extract actual visible nutrition facts.
    Returns None if no nutrition facts can be verified, never fabricating values.
    """
    try:
        from ocr_fallback import run_ocr_fallback
        ocr_result = run_ocr_fallback(image_bytes)
        if ocr_result and (
            ocr_result.get("calories")
            or ocr_result.get("protein")
            or ocr_result.get("carbohydrates")
            or ocr_result.get("total_fat")
        ):
            ocr_result["analysis_mode"] = "packaged"
            return ocr_result
    except Exception as e:
        logger.debug(f"Local OCR parser skipped or failed: {e}")

    return None

def lookup_standard_food(food_name: str) -> Optional[Dict[str, Any]]:
    """
    Looks up reference nutritional profile for a given food name in local composition datasets.
    Supports English & Hindi terms, traditional sweets (Gajak, Chikki, Jalebi, Laddu), fruits, and meals.
    """
    clean = (food_name or "").lower().strip()
    if not clean:
        return None

    # 1. Match against curated STANDARD_FOOD_OBJECTS
    for food in STANDARD_FOOD_OBJECTS:
        if clean == food["id"] or clean in food["name"].lower() or any(kw in clean or clean in kw for kw in food["keywords"]):
            return {
                "is_food": True,
                "product_name": food["name"],
                "food_category": food["category"],
                "confidence": 0.90,
                "likely_ingredients": food["ingredients"],
                "serving_size": food["serving_size"],
                "serving_weight_grams": food["serving_weight_grams"],
                "portion_estimated_with_visual_cues": False,
                "serving_options": food["serving_options"],
                "alternative_candidates": food.get("alternative_candidates", []),
                "calories": food["calories"],
                "protein": food["protein"],
                "carbohydrates": food["carbs"],
                "total_fat": food["fat"],
                "fiber": food["fiber"],
                "sugar": food["sugar"],
                "sodium": food["sodium"],
                "allergens": [],
                "analysis_mode": "food_object",
                "warnings": food["warnings"]
            }

    # 2. Match against comprehensive INDIAN_FOOD_DATASET
    try:
        from indian_foods_data import search_indian_food
        indian_matches = search_indian_food(clean)
        if indian_matches:
            top = indian_matches[0]
            cals = float(top.get("calories", 0.0))
            prot = float(top.get("protein", 0.0))
            carbs = float(top.get("carbs", 0.0))
            fat = float(top.get("fat", 0.0))
            sugar = float(top.get("sugar", 0.0))
            fiber = float(top.get("fiber", 0.0))
            sodium = float(top.get("sodium", 0.0))
            serving = top.get("serving_size", "1 serving (~100g)")
            serving_g = float(top.get("serving_weight_grams", 100.0))
            return {
                "is_food": True,
                "product_name": top["name"],
                "food_category": top.get("category", "Traditional Indian Food"),
                "confidence": 0.85,
                "likely_ingredients": [top["name"]],
                "serving_size": serving,
                "serving_weight_grams": serving_g,
                "portion_estimated_with_visual_cues": False,
                "serving_options": [serving, "100g standard", "1 large serving (~200g)"],
                "alternative_candidates": [m["name"] for m in indian_matches[1:4]],
                "calories": cals,
                "protein": prot,
                "carbohydrates": carbs,
                "total_fat": fat,
                "fiber": fiber,
                "sugar": sugar,
                "sodium": sodium,
                "allergens": [],
                "analysis_mode": "food_object",
                "warnings": [f"Values are reference estimates for traditional {top['name']}. Home recipes and restaurant preparations may vary."]
            }
    except Exception as e:
        logger.debug(f"Error querying indian_foods_data: {e}")

    return None

def smart_local_food_object_analyzer(
    image_bytes: bytes,
    query_hint: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Local fallback for food object analysis when Gemini API is unconfigured or offline.
    Uses OCR hints, query hints, and reference catalog of validated whole/cooked foods.
    Returns None if the image does not match any recognizable food item.
    """
    if query_hint:
        matched = lookup_standard_food(query_hint)
        if matched:
            return matched

    try:
        from ocr_fallback import run_ocr_fallback
        ocr_res = run_ocr_fallback(image_bytes)
        raw_text = (ocr_res.get("product_name", "") + " " + " ".join(ocr_res.get("ingredients", []))).lower() if ocr_res else ""
    except Exception:
        raw_text = ""

    if raw_text:
        matched = lookup_standard_food(raw_text)
        if matched:
            return matched

    # Match against reference catalog
    for food in STANDARD_FOOD_OBJECTS:
        for kw in food["keywords"]:
            if kw in raw_text:
                return {
                    "is_food": True,
                    "product_name": food["name"],
                    "food_category": food["category"],
                    "confidence": 0.85,
                    "likely_ingredients": food["ingredients"],
                    "serving_size": food["serving_size"],
                    "serving_weight_grams": food["serving_weight_grams"],
                    "portion_estimated_with_visual_cues": False,
                    "serving_options": food["serving_options"],
                    "alternative_candidates": food.get("alternative_candidates", []),
                    "calories": food["calories"],
                    "protein": food["protein"],
                    "carbohydrates": food["carbs"],
                    "total_fat": food["fat"],
                    "fiber": food["fiber"],
                    "sugar": food["sugar"],
                    "sodium": food["sodium"],
                    "allergens": [],
                    "analysis_mode": "food_object",
                    "warnings": food["warnings"]
                }

    return None

def analyze_packaged_food_image_with_gemini(image_bytes: bytes) -> Optional[Dict[str, Any]]:
    """
    Uses Google Gemini Vision to extract structured nutrition facts from packaged food labels.
    """
    client = get_gemini_client()
    if not client:
        logger.info("Gemini API key not configured. Using Smart Nutrition Vision Fallback.")
        return smart_local_image_analyzer(image_bytes)

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

    prompt = """
You are an expert food nutrition label computer vision analyzer.
Analyze the provided image of a packaged food product or nutrition label.

CRITICAL INSTRUCTIONS:
- First, check if this is an image of a packaged food label or nutrition facts panel.
  If this is an ordinary unpackaged food item (like an apple, a cooked meal, or bread) or NOT food, note that.
- Food packages frequently show two side-by-side columns (e.g. per serving vs per 100g).
  Carefully identify the primary product nutrition panel. Do NOT combine or average numbers from two separate columns.
- If information is not visible or obscured, return null for that field. NEVER invent or hallucinate values.

Extract the following information and output strictly valid JSON matching this schema:
{
  "is_food": true,
  "analysis_mode": "packaged",
  "product_name": "string (name of the food item or 'Unknown Product')",
  "serving_size": "string or null",
  "calories": number or null (kcal),
  "total_fat": number or null (grams),
  "saturated_fat": number or null (grams),
  "trans_fat": number or null (grams),
  "carbohydrates": number or null (grams),
  "sugar": number or null (grams),
  "added_sugar": number or null (grams),
  "fiber": number or null (grams),
  "protein": number or null (grams),
  "sodium": number or null (milligrams),
  "ingredients": ["list of strings"] or [],
  "allergens": ["list of strings"] or []
}
Output pure JSON only, without markdown fences or additional prose.
"""

    try:
        from google.genai import types
        pil_image = Image.open(io.BytesIO(image_bytes))

        response = client.models.generate_content(
            model=model_name,
            contents=[pil_image, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )

        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        parsed = json.loads(response_text.strip())
        parsed["analysis_mode"] = "packaged"
        logger.info(f"Gemini Vision successfully parsed packaged nutrition: {parsed.get('product_name')}")
        return parsed

    except Exception as e:
        logger.error(f"Gemini Vision analysis error: {e}. Falling back to Smart Nutrition analyzer.")
        return smart_local_image_analyzer(image_bytes)

def analyze_food_object_image_with_gemini(
    image_bytes: bytes,
    portion_hint: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Uses Google Gemini Vision to recognize unpackaged food objects, cooked meals, whole produce,
    estimate likely ingredients, portion size, serving options, and approximate reference nutrition.
    """
    client = get_gemini_client()
    if not client:
        logger.info("Gemini API key not configured. Using Smart Food Object Fallback.")
        return smart_local_food_object_analyzer(image_bytes)

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

    prompt = """
You are an expert food scientist, clinical nutritionist, and computer vision recognition engine.
Analyze the provided photograph of a food item or meal.

CRITICAL INSTRUCTIONS:
1. NON-FOOD / UNRECOGNIZABLE IMAGES:
   If the image does NOT contain recognizable food (e.g. household object, person, pet, blank surface, document, or completely blurry image), return strictly:
   {"is_food": false, "error": "No recognizable food items detected in the image."}

2. FOOD OBJECT RECOGNITION:
   If recognizable food is present (such as fruits, vegetables, cooked meals, curries, roti, rice, eggs, pizza, salad, snacks, bakery):
   - Identify the primary food or dish name accurately.
   - Estimate food category (e.g. "Whole Fresh Fruit", "Cooked Meal", "Breads & Grains", "Vegetables & Salads", "Fast Food", "Snacks & Savories", "High Protein Food").
   - Assess your identification confidence between 0.0 and 1.0. If food identity or ingredients are uncertain (e.g. a mixed curry where ingredients are not visible), set confidence < 0.6 and document uncertainties in "warnings".
   - Estimate portion size based on visual scale cues (plate, bowl, hand). If uncertain, use a standard serving and set "portion_estimated_with_visual_cues": false.
   - Provide realistic alternative food candidates in "alternative_candidates" (e.g. 2-3 other possible dishes if uncertain, such as ["Naan", "Paratha", "Chapati"]).
   - Provide realistic alternative serving options in "serving_options" (e.g. ["1 piece / unit", "100g standard", "1 cup / katori (~150g)", "1 serving (~200g)"]).
   - Calculate approximate nutritional values (calories, protein, carbohydrates, total_fat, saturated_fat, fiber, sugar, sodium) for the identified portion using validated reference data (USDA / Indian Food Composition Tables).
   - NEVER claim an image can reveal exact salt quantity, cooking oils, or hidden sugars. Explicitly include estimation caveats in "warnings".

Output strictly valid JSON matching this schema:
{
  "is_food": true,
  "analysis_mode": "food_object",
  "product_name": "string (clear name of food item or dish)",
  "food_category": "string",
  "confidence": number (0.0 to 1.0),
  "alternative_candidates": ["list of strings"],
  "likely_ingredients": ["list of strings"],
  "serving_size": "string (e.g. '1 medium (~150g)')",
  "serving_weight_grams": number,
  "portion_estimated_with_visual_cues": boolean,
  "serving_options": ["list of serving options"],
  "calories": number,
  "total_fat": number,
  "saturated_fat": number or null,
  "trans_fat": number or null,
  "carbohydrates": number,
  "fiber": number,
  "sugar": number,
  "protein": number,
  "sodium": number,
  "allergens": ["list of allergens if present"],
  "health_analysis": "string explaining nutritional balance",
  "practical_recommendations": ["list of practical dietary advice"],
  "warnings": ["list of visual estimation caveats"]
}
Output pure JSON only, without markdown fences or additional prose.
"""

    try:
        from google.genai import types
        pil_image = Image.open(io.BytesIO(image_bytes))

        response = client.models.generate_content(
            model=model_name,
            contents=[pil_image, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )

        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        parsed = json.loads(response_text.strip())
        parsed["analysis_mode"] = "food_object"
        logger.info(f"Gemini Vision successfully recognized food object: {parsed.get('product_name')}")
        return parsed

    except Exception as e:
        logger.error(f"Gemini Vision food object error: {e}. Falling back to Smart Food Object analyzer.")
        return smart_local_food_object_analyzer(image_bytes)

def analyze_food_image_with_gemini(
    image_bytes: bytes,
    mode: str = "auto"
) -> Optional[Dict[str, Any]]:
    """
    Unified Gemini Vision Image Analysis supporting both Packaged Food labels and Food Objects.
    Modes:
      - 'packaged': Analyzes Nutrition Facts table & ingredients on packaged goods.
      - 'food_object': Recognizes unpackaged food objects, cooked meals, produce.
      - 'auto': Automatically classifies whether the image is packaged label or whole food object.
    """
    clean_mode = (mode or "auto").lower().strip()
    if clean_mode in ["packaged", "label", "nutrition_table"]:
        return analyze_packaged_food_image_with_gemini(image_bytes)
    elif clean_mode in ["food_object", "food", "object", "dish"]:
        return analyze_food_object_image_with_gemini(image_bytes)

    # AUTO MODE: Use Gemini Vision to detect and classify
    client = get_gemini_client()
    if not client:
        # Fallback heuristic: check if OCR finds label text
        pkg = smart_local_image_analyzer(image_bytes)
        if pkg:
            return pkg
        return smart_local_food_object_analyzer(image_bytes)

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    prompt = """
You are an expert food nutritionist and computer vision system.
Analyze the provided image.
First determine whether the image is:
1. "packaged": A packaged food product or label showing a nutrition facts table or ingredient list.
2. "food_object": An ordinary unpackaged food item, cooked dish, fruit, vegetable, or meal.
3. "not_food": An image with NO recognizable food or a completely blurry unidentifiable photo.

If "not_food":
Return strictly: {"is_food": false, "error": "No recognizable food items detected in the image."}

If "packaged":
Extract nutrition table values (product_name, serving_size, calories, total_fat, saturated_fat, trans_fat, carbohydrates, sugar, added_sugar, fiber, protein, sodium, ingredients, allergens). Set "analysis_mode": "packaged".

If "food_object":
Identify food_name, food_category, confidence (0.0-1.0), likely_ingredients, serving_size, serving_weight_grams, portion_estimated_with_visual_cues, serving_options, approximate calories, total_fat, saturated_fat, carbohydrates, fiber, sugar, protein, sodium, allergens, health_analysis, practical_recommendations, warnings. Set "analysis_mode": "food_object".

Output pure JSON only matching these respective structures.
"""
    try:
        from google.genai import types
        pil_image = Image.open(io.BytesIO(image_bytes))

        response = client.models.generate_content(
            model=model_name,
            contents=[pil_image, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )

        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        parsed = json.loads(response_text.strip())
        logger.info(f"Gemini Vision auto-analysis result: {parsed.get('product_name')} ({parsed.get('analysis_mode')})")
        return parsed
    except Exception as e:
        logger.error(f"Gemini Vision auto-analysis failed: {e}. Falling back.")
        pkg = smart_local_image_analyzer(image_bytes)
        if pkg:
            return pkg
        return smart_local_food_object_analyzer(image_bytes)


def generate_follow_up_suggestions(user_msg: str, reply: str) -> List[str]:
    """Generates 2 to 3 contextual follow-up questions tailored to the user's intent."""
    m = user_msg.lower()
    if "gajak" in m or "chikki" in m:
        return [
            "How much gajak can I eat daily?",
            "Compare gajak with peanut chikki",
            "What are healthy low-sugar winter snacks?"
        ]
    if "samosa" in m or "kachori" in m:
        return [
            "How many calories are burned per samosa?",
            "Can I make healthy air-fried samosas?",
            "Compare samosa and kachori"
        ]
    if "breakfast" in m:
        return [
            "Quick high-protein breakfast under 10 minutes",
            "Is poha or idli better for weight loss?",
            "How to balance Indian vegetarian breakfast?"
        ]
    if "sugar" in m or "sweet" in m or "diabet" in m:
        return [
            "What are common hidden sugars in packaged food?",
            "Is jaggery or honey safer than white sugar?",
            "How to prevent post-meal sugar spikes?"
        ]
    if "protein" in m:
        return [
            "Top vegetarian protein sources in India",
            "How much daily protein do I need?",
            "Are soya chunks safe for daily consumption?"
        ]
    if "scan" in m or "score" in m or "food" in m or "healthy" in m:
        return [
            "Why did this food receive this health score?",
            "Suggest 3 healthier alternatives",
            "What portion size is recommended?"
        ]
    return [
        "Tell me more about this",
        "Suggest healthy Indian alternatives",
        "How does this impact my daily nutrition?"
    ]


def autonomous_nutrition_agent(
    user_message: str,
    recent_scan_context: Optional[Dict[str, Any]] = None,
    user_profile: Optional[Dict[str, Any]] = None
) -> Tuple[str, List[str]]:
    """
    Autonomous Nutritional Intelligence AI Agent (NutriCoach AI).
    Operates with deep dietary, macronutrient, metabolic, and Indian ingredient knowledge.
    Provides structured, accurate, evidence-backed nutritional advice.
    """
    msg = user_message.lower().strip()
    allergens = (user_profile.get("allergens") or "").lower() if user_profile else ""
    is_diabetic = bool(user_profile.get("is_diabetic")) if user_profile else False
    diet_pref = (user_profile.get("dietary_preference") or "None") if user_profile else "None"

    # Allergy warning helper
    allergy_warning = ""
    if allergens and recent_scan_context:
        scanned_ing = (recent_scan_context.get("ingredients") or "").lower()
        matched = [a.strip() for a in allergens.split(",") if a.strip() and a.strip() in scanned_ing]
        if matched:
            allergy_warning = f"\n\n🚨 **ALLERGY ALERT:** This product contains confirmed allergens from your profile: **{', '.join(matched).upper()}**! Please exercise extreme caution."

    # 1. Ask about recent scan or health score
    if any(k in msg for k in ["my scan", "latest scan", "scanned food", "this food", "my food", "why this score", "explain my score", "explain score"]):
        if not recent_scan_context:
            reply = (
                "### ℹ️ No Recent Food Scan Found\n\n"
                "I don't see any recent food scan associated with your account yet!\n\n"
                "**How to get started:**\n"
                "- Tap **Scan Food** at the bottom to photograph any packaged food label or home-cooked dish.\n"
                "- Or simply ask me about any food directly (e.g. *'Is gajak healthy?'*, *'Compare samosa and kachori'*, or *'Analyze Parle-G'*)."
            )
            return reply, [
                "Is gajak healthy?",
                "Suggest a healthy Indian breakfast",
                "Suggest high-protein vegetarian foods"
            ]

        p_name = recent_scan_context.get("product_name", "Scanned Food Item")
        score = recent_scan_context.get("health_score", 70)
        category = recent_scan_context.get("classification", "Moderate")
        cals = recent_scan_context.get("calories", 0)
        prot = recent_scan_context.get("protein", 0)
        fat = recent_scan_context.get("fat", 0)
        carbs = recent_scan_context.get("carbs", 0)
        sugar = recent_scan_context.get("sugar", 0)
        sodium = recent_scan_context.get("sodium", 0)
        ing = recent_scan_context.get("ingredients")

        health_verdict = (
            "✅ **Healthy choice**" if score >= 70
            else ("⚠️ **Moderate choice** (consume in moderation)" if score >= 45
            else "❌ **Unhealthy / High-risk food** (limit consumption)")
        )

        reply = (
            f"### 🥗 Nutritional Evaluation for **{p_name}**\n\n"
            f"**SafeBite Health Score:** `{score}/100` ({category})\n"
            f"**Status:** {health_verdict}{allergy_warning}\n\n"
            f"#### 📊 Nutritional Breakdown (per serving):\n"
            f"- **Calories:** {cals} kcal\n"
            f"- **Protein:** {prot}g {'(💪 Good protein source)' if prot >= 8 else '(Low protein)'}\n"
            f"- **Carbohydrates:** {carbs}g {'(⚠️ High sugar content: ' + str(sugar) + 'g)' if sugar and sugar > 10 else ''}\n"
            f"- **Total Fat:** {fat}g\n"
            f"- **Sodium:** {sodium}mg\n\n"
            f"#### 💡 Why did it receive this score?\n"
            f"{recent_scan_context.get('analysis') or 'The score evaluates nutrient density: positive points for protein and dietary fiber vs penalties for excess refined sugars, saturated/trans fats, and chemical additives.'}\n\n"
            f"#### 🌱 NutriCoach Guidance:\n"
            f"- **Portion control:** Check serving size before eating; packaged snacks often count 2–3 servings per pack.\n"
            f"- **Balance:** Pair with fresh salad or lean protein to minimize blood glucose spike.\n\n"
            f"*Note: SafeBite provides educational nutrition insights, not medical prescriptions.*"
        )
        return reply, generate_follow_up_suggestions(user_message, reply)

    # 2. Gajak inquiry
    if "gajak" in msg:
        reply = (
            "### 🥜 Is Gajak Healthy?\n\n"
            "**Quick Answer:** Gajak can be enjoyed as an occasional winter treat in controlled portions, but it is calorie-dense and high in sugar.\n\n"
            "#### 🌟 Potential Benefits:\n"
            "- **Sesame Seeds (Til):** Excellent source of plant protein, dietary fiber, calcium, iron, and heart-healthy unsaturated fats.\n"
            "- **Mineral Content:** Traditional jaggery retains trace minerals like magnesium and potassium.\n\n"
            "#### ⚠️ Things to Consider:\n"
            "- **High Sugar & Calories:** Gajak contains ~450–500 kcal per 100g, mostly from concentrated jaggery syrup.\n"
            "- **Glycemic Impact:** Jaggery has a high glycemic index (~84), causing rapid blood sugar spikes.\n\n"
            "#### 📏 Portion Guidance:\n"
            "- Limit intake to **1 small piece (20–25g)** rather than eating it in large amounts.\n"
            "- If diabetic, treat it as a high-sugar dessert and monitor your glucose.\n\n"
            f"*SafeBite Tip: Pair a small piece of gajak with raw almonds or walnuts to slow down sugar absorption!*"
        )
        return reply, [
            "Compare gajak with peanut chikki",
            "How can I reduce sugar intake?",
            "Suggest healthy winter snacks"
        ]

    # 3. Samosa vs Kachori Comparison
    if ("samosa" in msg and "kachori" in msg) or ("compare" in msg and ("samosa" in msg or "kachori" in msg)):
        reply = (
            "### 🥟 Food Comparison: Samosa vs. Kachori\n\n"
            "Here is the side-by-side nutritional breakdown based on typical standard Indian preparation (per 1 medium piece, ~100g):\n\n"
            "| Metric | Samosa (1 pc) | Khasta Kachori (1 pc) |\n"
            "| :--- | :--- | :--- |\n"
            "| **Calories** | ~260–300 kcal | ~320–380 kcal |\n"
            "| **Carbohydrates** | ~32g (Potato filling) | ~28g (Maida crust) |\n"
            "| **Protein** | ~4g | ~6g (Urad/Moong dal) |\n"
            "| **Total Fat** | ~17g | ~24g (Higher frying time) |\n"
            "| **SafeBite Score** | **35/100 (Unhealthy)** | **30/100 (Unhealthy)** |\n\n"
            "#### ⚖️ Key Nutritional Trade-Offs:\n"
            "1. **Kachori has higher fat:** The dough contains shortening (moyen) and is fried longer, absorbing more oil.\n"
            "2. **Samosa has higher carb load:** Spiced potato filling adds starchy rapid carbs inside refined maida.\n"
            "3. **Dal advantage in Kachori:** Kachori contains slightly more protein from lentils, but the saturated fat offsets this.\n\n"
            "#### 💡 Healthier Alternatives:\n"
            "- **Air-fried Samosa:** Baked or air-fried with wheat/patti sheet reduces fat by 70% (~120 kcal).\n"
            "- **Steamed Moong Dal Tikki:** Enjoy the kachori spice profile without the deep frying."
        )
        return reply, [
            "Suggest a healthy Indian breakfast",
            "How to make air-fried samosas?",
            "What are clean Indian snack options?"
        ]

    # 4. Healthy Indian Breakfast
    if "breakfast" in msg:
        reply = (
            "### 🥣 Healthy Indian Breakfast Recommendations\n\n"
            "A balanced breakfast should provide clean protein, complex fiber, and minimal refined sugar:\n\n"
            "1. **Moong Dal Chilla / Besan Chilla with Paneer (Top Choice)**\n"
            "   - **Nutrients:** ~220 kcal, 14g protein, 6g fiber per 2 chillas.\n"
            "   - **Advantage:** Low glycemic, high satiety, 100% vegetarian.\n\n"
            "2. **Vegetable Poha with Roasted Peanuts & Peas**\n"
            "   - **Nutrients:** ~240 kcal, 6g protein, 5g fiber.\n"
            "   - **Advantage:** Easy to digest, rich in iron; squeeze lemon for vitamin C absorption.\n\n"
            "3. **Steamed Idli with Vegetable Sambar (Less Chutney)**\n"
            "   - **Nutrients:** ~210 kcal (2 idlis + sambar), 8g protein.\n"
            "   - **Advantage:** Fermented batter supports gut microbiome; lentils in sambar add protein.\n\n"
            "4. **Sprouted Moong Salad with Boiled Eggs or Tofu**\n"
            "   - **Nutrients:** ~200 kcal, 16g protein, zero refined oil.\n"
            "   - **Advantage:** Maximum micronutrient density and steady energy until lunch."
        )
        return reply, [
            "Suggest high-protein vegetarian foods",
            "How can I reduce sugar intake?",
            "Create a balanced meal plan"
        ]

    # 5. Sugar Reduction Strategies
    if "reduce sugar" in msg or "cut sugar" in msg or "sugar intake" in msg:
        reply = (
            "### 🚫 Evidence-Based Ways to Cut Down Added Sugar\n\n"
            "1. **Audit Liquid Calories (Biggest Trap):**\n"
            "   - 1 cup of sweet chai with 2 tsp sugar = 40 kcal pure sucrose (~20g daily).\n"
            "   - Avoid packaged fruit juices, energy drinks, and flavored yogurts (often have 15–25g added sugar).\n\n"
            "2. **Decode Disguised Ingredients:**\n"
            "   - Check labels for *Maltodextrin, Invert Sugar, High Fructose Corn Syrup, Dextrose, Rice Malt Syrup*.\n"
            "   - Rule of thumb: If sugar is in the top 3 ingredients, treat it as a dessert.\n\n"
            "3. **Don't Rely Solely on Jaggery/Honey:**\n"
            "   - Jaggery and honey have ~90% of the caloric and glycemic impact of table sugar. Use sparingly.\n\n"
            "4. **Cinnamon & Whole Fruits Trick:**\n"
            "   - Add Ceylon cinnamon to oats or tea to curb sugar cravings.\n"
            "   - Satisfy sweetness with whole fruits (apple, guava, papaya) which come packed with fiber."
        )
        return reply, [
            "Is jaggery or honey safer than white sugar?",
            "What are common hidden sugars in packaged food?",
            "Suggest a healthy Indian breakfast"
        ]

    # 6. High-Protein Vegetarian Foods
    if "protein" in msg:
        reply = (
            "### 💪 Top High-Protein Vegetarian Foods (Indian Diet)\n\n"
            "Target 1.2g to 1.6g protein per kg of bodyweight daily for muscle health and fat loss:\n\n"
            "| Food Source | Protein (per 100g) | Calorie Profile |\n"
            "| :--- | :--- | :--- |\n"
            "| **Soya Chunks / Nutrela** | **52g** | High protein, zero cholesterol |\n"
            "| **Low-Fat Paneer / Cottage Cheese** | **18g–20g** | High satiety, calcium-rich |\n"
            "| **Tofu (Soy Paneer)** | **15g–17g** | Low calorie, low fat |\n"
            "| **Greek Yogurt / Hung Curd** | **10g** | Probiotics + leucine |\n"
            "| **Sprouted Green Moong** | **9g** (cooked) | High bio-availability + fiber |\n"
            "| **Lentils (Dal), Rajma, Chole** | **8g–9g** (cooked) | Complex carbs + protein |\n\n"
            "**NutriCoach Tip:** Combine cereals with legumes (e.g. Rice + Dal or Roti + Chole) to create a complete essential amino acid profile!"
        )
        return reply, [
            "Are soya chunks safe for daily consumption?",
            "Suggest a healthy Indian breakfast",
            "Create a balanced meal plan"
        ]

    # 7. Balanced Meal Plan
    if "meal plan" in msg or "balanced meal" in msg or "diet plan" in msg:
        reply = (
            "### 🥗 The NutriCoach Half-Plate Balanced Meal Strategy\n\n"
            "Follow the scientifically backed **50-25-25 plate formula** for lunch & dinner:\n\n"
            "- **50% of Plate (Fiber & Micronutrients):** Raw cucumber, tomato, carrot salad, followed by steamed or lightly sautéed green vegetables (palak, bhindi, methi, tori).\n"
            "- **25% of Plate (Clean Protein):** 100g low-fat paneer, 50g soya chunks curry, 1 bowl thick dal/chole, or 2 boiled eggs.\n"
            "- **25% of Plate (Complex Carbs):** 1–2 multigrain or millet rotis (Jowar, Bajra, Ragi) or 1 katori brown rice.\n\n"
            "**Food Sequencing Secret:** Eat fiber and protein **first**, and carbs **last**. This blunts post-meal glucose spikes by up to 35%!"
        )
        return reply, [
            "How can I reduce sugar intake?",
            "Suggest high-protein vegetarian foods",
            "Suggest a healthy Indian breakfast"
        ]

    # 8. Follow-up: "Why?", "What about sugar?", "Is there an alternative?"
    if msg in ["why", "why?", "explain why", "what about sugar", "what about sugar?", "is there a healthier alternative", "alternative?", "how much can i eat"]:
        reply = (
            "### 🔍 Detailed Nutritional Insight\n\n"
            "The key dietary factor behind this is the **nutrient-to-calorie density ratio**:\n\n"
            "1. **Metabolic Impact:** Foods rich in refined starches and added sugars create immediate insulin spikes followed by an energy crash, encouraging overeating.\n"
            "2. **Satiety Signals:** Protein and soluble dietary fiber trigger GLP-1 and peptide YY release, signaling your brain that you are genuinely full.\n"
            "3. **Practical Alternative:** Swap deep-fried or high-sugar packaged items with roasted makhana, chana, or whole fruits with nuts."
        )
        return reply, [
            "Suggest a healthy Indian breakfast",
            "Suggest high-protein vegetarian foods",
            "How can I reduce sugar intake?"
        ]

    # Default General Nutrition Response
    reply = (
        f"### 🌿 NutriCoach AI Guidance\n\n"
        f"Regarding **\"{user_message}\"**:\n\n"
        f"1. **Core Principle:** Prioritize whole, minimally processed foods with recognizable ingredients and zero trans fats.\n"
        f"2. **Glycemic Balance:** Pair carbohydrate sources with healthy proteins and dietary fibers to avoid insulin spikes.\n"
        f"3. **SafeBite Scoring Engine:** Foods are evaluated from 0 to 100 based on positive nutrients (protein, fiber) against negative factors (excess sugars, sodium, chemical additives).\n\n"
        f"💡 *Ask me about specific Indian foods (gajak, samosa, poha, paneer), compare two snacks, or ask how to optimize your daily meals!*"
    )
    return reply, generate_follow_up_suggestions(user_message, reply)


def chat_with_gemini(
    user_message: str,
    recent_scan_context: Optional[Dict[str, Any]] = None,
    user_profile: Optional[Dict[str, Any]] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> Tuple[str, List[str]]:
    """
    Nutritional conversational assistant powered by NutriCoach AI (Gemini / Groq with local fallback).
    Incorporates user scan context, dietary profile, and conversation memory.
    """
    system_instruction = (
        "You are NutriCoach AI, SafeBite's personal nutrition and dietary guide. "
        "Your mission is to provide intelligent, friendly, evidence-backed nutritional education "
        "tailored to Indian foods, packaged snacks, and everyday eating habits.\n\n"
        "Guidelines:\n"
        "1. GROUNDING IN DATA: If a user scan context is provided, explain the health score, macros, and ingredients. "
        "If NO scan is provided and user asks 'is this food healthy?' or 'why this score?', politely ask which food they mean. "
        "NEVER invent previous scans or scores.\n"
        "2. PERSONALIZATION: If user profile contains dietary preferences or allergies, warn if the food contains their allergens, "
        "and adapt suggestions (e.g. vegetarian protein for vegetarians, low glycemic for diabetics).\n"
        "3. INDIAN FOOD SPECIALIST: Provide deep, culturally accurate nutritional breakdowns for Indian foods "
        "(gajak vs chikki, samosa vs kachori, poha, upma, idli, paneer, dal, soya chunks).\n"
        "4. FORMATTING: Use structured Markdown with bold titles, short bullets, and clear headers. "
        "Keep responses concise (under 250 words) unless in-depth explanation is requested.\n"
        "5. MULTILINGUAL: If the user writes in Hindi or Hinglish, reply naturally in Hindi/Hinglish with English nutrition terms.\n"
        "6. MEDICAL DISCLAIMER: Always maintain educational boundaries. SafeBite provides dietary guidance, not medical prescriptions."
    )

    context_parts = []
    if recent_scan_context:
        context_parts.append(
            f"ACTIVE SCANNED FOOD CONTEXT:\n"
            f"- Product: {recent_scan_context.get('product_name', 'Unknown')}\n"
            f"- Health Score: {recent_scan_context.get('health_score')}/100 ({recent_scan_context.get('classification')})\n"
            f"- Calories: {recent_scan_context.get('calories')} kcal\n"
            f"- Protein: {recent_scan_context.get('protein')}g, Carbs: {recent_scan_context.get('carbs')}g, Fat: {recent_scan_context.get('fat')}g\n"
            f"- Ingredients: {recent_scan_context.get('ingredients', 'None')}"
        )
    if user_profile:
        context_parts.append(
            f"USER PROFILE:\n"
            f"- Dietary Preference: {user_profile.get('dietary_preference', 'None')}\n"
            f"- Confirmed Allergens: {user_profile.get('allergens', 'None')}\n"
            f"- Diabetic: {'Yes' if user_profile.get('is_diabetic') else 'No'}"
        )

    context_str = "\n\n".join(context_parts)

    # 1. Try Groq (Ultra-fast LLM inference)
    groq_client = get_groq_client()
    if groq_client:
        try:
            model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b").strip()
            messages = [{"role": "system", "content": system_instruction}]
            if context_str:
                messages.append({"role": "system", "content": context_str})
            if conversation_history:
                for h in conversation_history[-6:]:
                    messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
            messages.append({"role": "user", "content": user_message})

            resp = groq_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=650,
                temperature=0.7
            )
            ans = resp.choices[0].message.content
            if ans and ans.strip():
                clean_ans = ans.strip()
                return clean_ans, generate_follow_up_suggestions(user_message, clean_ans)
        except Exception as e:
            logger.warning(f"Groq API call failed: {e}. Trying Gemini...")

    # 2. Try Gemini
    client = get_gemini_client()
    if client:
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        history_str = ""
        if conversation_history:
            history_str = "\n".join([f"{h.get('role', 'user').title()}: {h.get('content')}" for h in conversation_history[-6:]])
            history_str = f"\nRECENT CONVERSATION HISTORY:\n{history_str}\n"

        full_prompt = f"{system_instruction}\n\n{context_str}\n{history_str}\nUser: {user_message}"
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=full_prompt
            )
            clean_reply = response.text.strip()
            return clean_reply, generate_follow_up_suggestions(user_message, clean_reply)
        except Exception as e:
            logger.warning(f"Gemini API request failed: {e}. Falling back to Autonomous Nutrition Agent.")

    # 3. Deterministic Local Autonomous Nutrition Agent
    return autonomous_nutrition_agent(user_message, recent_scan_context, user_profile)
