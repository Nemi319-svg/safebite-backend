"""
SafeBite Universal Food Product Search & Health Analyzer Service
===============================================================
Provides multi-tier product search across:
1. Curated Indian and international packaged food database (Maggi, Kurkure, Lay's, Oreo, Amul, Parle, etc.)
2. SQLite / local cache database
3. OpenFoodFacts Search API (in.openfoodfacts.org & world.openfoodfacts.org)

Features transparent health scoring, FSSAI warnings, additive inspection,
personalized dietary suitability (diabetic, low-sugar, low-sodium, vegetarian, allergens),
and side-by-side product comparisons.
"""

import datetime
import logging
import math
import re
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

from health_calculator import calculate_health_score, get_healthier_alternatives
from models import (
    AdminAddProductRequest,
    ProductCompareItem,
    ProductDetailResponse,
    ProductHealthAnalysisResponse,
    ProductMultiCompareResponse,
    ProductNutritionValues,
    ProductSearchResponse,
    ProductSummaryItem,
)

logger = logging.getLogger("safebite.product_search")

# ============================================================================
# In-Memory Search & Query Cache with TTL
# ============================================================================
class SearchTTLCache:
    def __init__(self, ttl_seconds: int = 300, max_size: int = 256):
        self.ttl = ttl_seconds
        self.max_size = max_size
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self._cache:
                timestamp, value = self._cache[key]
                if time.time() - timestamp < self.ttl:
                    return value
                del self._cache[key]
            return None

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            if len(self._cache) >= self.max_size:
                # Evict oldest entry
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][0], default=None)
                if oldest_key:
                    del self._cache[oldest_key]
            self._cache[key] = (time.time(), value)


_search_cache = SearchTTLCache(ttl_seconds=300)
_product_cache: Dict[str, Dict[str, Any]] = {}
_catalog_lock = threading.Lock()


