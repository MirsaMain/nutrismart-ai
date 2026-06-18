from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class WorkoutPriority:
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


def determine_workout_priorities(
    latest_record: pd.Series,
    limit: int = 4,
) -> list[dict[str, Any]]:
    priorities: list[WorkoutPriority] = []

    faf = _number_value(latest_record, "faf", 1.0)
    tue = _number_value(latest_record, "tue", 1.0)
    mtrans = _text_value(latest_record, "mtrans")
    risk_score = _number_value(
        latest_record,
        "risk_score",
        0.0,
    )
    bmi_category = str(
        latest_record.get("bmi_category", "")
    ).strip()

    if faf <= 1.0:
        priorities.append(
            WorkoutPriority(
                code="build_activity_consistency",
                title="Bangun kebiasaan bergerak secara bertahap",
                reason=(
                    "Tingkat aktivitas fisik pada skrining terakhir "
                    "masih rendah."
                ),
                actions=(
                    "Mulai dari sesi pendek yang realistis.",
                    "Utamakan konsistensi sebelum menambah intensitas.",
                    "Tambahkan waktu secara bertahap ketika tubuh sudah terbiasa.",
                ),
                severity=5,
            )
        )
    elif faf < 2.0:
        priorities.append(
            WorkoutPriority(
                code="increase_weekly_activity",
                title="Tingkatkan aktivitas mingguan secara bertahap",
                reason=(
                    "Aktivitas fisik sudah ada, tetapi masih dapat "
                    "ditingkatkan secara konsisten."
                ),
                actions=(
                    "Tambahkan satu sesi aerobik ringan atau sedang.",
                    "Pertahankan dua hari latihan kekuatan.",
                    "Gunakan hari pemulihan untuk mobilitas ringan.",
                ),
                severity=3,
            )
        )
    else:
        priorities.append(
            WorkoutPriority(
                code="maintain_activity_pattern",
                title="Pertahankan pola aktivitas yang konsisten",
                reason=(
                    "Tingkat aktivitas fisik pada skrining sudah cukup baik."
                ),
                actions=(
                    "Pertahankan variasi aerobik, kekuatan, dan pemulihan.",
                    "Hindari menaikkan volume latihan secara mendadak.",
                    "Gunakan satu hari istirahat penuh setiap minggu.",
                ),
                severity=2,
            )
        )

    if tue >= 1.5:
        priorities.append(
            WorkoutPriority(
                code="reduce_sedentary_time",
                title="Kurangi waktu duduk berkepanjangan",
                reason=(
                    "Penggunaan perangkat teknologi pada skrining "
                    "terakhir relatif tinggi."
                ),
                actions=(
                    "Berdiri atau berjalan singkat secara berkala.",
                    "Gunakan peregangan ringan di sela waktu layar.",
                    "Tempatkan pengingat bergerak pada jam kerja atau belajar.",
                ),
                severity=4,
            )
        )

    if mtrans in {
        "automobile",
        "public_transportation",
        "motorbike",
    }:
        priorities.append(
            WorkoutPriority(
                code="add_active_transport",
                title="Tambahkan kesempatan berjalan dalam aktivitas harian",
                reason="Moda transportasi utama relatif pasif.",
                actions=(
                    "Berjalan pada sebagian perjalanan bila aman.",
                    "Gunakan tangga untuk jarak yang sesuai kemampuan.",
                    "Tambahkan jalan singkat sebelum atau sesudah perjalanan.",
                ),
                severity=2,
            )
        )

    if bmi_category in {
        "Berat badan berlebih",
        "Obesitas",
    }:
        priorities.append(
            WorkoutPriority(
                code="prioritize_low_impact",
                title="Utamakan latihan low-impact",
                reason=(
                    "Kategori BMI terbaru memerlukan pendekatan yang "
                    "lebih ramah sendi dan bertahap."
                ),
                actions=(
                    "Pilih jalan kaki, sepeda statis, atau gerakan tanpa lompatan.",
                    "Gunakan kursi atau pegangan bila diperlukan.",
                    "Hentikan gerakan yang menimbulkan nyeri tajam.",
                ),
                severity=4,
            )
        )

    if risk_score >= 70:
        priorities.append(
            WorkoutPriority(
                code="high_score_gradual_change",
                title="Fokus pada perubahan kecil dan terukur",
                reason=(
                    "Skor pola hidup terakhir berada pada kategori tinggi."
                ),
                actions=(
                    "Pilih jadwal yang dapat dipertahankan selama satu minggu.",
                    "Jangan mengejar kelelahan sebagai ukuran keberhasilan.",
                    "Lakukan skrining ulang setelah menjalankan rencana secara konsisten.",
                ),
                severity=5,
            )
        )

    priorities.sort(
        key=lambda item: (-item.severity, item.title)
    )

    return [
        asdict(priority)
        for priority in priorities[:limit]
    ]
