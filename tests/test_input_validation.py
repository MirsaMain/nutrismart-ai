import pytest

from src.data.validator import validate_positive_number


def test_validate_positive_number():
    validate_positive_number(10, "Nilai")


def test_validate_positive_number_error():
    with pytest.raises(ValueError):
        validate_positive_number(0, "Nilai")
