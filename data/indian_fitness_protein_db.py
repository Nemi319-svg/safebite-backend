"""
SafeBite Indian High-Protein, Fitness & Post-Workout Recovery Food Database
============================================================================
Author: Vaibhav112027 <vaibhavv1239@gmail.com>

Provides protein bioavailability (PDCAAS), Leucine muscle-synthesis trigger levels,
cost-efficiency (INR per 10g protein), and complementary amino acid pairing rules
for authentic Indian vegetarian and non-vegetarian protein sources:
- Dairy & Cultured (Paneer, Hung Curd, Whey, Skimmed Milk)
- Legumes & Pulses (Soya Chunks, Roasted Chana, Sattu, Moong Dal, Rajma, Kala Chana)
- Seeds & Nuts (Pumpkin Seeds, Peanuts, Hemp Hearts, Chia, Almonds)
- Eggs & Lean Meats (Boiled Egg Whites, Chicken Breast, Rohu Fish)
"""

from typing import Dict, List, Optional, Any


INDIAN_FITNESS_PROTEIN_DB: Dict[str, Dict[str, Any]] = {
    "soya_chunks_nutrela": {
        "food_id": "soya_chunks_nutrela",
        "name": "Textured Soy Chunks (Boiled / Nutri Nugget)",
        "category": "Plant Protein Powerhouse",
        "serving_size_dry_g": 50.0,
        "calories": 172.0,
        "protein_g": 26.0,
        "carbs_g": 16.5,
        "fat_g": 0.3,
        "fiber_g": 6.5,
        "leucine_g": 2.1,
        "pdcaas_score": 0.99,
        "inr_per_10g_protein": 4.2,
        "is_vegetarian": True,
        "is_vegan": True,
        "health_score": 90,
        "amino_acid_notes": "Complete plant protein (PDCAAS 0.99) rich in all 9 essential amino acids.",
        "best_indian_pairing": "Soya Keema Matar or Soya Pulao with bell peppers and ginger-garlic.",
        "myth_buster": "Moderate intake (50g dry chunks/day) has zero estrogenic harm in healthy adults."
    },
    "low_fat_paneer": {
        "food_id": "low_fat_paneer",
        "name": "Low-Fat Paneer (Skimmed Milk Cottage Cheese)",
        "category": "Dairy Casein Protein",
        "serving_size_dry_g": 100.0,
        "calories": 185.0,
        "protein_g": 21.5,
        "carbs_g": 3.5,
        "fat_g": 9.0,
        "fiber_g": 0.0,
        "leucine_g": 2.0,
        "pdcaas_score": 1.00,
        "inr_per_10g_protein": 18.5,
        "is_vegetarian": True,
        "is_vegan": False,
        "health_score": 88,
        "amino_acid_notes": "Slow-digesting Casein protein; ideal for overnight muscle repair at dinner.",
        "best_indian_pairing": "Tandoori Paneer Tikka or Palak Paneer with minimal oil.",
        "myth_buster": "Standard full-fat paneer has 22-25g fat; low-fat paneer halves calories while retaining 21g+ protein."
    },
    "roasted_sattu_flour": {
        "food_id": "roasted_sattu_flour",
        "name": "Desi Sattu (Roasted Bengal Gram Flour)",
        "category": "Budget Plant Protein",
        "serving_size_dry_g": 50.0,
        "calories": 188.0,
        "protein_g": 11.2,
        "carbs_g": 31.0,
        "fat_g": 2.5,
        "fiber_g": 8.4,
        "leucine_g": 0.85,
        "pdcaas_score": 0.78,
        "inr_per_10g_protein": 6.0,
        "is_vegetarian": True,
        "is_vegan": True,
        "health_score": 92,
        "amino_acid_notes": "Slightly low in methionine; combine with whole wheat or rice for complete amino profile.",
        "best_indian_pairing": "Sattu Paratha or Chilled Namkeen Sattu Sharbat with lemon and black salt.",
        "myth_buster": "Most affordable high-fiber natural protein shake in India at ~Rs 6 per 10g protein."
    },
    "greek_yogurt_hung_curd": {
        "food_id": "greek_yogurt_hung_curd",
        "name": "Strained Hung Curd (Desi Chakka / Greek Yogurt)",
        "category": "Probiotic Dairy Protein",
        "serving_size_dry_g": 150.0,
        "calories": 145.0,
        "protein_g": 14.5,
        "carbs_g": 6.2,
        "fat_g": 6.5,
        "fiber_g": 0.0,
        "leucine_g": 1.45,
        "pdcaas_score": 1.00,
        "inr_per_10g_protein": 21.0,
        "is_vegetarian": True,
        "is_vegan": False,
        "health_score": 94,
        "amino_acid_notes": "Contains both fast whey and slow casein fractions with live probiotics.",
        "best_indian_pairing": "Use as high-protein dip with cucumber sticks or mix with roasted flaxseeds.",
        "myth_buster": "Regular watery dahi only has ~3.5g protein per 100g; straining whey concentrates protein by 2.5x."
    },
    "sprouted_moong_dal_bowl": {
        "food_id": "sprouted_moong_dal_bowl",
        "name": "Sprouted Whole Green Moong Salad",
        "category": "Enzyme-Active Legume",
        "serving_size_dry_g": 100.0,
        "calories": 112.0,
        "protein_g": 8.2,
        "carbs_g": 19.5,
        "fat_g": 0.6,
        "fiber_g": 5.8,
        "leucine_g": 0.62,
        "pdcaas_score": 0.76,
        "inr_per_10g_protein": 11.0,
        "is_vegetarian": True,
        "is_vegan": True,
        "health_score": 95,
        "amino_acid_notes": "Sprouting breaks down phytic acid, boosting mineral and amino acid digestibility.",
        "best_indian_pairing": "Steam lightly for 3 minutes and toss with chopped tomatoes, onion, lemon, and chaat masala.",
        "myth_buster": "Light steaming eliminates gas-causing lectins while preserving 95% Vitamin C."
    },
    "whole_eggs_boiled": {
        "food_id": "whole_eggs_boiled",
        "name": "Boiled Whole Eggs (2 Large Eggs)",
        "category": "Reference Gold-Standard Protein",
        "serving_size_dry_g": 100.0,
        "calories": 148.0,
        "protein_g": 12.6,
        "carbs_g": 0.8,
        "fat_g": 10.2,
        "fiber_g": 0.0,
        "leucine_g": 1.12,
        "pdcaas_score": 1.00,
        "inr_per_10g_protein": 11.5,
        "is_vegetarian": False,
        "is_vegan": False,
        "health_score": 93,
        "amino_acid_notes": "Biological Value (BV) 100; gold standard for amino acid digestibility and choline.",
        "best_indian_pairing": "Egg Bhurji with multigrain roti or boiled eggs with black pepper & rock salt.",
        "myth_buster": "1-2 whole eggs daily do not adversely spike blood cholesterol in healthy individuals."
    },
    "grilled_chicken_breast": {
        "food_id": "grilled_chicken_breast",
        "name": "Tandoori / Grilled Skinless Chicken Breast",
        "category": "Lean Poultry Protein",
        "serving_size_dry_g": 100.0,
        "calories": 165.0,
        "protein_g": 31.0,
        "carbs_g": 0.0,
        "fat_g": 3.6,
        "fiber_g": 0.0,
        "leucine_g": 2.45,
        "pdcaas_score": 1.00,
        "inr_per_10g_protein": 14.0,
        "is_vegetarian": False,
        "is_vegan": False,
        "health_score": 95,
        "amino_acid_notes": "Highest leucine-per-calorie density (2.45g leucine per 100g) for muscle protein synthesis.",
        "best_indian_pairing": "Marinate in dahi, turmeric, ginger-garlic, and roast on tawa/air-fryer.",
        "myth_buster": "Dry-rubbed tandoori chicken breast has zero saturated butter fat unlike Butter Chicken gravy."
    },
    "roasted_chana_black": {
        "food_id": "roasted_chana_black",
        "name": "Roasted Black Gram (Bhuna Kala Chana)",
        "category": "Crunchy Snack Protein",
        "serving_size_dry_g": 50.0,
        "calories": 180.0,
        "protein_g": 10.2,
        "carbs_g": 29.0,
        "fat_g": 2.6,
        "fiber_g": 7.8,
        "leucine_g": 0.74,
        "pdcaas_score": 0.78,
        "inr_per_10g_protein": 7.5,
        "is_vegetarian": True,
        "is_vegan": True,
        "health_score": 91,
        "amino_acid_notes": "High resistant starch + slow release energy ideal for pre-workout or 5 PM hunger.",
        "best_indian_pairing": "Pair with 1 glass masala chaas or a handful of roasted peanuts.",
        "myth_buster": "Superior Indian snack replacing deep-fried packaged potato chips."
    },
    "pumpkin_seeds_roasted": {
        "food_id": "pumpkin_seeds_roasted",
        "name": "Roasted Pumpkin Seeds (Kaddu Ke Beej)",
        "category": "Seed & Zinc Protein",
        "serving_size_dry_g": 30.0,
        "calories": 168.0,
        "protein_g": 9.1,
        "carbs_g": 3.2,
        "fat_g": 14.2,
        "fiber_g": 1.8,
        "leucine_g": 0.72,
        "pdcaas_score": 0.90,
        "inr_per_10g_protein": 24.0,
        "is_vegetarian": True,
        "is_vegan": True,
        "health_score": 93,
        "amino_acid_notes": "Rich in magnesium, zinc, and tryptophan supporting recovery and deep sleep.",
        "best_indian_pairing": "Sprinkle over morning oats, dal, or curd.",
        "myth_buster": "Gram-for-gram contains more protein (30g/100g) than almonds (21g/100g) with much lower oxalates."
    },
    "rohu_fish_curry_light": {
        "food_id": "rohu_fish_curry_light",
        "name": "Rohu / Surmai Fish (Light Mustard Curry or Grilled)",
        "category": "Omega-3 Lean Fish",
        "serving_size_dry_g": 120.0,
        "calories": 158.0,
        "protein_g": 22.8,
        "carbs_g": 2.0,
        "fat_g": 6.2,
        "fiber_g": 0.5,
        "leucine_g": 1.88,
        "pdcaas_score": 1.00,
        "inr_per_10g_protein": 16.0,
        "is_vegetarian": False,
        "is_vegan": False,
        "health_score": 94,
        "amino_acid_notes": "Rapidly absorbed marine protein rich in EPA/DHA anti-inflammatory Omega-3 fats.",
        "best_indian_pairing": "Steamed mustard-turmeric fish (Bhapa Maach) with brown rice.",
        "myth_buster": "Light steaming or pan-grilling preserves delicate Omega-3 fatty acids destroyed by deep frying."
    }
}


def get_protein_food_profile(food_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves protein bioavailability and cost efficiency data for a fitness food."""
    return INDIAN_FITNESS_PROTEIN_DB.get(food_id.lower().strip())


def get_best_budget_veg_proteins(max_inr_per_10g: float = 15.0) -> List[Dict[str, Any]]:
    """Returns budget-friendly vegetarian high-protein Indian foods sorted by cost efficiency."""
    matches = [
        item for item in INDIAN_FITNESS_PROTEIN_DB.values()
        if item["is_vegetarian"] and item["inr_per_10g_protein"] <= max_inr_per_10g
    ]
    return sorted(matches, key=lambda x: x["inr_per_10g_protein"])
