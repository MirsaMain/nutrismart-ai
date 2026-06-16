import pytest
from src.models.interpretation import classify_risk_score


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0, "Rendah"),
        (39.99, "Rendah"),
        (40, "Sedang"),
        (69.99, "Sedang"),
        (70, "Tinggi"),
        (100, "Tinggi"),
    ],
)
def test_classify_risk_score(score, expected):
    assert classify_risk_score(score) == expected


def test_invalid_risk_score():
    with pytest.raises(ValueError):
        classify_risk_score(101)
