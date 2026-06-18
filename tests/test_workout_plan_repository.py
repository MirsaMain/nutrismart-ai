from datetime import datetime, timezone

import pandas as pd

from src.database.repository import save_screening_record
from src.database.workout_plan_repository import (
    activate_workout_plan,
    get_active_workout_plan,
    list_workout_plans,
    save_active_workout_plan,
)


def sample_screening_result():
    return {
        "bmi": 27.2,
        "bmi_category": "Berat badan berlebih",
        "predicted_class": 1,
        "obesity_probability": 0.70,
        "risk_score": 70.0,
        "risk_category": "Tinggi",
    }


def sample_lifestyle_input():
    return {
        "FCVC": 2.0,
        "NCP": 3.0,
        "CH2O": 2.0,
        "FAF": 1.0,
        "TUE": 2.0,
        "FAVC": "yes",
        "CAEC": "Sometimes",
        "SCC": "no",
        "CALC": "no",
        "MTRANS": "Public_Transportation",
    }


def sample_plan(source_record_id: int, suffix: str = "A"):
    rows = []

    for index, day in enumerate(
        [
            "Senin",
            "Selasa",
            "Rabu",
            "Kamis",
            "Jumat",
            "Sabtu",
            "Minggu",
        ],
        start=1,
    ):
        rows.append(
            {
                "day_index": index,
                "Hari": day,
                "Jenis sesi": "Aerobik" if index < 7 else "Istirahat",
                "Judul": f"Workout {suffix} {day}",
                "Pemanasan": "Pemanasan",
                "Latihan utama": "Latihan utama",
                "Pendinginan": "Pendinginan",
                "Durasi (menit)": 20 if index < 7 else 0,
                "Intensitas": "Ringan",
                "Catatan": "Catatan",
            }
        )

    return {
        "plan_table": pd.DataFrame(rows),
        "priorities": [
            {
                "code": "example",
                "title": "Contoh",
                "reason": "Alasan",
                "actions": ["Aksi"],
                "severity": 1,
            }
        ],
        "reminders": ["Pengingat"],
        "fitness_level": "Pemula",
        "active_days": 4,
        "session_minutes": 20,
        "planned_weekly_minutes": 120,
        "training_location": "Di rumah",
        "equipment": "Tanpa alat",
        "activity_preference": "Jalan kaki",
        "support_option": "Tidak perlu dukungan khusus",
        "source_record_id": source_record_id,
        "source_risk_score": 70.0,
        "source_risk_category": "Tinggi",
        "source_bmi_category": "Berat badan berlebih",
    }


def create_screening_record(database_path):
    return save_screening_record(
        height_cm=165,
        weight_kg=74,
        screening_result=sample_screening_result(),
        lifestyle_input=sample_lifestyle_input(),
        database_path=database_path,
        recorded_at=datetime(
            2026,
            6,
            18,
            8,
            0,
            tzinfo=timezone.utc,
        ),
    )


def test_save_and_load_active_workout_plan(tmp_path):
    database_path = tmp_path / "test.db"
    record_id = create_screening_record(database_path)

    plan_id = save_active_workout_plan(
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

    loaded = get_active_workout_plan(
        database_path=database_path
    )

    assert plan_id == 1
    assert loaded is not None
    assert loaded["plan_id"] == 1
    assert loaded["is_saved"] is True
    assert len(loaded["plan_table"]) == 7


def test_new_workout_plan_deactivates_old(tmp_path):
    database_path = tmp_path / "test.db"
    record_id = create_screening_record(database_path)

    first_id = save_active_workout_plan(
        sample_plan(record_id, "A"),
        database_path=database_path,
    )
    second_id = save_active_workout_plan(
        sample_plan(record_id, "B"),
        database_path=database_path,
    )

    plans = list_workout_plans(
        database_path=database_path
    )

    first_active = int(
        plans.loc[
            plans["plan_id"] == first_id,
            "is_active",
        ].iloc[0]
    )
    second_active = int(
        plans.loc[
            plans["plan_id"] == second_id,
            "is_active",
        ].iloc[0]
    )

    assert first_active == 0
    assert second_active == 1


def test_old_workout_plan_can_be_reactivated(tmp_path):
    database_path = tmp_path / "test.db"
    record_id = create_screening_record(database_path)

    first_id = save_active_workout_plan(
        sample_plan(record_id, "A"),
        database_path=database_path,
    )
    save_active_workout_plan(
        sample_plan(record_id, "B"),
        database_path=database_path,
    )

    assert activate_workout_plan(
        first_id,
        database_path=database_path,
    )

    loaded = get_active_workout_plan(
        database_path=database_path
    )

    assert loaded["plan_id"] == first_id
