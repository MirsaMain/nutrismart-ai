from typing import Any

import pandas as pd

from src.recommendations.workout_priority_engine import (
    determine_workout_priorities,
)
from src.recommendations.workout_templates import (
    ACTIVE_RECOVERY_TEXT,
    AEROBIC_TEMPLATES,
    COOL_DOWN_TEXT,
    MOBILITY_TEXT,
    REST_TEXT,
    STRENGTH_WITHOUT_SUPPORT,
    STRENGTH_WITH_SUPPORT,
    WARM_UP_OPTIONS,
)


DAY_NAMES = [
    "Senin",
    "Selasa",
    "Rabu",
    "Kamis",
    "Jumat",
    "Sabtu",
    "Minggu",
]

VALID_FITNESS_LEVELS = {
    "Pemula",
    "Menengah",
    "Lanjutan",
}

VALID_LOCATIONS = {
    "Di rumah",
    "Luar ruangan",
    "Gym",
}

VALID_EQUIPMENT = {
    "Tanpa alat",
    "Resistance band",
    "Dumbbell ringan",
    "Peralatan gym",
}

VALID_PREFERENCES = {
    "Jalan kaki",
    "Kardio low-impact",
    "Campuran",
}

VALID_SUPPORT_OPTIONS = {
    "Tidak perlu dukungan khusus",
    "Perlu kursi atau pegangan",
}

VALID_ACTIVE_DAYS = {3, 4, 5, 6}
VALID_SESSION_MINUTES = {10, 20, 30, 45}


def _session_profile(
    fitness_level: str,
) -> dict[str, Any]:
    profiles = {
        "Pemula": {
            "intensity": "Ringan",
            "strength_sets": "1–2 set",
            "strength_repetitions": "6–10 repetisi nyaman",
            "aerobic_pattern": (
                "Gunakan kecepatan stabil dan istirahat singkat "
                "bila diperlukan."
            ),
        },
        "Menengah": {
            "intensity": "Ringan–sedang",
            "strength_sets": "2 set",
            "strength_repetitions": "8–12 repetisi terkontrol",
            "aerobic_pattern": (
                "Gunakan intensitas sedang yang masih memungkinkan "
                "berbicara."
            ),
        },
        "Lanjutan": {
            "intensity": "Sedang",
            "strength_sets": "2–3 set",
            "strength_repetitions": "8–12 repetisi terkontrol",
            "aerobic_pattern": (
                "Gunakan segmen sedang dan segmen pemulihan tanpa "
                "sprint maksimal."
            ),
        },
    }

    return profiles[fitness_level]


def _build_week_pattern(
    active_days: int,
) -> list[str]:
    """
    Menghasilkan pola tujuh hari.

    Jumlah hari selain 'Istirahat' selalu sama dengan pilihan active_days.
    Pola tiga hari tetap memiliki dua sesi latihan kekuatan.
    """
    patterns = {
        3: [
            "Kekuatan",
            "Istirahat",
            "Aerobik",
            "Istirahat",
            "Kekuatan",
            "Istirahat",
            "Istirahat",
        ],
        4: [
            "Aerobik",
            "Kekuatan",
            "Istirahat",
            "Aerobik",
            "Kekuatan",
            "Istirahat",
            "Istirahat",
        ],
        5: [
            "Aerobik",
            "Kekuatan",
            "Istirahat",
            "Aerobik",
            "Kekuatan",
            "Aerobik",
            "Istirahat",
        ],
        6: [
            "Aerobik",
            "Kekuatan",
            "Aerobik",
            "Mobilitas",
            "Kekuatan",
            "Aerobik",
            "Istirahat",
        ],
    }

    return patterns[active_days]


