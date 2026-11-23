"""
SafeBite - Allergy and Ingredient Intelligence Service

Provides comprehensive allergen and ingredient detection for Indian and international foods.
Includes support for:
- 14 major allergen classes with bilingual (English + Indian culinary terms) synonym matching.
- Hidden derivatives (whey, casein, maltodextrin, lecithin, semolina, maida, etc.).
- Confirmed vs. Possible (may contain / shared equipment) classification.
- Incomplete / unreadable ingredient list detection.
- Personalized cross-referencing against user allergen profiles and custom ingredient exclusions.
- Mandatory legal and safety disclaimers (never claim 100% allergen-free).
"""

from typing import List, Optional, Tuple, Set, Dict, Any
import re
try:
    from models import AllergenAlertItem
except ImportError:
    from backend.models import AllergenAlertItem

ALLERGEN_FREE_DISCLAIMER: str = (
    "The absence of an allergen alert does not guarantee a product is 100% allergen-free. "
    "Cross-contamination may occur during manufacturing or food handling. Always inspect original packaging."
)

# Canonical Allergen Definitions with Indian & International Synonyms
ALLERGEN_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "Peanuts": {
        "label": "Peanut / Groundnut",
        "synonyms": [
            "peanut", "peanuts", "groundnut", "groundnuts", "monkey nut", "monkey nuts",
            "arachis", "arachis hypogaea", "moongphali", "mungfali", "singdana",
            "peanut butter", "peanut oil", "peanut flour", "mixed nuts"
        ]
    },
    "Tree Nuts": {
        "label": "Tree Nuts",
        "synonyms": [
            "tree nut", "tree nuts", "almond", "almonds", "badam", "cashew", "cashews", "kaju",
            "walnut", "walnuts", "akhrot", "pistachio", "pistachios", "pista", "hazelnut",
            "hazelnuts", "macadamia", "pecan", "pecans", "brazil nut", "brazil nuts",
            "pine nut", "pine nuts", "chilgoza", "chestnut", "chestnuts", "cashew nut"
        ]
    },
    "Dairy": {
        "label": "Milk & Dairy",
        "synonyms": [
            "milk", "dairy", "doodh", "dahi", "curd", "curds", "yogurt", "yoghurt",
            "paneer", "cheese", "cheddar", "mozzarella", "butter", "makhan", "ghee",
            "cream", "malai", "whey", "whey protein", "casein", "caseinate",
            "calcium caseinate", "sodium caseinate", "lactose", "lactalbumin",
            "milk solids", "skimmed milk powder", "skim milk powder", "whole milk powder",
            "khoya", "mawa", "buttermilk", "chhas", "condensed milk", "cottage cheese"
        ]
    },
    "Gluten / Wheat": {
        "label": "Wheat & Gluten",
        "synonyms": [
            "refined wheat flour", "whole wheat flour", "wheat flour", "wheat", "gehu",
            "maida", "atta", "suji", "sooji", "rava", "semolina", "spelt", "barley",
            "jau", "rye", "vital wheat gluten", "gluten", "durum", "couscous", "farina",
            "triticale", "barley malt", "malt extract", "malt"
        ]
    },
    "Soy": {
        "label": "Soy / Soya",
        "synonyms": [
            "soy", "soya", "soybean", "soybeans", "edamame", "tofu", "soya chunks",
            "soy lecithin", "soya lecithin", "lecithin (ins 322)", "lecithin (e322)",
            "ins 322", "e322", "hydrolyzed soy protein", "soy sauce", "soya sauce",
            "soya flour", "textured vegetable protein", "tvp"
        ]
    },
    "Eggs": {
        "label": "Egg",
        "synonyms": [
            "egg", "eggs", "anda", "albumin", "albumen", "egg white", "egg yolk",
            "ovalbumin", "ovomucoid", "lysozyme", "lecithin (egg)", "meringue", "mayonnaise"
        ]
    },
    "Fish": {
        "label": "Fish",
        "synonyms": [
            "fish", "machhli", "machli", "salmon", "tuna", "cod", "tilapia", "anchovy",
            "anchovies", "gelatin (fish)", "fish gelatin", "surimi", "isinglass",
            "pomfret", "rohu", "katla"
        ]
    },
    "Shellfish": {
        "label": "Shellfish & Crustaceans",
        "synonyms": [
            "shellfish", "crustacean", "crustaceans", "mollusc", "molluscs", "shrimp",
            "shrimps", "prawn", "prawns", "jhinga", "crab", "kekda", "lobster",
            "clam", "clams", "mussel", "mussels", "oyster", "oysters", "squid",
            "calamari", "octopus"
        ]
    },
    "Sesame": {
        "label": "Sesame",
        "synonyms": [
            "sesame", "sesame seeds", "til", "gingelly", "tahini", "benne", "sesame oil"
        ]
    },
    "Mustard": {
        "label": "Mustard",
        "synonyms": [
            "mustard", "mustard seeds", "rai", "sarson", "kasundi", "mustard oil"
        ]
    },
    "Sulfites": {
        "label": "Sulfites",
        "synonyms": [
            "sulfite", "sulphite", "sulfites", "sulphites", "sulfur dioxide", "sulphur dioxide",
            "sodium metabisulfite", "sodium metabisulphite", "potassium metabisulphite",
            "ins 220", "ins 221", "ins 222", "ins 223", "ins 224", "ins 225", "ins 226", "ins 227", "ins 228",
            "e220", "e221", "e222", "e223", "e224", "e225", "e226", "e227", "e228"
        ]
    },
    "Celery": {
        "label": "Celery",
        "synonyms": ["celery", "celeriac", "celery seed", "celery salt"]
    },
    "Lupin": {
        "label": "Lupin",
        "synonyms": ["lupin", "lupine", "lupin flour"]
    }
}

