import pytest

from mixology import to_ml, normalize_unit, scale, match_score, suggest

def test_normalize_unit():
    assert normalize_unit("1 ml") == (1, "ml")
    assert normalize_unit("2 oz") == (2, "oz")
    assert normalize_unit("1/2 tbsp") == (0.5, "tbsp")

def test_ml_is_unchanged():
    assert to_ml(1) == 1
    assert to_ml(0.5) == 0.5
    assert to_ml(0) == 0
    assert to_ml(-1) == -1


def test_ounces_to_ml():
    assert to_ml(1, 'oz') == 29.5735
    assert to_ml(2, 'oz') == 59.147
    assert to_ml(0.5, 'oz') == 14.78675


def test_tablespoons_to_ml():
    assert to_ml(1, 'tbsp') == 14.7868
    assert to_ml(2, 'tbsp') == 29.5736
    assert to_ml(0.5, 'tbsp') == 7.3934


def test_zero_and_negative_values():
    assert to_ml(0, 'oz') == 0
    assert to_ml(-1, 'tbsp') == -14.7868
    assert to_ml(-2, 'oz') == -59.147


def test_piece_cant_be_converted():
    with pytest.raises(ValueError):
        to_ml(1, 'piece')


def test_unknown_unit_raises_value_error():
    with pytest.raises(ValueError):
        to_ml(1, 'unknown_unit')


def test_plain_number_with_unit():
    assert normalize_unit("1 ml") == (1, "ml")
    assert normalize_unit("2.5 oz") == (2.5, "oz")
    assert normalize_unit("-3 tbsp") == (-3, "tbsp")


def test_mixed_fraction_with_unit():
    assert normalize_unit("1 1/2 oz") == (1.5, "oz")


def test_simple_fraction_with_unit():
    assert normalize_unit("1/4 tsp") == (0.25, "tsp")
    assert normalize_unit("3/4 dash") == (0.75, "dash")


def test_unicode_fraction_with_unit():
    assert normalize_unit("½ oz") == (0.5, "oz")
    assert normalize_unit("⅓ tbsp") == (0.333333, "tbsp")
    assert normalize_unit("¾ tsp") == (0.75, "tsp")


def test_plural_units():
    assert normalize_unit("2 ounces") == (2, "oz")
    assert normalize_unit("3 tablespoons") == (3, "tbsp")
    assert normalize_unit("4 teaspoons") == (4, "tsp")
    assert normalize_unit("5 dashes") == (5, "dash")


def test_missing_unit_defaults_to_piece():
    assert normalize_unit("1") == (1, "piece")
    assert normalize_unit("2") == (2, "piece")
    assert normalize_unit("3") == (3, "piece")


def test_missing_quantity_defaults_to_one():
    assert normalize_unit("ml") == (1, "ml")
    assert normalize_unit("oz") == (1, "oz")
    assert normalize_unit("tbsp") == (1, "tbsp")
    assert normalize_unit("tsp") == (1, "tsp")
    assert normalize_unit("dash") == (1, "dash")


def test_normalize_unknown_unit_raises_value_error():
    with pytest.raises(ValueError):
        normalize_unit("3 gallons")


def test_empty_or_none_input_raises_value_error():
    with pytest.raises(ValueError):
        normalize_unit("")
    with pytest.raises(ValueError):
        normalize_unit(None)


def test_scale_double():
    assert scale([("1 oz", "2 oz"), ("1 tbsp", "2 tbsp")], 2) == [("2 oz", "4 oz"), ("2 tbsp", "4 tbsp")]


def test_scale_half():
    assert scale([("1 oz", "2 oz"), ("1 tbsp", "2 tbsp")], 0.5) == [("0.5 oz", "1 oz"), ("0.5 tbsp", "1 tbsp")]


def test_scale_by_one_is_unchanged():
    assert scale([("1 oz", "2 oz"), ("1 tbsp", "2 tbsp")], 1) == [("1 oz", "2 oz"), ("1 tbsp", "2 tbsp")]


def test_scale_empty_list():
    assert scale([], 2) == []


def test_scale_rounds_float_values():
    assert scale([("1/3 oz", "2/3 oz")], 3) == [("1 oz", "2 oz")]


