from datetime import datetime, timezone

import pandas as pd

from src.database.meal_plan_repository import (
    activate_meal_plan,
    get_active_meal_plan,
    list_meal_plans,
    save_active_meal_plan,
)
from src.database.repository import save_screening_record


def sample_screening_result(score: float = 62.5):
    return {
        "bmi": 23.88,
        "bmi_category": "Normal",
        "predicted_class": 1,
        "obesity_probability": score / 100,
        "risk_score": score,
        "risk_category": "Sedang",
    }


def sample_lifestyle_input():
    return {
        "FCVC": 2.0,
        "NCP": 3.0,
        "CH2O": 2.0,
        "FAF": 1.0,
        "TUE": 1.0,
        "FAVC": "yes",
        "CAEC": "Sometimes",
        "SCC": "no",
        "CALC": "no",
        "MTRANS": "Public_Transportation",
    }


def sample_plan(source_record_id: int, menu_suffix: str = "A"):
    rows = []
    days = [
        "Senin",
        "Selasa",
        "Rabu",
        "Kamis",
        "Jumat",
        "Sabtu",
        "Minggu",
    ]
    meal_types = [
        "Sarapan",
        "Makan siang",
        "Makan malam",
        "Camilan",
    ]

    for day in days:
        for meal_type in meal_types:
            rows.append(
                {
                    "Hari": day,
                    "Waktu makan": meal_type,
                    "Menu": f"Menu {menu_suffix} {meal_type}",
                    "Susunan": "Susunan contoh",
                    "Catatan": "Catatan contoh",
                }
            )

    return {
        "plan_table": pd.DataFrame(rows),
        "priorities": [
            {
                "code": "example",
                "title": "Prioritas contoh",
                "reason": "Alasan contoh",
                "actions": ["Aksi satu"],
                "severity": 1,
            }
        ],
        "reminders": ["Pengingat contoh"],
        "diet_style": "Umum",
        "budget": "Sedang",
        "avoided_allergens": [],
        "include_snack": True,
        "source_record_id": source_record_id,
        "source_risk_score": 62.5,
        "source_risk_category": "Sedang",
    }


def create_screening_record(database_path):
    return save_screening_record(
        height_cm=165,
        weight_kg=65,
        screening_result=sample_screening_result(),
        lifestyle_input=sample_lifestyle_input(),
        database_path=database_path,
        recorded_at=datetime(
            2026,
            6,
            18,
            8,
            30,
            tzinfo=timezone.utc,
        ),
    )


def test_save_and_load_active_plan(tmp_path):
    database_path = tmp_path / "test.db"
    record_id = create_screening_record(database_path)

    plan_id = save_active_meal_plan(
        sample_plan(record_id),
        database_path=database_path,
        created_at=datetime(
            2026,
            6,
            18,
            9,
            0,
            tzinfo=timezone.utc,
        ),
    )

    loaded = get_active_meal_plan(
        database_path=database_path
    )

    assert plan_id == 1
    assert loaded is not None
    assert loaded["plan_id"] == 1
    assert loaded["is_saved"] is True
    assert len(loaded["plan_table"]) == 28
    assert loaded["source_record_id"] == record_id


def test_new_plan_deactivates_old_plan(tmp_path):
    database_path = tmp_path / "test.db"
    record_id = create_screening_record(database_path)

    first_id = save_active_meal_plan(
        sample_plan(record_id, "A"),
        database_path=database_path,
    )
    second_id = save_active_meal_plan(
        sample_plan(record_id, "B"),
        database_path=database_path,
    )

    plans = list_meal_plans(
        database_path=database_path
    )

    first_status = int(
        plans.loc[
            plans["plan_id"] == first_id,
            "is_active",
        ].iloc[0]
    )
    second_status = int(
        plans.loc[
            plans["plan_id"] == second_id,
            "is_active",
        ].iloc[0]
    )

    assert first_status == 0
    assert second_status == 1


def test_previous_plan_can_be_reactivated(tmp_path):
    database_path = tmp_path / "test.db"
    record_id = create_screening_record(database_path)

    first_id = save_active_meal_plan(
        sample_plan(record_id, "A"),
        database_path=database_path,
    )
    save_active_meal_plan(
        sample_plan(record_id, "B"),
        database_path=database_path,
    )

    assert activate_meal_plan(
        first_id,
        database_path=database_path,
    )

    loaded = get_active_meal_plan(
        database_path=database_path
    )

    assert loaded["plan_id"] == first_id