# Common Industrial Additives & Exclusions
COMMON_EXCLUSIONS: Dict[str, Dict[str, Any]] = {
    "Palm Oil": {
        "label": "Palm Oil",
        "synonyms": [
            "fractionated palm oil", "refined palm oil", "edible vegetable oil (palm)",
            "vegetable fat (palm)", "palm kernel oil", "palm oil", "palmitate", "palmolein"
        ]
    },
    "High Fructose Corn Syrup": {
        "label": "High Fructose Corn Syrup / HFCS",
        "synonyms": ["high fructose corn syrup", "glucose-fructose syrup", "corn syrup", "hfcs"]
    },
    "Monosodium Glutamate": {
        "label": "MSG / Monosodium Glutamate",
        "synonyms": [
            "monosodium glutamate", "flavor enhancer 621", "flavour enhancer 621",
            "ajinomoto", "ins 621", "e621", "msg"
        ]
    },
    "Artificial Sweeteners": {
        "label": "Artificial Sweeteners",
        "synonyms": [
            "acesulfame potassium", "acesulfame k", "ins 950", "e950",
            "aspartame", "ins 951", "e951", "sucralose", "ins 955", "e955",
            "saccharin", "ins 954", "e954", "neotame", "ins 961", "e961"
        ]
    },
    "Artificial Colors": {
        "label": "Synthetic Food Dyes",
        "synonyms": [
            "sunset yellow", "ins 110", "e110", "tartrazine", "ins 102", "e102", "yellow 5",
            "carmoisine", "ins 122", "e122", "allura red", "ins 129", "e129",
            "brilliant blue", "ins 133", "e133", "ponceau 4r", "ins 124", "e124",
            "erythrosine", "ins 127", "e127"
        ]
    }
}

# Precautionary cross-contamination indicator regex
PRECAUTIONARY_PATTERN = re.compile(
    r"(?:may contain|manufactured (?:in|on)|processed (?:in|on)|shared equipment|traces of|facility that also processes|packaged in a facility)",
    re.IGNORECASE
)

# Text truncation / partial OCR indicators
PARTIAL_INDICATORS = [
    r"\.\.\.$",
    r",\s*$",
    r"and\s*$",
    r"\[(?:cut off|partial|unreadable|truncated)\]",
    r"contains other",
    r"etc\.\s*$"
]


def determine_ingredient_completeness(
    ingredients_text: Optional[str],
    analysis_mode: str = "packaged"
) -> str:
    """
    Evaluates whether an ingredient list appears complete, partial, unreadable, or unavailable.
    """
    if analysis_mode == "food_object":
        return "complete"

    if not ingredients_text or not ingredients_text.strip():
        return "unavailable"

    clean = ingredients_text.strip()
    clean_lower = clean.lower()

    if clean_lower in ["unreadable", "unknown", "n/a", "none"]:
        return "unreadable"

    if len(clean) < 15:
        return "partial"

    for pattern in PARTIAL_INDICATORS:
        if re.search(pattern, clean_lower):
            return "partial"

    return "complete"