def test_scale_keeps_units():
    assert scale([("1 oz", "2 oz"), ("1 tbsp", "2 tbsp")], 2) == [("2 oz", "4 oz"), ("2 tbsp", "4 tbsp")]


def test_scale_zero_factor():
    with pytest.raises(ValueError):
        scale([("1 oz", "2 oz")], 0)


def test_scale_negative_factor():
    with pytest.raises(ValueError):
        scale([("1 oz", "2 oz")], -1)


def test_scale_does_not_modify_original_list():
    original = [("1 oz", "2 oz"), ("1 tbsp", "2 tbsp")]
    scaled = scale(original, 2)
    assert original == [("1 oz", "2 oz"), ("1 tbsp", "2 tbsp")]
    assert scaled == [("2 oz", "4 oz"), ("2 tbsp", "4 tbsp")]


def test_match_score_all_available():
    assert match_score(["Gin", "Lemon Juice"], ["Gin", "Lemon Juice"]) == 2.0


def test_match_score_half_available():
    assert match_score(["Gin", "Lemon Juice"], ["Gin", "Simple Syrup"]) == 1.0

def test_match_score_none_available():
    assert match_score(["Gin", "Lemon Juice"], ["Simple Syrup", "Water"]) == 0.0


def test_match_score_empty_available():
    assert match_score(["Gin", "Lemon Juice"], []) == 0.0


def test_match_score_ignores_case_and_spaces():
    assert match_score(["Gin", "Lemon Juice"], ["gin", "lemon juice"]) == 2.0
    assert match_score(["Gin", "Lemon Juice"], ["  gin  ", "  lemon juice  "]) == 2.0


def test_match_score_ignores_duplicates_in_available():
    assert match_score(["Gin", "Lemon Juice"], ["Gin", "Gin", "Lemon Juice"]) == 2.0


def test_match_score_empty_recipe_ingredients():
    with pytest.raises(ValueError):
        match_score([], ["Gin", "Lemon Juice"])


def test_match_score_extra_available_ingredients():
    assert match_score(["Gin", "Lemon Juice"], ["Gin", "Lemon Juice", "Simple Syrup"]) == 2.0


def test_suggest_sorts_by_match_ratio():
    cocktail = [
        {"name": "  Mojito  ", "ingredients": ["Gin", "Lemon Juice"]},
        {"name": "Margarita", "ingredients": ["Tequila", "Lime Juice"]}
    ]
    assert suggest(cocktail, ["Gin", "Lemon Juice"]) == [
        ("  Mojito  ", 1.0),
        ("Margarita", 0.0)
    ]


def test_suggest_limits_results():
    cocktail = [
        {"name": "Mojito", "ingredients": ["Gin", "Lemon Juice"]},
        {"name": "Margarita", "ingredients": ["Tequila", "Lime Juice"]},
        {"name": "Daiquiri", "ingredients": ["Rum", "Lime Juice"]}
    ]
    assert suggest(cocktail, ["Gin", "Lemon Juice"], limit=2) == [
        ("Mojito", 1.0),
        ("Margarita", 0.0)
    ]


def test_suggest_limit_larger_than_results():
    cocktail = [
        {"name": "Mojito", "ingredients": ["Gin", "Lemon Juice"]},
        {"name": "Margarita", "ingredients": ["Tequila", "Lime Juice"]}
    ]
    assert suggest(cocktail, ["Gin", "Lemon Juice"], limit=5) == [
        ("Mojito", 1.0),
        ("Margarita", 0.0)
    ]


def test_suggest_empty_cocktail_list():
    assert suggest([], ["Gin", "Lemon Juice"]) == []


def test_suggest_skips_cocktails_with_no_ingredients():
    cocktail = [
        {"name": "Mojito", "ingredients": ["Gin", "Lemon Juice"]},
        {"name": "Mystery Cocktail", "ingredients": []}
    ]
    assert suggest(cocktail, ["Gin", "Lemon Juice"]) == [
        ("Mojito", 1.0)
    ]


def test_suggest_zero_match_ratio():
    cocktail = [
        {"name": "Margarita", "ingredients": ["Tequila", "Lime Juice"]}
    ]
    assert suggest(cocktail, ["Gin", "Lemon Juice"]) == [
        ("Margarita", 0.0)
    ]        