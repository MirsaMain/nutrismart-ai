import pandas as pd

from src.services.history_service import build_daily_history


def test_daily_history_forward_fills_missing_date():
    history = pd.DataFrame(
        [
            {
                "record_id": 1,
                "recorded_at": "2026-06-15T08:00:00+00:00",
                "recorded_date": "2026-06-15",
                "risk_score": 45.0,
                "risk_category": "Sedang",
                "bmi": 24.0,
                "bmi_category": "Normal",
                "weight_kg": 65.0,
                "predicted_class": 0,
                "obesity_probability": 0.45,
            },
            {
                "record_id": 2,
                "recorded_at": "2026-06-17T08:00:00+00:00",
                "recorded_date": "2026-06-17",
                "risk_score": 72.0,
                "risk_category": "Tinggi",
                "bmi": 24.5,
                "bmi_category": "Normal",
                "weight_kg": 66.0,
                "predicted_class": 1,
                "obesity_probability": 0.72,
            },
        ]
    )

    daily = build_daily_history(
        history,
        end_date="2026-06-17",
    )

    middle_day = daily.loc[
        daily["recorded_date"]
        == pd.Timestamp("2026-06-16")
    ].iloc[0]

    assert middle_day["risk_score"] == 45.0
    assert middle_day["data_status"] == (
        "Diteruskan dari pembaruan terakhir"
    )
    assert bool(middle_day["is_actual"]) is False


def test_latest_record_of_same_day_is_used():
    history = pd.DataFrame(
        [
            {
                "record_id": 1,
                "recorded_at": "2026-06-17T08:00:00+00:00",
                "recorded_date": "2026-06-17",
                "risk_score": 40.0,
                "risk_category": "Sedang",
                "bmi": 24.0,
                "bmi_category": "Normal",
                "weight_kg": 65.0,
                "predicted_class": 0,
                "obesity_probability": 0.40,
            },
            {
                "record_id": 2,
                "recorded_at": "2026-06-17T20:00:00+00:00",
                "recorded_date": "2026-06-17",
                "risk_score": 58.0,
                "risk_category": "Sedang",
                "bmi": 24.1,
                "bmi_category": "Normal",
                "weight_kg": 65.2,
                "predicted_class": 1,
                "obesity_probability": 0.58,
            },
        ]
    )

    daily = build_daily_history(
        history,
        end_date="2026-06-17",
    )

    assert len(daily) == 1
    assert daily.iloc[0]["record_id"] == 2
    assert daily.iloc[0]["risk_score"] == 58.0