def _normalize_tokens(text: str) -> str:
    """Cleans delimiters to space-padded punctuation for accurate whole-word/phrase regex matching."""
    cleaned = re.sub(r"[\(\)\[\]\{\}\:\;\,\.\/\-\_\+\*]", " ", text.lower())
    return " " + " ".join(cleaned.split()) + " "


def _split_phrases(text: str) -> List[Tuple[str, bool]]:
    """
    Splits text into clauses and identifies whether clause contains precautionary language ('may contain').
    Returns list of (clause_text, is_precautionary).
    """
    sentences = re.split(r"[.;]", text)
    result = []
    for s in sentences:
        s_clean = s.strip()
        if not s_clean:
            continue
        is_precautionary = bool(PRECAUTIONARY_PATTERN.search(s_clean))
        result.append((s_clean, is_precautionary))
    return result


def _map_user_preference_to_allergens(user_pref: str) -> Set[str]:
    """
    Maps user-stated allergy/preference strings to canonical taxonomy keys.
    e.g. 'nut allergy' -> {'Peanuts', 'Tree Nuts'}, 'lactose' -> {'Dairy'}.
    """
    pref = user_pref.lower().strip()
    matched_keys = set()

    if any(w in pref for w in ["nut", "nuts", "peanut", "groundnut", "badam", "kaju", "almond", "cashew"]):
        if "peanut" in pref or "groundnut" in pref:
            matched_keys.add("Peanuts")
        elif "tree nut" in pref:
            matched_keys.add("Tree Nuts")
        else:
            matched_keys.add("Peanuts")
            matched_keys.add("Tree Nuts")

    if any(w in pref for w in ["dairy", "lactose", "milk", "cheese", "paneer", "whey", "casein"]):
        matched_keys.add("Dairy")

    if any(w in pref for w in ["gluten", "celiac", "wheat", "maida", "atta", "sooji", "rava"]):
        matched_keys.add("Gluten / Wheat")

    if any(w in pref for w in ["soy", "soya"]):
        matched_keys.add("Soy")

    if any(w in pref for w in ["egg", "eggs", "anda"]):
        matched_keys.add("Eggs")

    if any(w in pref for w in ["fish", "salmon", "machli", "machhli"]):
        matched_keys.add("Fish")

    if any(w in pref for w in ["shellfish", "shrimp", "prawn", "crab", "lobster", "crustacean"]):
        matched_keys.add("Shellfish")

    if any(w in pref for w in ["sesame", "til"]):
        matched_keys.add("Sesame")

    if any(w in pref for w in ["mustard", "sarson", "rai"]):
        matched_keys.add("Mustard")

    if any(w in pref for w in ["sulfite", "sulphite", "sulfur dioxide"]):
        matched_keys.add("Sulfites")

    return matched_keys


def _filter_redundant_terms(terms: List[str]) -> List[str]:
    """
    Removes substrings if a more specific/longer matched term is already present.
    e.g. if 'refined wheat flour' is present, remove 'wheat' and 'wheat flour'.
    """
    sorted_terms = sorted(list(set(terms)), key=len, reverse=True)
    kept = []
    for t in sorted_terms:
        if not any(t != other and t in other for other in kept):
            kept.append(t)
    return sorted(kept)


