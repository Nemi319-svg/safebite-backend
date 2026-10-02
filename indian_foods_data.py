from typing import List, Dict, Any

INDIAN_FOOD_DATASET: List[Dict[str, Any]] = [
    {
        "name": "Dal Tadka (Yellow Lentils)",
        "calories": 160.0,
        "protein": 8.5,
        "carbs": 24.0,
        "fat": 4.0,
        "fiber": 6.0,
        "sugar": 1.5,
        "sodium": 320.0,
        "category": "Lentils & Curries"
    },
    {
        "name": "Roti (Whole Wheat Chapati)",
        "calories": 104.0,
        "protein": 3.4,
        "carbs": 22.0,
        "fat": 0.5,
        "fiber": 3.2,
        "sugar": 0.2,
        "sodium": 120.0,
        "category": "Breads"
    },
    {
        "name": "Poha (Flattened Rice with Veggies)",
        "calories": 180.0,
        "protein": 4.0,
        "carbs": 33.0,
        "fat": 3.8,
        "fiber": 2.5,
        "sugar": 1.2,
        "sodium": 280.0,
        "category": "Breakfast"
    },
    {
        "name": "Idli (Steamed Rice & Urad Cake - 2 pcs)",
        "calories": 130.0,
        "protein": 4.5,
        "carbs": 26.0,
        "fat": 0.8,
        "fiber": 2.0,
        "sugar": 0.5,
        "sodium": 190.0,
        "category": "Breakfast"
    },
    {
        "name": "Plain Dosa",
        "calories": 168.0,
        "protein": 3.9,
        "carbs": 29.0,
        "fat": 3.7,
        "fiber": 1.8,
        "sugar": 0.6,
        "sodium": 240.0,
        "category": "Breakfast"
    },
    {
        "name": "Masala Dosa with Potato Filling",
        "calories": 280.0,
        "protein": 6.0,
        "carbs": 42.0,
        "fat": 10.0,
        "fiber": 3.5,
        "sugar": 1.8,
        "sodium": 420.0,
        "category": "Breakfast"
    },
    {
        "name": "Paneer Tikka (Grilled Cottage Cheese)",
        "calories": 240.0,
        "protein": 16.0,
        "carbs": 7.0,
        "fat": 17.0,
        "fiber": 2.0,
        "sugar": 2.0,
        "sodium": 350.0,
        "category": "Dairy & Appetizers"
    },
    {
        "name": "Palak Paneer",
        "calories": 220.0,
        "protein": 11.5,
        "carbs": 9.0,
        "fat": 16.0,
        "fiber": 4.2,
        "sugar": 2.2,
        "sodium": 380.0,
        "category": "Curries"
    },
    {
        "name": "Steamed Basmati Rice (1 cup cooked)",
        "calories": 205.0,
        "protein": 4.2,
        "carbs": 45.0,
        "fat": 0.5,
        "fiber": 0.8,
        "sugar": 0.1,
        "sodium": 5.0,
        "category": "Grains & Rice"
    },
    {
        "name": "Brown Rice (1 cup cooked)",
        "calories": 218.0,
        "protein": 4.5,
        "carbs": 45.8,
        "fat": 1.6,
        "fiber": 3.5,
        "sugar": 0.3,
        "sodium": 2.0,
        "category": "Grains & Rice"
    },
    {
        "name": "Rajma Masala (Red Kidney Beans Curry)",
        "calories": 210.0,
        "protein": 9.0,
        "carbs": 32.0,
        "fat": 5.5,
        "fiber": 8.0,
        "sugar": 2.5,
        "sodium": 390.0,
        "category": "Curries"
    },
    {
        "name": "Chole Masala (Chickpeas Curry)",
        "calories": 240.0,
        "protein": 10.0,
        "carbs": 36.0,
        "fat": 7.0,
        "fiber": 9.0,
        "sugar": 3.0,
        "sodium": 420.0,
        "category": "Curries"
    },
    {
        "name": "Vegetable Biryani",
        "calories": 290.0,
        "protein": 6.5,
        "carbs": 48.0,
        "fat": 9.0,
        "fiber": 4.0,
        "sugar": 2.8,
        "sodium": 460.0,
        "category": "Grains & Rice"
    },
    {
        "name": "Upma (Semolina Savory Porridge)",
        "calories": 195.0,
        "protein": 4.8,
        "carbs": 34.0,
        "fat": 4.5,
        "fiber": 2.8,
        "sugar": 1.0,
        "sodium": 310.0,
        "category": "Breakfast"
    },
    {
        "name": "Moong Dal Khichdi",
        "calories": 175.0,
        "protein": 7.0,
        "carbs": 30.0,
        "fat": 3.0,
        "fiber": 4.0,
        "sugar": 1.0,
        "sodium": 260.0,
        "category": "Main Course"
    },
    {
        "name": "Dhokla (Steamed Gram Flour Cakes - 2 pcs)",
        "calories": 150.0,
        "protein": 6.0,
        "carbs": 23.0,
        "fat": 3.5,
        "fiber": 2.5,
        "sugar": 3.0,
        "sodium": 340.0,
        "category": "Snacks"
    },
    {
        "name": "Samosa (1 piece fried)",
        "calories": 262.0,
        "protein": 3.5,
        "carbs": 32.0,
        "fat": 14.0,
        "fiber": 2.0,
        "sugar": 1.5,
        "sodium": 410.0,
        "category": "Snacks"
    },
    {
        "name": "Spiced Buttermilk (Chaas - 1 glass)",
        "calories": 45.0,
        "protein": 3.0,
        "carbs": 4.5,
        "fat": 1.5,
        "fiber": 0.2,
        "sugar": 3.5,
        "sodium": 180.0,
        "category": "Beverages"
    }
]

def search_indian_food(query: str) -> List[Dict[str, Any]]:
    """Filters dishes by name or category containing the query string."""
    q = query.strip().lower()
    if not q:
        return INDIAN_FOOD_DATASET[:10]
    return [
        dish for dish in INDIAN_FOOD_DATASET
        if q in dish["name"].lower() or q in (dish.get("category") or "").lower()
    ]
