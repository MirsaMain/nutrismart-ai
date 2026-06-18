import pandas as pd

from src.recommendations.priority_engine import (
    determine_meal_priorities,
)


def test_priority_engine_detects_main_food_issues():
    record = pd.Series(
        {
            "favc": "yes",
            "fcvc": 1.0,
            "ch2o": 1.0,
            "caec": "Frequently",
            "scc": "no",
            "calc": "no",
            "ncp": 3.0,
            "risk_score": 78.0,
        }
    )

    priorities = determine_meal_priorities(
        record,
        limit=10,
    )

    codes = {
        priority["code"]
        for priority in priorities
    }

    assert "reduce_high_calorie_food" in codes
    assert "increase_vegetables" in codes
    assert "increase_water" in codes
    assert "structured_snacking" in codes
    assert "high_score_focus" in codes


def test_priority_engine_returns_maintenance_when_no_issue():
    record = pd.Series(
        {
            "favc": "no",
            "fcvc": 3.0,
            "ch2o": 3.0,
            "caec": "no",
            "scc": "yes",
            "calc": "no",
            "ncp": 3.0,
            "risk_score": 25.0,
        }
    )

    priorities = determine_meal_priorities(record)

    assert priorities[0]["code"] == (
        "maintain_balanced_pattern"
    )