# ============================================================================
# Curated Indian & Packaged Food Database
# ============================================================================
# Realistic, verified nutritional data per 100g for popular packaged food products
CURATED_PRODUCTS: Dict[str, Dict[str, Any]] = {
    # ------------------ NOODLES & INSTANT FOODS ------------------
    "maggi_2min_masala": {
        "id": "maggi_2min_masala",
        "name": "Maggi 2-Minute Masala Noodles",
        "brand": "Nestle",
        "category": "Instant Foods",
        "barcode": "8901058852444",
        "image_url": "https://images.openfoodfacts.org/images/products/890/105/885/2444/front_en.11.400.jpg",
        "ingredients": "Refined wheat flour (Maida), Palm oil, Salt, Wheat gluten, Mineral (Calcium carbonate), Thickeners (508 & 412), Acidity regulators (501(i) & 500(i)) and Humectant (451(i)). Tastemaker: Mixed spices (Hydrolysed groundnut protein, Mixed spices, Onion powder, Garlic powder, Coriander, Turmeric, Chilli, Cumin, Aniseed, Fenugreek, Ginger, Black pepper, Clove, Nutmeg, Cardamom), Noodle powder, Sugar, Edible starch, Flavour enhancer (635), Acidity regulator (330).",
        "serving_size": "70g (1 pack)",
        "calories": 427.0,
        "protein": 8.0,
        "carbohydrates": 63.5,
        "total_sugar": 2.2,
        "added_sugar": 1.5,
        "total_fat": 15.7,
        "saturated_fat": 6.8,
        "trans_fat": 0.1,
        "sodium": 1020.0,
        "fiber": 3.6,
        "allergens": ["Gluten", "Groundnut / Peanut", "Soy (traces)"],
        "additives": ["INS 508", "INS 412", "INS 501(i)", "INS 500(i)", "INS 451(i)", "INS 635", "INS 330"],
        "data_source": "SafeBite Indian Food Database"
    },
    "maggi_nutrilicious_atta": {
        "id": "maggi_nutrilicious_atta",
        "name": "Maggi Nutri-licious Atta Masala Noodles",
        "brand": "Nestle",
        "category": "Instant Foods",
        "barcode": "8901058852505",
        "image_url": "https://images.openfoodfacts.org/images/products/890/105/885/2505/front_en.14.400.jpg",
        "ingredients": "Whole Wheat Flour (Atta 85.3%), Palm oil, Wheat gluten, Salt, Mineral (Calcium carbonate), Thickeners (508 & 412), Acidity regulators. Tastemaker: Mixed spices (Dehydrated vegetables (Carrot, Green peas), Onion powder, Turmeric, Coriander, Cumin), Salt, Sugar, Edible starch.",
        "serving_size": "72.5g (1 pack)",
        "calories": 405.0,
        "protein": 10.2,
        "carbohydrates": 64.0,
        "total_sugar": 2.5,
        "added_sugar": 1.0,
        "total_fat": 12.0,
        "saturated_fat": 5.2,
        "trans_fat": 0.05,
        "sodium": 880.0,
        "fiber": 6.8,
        "allergens": ["Gluten", "Wheat"],
        "additives": ["INS 508", "INS 412", "INS 501", "INS 330"],
        "data_source": "SafeBite Indian Food Database"
    },
    "yippee_magic_masala": {
        "id": "yippee_magic_masala",
        "name": "Sunfeast YiPPee! Magic Masala Noodles",
        "brand": "ITC Sunfeast",
        "category": "Instant Foods",
        "barcode": "8901725141011",
        "image_url": "https://images.openfoodfacts.org/images/products/890/172/514/1011/front_en.10.400.jpg",
        "ingredients": "Wheat Flour (Maida), Refined Palm Oil, Salt, Wheat Gluten, Mineral, Acidity Regulators. Masala Mix: Dehydrated Vegetables (Beans, Carrot, Cabbage), Spices & Condiments (Coriander, Cumin, Chilli, Ginger), Salt, Hydrolysed Vegetable Protein, Flavour Enhancers (INS 627, INS 631).",
        "serving_size": "65g (1 pack)",
        "calories": 468.0,
        "protein": 9.0,
        "carbohydrates": 64.0,
        "total_sugar": 3.0,
        "added_sugar": 1.8,
        "total_fat": 19.5,
        "saturated_fat": 8.9,
        "trans_fat": 0.1,
        "sodium": 990.0,
        "fiber": 3.5,
        "allergens": ["Gluten", "Soy"],
        "additives": ["INS 627", "INS 631", "INS 451", "INS 330"],
        "data_source": "SafeBite Indian Food Database"
    },

    # ------------------ SNACKS & CHIPS ------------------
    "kurkure_masala_munch": {
        "id": "kurkure_masala_munch",
        "name": "Kurkure Masala Munch Crunchy Snack",
        "brand": "PepsiCo Kurkure",
        "category": "Snacks",
        "barcode": "8901499008200",
        "image_url": "https://images.openfoodfacts.org/images/products/890/149/900/8200/front_en.15.400.jpg",
        "ingredients": "Rice Meal (42.8%), Edible Vegetable Oil (Palmolein Oil), Corn Meal (19.8%), Gram Meal (3.3%), Spices and Condiments (Chilli powder, Onion powder, Garlic powder, Coriander powder, Black pepper powder, Amchur, Cumin powder, Fenugreek), Salt, Sugar, Tartaric acid (INS 334).",
        "serving_size": "30g",
        "calories": 561.0,
        "protein": 6.1,
        "carbohydrates": 55.4,
        "total_sugar": 2.5,
        "added_sugar": 1.2,
        "total_fat": 35.0,
        "saturated_fat": 15.5,
        "trans_fat": 0.1,
        "sodium": 890.0,
        "fiber": 2.0,
        "allergens": ["Soy (traces)"],
        "additives": ["INS 334", "INS 330", "INS 551"],
        "data_source": "SafeBite Indian Food Database"
    },
    "kurkure_green_chutney": {
        "id": "kurkure_green_chutney",
        "name": "Kurkure Green Chutney Style",
        "brand": "PepsiCo Kurkure",
        "category": "Snacks",
        "barcode": "8901499008224",
        "image_url": "https://images.openfoodfacts.org/images/products/890/149/900/8224/front_en.8.400.jpg",
        "ingredients": "Rice Meal, Edible Vegetable Oil (Palmolein), Corn Meal, Gram Meal, Green Chutney Seasoning (Mint, Coriander, Green Chilli, Salt, Sugar, Acidity Regulator 330).",
        "serving_size": "30g",
        "calories": 558.0,
        "protein": 6.0,
        "carbohydrates": 56.0,
        "total_sugar": 3.0,
        "added_sugar": 1.5,
        "total_fat": 34.5,
        "saturated_fat": 15.0,
        "trans_fat": 0.1,
        "sodium": 870.0,
        "fiber": 2.1,
        "allergens": [],
        "additives": ["INS 330", "INS 296"],
        "data_source": "SafeBite Indian Food Database"
    },
    "lays_magic_masala": {
        "id": "lays_magic_masala",
        "name": "Lay's India's Magic Masala Potato Chips",
        "brand": "PepsiCo Lay's",
        "category": "Snacks",
        "barcode": "8901491101831",
        "image_url": "https://images.openfoodfacts.org/images/products/890/149/110/1831/front_en.21.400.jpg",
        "ingredients": "Potato, Edible Vegetable Oil (Palmolein, Rice Bran Oil), Spices & Condiments (Onion powder, Chilli powder, Dry mango powder, Coriander powder, Ginger powder, Garlic powder, Black pepper powder, Turmeric powder, Cumin powder), Salt, Black Salt, Sugar, Tomato powder, Citric acid (INS 330).",
        "serving_size": "30g",
        "calories": 544.0,
        "protein": 7.0,
        "carbohydrates": 52.0,
        "total_sugar": 3.0,
        "added_sugar": 1.5,
        "total_fat": 34.0,
        "saturated_fat": 14.5,
        "trans_fat": 0.1,
        "sodium": 780.0,
        "fiber": 4.0,
        "allergens": ["Milk (traces)"],
        "additives": ["INS 330", "INS 635"],
        "data_source": "SafeBite Indian Food Database"
    },
    "lays_classic_salted": {
        "id": "lays_classic_salted",
        "name": "Lay's Classic Salted Potato Chips",
        "brand": "PepsiCo Lay's",
        "category": "Snacks",
        "barcode": "8901491101824",
        "image_url": "https://images.openfoodfacts.org/images/products/890/149/110/1824/front_en.16.400.jpg",
        "ingredients": "Potato, Edible Vegetable Oil (Palmolein, Rice Bran Oil), Salt (1.5%).",
        "serving_size": "30g",
        "calories": 540.0,
        "protein": 6.8,
        "carbohydrates": 53.0,
        "total_sugar": 1.0,
        "added_sugar": 0.0,
        "total_fat": 33.6,
        "saturated_fat": 14.0,
        "trans_fat": 0.1,
        "sodium": 550.0,
        "fiber": 3.8,
        "allergens": [],
        "additives": [],
        "data_source": "SafeBite Indian Food Database"
    },
    "lays_cream_onion": {
        "id": "lays_cream_onion",
        "name": "Lay's American Style Cream & Onion Potato Chips",
        "brand": "PepsiCo Lay's",
        "category": "Snacks",
        "barcode": "8901491101848",
        "image_url": "https://images.openfoodfacts.org/images/products/890/149/110/1848/front_en.19.400.jpg",
        "ingredients": "Potato, Edible Vegetable Oil (Palmolein), Seasoning (Sugar, Salt, Milk Solids (Skimmed Milk Powder, Cheese Powder), Onion Powder, Parsley, Acidity Regulators 330 & 270).",
        "serving_size": "30g",
        "calories": 542.0,
        "protein": 6.9,
        "carbohydrates": 52.5,
        "total_sugar": 4.0,
        "added_sugar": 2.2,
        "total_fat": 33.8,
        "saturated_fat": 14.2,
        "trans_fat": 0.1,
        "sodium": 680.0,
        "fiber": 3.6,
        "allergens": ["Milk"],
        "additives": ["INS 330", "INS 270", "INS 627", "INS 631"],
        "data_source": "SafeBite Indian Food Database"
    },
    "haldirams_aloo_bhujia": {
        "id": "haldirams_aloo_bhujia",
        "name": "Haldiram's Aloo Bhujia",
        "brand": "Haldiram's",
        "category": "Snacks",
        "barcode": "8904063200121",
        "image_url": "https://images.openfoodfacts.org/images/products/890/406/320/0121/front_en.12.400.jpg",
        "ingredients": "Potatoes (44%), Edible Vegetable Oil (Cottonseed, Corn, Palmolein), Gram Pulse Flour, Tepary Beans Flour, Edible Starch, Spices (Mint, Ginger, Garlic, Red Chilli, Black Pepper, Clove), Salt, Mango Powder.",
        "serving_size": "35g",
        "calories": 582.0,
        "protein": 8.5,
        "carbohydrates": 43.0,
        "total_sugar": 2.0,
        "added_sugar": 0.0,
        "total_fat": 42.0,
        "saturated_fat": 16.5,
        "trans_fat": 0.1,
        "sodium": 760.0,
        "fiber": 3.8,
        "allergens": [],
        "additives": ["INS 330"],
        "data_source": "SafeBite Indian Food Database"
    },

    # ------------------ BISCUITS & COOKIES ------------------
    "oreo_vanilla": {
        "id": "oreo_vanilla",
        "name": "Oreo Original Vanilla Sandwich Biscuits",
        "brand": "Mondelez Oreo",
        "category": "Biscuits",
        "barcode": "7622201764653",
        "image_url": "https://images.openfoodfacts.org/images/products/762/220/176/4653/front_en.28.400.jpg",
        "ingredients": "Refined Wheat Flour (Maida), Sugar, Fractionated Palm Oil, Cocoa Solids (2.3%), Invert Sugar, Leavening Agents (500(ii), 503(ii)), Salt, Emulsifier (322), Nature Identical Vanilla Flavour.",
        "serving_size": "28.8g (3 biscuits)",
        "calories": 480.0,
        "protein": 5.0,
        "carbohydrates": 70.0,
        "total_sugar": 38.0,
        "added_sugar": 36.5,
        "total_fat": 20.0,
        "saturated_fat": 9.8,
        "trans_fat": 0.1,
        "sodium": 410.0,
        "fiber": 2.5,
        "allergens": ["Gluten", "Soy", "Milk (traces)"],
        "additives": ["INS 500(ii)", "INS 503(ii)", "INS 322"],
        "data_source": "SafeBite Indian Food Database"
    },
    "oreo_chocolate": {
        "id": "oreo_chocolate",
        "name": "Oreo Chocolate Creme Sandwich Biscuits",
        "brand": "Mondelez Oreo",
        "category": "Biscuits",
        "barcode": "7622201764677",
        "image_url": "https://images.openfoodfacts.org/images/products/762/220/176/4677/front_en.18.400.jpg",
        "ingredients": "Refined Wheat Flour, Sugar, Palm Oil, Cocoa Solids (4.5%), Invert Sugar, Leavening Agents, Salt, Emulsifier (322).",
        "serving_size": "28.8g",
        "calories": 485.0,
        "protein": 5.2,
        "carbohydrates": 69.5,
        "total_sugar": 39.0,
        "added_sugar": 37.0,
        "total_fat": 20.5,
        "saturated_fat": 10.2,
        "trans_fat": 0.1,
        "sodium": 400.0,
        "fiber": 2.6,
        "allergens": ["Gluten", "Soy"],
        "additives": ["INS 500(ii)", "INS 503(ii)", "INS 322"],
        "data_source": "SafeBite Indian Food Database"
    },
    "parle_g_gluco": {
        "id": "parle_g_gluco",
        "name": "Parle-G Original Gluco Biscuits",
        "brand": "Parle",
        "category": "Biscuits",
        "barcode": "8901719101038",
        "image_url": "https://images.openfoodfacts.org/images/products/890/171/910/1038/front_en.24.400.jpg",
        "ingredients": "Wheat Flour (Maida 67%), Sugar, Edible Vegetable Oil (Palm Oil), Invert Sugar Syrup, Leavening Agents (503(ii), 500(ii)), Salt, Milk Solids (0.6%), Emulsifier (471), Dough Conditioner (223).",
        "serving_size": "25g (5 biscuits)",
        "calories": 454.0,
        "protein": 6.5,
        "carbohydrates": 78.2,
        "total_sugar": 26.5,
        "added_sugar": 24.8,
        "total_fat": 13.0,
        "saturated_fat": 6.2,
        "trans_fat": 0.05,
        "sodium": 280.0,
        "fiber": 1.2,
        "allergens": ["Gluten", "Milk", "Sulphites"],
        "additives": ["INS 503(ii)", "INS 500(ii)", "INS 471", "INS 223"],
        "data_source": "SafeBite Indian Food Database"
    },
    "britannia_good_day_butter": {
        "id": "britannia_good_day_butter",
        "name": "Britannia Good Day Butter Cookies",
        "brand": "Britannia",
        "category": "Biscuits",
        "barcode": "8901063012826",
        "image_url": "https://images.openfoodfacts.org/images/products/890/106/301/2826/front_en.16.400.jpg",
        "ingredients": "Refined Wheat Flour (Maida), Sugar, Edible Vegetable Oil (Palm), Butter (2%), Invert Sugar Syrup, Milk Solids, Leavening Agents, Salt, Emulsifiers (322, 471).",
        "serving_size": "30g",
        "calories": 495.0,
        "protein": 6.0,
        "carbohydrates": 68.0,
        "total_sugar": 22.0,
        "added_sugar": 20.5,
        "total_fat": 22.0,
        "saturated_fat": 10.5,
        "trans_fat": 0.1,
        "sodium": 260.0,
        "fiber": 1.0,
        "allergens": ["Gluten", "Milk", "Soy"],
        "additives": ["INS 322", "INS 471", "INS 500(ii)", "INS 503(ii)"],
        "data_source": "SafeBite Indian Food Database"
    },
    "britannia_bourbon": {
        "id": "britannia_bourbon",
        "name": "Britannia Bourbon Chocolate Cream Biscuits",
        "brand": "Britannia",
        "category": "Biscuits",
        "barcode": "8901063013236",
        "image_url": "https://images.openfoodfacts.org/images/products/890/106/301/3236/front_en.11.400.jpg",
        "ingredients": "Refined Wheat Flour, Sugar (38%), Edible Vegetable Oil, Cocoa Solids (2.3%), Invert Sugar Syrup, Leavening Agents, Salt, Emulsifier (322, 471).",
        "serving_size": "25g",
        "calories": 488.0,
        "protein": 5.5,
        "carbohydrates": 72.0,
        "total_sugar": 38.0,
        "added_sugar": 36.0,
        "total_fat": 20.0,
        "saturated_fat": 9.5,
        "trans_fat": 0.1,
        "sodium": 220.0,
        "fiber": 1.5,
        "allergens": ["Gluten", "Soy"],
        "additives": ["INS 500", "INS 503", "INS 322"],
        "data_source": "SafeBite Indian Food Database"
    },
    "britannia_nutrichoice_digestive": {
        "id": "britannia_nutrichoice_digestive",
        "name": "Britannia NutriChoice High Fibre Digestive Biscuits",
        "brand": "Britannia",
        "category": "Biscuits",
        "barcode": "8901063018019",
        "image_url": "https://images.openfoodfacts.org/images/products/890/106/301/8019/front_en.15.400.jpg",
        "ingredients": "Wheat Flour (Atta 55%), Refined Palm Oil, Sugar, Wheat Bran (4.5%), Invert Sugar, Leavening Agents, Salt, Milk Solids, Malt Extract.",
        "serving_size": "25g",
        "calories": 480.0,
        "protein": 9.0,
        "carbohydrates": 66.0,
        "total_sugar": 14.5,
        "added_sugar": 13.0,
        "total_fat": 20.0,
        "saturated_fat": 9.0,
        "trans_fat": 0.05,
        "sodium": 480.0,
        "fiber": 6.0,
        "allergens": ["Gluten", "Milk"],
        "additives": ["INS 500(ii)", "INS 503(ii)", "INS 471"],
        "data_source": "SafeBite Indian Food Database"
    },
    "britannia_whole_wheat_bread": {
        "id": "britannia_whole_wheat_bread",
        "name": "Britannia 100% Whole Wheat Bread",
        "brand": "Britannia",
        "category": "Breakfast & Bakery",
        "barcode": "8901063019009",
        "image_url": "https://images.openfoodfacts.org/images/products/890/106/301/9009/front_en.8.400.jpg",
        "ingredients": "Whole Wheat Flour (Atta 62%), Water, Sugar, Yeast, Edible Vegetable Oil, Salt, Soya Flour, Preservative (282), Emulsifier (481(i)), Flour Treatment Agent (1100).",
        "serving_size": "40g (2 slices)",
        "calories": 245.0,
        "protein": 9.5,
        "carbohydrates": 48.0,
        "total_sugar": 4.5,
        "added_sugar": 3.0,
        "total_fat": 2.2,
        "saturated_fat": 0.8,
        "trans_fat": 0.0,
        "sodium": 420.0,
        "fiber": 6.5,
        "allergens": ["Gluten", "Soy"],
        "additives": ["INS 282", "INS 481(i)", "INS 1100"],
        "data_source": "SafeBite Indian Food Database"
    },

    # ------------------ DAIRY PRODUCTS ------------------
    "amul_taaza_milk": {
        "id": "amul_taaza_milk",
        "name": "Amul Taaza Homogenised Toned Milk",
        "brand": "Amul",
        "category": "Dairy",
        "barcode": "8906002040006",
        "image_url": "https://images.openfoodfacts.org/images/products/890/600/204/0006/front_en.18.400.jpg",
        "ingredients": "Toned Milk (Milk Solids), Vitamin A & D fortified.",
        "serving_size": "200ml (1 glass)",
        "calories": 58.0,
        "protein": 3.1,
        "carbohydrates": 4.7,
        "total_sugar": 4.7,
        "added_sugar": 0.0,
        "total_fat": 3.0,
        "saturated_fat": 1.9,
        "trans_fat": 0.0,
        "sodium": 50.0,
        "fiber": 0.0,
        "allergens": ["Milk"],
        "additives": [],
        "data_source": "SafeBite Indian Food Database"
    },
    "amul_gold_milk": {
        "id": "amul_gold_milk",
        "name": "Amul Gold Full Cream Milk",
        "brand": "Amul",
        "category": "Dairy",
        "barcode": "8906002040020",
        "image_url": "https://images.openfoodfacts.org/images/products/890/600/204/0020/front_en.12.400.jpg",
        "ingredients": "Standardised Full Cream Milk, Vitamin A & D fortified.",
        "serving_size": "200ml",
        "calories": 87.0,
        "protein": 3.5,
        "carbohydrates": 5.0,
        "total_sugar": 5.0,
        "added_sugar": 0.0,
        "total_fat": 6.0,
        "saturated_fat": 3.8,
        "trans_fat": 0.0,
        "sodium": 52.0,
        "fiber": 0.0,
        "allergens": ["Milk"],
        "additives": [],
        "data_source": "SafeBite Indian Food Database"
    },
    "amul_butter": {
        "id": "amul_butter",
        "name": "Amul Pasteurized Salted Butter",
        "brand": "Amul",
        "category": "Dairy",
        "barcode": "8906002043014",
        "image_url": "https://images.openfoodfacts.org/images/products/890/600/204/3014/front_en.14.400.jpg",
        "ingredients": "Butter (Milk Fat 80%), Common Salt, Annatto / Carotene Natural Colour.",
        "serving_size": "10g",
        "calories": 722.0,
        "protein": 0.6,
        "carbohydrates": 0.0,
        "total_sugar": 0.0,
        "added_sugar": 0.0,
        "total_fat": 80.0,
        "saturated_fat": 51.0,
        "trans_fat": 2.5,
        "sodium": 830.0,
        "fiber": 0.0,
        "allergens": ["Milk"],
        "additives": ["INS 160b(ii)"],
        "data_source": "SafeBite Indian Food Database"
    },
    "amul_malai_paneer": {
        "id": "amul_malai_paneer",
        "name": "Amul Fresh Malai Paneer",
        "brand": "Amul",
        "category": "Dairy",
        "barcode": "8906002045018",
        "image_url": "https://images.openfoodfacts.org/images/products/890/600/204/5018/front_en.10.400.jpg",
        "ingredients": "Pasteurized Milk, Citric Acid.",
        "serving_size": "100g",
        "calories": 289.0,
        "protein": 18.5,
        "carbohydrates": 3.2,
        "total_sugar": 2.0,
        "added_sugar": 0.0,
        "total_fat": 22.0,
        "saturated_fat": 14.0,
        "trans_fat": 0.0,
        "sodium": 30.0,
        "fiber": 0.0,
        "allergens": ["Milk"],
        "additives": [],
        "data_source": "SafeBite Indian Food Database"
    },

    # ------------------ BEVERAGES & COLD DRINKS ------------------
    "coca_cola_original": {
        "id": "coca_cola_original",
        "name": "Coca-Cola Original Taste Carbonated Drink",
        "brand": "Coca-Cola",
        "category": "Beverages",
        "barcode": "8901764012235",
        "image_url": "https://images.openfoodfacts.org/images/products/890/176/401/2235/front_en.15.400.jpg",
        "ingredients": "Carbonated Water, Sugar, Acidity Regulator (338), Colour (150d), Natural Flavours, Caffeine.",
        "serving_size": "250ml",
        "calories": 44.0,
        "protein": 0.0,
        "carbohydrates": 10.6,
        "total_sugar": 10.6,
        "added_sugar": 10.6,
        "total_fat": 0.0,
        "saturated_fat": 0.0,
        "trans_fat": 0.0,
        "sodium": 8.5,
        "fiber": 0.0,
        "allergens": [],
        "additives": ["INS 338", "INS 150d"],
        "data_source": "SafeBite Indian Food Database"
    },
    "coca_cola_zero": {
        "id": "coca_cola_zero",
        "name": "Coca-Cola Zero Sugar Can",
        "brand": "Coca-Cola",
        "category": "Beverages",
        "barcode": "8901764012358",
        "image_url": "https://images.openfoodfacts.org/images/products/890/176/401/2358/front_en.12.400.jpg",
        "ingredients": "Carbonated Water, Colour (150d), Acidity Regulators (338, 331), Non-caloric Sweeteners (950, 955), Caffeine.",
        "serving_size": "300ml",
        "calories": 0.3,
        "protein": 0.0,
        "carbohydrates": 0.0,
        "total_sugar": 0.0,
        "added_sugar": 0.0,
        "total_fat": 0.0,
        "saturated_fat": 0.0,
        "trans_fat": 0.0,
        "sodium": 9.0,
        "fiber": 0.0,
        "allergens": [],
        "additives": ["INS 150d", "INS 338", "INS 331", "INS 950", "INS 955"],
        "data_source": "SafeBite Indian Food Database"
    },
    "pepsi_cola": {
        "id": "pepsi_cola",
        "name": "Pepsi Cola Refreshing Drink",
        "brand": "PepsiCo",
        "category": "Beverages",
        "barcode": "8902080000403",
        "image_url": "https://images.openfoodfacts.org/images/products/890/208/000/0403/front_en.14.400.jpg",
        "ingredients": "Carbonated Water, Sugar, Acidity Regulator (338), Colour (150d), Caffeine, Natural Flavours.",
        "serving_size": "250ml",
        "calories": 43.0,
        "protein": 0.0,
        "carbohydrates": 10.7,
        "total_sugar": 10.7,
        "added_sugar": 10.7,
        "total_fat": 0.0,
        "saturated_fat": 0.0,
        "trans_fat": 0.0,
        "sodium": 11.0,
        "fiber": 0.0,
        "allergens": [],
        "additives": ["INS 338", "INS 150d"],
        "data_source": "SafeBite Indian Food Database"
    },
    "thums_up": {
        "id": "thums_up",
        "name": "Thums Up Strong Cola",
        "brand": "Coca-Cola Thums Up",
        "category": "Beverages",
        "barcode": "8901764022234",
        "image_url": "https://images.openfoodfacts.org/images/products/890/176/402/2234/front_en.10.400.jpg",
        "ingredients": "Carbonated Water, Sugar, Acidity Regulator (338), Colour (150d), Caffeine (strong flavour).",
        "serving_size": "250ml",
        "calories": 40.0,
        "protein": 0.0,
        "carbohydrates": 10.0,
        "total_sugar": 10.0,
        "added_sugar": 10.0,
        "total_fat": 0.0,
        "saturated_fat": 0.0,
        "trans_fat": 0.0,
        "sodium": 12.0,
        "fiber": 0.0,
        "allergens": [],
        "additives": ["INS 338", "INS 150d"],
        "data_source": "SafeBite Indian Food Database"
    },

    # ------------------ HEALTH & MALT DRINKS ------------------
    "cadbury_bournvita": {
        "id": "cadbury_bournvita",
        "name": "Cadbury Bournvita Chocolate Health Drink",
        "brand": "Cadbury",
        "category": "Health & Malt Drinks",
        "barcode": "7622201752001",
        "image_url": "https://images.openfoodfacts.org/images/products/762/220/175/2001/front_en.16.400.jpg",
        "ingredients": "Cereal Extract (51%), Sugar, Cocoa Solids, Caramel (150c), Milk Solids, Liquid Glucose, Emulsifiers (322, 471), Vitamins (A, B1, B2, B6, B12, C, D), Minerals (Iron, Calcium, Zinc).",
        "serving_size": "20g (with milk)",
        "calories": 380.0,
        "protein": 7.0,
        "carbohydrates": 85.0,
        "total_sugar": 32.0,
        "added_sugar": 28.0,
        "total_fat": 1.8,
        "saturated_fat": 0.9,
        "trans_fat": 0.0,
        "sodium": 310.0,
        "fiber": 3.5,
        "allergens": ["Gluten (Barley / Wheat)", "Milk", "Soy"],
        "additives": ["INS 150c", "INS 322", "INS 471", "INS 500(ii)"],
        "data_source": "SafeBite Indian Food Database"
    },
    "horlicks_classic_malt": {
        "id": "horlicks_classic_malt",
        "name": "Horlicks Classic Malt Nutrition Drink",
        "brand": "Horlicks",
        "category": "Health & Malt Drinks",
        "barcode": "8901030383793",
        "image_url": "https://images.openfoodfacts.org/images/products/890/103/038/3793/front_en.14.400.jpg",
        "ingredients": "Malted Barley (39%), Wheat Flour (27%), Milk Solids (14%), Sugar, Minerals, Salt, Acidity Regulators (501(ii), 500(ii)), Vitamins.",
        "serving_size": "27g (with milk)",
        "calories": 377.0,
        "protein": 11.0,
        "carbohydrates": 79.0,
        "total_sugar": 32.0,
        "added_sugar": 18.0,
        "total_fat": 2.0,
        "saturated_fat": 1.1,
        "trans_fat": 0.0,
        "sodium": 400.0,
        "fiber": 4.0,
        "allergens": ["Gluten (Barley, Wheat)", "Milk"],
        "additives": ["INS 501(ii)", "INS 500(ii)"],
        "data_source": "SafeBite Indian Food Database"
    },

    # ------------------ OATS & BREAKFAST CEREALS ------------------
    "quaker_rolled_oats": {
        "id": "quaker_rolled_oats",
        "name": "Quaker Rolled White Oats (100% Wholegrain)",
        "brand": "PepsiCo Quaker",
        "category": "Breakfast & Cereals",
        "barcode": "8901491001889",
        "image_url": "https://images.openfoodfacts.org/images/products/890/149/100/1889/front_en.18.400.jpg",
        "ingredients": "100% Rolled Whole Grain Oats.",
        "serving_size": "40g",
        "calories": 389.0,
        "protein": 16.9,
        "carbohydrates": 66.3,
        "total_sugar": 0.0,
        "added_sugar": 0.0,
        "total_fat": 6.9,
        "saturated_fat": 1.2,
        "trans_fat": 0.0,
        "sodium": 2.0,
        "fiber": 10.6,
        "allergens": ["Oats (may contain traces of gluten from wheat)"],
        "additives": [],
        "data_source": "SafeBite Indian Food Database"
    },
    "saffola_masala_oats": {
        "id": "saffola_masala_oats",
        "name": "Saffola Masala Oats Classic Masala",
        "brand": "Marico Saffola",
        "category": "Breakfast & Cereals",
        "barcode": "8901088002015",
        "image_url": "https://images.openfoodfacts.org/images/products/890/108/800/2015/front_en.10.400.jpg",
        "ingredients": "Rolled Oats (73.9%), Spices and Condiments (Onion, Turmeric, Pepper, Cumin, Garlic, Fenugreek, Clove, Nutmeg), Salt, Dried Vegetables (Carrots, Green Peas), Edible Vegetable Oil (Rice Bran).",
        "serving_size": "38g",
        "calories": 390.0,
        "protein": 9.5,
        "carbohydrates": 67.0,
        "total_sugar": 4.5,
        "added_sugar": 1.5,
        "total_fat": 9.2,
        "saturated_fat": 2.1,
        "trans_fat": 0.05,
        "sodium": 820.0,
        "fiber": 7.8,
        "allergens": ["Oats"],
        "additives": ["INS 627", "INS 631", "INS 330"],
        "data_source": "SafeBite Indian Food Database"
    },

    # ------------------ CHOCOLATES & CONFECTIONERY ------------------
    "cadbury_dairy_milk": {
        "id": "cadbury_dairy_milk",
        "name": "Cadbury Dairy Milk Chocolate",
        "brand": "Mondelez Cadbury",
        "category": "Chocolates",
        "barcode": "7622201446757",
        "image_url": "https://images.openfoodfacts.org/images/products/762/220/144/6757/front_en.21.400.jpg",
        "ingredients": "Sugar, Milk Solids (22%), Cocoa Butter, Cocoa Solids, Emulsifiers (442, 476), Flavours (Natural, Nature Identical and Artificial Vanilla Flavouring Substances).",
        "serving_size": "20g",
        "calories": 534.0,
        "protein": 7.8,
        "carbohydrates": 60.5,
        "total_sugar": 57.0,
        "added_sugar": 52.0,
        "total_fat": 29.5,
        "saturated_fat": 18.0,
        "trans_fat": 0.1,
        "sodium": 150.0,
        "fiber": 2.0,
        "allergens": ["Milk", "Soy"],
        "additives": ["INS 442", "INS 476"],
        "data_source": "SafeBite Indian Food Database"
    },
    # ------------------ BINGO & UNCLE CHIPPS (SNACKS) ------------------
    "bingo_mad_angles": {
        "id": "bingo_mad_angles",
        "name": "Bingo! Mad Angles Achaari Masti",
        "brand": "ITC Bingo",
        "category": "Snacks",
        "barcode": "8901725131122",
        "image_url": "https://images.openfoodfacts.org/images/products/890/172/513/1122/front_en.10.400.jpg",
        "ingredients": "Rice Grits (40%), Edible Vegetable Oil (Palmolein), Corn Grits (18%), Gram Grits (6%), Seasoning (Spices & Condiments, Iodized Salt, Black Salt, Mango powder, Acidity Regulator 330, Flavour Enhancers 627, 631).",
        "serving_size": "30g",
        "calories": 542.0,
        "protein": 6.5,
        "carbohydrates": 57.0,
        "total_sugar": 4.0,
        "added_sugar": 1.5,
        "total_fat": 32.0,
        "saturated_fat": 14.5,
        "trans_fat": 0.1,
        "sodium": 860.0,
        "fiber": 3.0,
        "allergens": ["Gluten (traces)", "Milk (traces)"],
        "additives": ["INS 330", "INS 627", "INS 631"],
        "data_source": "SafeBite Indian Food Database"
    },
    "bingo_tedhe_medhe": {
        "id": "bingo_tedhe_medhe",
        "name": "Bingo! Tedhe Medhe Masala Tadka",
        "brand": "ITC Bingo",
        "category": "Snacks",
        "barcode": "8901725132233",
        "image_url": "https://images.openfoodfacts.org/images/products/890/172/513/2233/front_en.12.400.jpg",
        "ingredients": "Rice Grits, Edible Vegetable Oil (Palmolein), Corn Grits, Gram Grits, Spices and Condiments (Onion powder, Chilli powder, Coriander powder, Garlic powder), Salt.",
        "serving_size": "30g",
        "calories": 558.0,
        "protein": 6.0,
        "carbohydrates": 55.5,
        "total_sugar": 3.5,
        "added_sugar": 1.0,
        "total_fat": 34.5,
        "saturated_fat": 15.0,
        "trans_fat": 0.1,
        "sodium": 920.0,
        "fiber": 2.5,
        "allergens": ["Soy"],
        "additives": ["INS 330", "INS 635"],
        "data_source": "SafeBite Indian Food Database"
    },
    "uncle_chipps_spicy": {
        "id": "uncle_chipps_spicy",
        "name": "Uncle Chipps Spicy Treat Potato Chips",
        "brand": "Uncle Chipps",
        "category": "Snacks",
        "barcode": "8901491103344",
        "image_url": "https://images.openfoodfacts.org/images/products/890/149/110/3344/front_en.14.400.jpg",
        "ingredients": "Potato (60%), Edible Vegetable Oil (Palmolein), Seasoning (Spices & Condiments, Iodized Salt, Black Salt, Mango powder, Acidity Regulators 330 & 296).",
        "serving_size": "30g",
        "calories": 548.0,
        "protein": 6.5,
        "carbohydrates": 52.5,
        "total_sugar": 2.8,
        "added_sugar": 1.2,
        "total_fat": 34.5,
        "saturated_fat": 14.5,
        "trans_fat": 0.1,
        "sodium": 810.0,
        "fiber": 3.8,
        "allergens": ["Milk (traces)"],
        "additives": ["INS 330", "INS 296", "INS 635"],
        "data_source": "SafeBite Indian Food Database"
    },
    "uncle_chipps_salted": {
        "id": "uncle_chipps_salted",
        "name": "Uncle Chipps Plain Salted Potato Chips",
        "brand": "Uncle Chipps",
        "category": "Snacks",
        "barcode": "8901491103351",
        "image_url": "https://images.openfoodfacts.org/images/products/890/149/110/3351/front_en.11.400.jpg",
        "ingredients": "Potato (65%), Edible Vegetable Oil (Palmolein), Iodized Salt (1.5%).",
        "serving_size": "30g",
        "calories": 545.0,
        "protein": 6.7,
        "carbohydrates": 53.0,
        "total_sugar": 1.0,
        "added_sugar": 0.0,
        "total_fat": 34.0,
        "saturated_fat": 14.2,
        "trans_fat": 0.1,
        "sodium": 580.0,
        "fiber": 3.6,
        "allergens": [],
        "additives": [],
        "data_source": "SafeBite Indian Food Database"
    },

    # ------------------ COLD DRINKS & SODA BRANDS ------------------
    "sprite_lemon_lime": {
        "id": "sprite_lemon_lime",
        "name": "Sprite Lemon-Lime Sparkling Soft Drink",
        "brand": "Coca-Cola",
        "category": "Beverages",
        "barcode": "5449000000453",
        "image_url": "https://images.openfoodfacts.org/images/products/544/900/000/0453/front_en.120.400.jpg",
        "ingredients": "Carbonated Water, Sugar, Acidity Regulators (330, 331), Preservative (211), Flavours (Natural Flavouring Substances).",
        "serving_size": "200ml",
        "calories": 48.0,
        "protein": 0.0,
        "carbohydrates": 11.8,
        "total_sugar": 11.8,
        "added_sugar": 11.8,
        "total_fat": 0.0,
        "saturated_fat": 0.0,
        "trans_fat": 0.0,
        "sodium": 14.0,
        "fiber": 0.0,
        "allergens": [],
        "additives": ["INS 330", "INS 331", "INS 211"],
        "data_source": "SafeBite Indian Food Database"
    },
    "fanta_orange": {
        "id": "fanta_orange",
        "name": "Fanta Orange Carbonated Soft Drink",
        "brand": "Coca-Cola",
        "category": "Beverages",
        "barcode": "5449000011527",
        "image_url": "https://images.openfoodfacts.org/images/products/544/900/001/1527/front_en.145.400.jpg",
        "ingredients": "Carbonated Water, Sugar, Orange Juice from Concentrate, Acidity Regulator (330), Stabilizers (414, 445), Preservative (211), Synthetic Food Colour (110).",
        "serving_size": "200ml",
        "calories": 52.0,
        "protein": 0.0,
        "carbohydrates": 13.0,
        "total_sugar": 13.0,
        "added_sugar": 13.0,
        "total_fat": 0.0,
        "saturated_fat": 0.0,
        "trans_fat": 0.0,
        "sodium": 15.0,
        "fiber": 0.0,
        "allergens": [],
        "additives": ["INS 330", "INS 414", "INS 445", "INS 211", "INS 110 (Sunset Yellow)"],
        "data_source": "SafeBite Indian Food Database"
    },
    "mountain_dew": {
        "id": "mountain_dew",
        "name": "Mountain Dew Citrus Carbonated Drink",
        "brand": "PepsiCo",
        "category": "Beverages",
        "barcode": "8902080000115",
        "image_url": "https://images.openfoodfacts.org/images/products/890/208/000/0115/front_en.18.400.jpg",
        "ingredients": "Carbonated Water, Sugar, Acidity Regulator (330), Caffeine, Preservative (211), Stabilizer (445), Colour (102 Tartrazine).",
        "serving_size": "200ml",
        "calories": 49.0,
        "protein": 0.0,
        "carbohydrates": 12.3,
        "total_sugar": 12.3,
        "added_sugar": 12.3,
        "total_fat": 0.0,
        "saturated_fat": 0.0,
        "trans_fat": 0.0,
        "sodium": 16.0,
        "fiber": 0.0,
        "allergens": [],
        "additives": ["INS 330", "INS 211", "INS 445", "INS 102 (Tartrazine)"],
        "data_source": "SafeBite Indian Food Database"
    },
    "frooti_mango": {
        "id": "frooti_mango",
        "name": "Frooti Fresh 'N' Juicy Mango Drink",
        "brand": "Parle Agro",
        "category": "Beverages",
        "barcode": "8901719111234",
        "image_url": "https://images.openfoodfacts.org/images/products/890/171/911/1234/front_en.14.400.jpg",
        "ingredients": "Water, Mango Pulp (19.5%), Sugar, Acidity Regulator (330), Antioxidant (300), Permitted Class II Preservatives (211, 224).",
        "serving_size": "150ml",
        "calories": 65.0,
        "protein": 0.1,
        "carbohydrates": 16.2,
        "total_sugar": 15.5,
        "added_sugar": 13.5,
        "total_fat": 0.0,
        "saturated_fat": 0.0,
        "trans_fat": 0.0,
        "sodium": 20.0,
        "fiber": 0.2,
        "allergens": ["Sulphites"],
        "additives": ["INS 330", "INS 300", "INS 211", "INS 224"],
        "data_source": "SafeBite Indian Food Database"
    },
    "maaza_mango": {
        "id": "maaza_mango",
        "name": "Maaza Mango Fruit Drink",
        "brand": "Coca-Cola",
        "category": "Beverages",
        "barcode": "8901764023345",
        "image_url": "https://images.openfoodfacts.org/images/products/890/176/402/3345/front_en.12.400.jpg",
        "ingredients": "Water, Alphonso Mango Pulp (19.5%), Sugar, Acidity Regulator (330), Antioxidant (300), Preservative (202).",
        "serving_size": "150ml",
        "calories": 62.0,
        "protein": 0.2,
        "carbohydrates": 15.5,
        "total_sugar": 14.8,
        "added_sugar": 12.8,
        "total_fat": 0.0,
        "saturated_fat": 0.0,
        "trans_fat": 0.0,
        "sodium": 18.0,
        "fiber": 0.3,
        "allergens": [],
        "additives": ["INS 330", "INS 300", "INS 202"],
        "data_source": "SafeBite Indian Food Database"
    },
    "limca_lime": {
        "id": "limca_lime",
        "name": "Limca Lime & Lemoni Fizzy Drink",
        "brand": "Coca-Cola",
        "category": "Beverages",
        "barcode": "8901764034456",
        "image_url": "https://images.openfoodfacts.org/images/products/890/176/403/4456/front_en.10.400.jpg",
        "ingredients": "Carbonated Water, Sugar, Acidity Regulators (330, 331), Stabilizers (414, 471), Preservative (211).",
        "serving_size": "200ml",
        "calories": 44.0,
        "protein": 0.0,
        "carbohydrates": 10.8,
        "total_sugar": 10.5,
        "added_sugar": 10.5,
        "total_fat": 0.0,
        "saturated_fat": 0.0,
        "trans_fat": 0.0,
        "sodium": 12.0,
        "fiber": 0.0,
        "allergens": [],
        "additives": ["INS 330", "INS 331", "INS 414", "INS 471", "INS 211"],
        "data_source": "SafeBite Indian Food Database"
    },
    "red_bull_energy": {
        "id": "red_bull_energy",
        "name": "Red Bull Energy Drink",
        "brand": "Red Bull",
        "category": "Beverages",
        "barcode": "9002490100070",
        "image_url": "https://images.openfoodfacts.org/images/products/900/249/010/0070/front_en.180.400.jpg",
        "ingredients": "Carbonated Water, Sucrose, Glucose, Acidity Regulators (330, 331), Taurine (0.4%), Caffeine (0.03%), Vitamins (Niacin, B6, B12, Pantothenic acid), Colours (Caramel I, Riboflavin).",
        "serving_size": "250ml (1 can)",
        "calories": 45.0,
        "protein": 0.0,
        "carbohydrates": 11.0,
        "total_sugar": 11.0,
        "added_sugar": 11.0,
        "total_fat": 0.0,
        "saturated_fat": 0.0,
        "trans_fat": 0.0,
        "sodium": 40.0,
        "fiber": 0.0,
        "allergens": [],
        "additives": ["INS 330", "INS 331", "INS 150a", "INS 101"],
        "data_source": "SafeBite Indian Food Database"
    },

    # ------------------ MORE BISCUITS & CHOCOLATES ------------------
    "parle_monaco": {
        "id": "parle_monaco",
        "name": "Parle Monaco Classic Salted Crackers",
        "brand": "Parle",
        "category": "Biscuits",
        "barcode": "8901719102035",
        "image_url": "https://images.openfoodfacts.org/images/products/890/171/910/2035/front_en.10.400.jpg",
        "ingredients": "Refined Wheat Flour (Maida 72%), Edible Vegetable Oil (Palm Oil), Sugar, Leavening Agents (503(ii), 500(ii)), Invert Sugar Syrup, Iodized Salt (2.1%), Yeast, Emulsifier (471).",
        "serving_size": "25g",
        "calories": 485.0,
        "protein": 8.0,
        "carbohydrates": 68.5,
        "total_sugar": 8.5,
        "added_sugar": 6.5,
        "total_fat": 20.0,
        "saturated_fat": 9.5,
        "trans_fat": 0.1,
        "sodium": 820.0,
        "fiber": 1.8,
        "allergens": ["Gluten (Wheat)"],
        "additives": ["INS 503(ii)", "INS 500(ii)", "INS 471"],
        "data_source": "SafeBite Indian Food Database"
    },
    "parle_hide_seek": {
        "id": "parle_hide_seek",
        "name": "Parle Hide & Seek Chocolate Chip Biscuits",
        "brand": "Parle",
        "category": "Biscuits",
        "barcode": "8901719103056",
        "image_url": "https://images.openfoodfacts.org/images/products/890/171/910/3056/front_en.12.400.jpg",
        "ingredients": "Refined Wheat Flour (Maida), Chocolate Chips (Sugar, Cocoa Mass, Cocoa Butter, Dextrose, Emulsifier 322), Sugar, Edible Vegetable Oil (Palm Oil), Invert Sugar Syrup, Cocoa Solids, Leavening Agents.",
        "serving_size": "33g",
        "calories": 490.0,
        "protein": 5.8,
        "carbohydrates": 71.0,
        "total_sugar": 32.0,
        "added_sugar": 30.0,
        "total_fat": 20.5,
        "saturated_fat": 10.0,
        "trans_fat": 0.1,
        "sodium": 240.0,
        "fiber": 2.5,
        "allergens": ["Gluten (Wheat)", "Soy"],
        "additives": ["INS 322", "INS 503(ii)", "INS 500(ii)"],
        "data_source": "SafeBite Indian Food Database"
    },
    "cadbury_5_star": {
        "id": "cadbury_5_star",
        "name": "Cadbury 5 Star Chocolate Bar",
        "brand": "Mondelez Cadbury",
        "category": "Chocolates",
        "barcode": "7622201759013",
        "image_url": "https://images.openfoodfacts.org/images/products/762/220/175/9013/front_en.11.400.jpg",
        "ingredients": "Sugar, Liquid Glucose, Milk Solids, Invert Sugar, Hydrogenated Vegetable Fat, Cocoa Butter, Cocoa Solids, Emulsifiers (442, 471), Salt.",
        "serving_size": "20g",
        "calories": 465.0,
        "protein": 4.0,
        "carbohydrates": 73.0,
        "total_sugar": 58.0,
        "added_sugar": 52.0,
        "total_fat": 17.5,
        "saturated_fat": 10.0,
        "trans_fat": 0.1,
        "sodium": 160.0,
        "fiber": 1.5,
        "allergens": ["Milk", "Soy"],
        "additives": ["INS 442", "INS 471"],
        "data_source": "SafeBite Indian Food Database"
    },
    "nestle_munch": {
        "id": "nestle_munch",
        "name": "Nestle Munch Crunchy Wafer Bar",
        "brand": "Nestle",
        "category": "Chocolates",
        "barcode": "8901058862342",
        "image_url": "https://images.openfoodfacts.org/images/products/890/105/886/2342/front_en.9.400.jpg",
        "ingredients": "Sugar, Refined Wheat Flour (Maida), Hydrogenated Vegetable Fats, Milk Solids, Cocoa Solids (3.8%), Emulsifier (Soya Lecithin), Leavening Agent (500(ii)), Salt.",
        "serving_size": "18g",
        "calories": 478.0,
        "protein": 5.0,
        "carbohydrates": 68.0,
        "total_sugar": 44.0,
        "added_sugar": 40.0,
        "total_fat": 20.5,
        "saturated_fat": 12.0,
        "trans_fat": 0.1,
        "sodium": 110.0,
        "fiber": 1.8,
        "allergens": ["Gluten", "Milk", "Soy"],
        "additives": ["INS 322", "INS 500(ii)"],
        "data_source": "SafeBite Indian Food Database"
    },
    "snickers_bar": {
        "id": "snickers_bar",
        "name": "Snickers Peanut Chocolate Bar",
        "brand": "Mars",
        "category": "Chocolates",
        "barcode": "5000159461122",
        "image_url": "https://images.openfoodfacts.org/images/products/500/015/946/1122/front_en.18.400.jpg",
        "ingredients": "Milk Chocolate (Sugar, Cocoa Butter, Cocoa Mass, Skimmed Milk Powder, Lactose), Peanuts (22%), Glucose Syrup, Sugar, Palm Fat, Skimmed Milk Powder, Salt, Egg White Powder.",
        "serving_size": "45g",
        "calories": 488.0,
        "protein": 8.5,
        "carbohydrates": 60.0,
        "total_sugar": 50.0,
        "added_sugar": 42.0,
        "total_fat": 24.0,
        "saturated_fat": 10.5,
        "trans_fat": 0.1,
        "sodium": 220.0,
        "fiber": 2.8,
        "allergens": ["Peanuts", "Milk", "Egg", "Soy"],
        "additives": ["INS 322"],
        "data_source": "SafeBite Indian Food Database"
    },
    "nestle_kitkat": {
        "id": "nestle_kitkat",
        "name": "Nestle KitKat 4-Finger Crisp Wafer Chocolate",
        "brand": "Nestle",
        "category": "Chocolates",
        "barcode": "8901058863648",
        "image_url": "https://images.openfoodfacts.org/images/products/890/105/886/3648/front_en.14.400.jpg",
        "ingredients": "Sugar, Milk Solids, Refined Wheat Flour (Maida), Cocoa Butter, Cocoa Solids, Hydrogenated Vegetable Fats, Emulsifier (Soya lecithin), Yeast, Raising Agent (500(ii)).",
        "serving_size": "37.3g (4 fingers)",
        "calories": 518.0,
        "protein": 7.2,
        "carbohydrates": 64.5,
        "total_sugar": 45.0,
        "added_sugar": 42.0,
        "total_fat": 26.0,
        "saturated_fat": 15.5,
        "trans_fat": 0.1,
        "sodium": 130.0,
        "fiber": 2.1,
        "allergens": ["Gluten", "Milk", "Soy"],
        "additives": ["INS 322", "INS 500(ii)"],
        "data_source": "SafeBite Indian Food Database"
    }
}


