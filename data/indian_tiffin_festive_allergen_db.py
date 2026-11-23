"""
SafeBite Indian Tiffin & Festive Food Allergen Cross-Contamination Database
============================================================================
Author: Vaibhav112027 <vaibhavv1239@gmail.com>

Provides detailed allergen profiling, hidden Indian ingredient alerts, and
shared-facility cross-contamination analysis for Indian tiffin meals, snacks,
and festive sweets (Diwali, Holi, Navratri, daily lunchboxes):
- Confirms primary allergens (Dairy, Gluten/Wheat, Peanuts, Tree Nuts, Sesame, Mustard, Soy)
- Exposes hidden Indian culinary traps:
  * Commercial Hing (Asafoetida) typically contains 60-70% wheat maida/starch
  * Besan (Gram flour) and Rice flour often share grinding mills with wheat
  * Halwai sweets share ghee/milk kaddhais with cashews, pistachios, and peanuts
  * South Indian tadka & street chutneys commonly contain hidden peanuts/urad dal
- Recommends safe allergen-free homemade Indian substitutions.
"""

from typing import Dict, List, Optional, Any


INDIAN_TIFFIN_FESTIVE_DB: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # 1. DAILY TIFFIN & LUNCHBOX ITEMS (टिफिन और लंचबॉक्स)
    # =========================================================================
    "aloo_paratha_butter": {
        "item_id": "aloo_paratha_butter",
        "name": "Aloo Paratha with Butter & Curd",
        "category": "Daily Tiffin",
        "confirmed_allergens": ["Gluten (Wheat)", "Milk (Butter, Ghee, Curd)"],
        "hidden_cross_contamination": [
            "Store-bought chaat masala or paratha masala may contain compounded Hing (wheat-based)"
        ],
        "severity_risk": "high_for_celiac_and_dairy",
        "safe_substitutes": {
            "Gluten (Wheat)": "Make Aloo Paratha using 100% Rajgira (Amaranth) or Singhora/Buckwheat (Kuttu) flour",
            "Milk (Butter, Ghee, Curd)": "Brush with cold-pressed sesame or mustard oil and pair with coconut yogurt"
        },
        "clinical_note": "Standard wheat paratha contains high gluten. Dairy-free version requires oil instead of butter/ghee."
    },
    "kanda_poha_peanuts": {
        "item_id": "kanda_poha_peanuts",
        "name": "Kanda Poha (Flattened Rice with Peanuts & Hing Tadka)",
        "category": "Daily Tiffin",
        "confirmed_allergens": ["Peanuts", "Mustard"],
        "hidden_cross_contamination": [
            "CRITICAL FOR CELIAC: Commercial powdered Hing (asafoetida) used in tadka is compounded with wheat flour!",
            "Sev topping added at stalls is fried in shared peanut/cottonseed oil"
        ],
        "severity_risk": "high_for_peanut_and_gluten",
        "safe_substitutes": {
            "Peanuts": "Replace peanuts with roasted pumpkin seeds, sunflower seeds, or roasted chana dal",
            "Gluten (Wheat)": "Verify pure gluten-free Hing (compounded with rice flour/gum arabic) or omit Hing"
        },
        "clinical_note": "Rice poha is naturally gluten-free, making it a popular tiffin choice—just avoid wheat-compounded hing and peanuts."
    },
    "khaman_dhokla": {
        "item_id": "khaman_dhokla",
        "name": "Gujarati Khaman Dhokla (Steamed Chickpea Cake)",
        "category": "Daily Tiffin",
        "confirmed_allergens": ["Mustard", "Sesame (Tadka)"],
        "hidden_cross_contamination": [
            "Commercial Besan (gram flour) is frequently cross-contaminated with wheat in shared stone mills",
            "Sweet shops add compounded Hing (wheat gluten) in tempering",
            "Some instant dhokla mixes contain Sooji (wheat semolina)"
        ],
        "severity_risk": "moderate_hidden_gluten",
        "safe_substitutes": {
            "Gluten (Wheat)": "Use certified gluten-free single-mill besan and omit wheat-based hing",
            "Sesame": "Temper purely with mustard seeds, curry leaves, and green chilies"
        },
        "clinical_note": "Great steamed protein snack, but verify besan purity and absence of sooji for strict celiac safety."
    },
    "idli_sambar_chutney": {
        "item_id": "idli_sambar_chutney",
        "name": "Steamed Idli with Sambar & White Coconut Chutney",
        "category": "Daily Tiffin",
        "confirmed_allergens": ["Mustard", "Urad Dal (Legume)"],
        "hidden_cross_contamination": [
            "HIDDEN PEANUT TRAP: Many restaurant/canteen white chutneys blend roasted peanuts with coconut to thicken and cut cost!",
            "Sambar masala & sambar tadka almost universally use wheat-compounded Hing!"
        ],
        "severity_risk": "high_hidden_peanut_and_hing",
        "safe_substitutes": {
            "Peanuts": "Prepare pure coconut + roasted chana dal chutney at home without groundnuts",
            "Gluten (Wheat)": "Use homemade sambar powder and rice-flour-compounded Hing"
        },
        "clinical_note": "Idli itself is naturally dairy-free, nut-free, and gluten-free—cross-contamination comes strictly from chutney and sambar tadka."
    },
    "sabudana_khichdi": {
        "item_id": "sabudana_khichdi",
        "name": "Sabudana Khichdi (Tapioca Pearls with Crushed Peanuts)",
        "category": "Fasting / Tiffin",
        "confirmed_allergens": ["Peanuts", "Milk (if cooked in Ghee)"],
        "hidden_cross_contamination": [
            "Prepared with crushed roasted peanuts as primary binding ingredient"
        ],
        "severity_risk": "critical_for_peanut_allergy",
        "safe_substitutes": {
            "Peanuts": "Replace crushed peanuts with coarsely crushed roasted makhana (foxnuts) or sunflower seeds",
            "Milk": "Cook in cold-pressed groundnut/sesame oil instead of ghee"
        },
        "clinical_note": "100% naturally gluten-free, but dangerous for peanut-allergic individuals unless peanuts are omitted."
    },
    "pav_bhaji_tiffin": {
        "item_id": "pav_bhaji_tiffin",
        "name": "Mumbai Pav Bhaji (Buttered Bread Rolls + Veg Mash)",
        "category": "Evening Tiffin",
        "confirmed_allergens": ["Gluten (Wheat Pav)", "Milk (Heavy Butter)", "Soy (Commercial bread improvers)"],
        "hidden_cross_contamination": [
            "Commercial pav buns frequently contain milk powder, whey, and soy flour",
            "Vendor griddles (tawa) are used continuously with large slabs of salted butter"
        ],
        "severity_risk": "high_for_dairy_and_gluten",
        "safe_substitutes": {
            "Gluten (Wheat)": "Serve the vegetable bhaji over steamed rice or with gluten-free millet bhakri",
            "Milk": "Cook bhaji with cold-pressed olive or mustard oil instead of butter"
        },
        "clinical_note": "Vegetable bhaji alone is safe once cooked without butter; the pav bun is the primary gluten/soy/dairy carrier."
    },
    "rajma_chawal_tiffin": {
        "item_id": "rajma_chawal_tiffin",
        "name": "Punjabi Rajma Chawal (Red Kidney Beans & Basmati Rice)",
        "category": "Daily Tiffin",
        "confirmed_allergens": ["Legumes (Red Kidney Beans)"],
        "hidden_cross_contamination": [
            "Restaurant rajma frequently adds cream, butter, or hing (wheat-based)"
        ],
        "severity_risk": "low_for_major_allergens",
        "safe_substitutes": {
            "Milk": "Skip cream/butter garnish; use pure tomato-onion-ginger masala base",
            "Gluten (Wheat)": "Omit commercial hing"
        },
        "clinical_note": "One of the safest allergen-friendly complete protein Indian lunchbox meals when made at home."
    },

    # =========================================================================
    # 2. FESTIVE SWEETS & MITHAI (त्योहारी मिठाइयाँ)
    # =========================================================================
    "kaju_katli": {
        "item_id": "kaju_katli",
        "name": "Kaju Katli (Cashew Fudge with Silver Vark)",
        "category": "Festive Mithai",
        "confirmed_allergens": ["Tree Nuts (Cashew)"],
        "hidden_cross_contamination": [
            "Halwai kitchens process almonds, pistachios, walnuts, peanuts, and milk khoya on identical marble slabs",
            "Cheaper commercial kaju katli mixes peanut paste or milk powder as adulterants"
        ],
        "severity_risk": "critical_anaphylaxis_tree_nut",
        "safe_substitutes": {
            "Tree Nuts": "Make Sunflower Seed Katli or Roasted Pumpkin Seed Barfi (identical fudge texture, zero tree nuts!)",
            "Peanuts": "Prepare strictly at home with whole single-origin cashews if only peanut-allergic"
        },
        "clinical_note": "Severe anaphylaxis trigger for tree-nut and peanut allergic children during Diwali."
    },
    "besan_ladoo": {
        "item_id": "besan_ladoo",
        "name": "Desi Ghee Besan Ladoo (with Cardamom & Nuts)",
        "category": "Festive Mithai",
        "confirmed_allergens": ["Milk (Desi Ghee)", "Tree Nuts (Almond/Pistachio garnish)"],
        "hidden_cross_contamination": [
            "Halwais frequently mix wheat rava/sooji into besan ladoo for grainy crunch (HIDDEN GLUTEN!)",
            "Shared grinding mills contaminate chickpea besan with wheat"
        ],
        "severity_risk": "high_dairy_nut_and_hidden_gluten",
        "safe_substitutes": {
            "Milk": "Roast besan slowly in cold-pressed coconut oil instead of ghee",
            "Gluten (Wheat)": "Use certified gluten-free coarse besan; never add sooji",
            "Tree Nuts": "Garnish with roasted melon seeds (magaj) or pumpkin seeds"
        },
        "clinical_note": "Melon seeds (magaj) are a classic safe seed alternative to chopped pistachios/almonds in ladoos."
    },
    "motichoor_ladoo": {
        "item_id": "motichoor_ladoo",
        "name": "Motichoor Boondi Ladoo",
        "category": "Festive Mithai",
        "confirmed_allergens": ["Milk (Ghee)", "Tree Nuts (Pistachio/Cashew)", "Synthetic Dyes (E102/E110)"],
        "hidden_cross_contamination": [
            "Commercial boondi is fried in shared oil vats containing wheat samosas, kachoris, and peanuts",
            "Contains synthetic azo food colors Tartrazine (E102) & Sunset Yellow (E110) which trigger pseudo-allergic hives"
        ],
        "severity_risk": "high_cross_contamination",
        "safe_substitutes": {
            "Gluten & Nuts": "Prepare boondi at home using pure besan, saffron (kesar) for natural color, and melon seeds"
        },
        "clinical_note": "High risk of wheat and nut cross-contact at commercial sweet counters."
    },
    "gulab_jamun": {
        "item_id": "gulab_jamun",
        "name": "Khoya Gulab Jamun (Milk Solids Dumplings in Syrup)",
        "category": "Festive Mithai",
        "confirmed_allergens": ["Milk (Khoya/Mawa & Paneer)", "Gluten (Maida binding flour)", "Tree Nuts (Pistachio stuffing)"],
        "hidden_cross_contamination": [
            "Deep fried in shared ghee/oil containing gluten snacks",
            "Commercial mawa is frequently blended with soy milk powder or starch"
        ],
        "severity_risk": "critical_dairy_and_gluten",
        "safe_substitutes": {
            "Gluten (Wheat)": "Bind homemade khoya using potato starch or arrowroot flour instead of maida",
            "Milk": "Switch to dairy-free Sweet Potato / Coconut Ladoo"
        },
        "clinical_note": "Triple allergen threat (Dairy + Gluten + Nuts) in traditional commercial form."
    },
    "gujiya_holi": {
        "item_id": "gujiya_holi",
        "name": "Holi Mawa Gujiya (Deep-Fried Pastry)",
        "category": "Festive Mithai",
        "confirmed_allergens": ["Gluten (Maida shell)", "Milk (Khoya/Mawa stuffing)", "Tree Nuts (Almonds, Cashews, Pistachios)"],
        "hidden_cross_contamination": [
            "Suji (wheat semolina) is mixed inside the mawa filling"
        ],
        "severity_risk": "critical_gluten_dairy_nuts",
        "safe_substitutes": {
            "Tree Nuts & Dairy": "Stuff with roasted dry coconut, organic jaggery, and cardamom; bake instead of frying"
        },
        "clinical_note": "Combines refined gluten shell with concentrated dairy and mixed tree nuts."
    },
    "rasmalai": {
        "item_id": "rasmalai",
        "name": "Bengali Rasmalai (Chhena Discs in Saffron Milk)",
        "category": "Festive Mithai",
        "confirmed_allergens": ["Milk (Chhena & Thickened Rabri)", "Tree Nuts (Pistachio & Almond slivers)"],
        "hidden_cross_contamination": [
            "Some commercial recipes dust chhena balls with cornstarch or maida for binding"
        ],
        "severity_risk": "critical_dairy_and_nuts",
        "safe_substitutes": {
            "Milk": "Prepare Coconut Milk Rasmalai using tofu/almond-milk curdled chhena (if not nut-allergic) or coconut cream rabri"
        },
        "clinical_note": "Pure milk concentrate; unsafe for even mild lactose/casein sensitivities."
    },

    # =========================================================================
    # 3. INDIAN SAVORY SNACKS & NAMKEEN (नमकीन)
    # =========================================================================
    "poha_chivda_mix": {
        "item_id": "poha_chivda_mix",
        "name": "Diwali Roasted Poha Chivda Mix",
        "category": "Festive Namkeen",
        "confirmed_allergens": ["Peanuts", "Tree Nuts (Cashews)", "Mustard", "Sesame"],
        "hidden_cross_contamination": [
            "Uses Hing (wheat-compounded) in tempering",
            "Packaged chivda manufactured on lines processing wheat sev and soy snacks"
        ],
        "severity_risk": "high_peanut_and_cashew",
        "safe_substitutes": {
            "Peanuts & Tree Nuts": "Roast thin poha with dry coconut slices, curry leaves, roasted chana dal, and pumpkin seeds"
        },
        "clinical_note": "Easy to customize at home into a top-8 allergen-free crunchy snack."
    },
    "bhakarwadi_snack": {
        "item_id": "bhakarwadi_snack",
        "name": "Maharashtrian Crispy Bhakarwadi",
        "category": "Savory Snack",
        "confirmed_allergens": ["Gluten (Maida & Besan)", "Sesame Seeds (Til)", "Poppy Seeds (Khuskhus)"],
        "hidden_cross_contamination": [
            "Fried on shared commercial lines with peanuts and cashews"
        ],
        "severity_risk": "high_gluten_and_sesame",
        "safe_substitutes": {
            "Gluten & Sesame": "Opt for roasted rice-flour chakli made with cumin seeds instead of sesame"
        },
        "clinical_note": "Sesame is a potent top-9 allergen heavily concentrated inside Bhakarwadi spice filling."
    }
}


def get_tiffin_festive_profile(item_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves allergen & cross-contamination profile for an Indian tiffin or festive food."""
    return INDIAN_TIFFIN_FESTIVE_DB.get(item_id.lower().strip())


def list_all_tiffin_items() -> List[Dict[str, Any]]:
    """Returns all items in the tiffin & festive allergen database."""
    return list(INDIAN_TIFFIN_FESTIVE_DB.values())