def assess_allergies_and_ingredients(
    ingredients_text: Optional[str] = "",
    declared_allergens: Optional[List[str]] = None,
    user_allergens: Optional[str] = "",
    user_exclusions: Optional[str] = "",
    product_name: str = "",
    analysis_mode: str = "packaged"
) -> Tuple[List[AllergenAlertItem], str, str]:
    """
    Main evaluation pipeline.
    Returns:
        (allergy_alerts: List[AllergenAlertItem],
         ingredient_completeness: str,
         allergen_free_disclaimer: str)
    """
    completeness = determine_ingredient_completeness(ingredients_text, analysis_mode)

    # 1. Parse user preferences
    active_user_allergen_categories: Set[str] = set()
    user_allergen_raw_tokens: List[str] = []
    if user_allergens:
        for raw_item in re.split(r"[,;/]", user_allergens):
            item = raw_item.strip().lower()
            if not item:
                continue
            user_allergen_raw_tokens.append(item)
            active_user_allergen_categories.update(_map_user_preference_to_allergens(item))

    user_exclusion_tokens: List[str] = []
    if user_exclusions:
        for raw_item in re.split(r"[,;/]", user_exclusions):
            item = raw_item.strip().lower()
            if item:
                user_exclusion_tokens.append(item)

    full_text = f"{product_name} {ingredients_text or ''}".strip()
    norm_text = _normalize_tokens(full_text)
    clauses = _split_phrases(full_text)

    # Buckets: category -> match_type -> list of matched terms
    category_matches: Dict[str, Dict[str, List[str]]] = {}

    def add_match(category: str, match_type: str, term: str):
        if category not in category_matches:
            category_matches[category] = {"confirmed": [], "possible": []}
        category_matches[category][match_type].append(term)

    # 2. Check explicitly declared allergens
    if declared_allergens:
        for da in declared_allergens:
            da_clean = str(da).strip()
            if not da_clean:
                continue
            da_lower = da_clean.lower()
            matched_cat = None
            for cat_name, cat_data in ALLERGEN_TAXONOMY.items():
                if any(syn in da_lower for syn in cat_data["synonyms"]):
                    matched_cat = cat_name
                    break
            category = matched_cat or da_clean.title()
            add_match(category, "confirmed", da_clean)

    # 3. Check ingredients text against allergen taxonomy
    for cat_name, cat_data in ALLERGEN_TAXONOMY.items():
        for syn in cat_data["synonyms"]:
            pattern = rf"\b{re.escape(syn)}\b"
            if re.search(pattern, norm_text):
                is_precautionary = False
                for clause_text, prec in clauses:
                    if re.search(pattern, clause_text.lower()):
                        if prec:
                            is_precautionary = True
                            break
                match_type = "possible" if is_precautionary else "confirmed"
                add_match(cat_name, match_type, syn)

    # 4. Check Common Exclusions
    for ex_name, ex_data in COMMON_EXCLUSIONS.items():
        for syn in ex_data["synonyms"]:
            pattern = rf"\b{re.escape(syn)}\b"
            if re.search(pattern, norm_text):
                is_precautionary = False
                for clause_text, prec in clauses:
                    if re.search(pattern, clause_text.lower()):
                        if prec:
                            is_precautionary = True
                            break
                match_type = "possible" if is_precautionary else "confirmed"
                add_match(ex_name, match_type, syn)

    # 5. Check Custom Ad-Hoc Exclusions
    for ut in user_exclusion_tokens:
        if any(ut in ex_data["synonyms"] for ex_data in COMMON_EXCLUSIONS.values()):
            continue
        pattern = rf"\b{re.escape(ut)}\b"
        if re.search(pattern, norm_text):
            add_match("Excluded Ingredient", "confirmed", ut)

    # Build final consolidated alert items
    alerts: List[AllergenAlertItem] = []

    for cat_name, match_dict in category_matches.items():
        for match_type in ["confirmed", "possible"]:
            raw_terms = match_dict[match_type]
            if not raw_terms:
                continue
            filtered_terms = _filter_redundant_terms(raw_terms)
            terms_display = ", ".join(filtered_terms)

            # Check if this category or matched term triggers a user profile match
            is_allergen_user_match = (cat_name in active_user_allergen_categories) or any(
                any(ut in t.lower() for ut in user_allergen_raw_tokens) for t in filtered_terms
            )

            cat_synonyms = COMMON_EXCLUSIONS.get(cat_name, {}).get("synonyms", [])
            is_exclusion_user_match = any(
                ut in cat_name.lower() or any(ut == s or ut in s for s in cat_synonyms) or any(ut in t.lower() for t in filtered_terms)
                for ut in user_exclusion_tokens
            )

            is_user_match = is_allergen_user_match or is_exclusion_user_match

            if is_user_match:
                severity = "critical"
                if is_allergen_user_match:
                    if match_type == "confirmed":
                        msg = f"CRITICAL: Contains '{terms_display}', which directly violates your {cat_name} allergy profile!"
                    else:
                        msg = f"CRITICAL CAUTION: May contain traces of '{terms_display}', matching your {cat_name} allergy profile!"
                else:
                    msg = f"CRITICAL: Contains '{terms_display}', matching your exclusion preference for {cat_name}!"
            else:
                if match_type == "confirmed":
                    severity = "warning"
                    msg = f"Contains {cat_name}: {terms_display}"
                else:
                    severity = "info"
                    msg = f"May contain traces of {cat_name}: {terms_display}"

            alerts.append(
                AllergenAlertItem(
                    name=cat_name,
                    match_type=match_type,
                    matched_term=terms_display,
                    is_user_allergy=is_user_match,
                    severity=severity,
                    message=msg
                )
            )

    severity_order = {"critical": 0, "warning": 1, "info": 2}
    alerts.sort(key=lambda a: severity_order.get(a.severity, 3))

    return alerts, completeness, ALLERGEN_FREE_DISCLAIMER