# ============================================================================
# Helpers: FSSAI HFSS & Nutrition Analysis
# ============================================================================
def calculate_fssai_warnings(
    category: str,
    sugar: Optional[float],
    saturated_fat: Optional[float],
    sodium: Optional[float],
    trans_fat: Optional[float]
) -> List[str]:
    """
    Evaluates against FSSAI High Fat, Sugar and Salt (HFSS) thresholds.
    """
    warnings: List[str] = []
    is_liquid = category.lower() in ["beverages", "drinks", "juices", "soda", "cold drinks"]

    # 1. Sugar Alert
    if sugar is not None:
        if is_liquid and sugar > 5.0:
            warnings.append(f"⚠️ FSSAI Alert: High Sugar ({sugar:.1f}g/100ml exceeds beverage HFSS limit of 5.0g)")
        elif not is_liquid and sugar > 10.0:
            warnings.append(f"⚠️ FSSAI Alert: High Sugar ({sugar:.1f}g/100g exceeds solid HFSS limit of 10.0g)")

    # 2. Saturated Fat Alert
    if saturated_fat is not None and saturated_fat > 4.0:
        warnings.append(f"⚠️ FSSAI Alert: High Saturated Fat ({saturated_fat:.1f}g/100g exceeds HFSS recommendation)")

    # 3. Trans Fat Alert (FSSAI mandatory cap: <= 2% of total fat)
    if trans_fat is not None and trans_fat > 0.2:
        warnings.append(f"⚠️ FSSAI Warning: Detected Trans Fat ({trans_fat:.2f}g/100g). Limit intake for cardiovascular health.")

    # 4. Sodium / Salt Alert (FSSAI threshold: 600mg sodium / 1.5g salt per 100g in solids)
    if sodium is not None:
        if is_liquid and sodium > 150.0:
            warnings.append(f"⚠️ FSSAI Alert: High Sodium ({sodium:.0f}mg/100ml in liquid product)")
        elif not is_liquid and sodium > 600.0:
            warnings.append(f"⚠️ FSSAI Alert: High Sodium ({sodium:.0f}mg/100g exceeds 600mg daily HFSS ceiling)")

    return warnings


