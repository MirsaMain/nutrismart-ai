from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import streamlit as st

from src.config import MODEL_PATH
from src.features.input_schema import MODEL_FEATURES


@st.cache_resource(show_spinner=False)
def load_model(model_path: str = str(MODEL_PATH)) -> Any:
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Model tidak ditemukan di: {path}. "
            "Jalankan notebook 04 sampai best_model_pipeline.joblib terbentuk."
        )
    return joblib.load(path)


def build_model_input(input_data: dict[str, Any]) -> pd.DataFrame:
    missing = [f for f in MODEL_FEATURES if f not in input_data]
    extra = [f for f in input_data if f not in MODEL_FEATURES]

    if missing:
        raise ValueError(f"Fitur input yang hilang: {missing}")
    if extra:
        raise ValueError(f"Fitur input yang tidak dikenali: {extra}")

    return pd.DataFrame(
        [[input_data[f] for f in MODEL_FEATURES]],
        columns=MODEL_FEATURES,
    )


def predict_lifestyle_risk(model: Any, input_data: dict[str, Any]) -> dict:
    frame = build_model_input(input_data)
    probability = float(model.predict_proba(frame)[0, 1])
    predicted_class = int(model.predict(frame)[0])

    return {
        "predicted_class": predicted_class,
        "obesity_probability": probability,
        "risk_score": probability * 100,
    }
