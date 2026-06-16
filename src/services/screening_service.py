from src.features.bmi import calculate_bmi, classify_bmi


def process_bmi_screening(weight_kg: float, height_cm: float) -> dict:
    bmi = calculate_bmi(weight_kg, height_cm)
    return {
        "bmi": bmi,
        "bmi_category": classify_bmi(bmi),
    }