def explain_additives(additives: List[str]) -> List[str]:
    """
    Translates common INS numbers to clear human-readable explanations.
    """
    additive_map = {
        "ins 150d": "INS 150d (Caramel IV - Sulphite Ammonia Caramel): Artificial dark brown coloring.",
        "ins 150c": "INS 150c (Caramel III - Ammonia Caramel): Commercial browning color agent.",
        "ins 621": "INS 621 (Monosodium Glutamate / MSG): Umami flavour enhancer.",
        "ins 627": "INS 627 (Disodium Guanylate): Nucleotide savoury taste enhancer.",
        "ins 631": "INS 631 (Disodium Inosinate): Synergistic savoury taste enhancer.",
        "ins 635": "INS 635 (Disodium 5'-Ribonucleotides): Concentrated flavour enhancer.",
        "ins 330": "INS 330 (Citric Acid): Safe antioxidant and acidity regulator.",
        "ins 338": "INS 338 (Phosphoric Acid): Acidifier in colas that can impact dental enamel with high use.",
        "ins 950": "INS 950 (Acesulfame Potassium): Artificial non-caloric high-intensity sweetener.",
        "ins 955": "INS 955 (Sucralose): Artificial zero-calorie sweetener derived from sugar.",
        "ins 322": "INS 322 (Lecithin): Natural emulsifier aiding texture and blend stability.",
        "ins 471": "INS 471 (Mono- and Diglycerides of Fatty Acids): Plant/oil emulsifier.",
        "ins 500": "INS 500 (Sodium Carbonates): Safe baking soda raising agent.",
        "ins 503": "INS 503 (Ammonium Carbonates): Biscuit raising agent that evaporates on baking.",
    }
    explained: List[str] = []
    for add in additives:
        norm = add.lower().strip()
        matched = False
        for prefix, desc in additive_map.items():
            if prefix in norm:
                explained.append(desc)
                matched = True
                break
        if not matched:
            explained.append(f"{add}: Food additive (emulsifier, regulator, or stabilizer).")
    return explained


