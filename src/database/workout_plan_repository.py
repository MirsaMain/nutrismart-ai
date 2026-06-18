import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import DATABASE_PATH, DEFAULT_USER_ID
from src.database.connection import get_connection
from src.database.repository import initialize_database


CREATE_WORKOUT_PLANS_TABLE = '''
CREATE TABLE IF NOT EXISTS workout_plans (
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    source_record_id INTEGER NOT NULL,
    source_risk_score REAL NOT NULL,
    source_risk_category TEXT NOT NULL,
    source_bmi_category TEXT NOT NULL,
    fitness_level TEXT NOT NULL,
    active_days INTEGER NOT NULL,
    session_minutes INTEGER NOT NULL,
    planned_weekly_minutes INTEGER NOT NULL,
    training_location TEXT NOT NULL,
    equipment TEXT NOT NULL,
    activity_preference TEXT NOT NULL,
    support_option TEXT NOT NULL,
    priorities_json TEXT NOT NULL,
    reminders_json TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),
    created_at TEXT NOT NULL,
    FOREIGN KEY (source_record_id)
        REFERENCES screening_records(record_id)
);
'''

CREATE_WORKOUT_PLAN_ITEMS_TABLE = '''
CREATE TABLE IF NOT EXISTS workout_plan_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    day_index INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    session_type TEXT NOT NULL,
    title TEXT NOT NULL,
    warm_up TEXT NOT NULL,
    main_activity TEXT NOT NULL,
    cool_down TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    intensity TEXT NOT NULL,
    notes TEXT NOT NULL,
    FOREIGN KEY (plan_id)
        REFERENCES workout_plans(plan_id)
        ON DELETE CASCADE,
    UNIQUE (plan_id, day_index)
);
'''

CREATE_WORKOUT_PLAN_USER_INDEX = '''
CREATE INDEX IF NOT EXISTS idx_workout_plans_user_created
ON workout_plans (user_id, created_at);
'''

CREATE_WORKOUT_PLAN_ACTIVE_INDEX = '''
CREATE INDEX IF NOT EXISTS idx_workout_plans_user_active
ON workout_plans (user_id, is_active);
'''

REQUIRED_PLAN_COLUMNS = {
    "day_index",
    "Hari",
    "Jenis sesi",
    "Judul",
    "Pemanasan",
    "Latihan utama",
    "Pendinginan",
    "Durasi (menit)",
    "Intensitas",
    "Catatan",
}


def initialize_workout_plan_database(
    database_path: str | Path = DATABASE_PATH,
) -> None:
    initialize_database(database_path)

    with get_connection(database_path) as connection:
        connection.execute(CREATE_WORKOUT_PLANS_TABLE)
        connection.execute(CREATE_WORKOUT_PLAN_ITEMS_TABLE)
        connection.execute(CREATE_WORKOUT_PLAN_USER_INDEX)
        connection.execute(CREATE_WORKOUT_PLAN_ACTIVE_INDEX)
        connection.commit()


def _validate_plan(plan: dict[str, Any]) -> pd.DataFrame:
    required_keys = {
        "plan_table",
        "priorities",
        "reminders",
        "fitness_level",
        "active_days",
        "session_minutes",
        "training_location",
        "equipment",
        "activity_preference",
        "support_option",
        "planned_weekly_minutes",
        "source_record_id",
        "source_risk_score",
        "source_risk_category",
        "source_bmi_category",
    }

    missing_keys = sorted(required_keys.difference(plan))
    if missing_keys:
        raise ValueError(
            "Data workout plan belum lengkap. "
            f"Key yang hilang: {missing_keys}"
        )

    plan_table = plan["plan_table"]
    if not isinstance(plan_table, pd.DataFrame):
        raise TypeError("plan_table harus berupa pandas DataFrame.")

    if plan_table.empty:
        raise ValueError("Workout plan kosong dan tidak dapat disimpan.")

    missing_columns = sorted(
        REQUIRED_PLAN_COLUMNS.difference(plan_table.columns)
    )
    if missing_columns:
        raise ValueError(
            "Kolom workout plan belum lengkap: "
            f"{missing_columns}"
        )

    if len(plan_table) != 7:
        raise ValueError(
            "Workout plan harus memiliki tepat tujuh baris harian."
        )

    return plan_table.copy()


