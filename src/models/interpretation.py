from src.config import LOW_RISK_MAX, MEDIUM_RISK_MAX


def classify_risk_score(score: float) -> str:
    if not 0 <= score <= 100:
        raise ValueError("Skor risiko harus berada pada rentang 0 sampai 100.")
    if score < LOW_RISK_MAX:
        return "Rendah"
    if score < MEDIUM_RISK_MAX:
        return "Sedang"
    return "Tinggi"


def build_combined_interpretation(
    bmi_category: str,
    risk_category: str,
) -> str:
    if bmi_category == "Obesitas":
        return {
            "Rendah": (
                "BMI saat ini berada dalam kategori obesitas, tetapi pola hidup "
                "yang dicatat relatif lebih mendukung pengendalian berat badan. "
                "Hasil ini tidak berarti status obesitas telah hilang."
            ),
            "Sedang": (
                "BMI saat ini berada dalam kategori obesitas. Sebagian kebiasaan "
                "sudah mendukung pengendalian berat badan, tetapi masih terdapat "
                "faktor pola hidup yang perlu diperbaiki."
            ),
            "Tinggi": (
                "BMI saat ini berada dalam kategori obesitas dan pola hidup yang "
                "dicatat cenderung mempertahankan atau memperburuk risiko terkait obesitas."
            ),
        }[risk_category]

    if bmi_category == "Berat badan berlebih":
        return {
            "Rendah": (
                "BMI saat ini berada dalam kategori berat badan berlebih, tetapi "
                "pola hidup yang dicatat relatif mendukung pengendalian berat badan."
            ),
            "Sedang": (
                "BMI saat ini berada dalam kategori berat badan berlebih dan masih "
                "terdapat beberapa kebiasaan yang perlu diperbaiki."
            ),
            "Tinggi": (
                "BMI saat ini berada dalam kategori berat badan berlebih. Pola hidup "
                "yang dicatat menunjukkan skor tinggi dan dapat meningkatkan "
                "kecenderungan menuju obesitas apabila dipertahankan."
            ),
        }[risk_category]

    if bmi_category == "Normal":
        return {
            "Rendah": (
                "BMI saat ini berada dalam kategori normal dan pola hidup yang "
                "dicatat relatif mendukung pencegahan obesitas."
            ),
            "Sedang": (
                "BMI saat ini berada dalam kategori normal, tetapi terdapat beberapa "
                "kebiasaan yang perlu diperhatikan untuk menjaga berat badan."
            ),
            "Tinggi": (
                "BMI saat ini masih berada dalam kategori normal, tetapi pola hidup "
                "yang dicatat memiliki skor tinggi. Perbaikan kebiasaan diperlukan "
                "agar risiko tidak meningkat apabila pola tersebut dipertahankan."
            ),
        }[risk_category]

    return (
        "BMI saat ini berada dalam kategori berat badan kurang. Skor model tetap "
        "menjelaskan pola hidup terhadap obesitas, tetapi hasil perlu dibaca bersama "
        "kondisi tubuh dan tidak menggantikan konsultasi tenaga kesehatan."
    )
