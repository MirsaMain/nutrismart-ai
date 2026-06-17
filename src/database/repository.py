import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import DATABASE_PATH, DEFAULT_USER_ID
from src.database.connection import get_connection
from src.database.schema import (
    CREATE_SCREENING_RECORDS_TABLE,
    CREATE_USER_DATE_INDEX,
    CREATE_USER_DATETIME_INDEX,
    OPTIONAL_MIGRATION_COLUMNS,
)


def initialize_database(
    database_path: str | Path = DATABASE_PATH,
) -> None:
    with get_connection(database_path) as connection:
        connection.execute(CREATE_SCREENING_RECORDS_TABLE)

        existing_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(screening_records)"
            ).fetchall()
        }

        for column_name, column_type in OPTIONAL_MIGRATION_COLUMNS.items():
            if column_name not in existing_columns:
                connection.execute(
                    f"ALTER TABLE screening_records "
                    f"ADD COLUMN {column_name} {column_type}"
                )

        connection.execute(CREATE_USER_DATE_INDEX)
        connection.execute(CREATE_USER_DATETIME_INDEX)
        connection.commit()


def save_screening_record(
    *,
    height_cm: float,
    weight_kg: float,
    screening_result: dict[str, Any],
    lifestyle_input: dict[str, Any],
    user_id: str = DEFAULT_USER_ID,
    database_path: str | Path = DATABASE_PATH,
    recorded_at: datetime | None = None,
) -> int:
    initialize_database(database_path)

    current_time = recorded_at or datetime.now().astimezone()
    recorded_at_text = current_time.isoformat(timespec="seconds")
    recorded_date_text = current_time.date().isoformat()

    values = {
        "user_id": user_id,
        "recorded_at": recorded_at_text,
        "recorded_date": recorded_date_text,
        "height_cm": float(height_cm),
        "weight_kg": float(weight_kg),
        "bmi": float(screening_result["bmi"]),
        "bmi_category": str(screening_result["bmi_category"]),
        "predicted_class": int(screening_result["predicted_class"]),
        "obesity_probability": float(
            screening_result["obesity_probability"]
        ),
        "risk_score": float(screening_result["risk_score"]),
        "risk_category": str(screening_result["risk_category"]),
        "fcvc": float(lifestyle_input["FCVC"]),
        "ncp": float(lifestyle_input["NCP"]),
        "ch2o": float(lifestyle_input["CH2O"]),
        "faf": float(lifestyle_input["FAF"]),
        "tue": float(lifestyle_input["TUE"]),
        "favc": str(lifestyle_input["FAVC"]),
        "caec": str(lifestyle_input["CAEC"]),
        "scc": str(lifestyle_input["SCC"]),
        "calc": str(lifestyle_input["CALC"]),
        "mtrans": str(lifestyle_input["MTRANS"]),
        "input_json": json.dumps(
            lifestyle_input,
            ensure_ascii=False,
            sort_keys=True,
        ),
        "created_at": recorded_at_text,
    }

    sql = '''
    INSERT INTO screening_records (
        user_id,
        recorded_at,
        recorded_date,
        height_cm,
        weight_kg,
        bmi,
        bmi_category,
        predicted_class,
        obesity_probability,
        risk_score,
        risk_category,
        fcvc,
        ncp,
        ch2o,
        faf,
        tue,
        favc,
        caec,
        scc,
        calc,
        mtrans,
        input_json,
        created_at
    )
    VALUES (
        :user_id,
        :recorded_at,
        :recorded_date,
        :height_cm,
        :weight_kg,
        :bmi,
        :bmi_category,
        :predicted_class,
        :obesity_probability,
        :risk_score,
        :risk_category,
        :fcvc,
        :ncp,
        :ch2o,
        :faf,
        :tue,
        :favc,
        :caec,
        :scc,
        :calc,
        :mtrans,
        :input_json,
        :created_at
    )
    '''

    with get_connection(database_path) as connection:
        cursor = connection.execute(sql, values)
        connection.commit()
        return int(cursor.lastrowid)


def get_screening_history(
    user_id: str = DEFAULT_USER_ID,
    database_path: str | Path = DATABASE_PATH,
) -> pd.DataFrame:
    initialize_database(database_path)

    sql = '''
    SELECT
        record_id,
        user_id,
        recorded_at,
        recorded_date,
        height_cm,
        weight_kg,
        bmi,
        bmi_category,
        predicted_class,
        obesity_probability,
        risk_score,
        risk_category,
        fcvc,
        ncp,
        ch2o,
        faf,
        tue,
        favc,
        caec,
        scc,
        calc,
        mtrans,
        input_json,
        created_at
    FROM screening_records
    WHERE user_id = ?
    ORDER BY recorded_at ASC, record_id ASC
    '''

    with get_connection(database_path) as connection:
        rows = connection.execute(sql, (user_id,)).fetchall()

    return pd.DataFrame([dict(row) for row in rows])


def count_screening_records(
    user_id: str = DEFAULT_USER_ID,
    database_path: str | Path = DATABASE_PATH,
) -> int:
    initialize_database(database_path)

    with get_connection(database_path) as connection:
        row = connection.execute(
            '''
            SELECT COUNT(*) AS total
            FROM screening_records
            WHERE user_id = ?
            ''',
            (user_id,),
        ).fetchone()

    return int(row["total"])


def delete_screening_history(
    user_id: str = DEFAULT_USER_ID,
    database_path: str | Path = DATABASE_PATH,
) -> int:
    initialize_database(database_path)

    with get_connection(database_path) as connection:
        cursor = connection.execute(
            '''
            DELETE FROM screening_records
            WHERE user_id = ?
            ''',
            (user_id,),
        )
        connection.commit()

    return int(cursor.rowcount)