def save_active_workout_plan(
    plan: dict[str, Any],
    user_id: str = DEFAULT_USER_ID,
    database_path: str | Path = DATABASE_PATH,
    created_at: datetime | None = None,
) -> int:
    initialize_workout_plan_database(database_path)
    plan_table = _validate_plan(plan)

    current_time = created_at or datetime.now().astimezone()
    created_at_text = current_time.isoformat(timespec="seconds")

    plan_values = {
        "user_id": user_id,
        "source_record_id": int(plan["source_record_id"]),
        "source_risk_score": float(plan["source_risk_score"]),
        "source_risk_category": str(
            plan["source_risk_category"]
        ),
        "source_bmi_category": str(
            plan["source_bmi_category"]
        ),
        "fitness_level": str(plan["fitness_level"]),
        "active_days": int(plan["active_days"]),
        "session_minutes": int(plan["session_minutes"]),
        "planned_weekly_minutes": int(
            plan["planned_weekly_minutes"]
        ),
        "training_location": str(
            plan["training_location"]
        ),
        "equipment": str(plan["equipment"]),
        "activity_preference": str(
            plan["activity_preference"]
        ),
        "support_option": str(plan["support_option"]),
        "priorities_json": json.dumps(
            plan["priorities"],
            ensure_ascii=False,
            sort_keys=True,
        ),
        "reminders_json": json.dumps(
            plan["reminders"],
            ensure_ascii=False,
        ),
        "created_at": created_at_text,
    }

    with get_connection(database_path) as connection:
        connection.execute(
            '''
            UPDATE workout_plans
            SET is_active = 0
            WHERE user_id = ?
            ''',
            (user_id,),
        )

        cursor = connection.execute(
            '''
            INSERT INTO workout_plans (
                user_id,
                source_record_id,
                source_risk_score,
                source_risk_category,
                source_bmi_category,
                fitness_level,
                active_days,
                session_minutes,
                planned_weekly_minutes,
                training_location,
                equipment,
                activity_preference,
                support_option,
                priorities_json,
                reminders_json,
                is_active,
                created_at
            )
            VALUES (
                :user_id,
                :source_record_id,
                :source_risk_score,
                :source_risk_category,
                :source_bmi_category,
                :fitness_level,
                :active_days,
                :session_minutes,
                :planned_weekly_minutes,
                :training_location,
                :equipment,
                :activity_preference,
                :support_option,
                :priorities_json,
                :reminders_json,
                1,
                :created_at
            )
            ''',
            plan_values,
        )

        plan_id = int(cursor.lastrowid)

        item_rows = []
        for _, row in plan_table.iterrows():
            item_rows.append(
                {
                    "plan_id": plan_id,
                    "day_index": int(row["day_index"]),
                    "day_name": str(row["Hari"]),
                    "session_type": str(row["Jenis sesi"]),
                    "title": str(row["Judul"]),
                    "warm_up": str(row["Pemanasan"]),
                    "main_activity": str(row["Latihan utama"]),
                    "cool_down": str(row["Pendinginan"]),
                    "duration_minutes": int(
                        row["Durasi (menit)"]
                    ),
                    "intensity": str(row["Intensitas"]),
                    "notes": str(row["Catatan"]),
                }
            )

        connection.executemany(
            '''
            INSERT INTO workout_plan_items (
                plan_id,
                day_index,
                day_name,
                session_type,
                title,
                warm_up,
                main_activity,
                cool_down,
                duration_minutes,
                intensity,
                notes
            )
            VALUES (
                :plan_id,
                :day_index,
                :day_name,
                :session_type,
                :title,
                :warm_up,
                :main_activity,
                :cool_down,
                :duration_minutes,
                :intensity,
                :notes
            )
            ''',
            item_rows,
        )

        connection.commit()

    return plan_id


