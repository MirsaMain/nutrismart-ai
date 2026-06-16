def classify_risk(score: float) -> str:
    if score < 40:
        return "Rendah"
    if score < 70:
        return "Sedang"
    return "Tinggi"
