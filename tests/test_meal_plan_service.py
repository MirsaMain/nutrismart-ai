import pandas as pd

from src.recommendations.meal_plan_service import (
    generate_meal_plan,
)


def sample_record():
    return pd.Series(
        {
            "record_id": 7,
            "risk_score": 72.0,
            "risk_category": "Tinggi",
            "favc": "yes",
            "fcvc": 1.0,
            "ch2o": 1.0,
            "caec": "Sometimes",
            "scc": "no",
            "calc": "no",
            "ncp": 3.0,
        }
    )


def test_plan_contains_seven_days_and_four_meals():
    plan = generate_meal_plan(
        latest_record=sample_record(),
        diet_style="Umum",
        budget="Sedang",
        avoided_allergens=[],
        include_snack=True,
    )

    table = plan["plan_table"]

    assert table["Hari"].nunique() == 7
    assert len(table) == 28
    assert set(table["Waktu makan"]) == {
        "Sarapan",
        "Makan siang",
        "Makan malam",
        "Camilan",
    }


def test_plan_without_snack_contains_21_rows():
    plan = generate_meal_plan(
        latest_record=sample_record(),
        diet_style="Umum",
        budget="Hemat",
        avoided_allergens=[],
        include_snack=False,
    )

    assert len(plan["plan_table"]) == 21
    assert "Camilan" not in set(
        plan["plan_table"]["Waktu makan"]
    )


def test_vegetarian_plan_avoids_selected_allergens():
    plan = generate_meal_plan(
        latest_record=sample_record(),
        diet_style="Vegetarian",
        budget="Sedang",
        avoided_allergens=[
            "Telur",
            "Susu",
            "Kacang",
            "Kedelai",
        ],
        include_snack=True,
    )

    combined_text = " ".join(
        plan["plan_table"]["Menu"].tolist()
        + plan["plan_table"]["Susunan"].tolist()
    ).lower()

    assert "telur" not in combined_text
    assert "yoghurt" not in combined_text
    assert "tempe" not in combined_text
    assert "tahu" not in combined_text
    assert "kacang tanah" not in combined_text


def test_same_preferences_produce_same_plan():
    first_plan = generate_meal_plan(
        latest_record=sample_record(),
        diet_style="Umum",
        budget="Sedang",
        avoided_allergens=[],
        include_snack=True,
    )
    second_plan = generate_meal_plan(
        latest_record=sample_record(),
        diet_style="Umum",
        budget="Sedang",
        avoided_allergens=[],
        include_snack=True,
    )

    assert first_plan["plan_table"].equals(
        second_plan["plan_table"]
    )