def _load_plan_items(
    plan_id: int,
    database_path: str | Path,
) -> pd.DataFrame:
    with get_connection(database_path) as connection:
        rows = connection.execute(
            '''
            SELECT
                day_index,
                day_name AS "Hari",
                session_type AS "Jenis sesi",
                title AS "Judul",
                warm_up AS "Pemanasan",
                main_activity AS "Latihan utama",
                cool_down AS "Pendinginan",
                duration_minutes AS "Durasi (menit)",
                intensity AS "Intensitas",
                notes AS "Catatan"
            FROM workout_plan_items
            WHERE plan_id = ?
            ORDER BY day_index ASC
            ''',
            (plan_id,),
        ).fetchall()

    return pd.DataFrame([dict(row) for row in rows])


def get_active_workout_plan(
    user_id: str = DEFAULT_USER_ID,
    database_path: str | Path = DATABASE_PATH,
) -> dict[str, Any] | None:
    initialize_workout_plan_database(database_path)

    with get_connection(database_path) as connection:
        row = connection.execute(
            '''
            SELECT *
            FROM workout_plans
            WHERE user_id = ?
              AND is_active = 1
            ORDER BY created_at DESC, plan_id DESC
            LIMIT 1
            ''',
            (user_id,),
        ).fetchone()

    if row is None:
        return None

    plan_row = dict(row)
    plan_id = int(plan_row["plan_id"])

    return {
        "plan_id": plan_id,
        "plan_table": _load_plan_items(
            plan_id,
            database_path,
        ),
        "priorities": json.loads(
            plan_row["priorities_json"]
        ),
        "reminders": json.loads(
            plan_row["reminders_json"]
        ),
        "fitness_level": plan_row["fitness_level"],
        "active_days": int(plan_row["active_days"]),
        "session_minutes": int(
            plan_row["session_minutes"]
        ),
        "planned_weekly_minutes": int(
            plan_row["planned_weekly_minutes"]
        ),
        "training_location": plan_row[
            "training_location"
        ],
        "equipment": plan_row["equipment"],
        "activity_preference": plan_row[
            "activity_preference"
        ],
        "support_option": plan_row["support_option"],
        "source_record_id": int(
            plan_row["source_record_id"]
        ),
        "source_risk_score": float(
            plan_row["source_risk_score"]
        ),
        "source_risk_category": plan_row[
            "source_risk_category"
        ],
        "source_bmi_category": plan_row[
            "source_bmi_category"
        ],
        "created_at": plan_row["created_at"],
        "is_saved": True,
    }


def list_workout_plans(
    user_id: str = DEFAULT_USER_ID,
    database_path: str | Path = DATABASE_PATH,
) -> pd.DataFrame:
    initialize_workout_plan_database(database_path)

    with get_connection(database_path) as connection:
        rows = connection.execute(
            '''
            SELECT
                p.plan_id,
                p.created_at,
                p.source_record_id,
                p.source_risk_score,
                p.source_risk_category,
                p.source_bmi_category,
                p.fitness_level,
                p.active_days,
                p.session_minutes,
                p.planned_weekly_minutes,
                p.training_location,
                p.equipment,
                p.activity_preference,
                p.support_option,
                p.is_active,
                COUNT(i.item_id) AS item_count
            FROM workout_plans AS p
            LEFT JOIN workout_plan_items AS i
              ON i.plan_id = p.plan_id
            WHERE p.user_id = ?
            GROUP BY p.plan_id
            ORDER BY p.created_at DESC, p.plan_id DESC
            ''',
            (user_id,),
        ).fetchall()

    return pd.DataFrame([dict(row) for row in rows])


def activate_workout_plan(
    plan_id: int,
    user_id: str = DEFAULT_USER_ID,
    database_path: str | Path = DATABASE_PATH,
) -> bool:
    initialize_workout_plan_database(database_path)

    with get_connection(database_path) as connection:
        plan_exists = connection.execute(
            '''
            SELECT 1
            FROM workout_plans
            WHERE plan_id = ?
              AND user_id = ?
            ''',
            (plan_id, user_id),
        ).fetchone()

        if plan_exists is None:
            return False

        connection.execute(
            '''
            UPDATE workout_plans
            SET is_active = 0
            WHERE user_id = ?
            ''',
            (user_id,),
        )

        connection.execute(
            '''
            UPDATE workout_plans
            SET is_active = 1
            WHERE plan_id = ?
              AND user_id = ?
            ''',
            (plan_id, user_id),
        )

        connection.commit()

    return True
