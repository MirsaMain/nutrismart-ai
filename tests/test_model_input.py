import pytest
from src.features.input_schema import MODEL_FEATURES
from src.models.inference import build_model_input


def valid_input():
    return {
        "FCVC": 2.0,
        "NCP": 3.0,
        "CH2O": 2.0,
        "FAF": 1.0,
        "TUE": 1.0,
        "FAVC": "yes",
        "CAEC": "Sometimes",
        "SCC": "no",
        "CALC": "Sometimes",
        "MTRANS": "Public_Transportation",
    }


def test_build_model_input_order():
    frame = build_model_input(valid_input())
    assert list(frame.columns) == MODEL_FEATURES
    assert frame.shape == (1, len(MODEL_FEATURES))


def test_build_model_input_missing_feature():
    data = valid_input()
    data.pop("FAF")
    with pytest.raises(ValueError):
        build_model_input(data)