def generate_workout_plan(
    latest_record: pd.Series,
    fitness_level: str,
    active_days: int,
    session_minutes: int,
    training_location: str,
    equipment: str,
    activity_preference: str,
    support_option: str,
) -> dict[str, Any]:
    if fitness_level not in VALID_FITNESS_LEVELS:
        raise ValueError("Tingkat kebugaran tidak dikenali.")

    if active_days not in VALID_ACTIVE_DAYS:
        raise ValueError("Jumlah hari aktif tidak dikenali.")

    if session_minutes not in VALID_SESSION_MINUTES:
        raise ValueError("Durasi sesi tidak dikenali.")

    if training_location not in VALID_LOCATIONS:
        raise ValueError("Lokasi latihan tidak dikenali.")

    if equipment not in VALID_EQUIPMENT:
        raise ValueError("Peralatan latihan tidak dikenali.")

    if activity_preference not in VALID_PREFERENCES:
        raise ValueError("Preferensi aktivitas tidak dikenali.")

    if support_option not in VALID_SUPPORT_OPTIONS:
        raise ValueError("Pilihan dukungan tidak dikenali.")

    if (
        training_location != "Gym"
        and equipment == "Peralatan gym"
    ):
        raise ValueError(
            "Peralatan gym hanya dapat dipilih jika "
            "lokasi latihan adalah Gym."
        )

    profile = _session_profile(fitness_level)
    week_pattern = _build_week_pattern(active_days)

    warm_up = WARM_UP_OPTIONS[equipment]

    aerobic_activity = AEROBIC_TEMPLATES[
        training_location
    ][activity_preference]

    if support_option == "Perlu kursi atau pegangan":
        strength_activity = STRENGTH_WITH_SUPPORT[
            equipment
        ]
    else:
        strength_activity = STRENGTH_WITHOUT_SUPPORT[
            equipment
        ]

    plan_rows: list[dict[str, Any]] = []

    for day_index, (day_name, session_type) in enumerate(
        zip(DAY_NAMES, week_pattern),
        start=1,
    ):
        if session_type == "Aerobik":
            title = (
                f"Sesi aerobik — {activity_preference}"
            )
            main_activity = (
                f"{aerobic_activity} "
                f"{profile['aerobic_pattern']}"
            )
            duration = session_minutes
            intensity = profile["intensity"]
            session_warm_up = warm_up
            session_cool_down = COOL_DOWN_TEXT
            notes = (
                "Kurangi kecepatan atau berhenti bila muncul "
                "nyeri tajam, pusing, sesak tidak biasa, "
                "atau rasa tidak nyaman."
            )

        elif session_type == "Kekuatan":
            title = "Latihan kekuatan seluruh tubuh"
            main_activity = (
                f"{strength_activity} "
                f"Lakukan {profile['strength_sets']} dengan "
                f"{profile['strength_repetitions']}. "
                "Gunakan gerakan perlahan dan terkontrol."
            )
            duration = session_minutes
            intensity = profile["intensity"]
            session_warm_up = warm_up
            session_cool_down = COOL_DOWN_TEXT
            notes = (
                "Tidak perlu menahan napas. Kurangi rentang "
                "gerak atau beban bila teknik mulai berubah."
            )

        elif session_type == "Mobilitas":
            title = "Mobilitas dan fleksibilitas ringan"
            main_activity = MOBILITY_TEXT
            duration = min(session_minutes, 20)
            intensity = "Sangat ringan"
            session_warm_up = (
                "Mulai dari pernapasan tenang dan jalan "
                "di tempat perlahan."
            )
            session_cool_down = (
                "Akhiri dengan napas tenang dan posisi "
                "yang nyaman."
            )
            notes = (
                "Hindari gerakan memantul dan jangan "
                "memaksakan rentang gerak."
            )

        elif session_type == "Pemulihan":
            title = "Pemulihan aktif"
            main_activity = ACTIVE_RECOVERY_TEXT
            duration = min(session_minutes, 20)
            intensity = "Sangat ringan"
            session_warm_up = (
                "Mulai perlahan sesuai kondisi tubuh hari itu."
            )
            session_cool_down = (
                "Akhiri dengan jalan perlahan atau "
                "peregangan ringan."
            )
            notes = (
                "Sesi ini bukan latihan berat. Tujuannya "
                "menjaga tubuh tetap bergerak."
            )

        else:
            title = "Istirahat"
            main_activity = REST_TEXT
            duration = 0
            intensity = "Istirahat"
            session_warm_up = "-"
            session_cool_down = "-"
            notes = (
                "Tidur cukup dan perhatikan pemulihan. "
                "Jangan mengganti hari istirahat dengan "
                "latihan berat."
            )

        plan_rows.append(
            {
                "day_index": day_index,
                "Hari": day_name,
                "Jenis sesi": session_type,
                "Judul": title,
                "Pemanasan": session_warm_up,
                "Latihan utama": main_activity,
                "Pendinginan": session_cool_down,
                "Durasi (menit)": int(duration),
                "Intensitas": intensity,
                "Catatan": notes,
            }
        )

    plan_table = pd.DataFrame(plan_rows)

    priorities = determine_workout_priorities(
        latest_record=latest_record,
        limit=4,
    )

    planned_weekly_minutes = int(
        plan_table["Durasi (menit)"].sum()
    )

    planned_aerobic_minutes = int(
        plan_table.loc[
            plan_table["Jenis sesi"] == "Aerobik",
            "Durasi (menit)",
        ].sum()
    )

    planned_strength_days = int(
        (
            plan_table["Jenis sesi"] == "Kekuatan"
        ).sum()
    )

    actual_active_days = int(
        (
            plan_table["Jenis sesi"] != "Istirahat"
        ).sum()
    )

    if actual_active_days != active_days:
        raise RuntimeError(
            "Jumlah hari aktif yang dihasilkan tidak "
            "sesuai dengan pilihan pengguna."
        )

    reminders = [
        (
            "Mulai dari kemampuan saat ini dan tingkatkan "
            "durasi atau beban secara bertahap, bukan sekaligus."
        ),
        (
            "Intensitas sedang umumnya masih memungkinkan "
            "berbicara, meskipun napas lebih cepat."
        ),
        (
            "Hentikan latihan dan cari pertolongan bila muncul "
            "nyeri dada, pingsan, sesak tidak biasa, atau gejala berat."
        ),
        (
            "Satu rencana tidak menggantikan pemeriksaan atau "
            "program individual dari tenaga kesehatan dan pelatih "
            "yang kompeten."
        ),
    ]

    return {
        "plan_table": plan_table,
        "priorities": priorities,
        "reminders": reminders,
        "fitness_level": fitness_level,
        "active_days": int(active_days),
        "session_minutes": int(session_minutes),
        "training_location": training_location,
        "equipment": equipment,
        "activity_preference": activity_preference,
        "support_option": support_option,
        "planned_weekly_minutes": planned_weekly_minutes,
        "planned_aerobic_minutes": planned_aerobic_minutes,
        "planned_strength_days": planned_strength_days,
        "source_record_id": int(
            latest_record.get("record_id", 0)
        ),
        "source_risk_score": float(
            latest_record.get("risk_score", 0.0)
        ),
        "source_risk_category": str(
            latest_record.get(
                "risk_category",
                "",
            )
        ),
        "source_bmi_category": str(
            latest_record.get(
                "bmi_category",
                "",
            )
        ),
    }


def plan_to_csv_bytes(
    plan_table: pd.DataFrame,
) -> bytes:
    export_table = plan_table.drop(
        columns=["day_index"],
        errors="ignore",
    )

    return export_table.to_csv(
        index=False,
    ).encode("utf-8-sig")
