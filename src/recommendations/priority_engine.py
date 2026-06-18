from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class MealPriority:
    code: str
    title: str
    reason: str
    actions: tuple[str, ...]
    severity: int


def _text_value(record: pd.Series, key: str) -> str:
    value: Any = record.get(key, "")
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def _number_value(
    record: pd.Series,
    key: str,
    default: float = 0.0,
) -> float:
    value: Any = record.get(key, default)
    if pd.isna(value):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def determine_meal_priorities(
    latest_record: pd.Series,
    limit: int = 4,
) -> list[dict[str, Any]]:
    priorities: list[MealPriority] = []

    favc = _text_value(latest_record, "favc")
    fcvc = _number_value(latest_record, "fcvc", 2.0)
    ch2o = _number_value(latest_record, "ch2o", 2.0)
    caec = _text_value(latest_record, "caec")
    scc = _text_value(latest_record, "scc")
    calc = _text_value(latest_record, "calc")
    ncp = _number_value(latest_record, "ncp", 3.0)
    risk_score = _number_value(
        latest_record,
        "risk_score",
        0.0,
    )

    if favc == "yes":
        priorities.append(
            MealPriority(
                code="reduce_high_calorie_food",
                title="Kurangi makanan tinggi kalori",
                reason=(
                    "Skrining terakhir menunjukkan kebiasaan sering "
                    "mengonsumsi makanan tinggi kalori."
                ),
                actions=(
                    "Utamakan olahan kukus, rebus, panggang, atau tumis ringan.",
                    "Batasi gorengan, makanan cepat saji, dan minuman berpemanis.",
                    "Gunakan buah segar sebagai pilihan pencuci mulut.",
                ),
                severity=4,
            )
        )

    if fcvc < 2.0:
        priorities.append(
            MealPriority(
                code="increase_vegetables",
                title="Tingkatkan konsumsi sayur",
                reason=(
                    "Skor konsumsi sayur pada skrining terakhir masih rendah."
                ),
                actions=(
                    "Sertakan sayur pada makan siang dan makan malam.",
                    "Variasikan warna dan jenis sayur.",
                    "Gunakan pedoman Isi Piringku sebagai panduan porsi.",
                ),
                severity=4,
            )
        )

    if ch2o < 2.0:
        priorities.append(
            MealPriority(
                code="increase_water",
                title="Perbaiki kebiasaan minum air",
                reason=(
                    "Skor konsumsi air pada skrining terakhir masih rendah."
                ),
                actions=(
                    "Sediakan air putih saat makan dan di antara waktu makan.",
                    "Kurangi minuman berpemanis.",
                    "Gunakan pengingat minum secara berkala.",
                ),
                severity=3,
            )
        )

    if caec in {"frequently", "always"}:
        priorities.append(
            MealPriority(
                code="structured_snacking",
                title="Atur camilan secara terjadwal",
                reason=(
                    "Skrining menunjukkan kebiasaan makan di antara waktu "
                    "makan cukup sering."
                ),
                actions=(
                    "Pilih satu camilan terencana daripada mengemil terus-menerus.",
                    "Utamakan buah segar atau pilihan sederhana minim gula tambahan.",
                    "Hindari makan langsung dari kemasan besar.",
                ),
                severity=3,
            )
        )

    if scc == "no":
        priorities.append(
            MealPriority(
                code="portion_awareness",
                title="Tingkatkan kesadaran porsi",
                reason=(
                    "Skrining menunjukkan asupan belum dipantau secara teratur."
                ),
                actions=(
                    "Gunakan susunan piring yang konsisten.",
                    "Makan perlahan dan berhenti ketika cukup.",
                    "Catat pola makan secara sederhana, bukan untuk menghukum diri.",
                ),
                severity=2,
            )
        )

    if calc in {"frequently", "always"}:
        priorities.append(
            MealPriority(
                code="limit_alcohol",
                title="Batasi konsumsi alkohol",
                reason=(
                    "Frekuensi konsumsi alkohol pada skrining terakhir cukup tinggi."
                ),
                actions=(
                    "Pilih minuman tanpa alkohol dan tanpa gula tambahan.",
                    "Jangan mengganti makan utama dengan minuman beralkohol.",
                    "Cari bantuan profesional bila sulit mengurangi konsumsi.",
                ),
                severity=4,
            )
        )

    if ncp > 3.5:
        priorities.append(
            MealPriority(
                code="regular_meal_pattern",
                title="Rapikan jadwal makan utama",
                reason=(
                    "Jumlah makan utama pada skrining terakhir cukup tinggi."
                ),
                actions=(
                    "Gunakan tiga waktu makan utama yang teratur.",
                    "Tambahkan camilan hanya bila diperlukan.",
                    "Hindari makan utama berulang dalam jarak yang sangat dekat.",
                ),
                severity=2,
            )
        )

    if risk_score >= 70:
        priorities.append(
            MealPriority(
                code="high_score_focus",
                title="Fokus pada perubahan kecil yang konsisten",
                reason=(
                    "Skor pola hidup terakhir berada pada kategori tinggi."
                ),
                actions=(
                    "Pilih dua kebiasaan prioritas untuk satu minggu.",
                    "Pertahankan jadwal makan yang realistis.",
                    "Lakukan skrining ulang setelah menjalankan rencana secara konsisten.",
                ),
                severity=5,
            )
        )

    if not priorities:
        priorities.append(
            MealPriority(
                code="maintain_balanced_pattern",
                title="Pertahankan pola makan seimbang",
                reason=(
                    "Tidak ditemukan faktor pola makan yang sangat menonjol "
                    "pada skrining terakhir."
                ),
                actions=(
                    "Pertahankan variasi makanan.",
                    "Sertakan sayur, buah, makanan pokok, dan protein.",
                    "Batasi makanan tinggi gula, garam, dan lemak.",
                ),
                severity=1,
            )
        )

    priorities.sort(
        key=lambda item: (-item.severity, item.title)
    )
    return [
        asdict(priority)
        for priority in priorities[:limit]
    ]