def evaluate_personalized_suitability(
    product_dict: Dict[str, Any],
    is_diabetic: bool = False,
    low_sugar: bool = False,
    low_sodium: bool = False,
    is_vegetarian: bool = False,
    is_vegan: bool = False,
    allergen_avoidance: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Evaluates product suitability against user's specific health & dietary profile.
    """
    notes: List[str] = []
    flags: Dict[str, bool] = {
        "diabetic_friendly": True,
        "low_sodium_friendly": True,
        "vegetarian_compatible": True,
        "vegan_compatible": True,
        "allergen_safe": True,
    }

    sug = product_dict.get("total_sugar") or product_dict.get("sugar") or 0.0
    sod = product_dict.get("sodium") or 0.0
    category = product_dict.get("category", "")
    is_beverage = category.lower() in ["beverages", "drinks", "juices", "soda"]
    ingredients = (product_dict.get("ingredients") or "").lower()
    allergens = [a.lower() for a in product_dict.get("allergens", [])]

    # Diabetic / Low Sugar
    if is_diabetic or low_sugar:
        if is_beverage and sug > 4.0:
            flags["diabetic_friendly"] = False
            notes.append(f"Not recommended for diabetics: Contains {sug:.1f}g sugar/100ml which causes rapid glucose spikes.")
        elif not is_beverage and sug > 10.0:
            flags["diabetic_friendly"] = False
            notes.append(f"Not recommended for diabetics: High sugar content ({sug:.1f}g/100g).")
        else:
            notes.append("Moderate/Low sugar content aligns with blood glucose management.")

    # Low Sodium
    if low_sodium:
        if sod > 400.0:
            flags["low_sodium_friendly"] = False
            notes.append(f"Not suitable for low-sodium diets: Contains {sod:.0f}mg sodium per 100g.")
        else:
            notes.append("Acceptable sodium level for blood pressure management.")

    # Vegetarian
    non_veg_keywords = ["chicken", "meat", "pork", "beef", "gelatin", "carmine", "cochineal", "fish", "egg"]
    if is_vegetarian:
        found_non_veg = [kw for kw in non_veg_keywords if kw in ingredients]
        if found_non_veg:
            flags["vegetarian_compatible"] = False
            notes.append(f"Contains non-vegetarian ingredients: {', '.join(found_non_veg)}.")
        else:
            notes.append("Vegetarian friendly based on declared ingredients.")

    # Vegan
    dairy_keywords = ["milk", "cheese", "butter", "paneer", "whey", "casein", "ghee", "honey", "curd"]
    if is_vegan:
        found_dairy = [kw for kw in dairy_keywords if kw in ingredients or any(kw in a for a in allergens)]
        if found_dairy or not flags["vegetarian_compatible"]:
            flags["vegan_compatible"] = False
            notes.append(f"Contains dairy / animal derivatives: {', '.join(found_dairy)}.")
        else:
            notes.append("Vegan friendly based on declared ingredients.")

    # Allergen Avoidance
    if allergen_avoidance:
        detected_allergens: List[str] = []
        for avoid in allergen_avoidance:
            av_clean = avoid.lower().strip()
            if any(av_clean in a for a in allergens) or av_clean in ingredients:
                detected_allergens.append(avoid)
        if detected_allergens:
            flags["allergen_safe"] = False
            notes.append(f"⚠️ Allergen Warning: Contains allergens matching your profile: {', '.join(detected_allergens)}.")
        else:
            notes.append("Free from your flagged allergens based on current label.")

    return {
        "flags": flags,
        "notes": notes,
        "overall_fit": all(flags.values())
    }


# ============================================================================
# OpenFoodFacts API Integration Client
# ============================================================================
OFF_HEADERS = {
    "User-Agent": "SafeBite-ProductSearch/1.0 (contact@safebite.app; Android)"
}

def query_openfoodfacts_search(query: str, page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
    """
    Queries OpenFoodFacts search API with timeout and fallback.
    """
    clean_q = query.strip()
    if not clean_q:
        return []

    endpoints = [
        f"https://in.openfoodfacts.org/cgi/search.pl?search_terms={clean_q}&search_simple=1&action=process&json=1&page_size={page_size}&page={page}",
        f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={clean_q}&search_simple=1&action=process&json=1&page_size={page_size}&page={page}"
    ]

    for ep in endpoints:
        try:
            res = requests.get(ep, headers=OFF_HEADERS, timeout=4.0)
            if res.status_code == 200:
                data = res.json()
                raw_products = data.get("products", [])
                parsed = []
                for p in raw_products:
                    name = p.get("product_name") or p.get("product_name_en")
                    if not name or not name.strip():
                        continue
                    
                    code = str(p.get("code") or p.get("_id") or f"off_{hash(name)}")
                    brand = p.get("brands") or "Packaged Brand"
                    category = (p.get("categories") or "Packaged Food").split(",")[0].strip()
                    img = p.get("image_front_small_url") or p.get("image_url") or p.get("image_front_url")
                    
                    nutriments = p.get("nutriments", {})
                    cal = nutriments.get("energy-kcal_100g")
                    prot = nutriments.get("proteins_100g")
                    carb = nutriments.get("carbohydrates_100g")
                    sug = nutriments.get("sugars_100g")
                    add_sug = nutriments.get("added-sugars_100g")
                    fat = nutriments.get("fat_100g")
                    sat_fat = nutriments.get("saturated-fat_100g")
                    trans_fat = nutriments.get("trans-fat_100g")
                    sod = nutriments.get("sodium_100g")
                    # If sodium in grams, convert to mg
                    if sod is not None and sod <= 50.0:
                        sod = sod * 1000.0
                    fib = nutriments.get("fiber_100g")
                    
                    parsed.append({
                        "id": code,
                        "name": name.strip(),
                        "brand": brand.strip(),
                        "category": category,
                        "barcode": code if code.isdigit() else None,
                        "image_url": img,
                        "ingredients": p.get("ingredients_text") or "",
                        "serving_size": p.get("serving_size") or "100g",
                        "calories": float(cal) if cal is not None else None,
                        "protein": float(prot) if prot is not None else None,
                        "carbohydrates": float(carb) if carb is not None else None,
                        "total_sugar": float(sug) if sug is not None else None,
                        "added_sugar": float(add_sug) if add_sug is not None else None,
                        "total_fat": float(fat) if fat is not None else None,
                        "saturated_fat": float(sat_fat) if sat_fat is not None else None,
                        "trans_fat": float(trans_fat) if trans_fat is not None else None,
                        "sodium": float(sod) if sod is not None else None,
                        "fiber": float(fib) if fib is not None else None,
                        "allergens": [a.replace("en:", "").capitalize() for a in p.get("allergens_tags", []) if isinstance(a, str)],
                        "additives": [ad.replace("en:", "").upper() for ad in p.get("additives_tags", []) if isinstance(ad, str)],
                        "data_source": "OpenFoodFacts Database"
                    })
                return parsed
        except Exception as e:
            logger.warning(f"OpenFoodFacts search endpoint {ep} failed: {e}")
            continue

    return []


def query_openfoodfacts_barcode(barcode: str) -> Optional[Dict[str, Any]]:
    """
    Fetches a single product by barcode from OpenFoodFacts.
    """
    clean_b = barcode.strip()
    candidates = [clean_b]
    if clean_b.startswith("0"):
        candidates.append(clean_b.lstrip("0"))
    else:
        candidates.append("0" + clean_b)

    for code in candidates:
        endpoints = [
            f"https://world.openfoodfacts.org/api/v0/product/{code}.json",
            f"https://in.openfoodfacts.org/api/v0/product/{code}.json"
        ]
        for ep in endpoints:
            try:
                res = requests.get(ep, headers=OFF_HEADERS, timeout=4.0)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("status") == 1 and "product" in data:
                        p = data["product"]
                        name = p.get("product_name") or p.get("product_name_en") or "Packaged Food"
                        nutriments = p.get("nutriments", {})
                        cal = nutriments.get("energy-kcal_100g")
                        prot = nutriments.get("proteins_100g")
                        carb = nutriments.get("carbohydrates_100g")
                        sug = nutriments.get("sugars_100g")
                        add_sug = nutriments.get("added-sugars_100g")
                        fat = nutriments.get("fat_100g")
                        sat_fat = nutriments.get("saturated-fat_100g")
                        trans_fat = nutriments.get("trans-fat_100g")
                        sod = nutriments.get("sodium_100g")
                        if sod is not None and sod <= 50.0:
                            sod = sod * 1000.0
                        fib = nutriments.get("fiber_100g")

                        return {
                            "id": code,
                            "name": name.strip(),
                            "brand": p.get("brands") or "Packaged Brand",
                            "category": (p.get("categories") or "Packaged Food").split(",")[0].strip(),
                            "barcode": code,
                            "image_url": p.get("image_front_url") or p.get("image_url"),
                            "ingredients": p.get("ingredients_text") or "",
                            "serving_size": p.get("serving_size") or "100g",
                            "calories": float(cal) if cal is not None else None,
                            "protein": float(prot) if prot is not None else None,
                            "carbohydrates": float(carb) if carb is not None else None,
                            "total_sugar": float(sug) if sug is not None else None,
                            "added_sugar": float(add_sug) if add_sug is not None else None,
                            "total_fat": float(fat) if fat is not None else None,
                            "saturated_fat": float(sat_fat) if sat_fat is not None else None,
                            "trans_fat": float(trans_fat) if trans_fat is not None else None,
                            "sodium": float(sod) if sod is not None else None,
                            "fiber": float(fib) if fib is not None else None,
                            "allergens": [a.replace("en:", "").capitalize() for a in p.get("allergens_tags", []) if isinstance(a, str)],
                            "additives": [ad.replace("en:", "").upper() for ad in p.get("additives_tags", []) if isinstance(ad, str)],
                            "data_source": "OpenFoodFacts Database"
                        }
            except Exception as e:
                logger.debug(f"OpenFoodFacts barcode {code} ep {ep} failed: {e}")
                continue

    return None


# ============================================================================
# Main Service Implementation
# ============================================================================
class ProductSearchService:
    def __init__(self):
        self._curated = CURATED_PRODUCTS

    def search(
        self,
        query: Optional[str] = None,
        brand: Optional[str] = None,
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> ProductSearchResponse:
        """
        Unified multi-tier product search across Curated Catalog and OpenFoodFacts.
        """
        raw_query = (query or "").strip()
        cache_key = f"q:{raw_query.lower()}|b:{brand or ''}|c:{category or ''}|p:{page}|s:{page_size}"
        cached = _search_cache.get(cache_key)
        if cached:
            return cached

        results: List[Dict[str, Any]] = []
        seen_ids = set()

        q_lower = raw_query.lower()
        q_norm = re.sub(r"[^a-z0-9\s]", "", q_lower).strip()
        q_tokens = q_norm.split()
        if "coke" in q_tokens:
            q_tokens = [t if t != "coke" else "coca" for t in q_tokens]
        if "chips" in q_tokens and "uncle" in q_tokens:
            q_tokens = ["chipps" if t == "chips" else t for t in q_tokens]
        is_barcode_query = raw_query.isdigit() and len(raw_query) in range(8, 15)

        # 1. Search Curated Local Catalog
        with _catalog_lock:
            for pid, prod in self._curated.items():
                prod_norm = re.sub(r"[^a-z0-9\s]", "", f"{prod['name']} {prod.get('brand', '')} {prod.get('category', '')}".lower())
                name_match = all(t in prod_norm for t in q_tokens) if q_tokens else True
                brand_match = (re.sub(r"[^a-z0-9]", "", brand.lower()) in prod_norm) if brand else True
                cat_match = (re.sub(r"[^a-z0-9]", "", category.lower()) in prod_norm) if category else True
                barcode_match = (prod.get("barcode") == raw_query) if is_barcode_query else False

                if (name_match or barcode_match) and brand_match and cat_match:
                    results.append(prod)
                    seen_ids.add(prod["id"])
                    if prod.get("barcode"):
                        seen_ids.add(prod["barcode"])

        # 2. Enrich from OpenFoodFacts if query provided and more items requested
        if q_lower and len(results) < page_size:
            off_results = query_openfoodfacts_search(q_lower, page=page, page_size=page_size)
            for item in off_results:
                item_id = item["id"]
                if item_id not in seen_ids and (item.get("barcode") not in seen_ids if item.get("barcode") else True):
                    # Check brand/category filters
                    if brand and brand.lower() not in item["brand"].lower():
                        continue
                    if category and category.lower() not in item["category"].lower():
                        continue
                    results.append(item)
                    seen_ids.add(item_id)
                    # Cache in-memory for detail retrieval
                    _product_cache[item_id] = item

        # 3. Sort results: Exact/Prefix match on query comes first
        def rank_sort(item: Dict[str, Any]) -> int:
            n = item["name"].lower()
            if n.startswith(q_lower):
                return 0
            if q_lower in n:
                return 1
            if q_lower in item.get("brand", "").lower():
                return 2
            return 3

        if q_lower:
            results.sort(key=rank_sort)

        # 4. Apply pagination
        total = len(results)
        start = (page - 1) * page_size
        end = start + page_size
        paged_items = results[start:end]

        # 5. Build summary objects with calculated health scores
        summary_list: List[ProductSummaryItem] = []
        for item in paged_items:
            cal = item.get("calories") or 0.0
            prot = item.get("protein") or 0.0
            carb = item.get("carbohydrates") or 0.0
            fat = item.get("total_fat") or 0.0
            sug = item.get("total_sugar") or 0.0
            fib = item.get("fiber") or 0.0
            sod = item.get("sodium") or 0.0

            # Calculate Clinical Health Score
            score, classification, _, _, _ = calculate_health_score(
                calories=cal,
                protein=prot,
                carbs=carb,
                fat=fat,
                sugar=sug,
                fiber=fib,
                sodium=sod,
                product_name=item["name"],
                ingredients=item.get("ingredients", "")
            )

            summary_list.append(
                ProductSummaryItem(
                    id=item["id"],
                    name=item["name"],
                    brand=item["brand"],
                    category=item.get("category", "General"),
                    barcode=item.get("barcode"),
                    image_url=item.get("image_url"),
                    thumbnail_url=item.get("image_url"),
                    health_score=round(score, 1),
                    classification=classification,
                    calories=item.get("calories"),
                    sugar=item.get("total_sugar"),
                    protein=item.get("protein"),
                    fat=item.get("total_fat"),
                    sodium=item.get("sodium"),
                    data_source=item.get("data_source", "SafeBite Indian Food Database")
                )
            )

        # Suggestion keywords for search assistance
        suggestions = ["Maggi", "Kurkure", "Lays", "Oreo", "Amul Milk", "Parle-G", "Britannia Bread", "Coca-Cola", "Bournvita"]

        resp = ProductSearchResponse(
            status="success",
            query=raw_query,
            total=total,
            page=page,
            page_size=page_size,
            products=summary_list,
            suggestions=suggestions
        )
        _search_cache.set(cache_key, resp)
        return resp

    def get_detail(self, product_id: str) -> Optional[ProductDetailResponse]:
        """
        Retrieves complete product health details by ID or barcode.
        """
        clean_id = product_id.strip()

        # 1. Check in curated database
        item = self._curated.get(clean_id)
        if not item:
            # Check by barcode in curated database
            for prod in self._curated.values():
                if prod.get("barcode") == clean_id:
                    item = prod
                    break

        # 2. Check in memory cache
        if not item:
            item = _product_cache.get(clean_id)

        # 3. Check OpenFoodFacts
        if not item:
            item = query_openfoodfacts_barcode(clean_id)
            if item:
                _product_cache[clean_id] = item

        if not item:
            return None

        # Extract nutrition
        cal = item.get("calories")
        prot = item.get("protein")
        carb = item.get("carbohydrates")
        sug = item.get("total_sugar")
        add_sug = item.get("added_sugar")
        fat = item.get("total_fat")
        sat_fat = item.get("saturated_fat")
        trans_fat = item.get("trans_fat")
        sod = item.get("sodium")
        fib = item.get("fiber")

        # Check for insufficient data
        is_insufficient = (cal is None and prot is None and fat is None and carb is None)

        # Calculate clinical score
        score, classification, reasons, benefits, concerns = calculate_health_score(
            calories=cal or 0.0,
            protein=prot or 0.0,
            carbs=carb or 0.0,
            fat=fat or 0.0,
            sugar=sug or 0.0,
            fiber=fib or 0.0,
            sodium=sod or 0.0,
            product_name=item["name"],
            ingredients=item.get("ingredients", "")
        )

        fssai_alerts = calculate_fssai_warnings(
            category=item.get("category", "General"),
            sugar=sug,
            saturated_fat=sat_fat,
            sodium=sod,
            trans_fat=trans_fat
        )

        alternatives = get_healthier_alternatives(
            product_name=item["name"],
            classification=classification,
            ingredients=item.get("ingredients", ""),
            calories=cal or 0.0,
            fat=fat or 0.0
        )

        additive_explanations = explain_additives(item.get("additives", []))

        nutrition_per_100g = ProductNutritionValues(
            calories=cal,
            protein=prot,
            carbohydrates=carb,
            total_sugar=sug,
            added_sugar=add_sug,
            total_fat=fat,
            saturated_fat=sat_fat,
            trans_fat=trans_fat,
            sodium=sod,
            fiber=fib
        )

        return ProductDetailResponse(
            status="success",
            id=item["id"],
            name=item["name"],
            brand=item["brand"],
            barcode=item.get("barcode"),
            category=item.get("category", "General"),
            image_url=item.get("image_url"),
            ingredients=item.get("ingredients"),
            serving_size=item.get("serving_size"),
            nutrition_per_100g=nutrition_per_100g,
            allergens=item.get("allergens", []),
            additives=item.get("additives", []),
            additive_details=additive_explanations,
            fssai_warnings=fssai_alerts,
            health_score=round(score, 1) if not is_insufficient else None,
            classification=classification if not is_insufficient else "Unknown",
            positive_points=benefits,
            negative_points=concerns,
            healthier_alternatives=alternatives,
            data_source=item.get("data_source", "SafeBite Indian Food Database"),
            last_updated=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            is_data_insufficient=is_insufficient
        )

    def analyze_health(
        self,
        product_id: str,
        is_diabetic: bool = False,
        low_sugar: bool = False,
        low_sodium: bool = False,
        is_vegetarian: bool = False,
        is_vegan: bool = False,
        allergen_avoidance: Optional[List[str]] = None
    ) -> Optional[ProductHealthAnalysisResponse]:
        """
        Performs full health analysis and evaluates personalized suitability for a given product.
        """
        detail = self.get_detail(product_id)
        if not detail:
            return None

        # Build raw dict for suitability evaluator
        item_dict = {
            "name": detail.name,
            "category": detail.category,
            "ingredients": detail.ingredients,
            "total_sugar": detail.nutrition_per_100g.total_sugar,
            "sodium": detail.nutrition_per_100g.sodium,
            "allergens": detail.allergens
        }

        suitability = evaluate_personalized_suitability(
            item_dict,
            is_diabetic=is_diabetic,
            low_sugar=low_sugar,
            low_sodium=low_sodium,
            is_vegetarian=is_vegetarian,
            is_vegan=is_vegan,
            allergen_avoidance=allergen_avoidance
        )

        return ProductHealthAnalysisResponse(
            status="success",
            product_id=detail.id,
            product_name=detail.name,
            health_score=detail.health_score or 50.0,
            classification=detail.classification or "Moderate",
            positive_points=detail.positive_points,
            negative_points=detail.negative_points,
            fssai_warnings=detail.fssai_warnings,
            additive_information=detail.additive_details,
            allergen_warnings=[f"Contains: {a}" for a in detail.allergens],
            healthier_alternatives=detail.healthier_alternatives,
            personalized_suitability=suitability
        )

    def compare(self, product_ids: List[str]) -> ProductMultiCompareResponse:
        """
        Compares multiple products side-by-side with metric breakdowns and winner selection.
        """
        compare_items: List[ProductCompareItem] = []
        for pid in product_ids[:5]:
            detail = self.get_detail(pid)
            if detail:
                # Calculate favorable points for this product
                favs: List[str] = []
                prot = detail.nutrition_per_100g.protein or 0.0
                sug = detail.nutrition_per_100g.total_sugar or 0.0
                fib = detail.nutrition_per_100g.fiber or 0.0
                sat = detail.nutrition_per_100g.saturated_fat or 0.0
                sod = detail.nutrition_per_100g.sodium or 0.0

                if prot >= 10.0:
                    favs.append(f"High Protein ({prot:.1f}g)")
                if fib >= 5.0:
                    favs.append(f"High Dietary Fiber ({fib:.1f}g)")
                if sug <= 4.0:
                    favs.append(f"Low Sugar ({sug:.1f}g)")
                if sat <= 2.0:
                    favs.append("Low Saturated Fat")
                if sod <= 300.0:
                    favs.append("Low Sodium")

                compare_items.append(
                    ProductCompareItem(
                        id=detail.id,
                        name=detail.name,
                        brand=detail.brand,
                        category=detail.category,
                        image_url=detail.image_url,
                        health_score=detail.health_score or 50.0,
                        classification=detail.classification or "Moderate",
                        calories=detail.nutrition_per_100g.calories,
                        protein=detail.nutrition_per_100g.protein,
                        carbohydrates=detail.nutrition_per_100g.carbohydrates,
                        total_sugar=detail.nutrition_per_100g.total_sugar,
                        total_fat=detail.nutrition_per_100g.total_fat,
                        saturated_fat=detail.nutrition_per_100g.saturated_fat,
                        sodium=detail.nutrition_per_100g.sodium,
                        fiber=detail.nutrition_per_100g.fiber,
                        favorable_points=favs
                    )
                )

        if not compare_items:
            return ProductMultiCompareResponse(
                status="success",
                products=[],
                comparison_summary="No valid products found for comparison.",
                key_differences=[]
            )

        # Identify higher scoring product
        best_product = max(compare_items, key=lambda p: p.health_score)
        diffs: List[str] = []

        if len(compare_items) >= 2:
            p1 = compare_items[0]
            p2 = compare_items[1]
            diffs.append(f"{p1.name} Health Score: {p1.health_score} ({p1.classification}) vs {p2.name}: {p2.health_score} ({p2.classification})")
            
            sug_diff = (p1.total_sugar or 0.0) - (p2.total_sugar or 0.0)
            if abs(sug_diff) >= 2.0:
                lower = p1.name if sug_diff < 0 else p2.name
                diffs.append(f"{lower} has {abs(sug_diff):.1f}g less sugar per 100g.")

            prot_diff = (p1.protein or 0.0) - (p2.protein or 0.0)
            if abs(prot_diff) >= 2.0:
                higher = p1.name if prot_diff > 0 else p2.name
                diffs.append(f"{higher} provides {abs(prot_diff):.1f}g more protein per 100g.")

            sod_diff = (p1.sodium or 0.0) - (p2.sodium or 0.0)
            if abs(sod_diff) >= 100.0:
                lower_sod = p1.name if sod_diff < 0 else p2.name
                diffs.append(f"{lower_sod} contains {abs(sod_diff):.0f}mg less sodium.")

        summary = f"{best_product.name} presents the more nutritionally favorable profile with a score of {best_product.health_score}/100."

        return ProductMultiCompareResponse(
            status="success",
            products=compare_items,
            healthier_choice_id=best_product.id,
            healthier_choice_name=best_product.name,
            comparison_summary=summary,
            key_differences=diffs
        )

    def admin_add(self, req: AdminAddProductRequest) -> ProductDetailResponse:
        """
        Adds or updates a custom product in the curated database.
        """
        pid = req.id or f"custom_{re.sub(r'[^a-zA-Z0-9]', '_', req.name.lower())}_{int(time.time())}"
        new_prod = {
            "id": pid,
            "name": req.name.strip(),
            "brand": req.brand.strip(),
            "category": req.category,
            "barcode": req.barcode.strip() if req.barcode else None,
            "image_url": req.image_url,
            "ingredients": req.ingredients or "",
            "serving_size": req.serving_size or "100g",
            "calories": req.calories,
            "protein": req.protein,
            "carbohydrates": req.carbohydrates,
            "total_sugar": req.total_sugar,
            "added_sugar": req.added_sugar,
            "total_fat": req.total_fat,
            "saturated_fat": req.saturated_fat,
            "trans_fat": req.trans_fat,
            "sodium": req.sodium,
            "fiber": req.fiber,
            "allergens": req.allergens or [],
            "additives": req.additives or [],
            "data_source": "Admin Ingested Product"
        }

        with _catalog_lock:
            self._curated[pid] = new_prod
            if new_prod.get("barcode"):
                self._curated[new_prod["barcode"]] = new_prod

        return self.get_detail(pid)


# Singleton Service Instance
product_search_service = ProductSearchService()
