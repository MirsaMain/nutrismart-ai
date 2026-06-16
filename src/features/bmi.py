def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    if weight_kg <= 0:
        raise ValueError("Berat badan harus lebih dari nol.")
    if height_cm <= 0:
        raise ValueError("Tinggi badan harus lebih dari nol.")

    height_m = height_cm / 100
    return weight_kg / (height_m ** 2)


def classify_bmi(bmi: float) -> str:
    if bmi < 18.5:
        return "Berat badan kurang"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Berat badan berlebih"
    return "Obesitas"
