import pytest

from src.features.bmi import calculate_bmi, classify_bmi


def test_calculate_bmi():
    assert calculate_bmi(65, 165) == pytest.approx(23.88, abs=0.01)


def test_classify_bmi_normal():
    assert classify_bmi(23.0) == "Normal"


def test_invalid_weight():
    with pytest.raises(ValueError):
        calculate_bmi(0, 165)
