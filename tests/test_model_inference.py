from pathlib import Path

import pytest

from src.models.inference import load_model


def test_missing_model_file():
    with pytest.raises(FileNotFoundError):
        load_model(Path("artifacts/model_yang_tidak_ada.joblib"))
