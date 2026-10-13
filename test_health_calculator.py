import pytest
from health_calculator import calculate_health_score, get_healthier_alternatives

def test_natural_peanut_butter_healthy():
    score, classification, reasons, benefits, concerns = calculate_health_score(
        calories=625.0,
        protein=30.0,
        carbs=18.0,
        fat=50.0,
        sugar=4.0,
        fiber=8.0,
        sodium=10.0,
        product_name="Pintola All Natural Peanut Butter Crunchy",
        ingredients="100% Roasted Peanuts"
    )
    assert classification == "Healthy"
    assert score >= 88.0
    assert any("plant protein" in b.lower() for b in benefits)
    assert any("unsaturated" in b.lower() or "oleic" in b.lower() or "mufa" in b.lower() for b in benefits)
    assert len(concerns) == 0

def test_sweetened_peanut_spread_unhealthy():
    score, classification, reasons, benefits, concerns = calculate_health_score(
        calories=600.0,
        protein=20.0,
        carbs=30.0,
        fat=45.0,
        sugar=28.0,
        fiber=4.0,
        sodium=200.0,
        product_name="Sweetened Peanut Butter Spread",
        ingredients="Peanuts, sugar, hydrogenated vegetable oil, salt"
    )
    assert classification == "Unhealthy"
    assert any("hydrogenated" in c.lower() or "sugar" in c.lower() for c in concerns)

def test_peanut_butter_alternatives():
    alts = get_healthier_alternatives(
        product_name="Pintola All Natural Peanut Butter",
        classification="Healthy",
        ingredients="100% Roasted Peanuts",
        calories=625.0,
        fat=50.0
    )
    assert len(alts) > 0
    assert any("peanut butter" in a.lower() or "almond butter" in a.lower() for a in alts)
    assert not any("chutney" in a.lower() or "salsa" in a.lower() for a in alts)

def test_cold_drink_unhealthy_with_hydrating_swaps():
    score, classification, reasons, benefits, concerns = calculate_health_score(
        calories=44.0,
        protein=0.0,
        carbs=11.0,
        fat=0.0,
        sugar=11.0,
        product_name="Coca Cola",
        ingredients="Carbonated water, sugar, caramel iv, phosphoric acid, caffeine"
    )
    assert classification == "Unhealthy"
    assert score < 30.0
    
    alts = get_healthier_alternatives(
        product_name="Coca Cola",
        classification="Unhealthy"
    )
    assert any("nariyal pani" in a.lower() or "chaas" in a.lower() or "nimbu soda" in a.lower() for a in alts)

def test_raw_almonds_healthy():
    score, classification, reasons, benefits, concerns = calculate_health_score(
        calories=579.0,
        protein=21.0,
        carbs=22.0,
        fat=50.0,
        sugar=4.0,
        fiber=12.0,
        product_name="California Raw Almonds Badam",
        ingredients="Whole Raw Almonds"
    )
    assert classification == "Healthy"
    assert score >= 88.0

def test_fresh_apple_healthy():
    score, classification, reasons, benefits, concerns = calculate_health_score(
        calories=52.0,
        protein=0.3,
        carbs=13.8,
        fat=0.2,
        sugar=10.4,
        fiber=2.4,
        sodium=1.0,
        product_name="Fresh Red Apple (Seb)",
        ingredients="100% Raw Apple"
    )
    assert classification == "Healthy"
    assert score >= 90.0
    assert any("fruit" in b.lower() or "fiber" in b.lower() for b in benefits)
    assert len(concerns) == 0

    alts = get_healthier_alternatives("Fresh Apple", "Healthy")
    assert len(alts) > 0
    assert any("peanut butter" in a.lower() or "almond" in a.lower() or "fiber" in a.lower() for a in alts)

def test_potato_chips_piece_unhealthy():
    score, classification, reasons, benefits, concerns = calculate_health_score(
        calories=536.0,
        protein=7.0,
        carbs=53.0,
        fat=34.0,
        sugar=0.5,
        fiber=3.0,
        sodium=550.0,
        product_name="Fried Potato Chips Piece",
        ingredients="Potatoes, Refined Palm Oil, Iodized Salt"
    )
    assert classification == "Unhealthy"
    assert score < 40.0
    assert any("palm oil" in c.lower() or "sodium" in c.lower() or "fat" in c.lower() for c in concerns)

    alts = get_healthier_alternatives("Potato Chips", "Unhealthy")
    assert any("makhana" in a.lower() or "popcorn" in a.lower() for a in alts)
