import pytest

from mixology import to_ml

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
    
