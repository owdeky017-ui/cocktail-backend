import pytest

from mixology import to_ml, normalize_unit

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
    
