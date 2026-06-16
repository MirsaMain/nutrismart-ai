from typing import Any

from src.features.bmi import calculate_bmi, classify_bmi
from src.models.inference import predict_lifestyle_risk
from src.models.interpretation import (
    build_combined_interpretation,
    classify_risk_score,
)


def process_screening(
    model: Any,
    height_cm: float,
    weight_kg: float,
    lifestyle_input: dict,
) -> dict:
    bmi = calculate_bmi(weight_kg=weight_kg, height_cm=height_cm)
    bmi_category = classify_bmi(bmi)

    model_result = predict_lifestyle_risk(
        model=model,
        input_data=lifestyle_input,
    )

    risk_category = classify_risk_score(model_result["risk_score"])
    interpretation = build_combined_interpretation(
        bmi_category=bmi_category,
        risk_category=risk_category,
    )

    return {
        "bmi": bmi,
        "bmi_category": bmi_category,
        "predicted_class": model_result["predicted_class"],
        "obesity_probability": model_result["obesity_probability"],
        "risk_score": model_result["risk_score"],
        "risk_category": risk_category,
        "interpretation": interpretation,
        "lifestyle_input": lifestyle_input,
    }
