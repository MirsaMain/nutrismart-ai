import pandas as pd
import pytest

from src.recommendations.workout_plan_service import (
    generate_workout_plan,
)


def sample_record():
    return pd.Series(
        {
            "record_id": 11,
            "risk_score": 70.0,
            "risk_category": "Tinggi",
            "bmi_category": "Berat badan berlebih",
            "faf": 1.0,
            "tue": 2.0,
            "mtrans": "Public_Transportation",
        }
    )


def test_plan_has_seven_days():
    plan = generate_workout_plan(
        latest_record=sample_record(),
        fitness_level="Pemula",
        active_days=4,
        session_minutes=20,
        training_location="Di rumah",
        equipment="Tanpa alat",
        activity_preference="Jalan kaki",
        support_option="Tidak perlu dukungan khusus",
    )

    assert len(plan["plan_table"]) == 7
    assert plan["plan_table"]["Hari"].nunique() == 7
    assert plan["planned_weekly_minutes"] > 0


def test_supported_plan_uses_chair_friendly_strength():
    plan = generate_workout_plan(
        latest_record=sample_record(),
        fitness_level="Pemula",
        active_days=4,
        session_minutes=20,
        training_location="Di rumah",
        equipment="Tanpa alat",
        activity_preference="Kardio low-impact",
        support_option="Perlu kursi atau pegangan",
    )

    strength_rows = plan["plan_table"].loc[
        plan["plan_table"]["Jenis sesi"] == "Kekuatan"
    ]

    combined_text = " ".join(
        strength_rows["Latihan utama"].tolist()
    ).lower()

    assert "kursi" in combined_text or "pegangan" in combined_text


def test_gym_equipment_requires_gym_location():
    with pytest.raises(ValueError):
        generate_workout_plan(
            latest_record=sample_record(),
            fitness_level="Menengah",
            active_days=5,
            session_minutes=30,
            training_location="Di rumah",
            equipment="Peralatan gym",
            activity_preference="Campuran",
            support_option="Tidak perlu dukungan khusus",
        )


def test_three_day_plan_keeps_two_strength_exposures():
    plan = generate_workout_plan(
        latest_record=sample_record(),
        fitness_level="Pemula",
        active_days=3,
        session_minutes=20,
        training_location="Di rumah",
        equipment="Tanpa alat",
        activity_preference="Jalan kaki",
        support_option="Tidak perlu dukungan khusus",
    )

    assert (
        plan["plan_table"]["Jenis sesi"] != "Istirahat"
    ).sum() == 3
    assert plan["planned_strength_days"] == 2
