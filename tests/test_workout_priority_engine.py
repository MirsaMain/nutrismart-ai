import pandas as pd

from src.recommendations.workout_priority_engine import (
    determine_workout_priorities,
)


def test_low_activity_and_high_screen_time_priorities():
    record = pd.Series(
        {
            "faf": 0.5,
            "tue": 2.0,
            "mtrans": "Automobile",
            "risk_score": 78.0,
            "bmi_category": "Obesitas",
        }
    )

    priorities = determine_workout_priorities(
        record,
        limit=10,
    )

    codes = {
        item["code"]
        for item in priorities
    }

    assert "build_activity_consistency" in codes
    assert "reduce_sedentary_time" in codes
    assert "add_active_transport" in codes
    assert "prioritize_low_impact" in codes
    assert "high_score_gradual_change" in codes
