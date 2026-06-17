from datetime import datetime, timezone

from src.database.repository import (
    count_screening_records,
    get_screening_history,
    save_screening_record,
)


def sample_result(score=62.5):
    return {
        "bmi": 23.88,
        "bmi_category": "Normal",
        "predicted_class": 1,
        "obesity_probability": score / 100,
        "risk_score": score,
        "risk_category": "Sedang",
    }


def sample_input():
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


def test_save_and_read_screening_record(tmp_path):
    database_path = tmp_path / "test.db"

    record_id = save_screening_record(
        height_cm=165,
        weight_kg=65,
        screening_result=sample_result(),
        lifestyle_input=sample_input(),
        database_path=database_path,
        recorded_at=datetime(
            2026,
            6,
            17,
            8,
            30,
            tzinfo=timezone.utc,
        ),
    )

    history = get_screening_history(
        database_path=database_path,
    )

    assert record_id == 1
    assert len(history) == 1
    assert history.iloc[0]["risk_score"] == 62.5
    assert history.iloc[0]["recorded_date"] == "2026-06-17"
    assert count_screening_records(
        database_path=database_path
    ) == 1
