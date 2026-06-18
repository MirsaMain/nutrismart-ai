import hashlib
import random
from typing import Any

import pandas as pd

from src.recommendations.meal_templates import MEAL_TEMPLATES
from src.recommendations.priority_engine import (
    determine_meal_priorities,
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

MEAL_ORDER = [
    "Sarapan",
    "Makan siang",
    "Makan malam",
    "Camilan",
]

BUDGET_RANK = {
    "Hemat": 1,
    "Sedang": 2,
}


def _stable_seed(parts: list[str]) -> int:
    digest = hashlib.sha256(
        "|".join(parts).encode("utf-8")
    ).hexdigest()
    return int(digest[:16], 16)


def _filter_templates(
    meal_type: str,
    diet_style: str,
    budget: str,
    avoided_allergens: set[str],
) -> list[dict[str, Any]]:
    budget_rank = BUDGET_RANK[budget]

    candidates = [
        item
        for item in MEAL_TEMPLATES
        if item["meal_type"] == meal_type
        and diet_style in item["diet_styles"]
        and item["budget_rank"] <= budget_rank
        and not avoided_allergens.intersection(
            set(item["allergens"])
        )
    ]

    if not candidates:
        raise ValueError(
            f"Tidak ada pilihan {meal_type.lower()} yang sesuai "
            "dengan kombinasi pola makan, anggaran, dan bahan yang dihindari."
        )

    return candidates


def generate_meal_plan(
    latest_record: pd.Series,
    diet_style: str,
    budget: str,
    avoided_allergens: list[str],
    include_snack: bool = True,
) -> dict[str, Any]:
    if diet_style not in {"Umum", "Vegetarian"}:
        raise ValueError("Pola makan tidak dikenali.")

    if budget not in BUDGET_RANK:
        raise ValueError("Pilihan anggaran tidak dikenali.")

    avoided_set = set(avoided_allergens)

    record_id = str(latest_record.get("record_id", "0"))
    risk_category = str(
        latest_record.get("risk_category", "")
    )

    seed = _stable_seed(
        [
            record_id,
            diet_style,
            budget,
            ",".join(sorted(avoided_set)),
            str(include_snack),
            risk_category,
        ]
    )

    randomizer = random.Random(seed)

    selected_meal_types = (
        MEAL_ORDER
        if include_snack
        else MEAL_ORDER[:-1]
    )

    pools: dict[str, list[dict[str, Any]]] = {}

    for meal_type in selected_meal_types:
        pool = _filter_templates(
            meal_type=meal_type,
            diet_style=diet_style,
            budget=budget,
            avoided_allergens=avoided_set,
        )
        pool = pool.copy()
        randomizer.shuffle(pool)
        pools[meal_type] = pool

    plan_rows: list[dict[str, Any]] = []

    for day_index, day_name in enumerate(DAY_NAMES):
        for meal_type in selected_meal_types:
            pool = pools[meal_type]
            item = pool[day_index % len(pool)]

            plan_rows.append(
                {
                    "Hari": day_name,
                    "Waktu makan": meal_type,
                    "Menu": item["name"],
                    "Susunan": item["components"],
                    "Catatan": (
                        "Sesuaikan jumlah makanan dengan rasa lapar, "
                        "kebutuhan pribadi, dan pedoman Isi Piringku."
                    ),
                }
            )

    plan_table = pd.DataFrame(plan_rows)

    priorities = determine_meal_priorities(
        latest_record=latest_record,
        limit=4,
    )

    reminders = [
        (
            "Gunakan pedoman Isi Piringku: sekitar separuh piring "
            "berisi sayur dan buah, sedangkan separuh lainnya "
            "berisi makanan pokok dan sumber protein."
        ),
        (
            "Utamakan variasi makanan yang minim proses dan batasi "
            "makanan tinggi gula, garam, serta lemak."
        ),
        (
            "Air putih menjadi minuman utama. Sesuaikan kebutuhan "
            "dengan kondisi tubuh, cuaca, dan aktivitas."
        ),
        (
            "Menu dapat ditukar antahari selama kelompok makanannya "
            "tetap seimbang."
        ),
    ]

    return {
        "plan_table": plan_table,
        "priorities": priorities,
        "reminders": reminders,
        "diet_style": diet_style,
        "budget": budget,
        "avoided_allergens": sorted(avoided_set),
        "include_snack": include_snack,
        "source_record_id": int(
            latest_record.get("record_id", 0)
        ),
        "source_risk_score": float(
            latest_record.get("risk_score", 0)
        ),
        "source_risk_category": str(
            latest_record.get("risk_category", "")
        ),
    }


def plan_to_csv_bytes(
    plan_table: pd.DataFrame,
) -> bytes:
    return plan_table.to_csv(
        index=False,
    ).encode("utf-8-sig")
