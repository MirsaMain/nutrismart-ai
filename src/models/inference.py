from pathlib import Path

import joblib
import pandas as pd


def load_model(model_path: str | Path):
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(
            "Model belum tersedia. Jalankan eksperimen dan ekspor model terlebih dahulu."
        )
    return joblib.load(path)


def predict_risk_score(model, input_data: dict) -> float:
    frame = pd.DataFrame([input_data])
    probability = model.predict_proba(frame)[0, 1]
    return float(probability * 100)
