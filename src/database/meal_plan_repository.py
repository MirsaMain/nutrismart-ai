import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import DATABASE_PATH, DEFAULT_USER_ID
from src.database.connection import get_connection
from src.database.repository import initialize_database

CREATE_MEAL_PLANS_TABLE = """
CREATE TABLE IF NOT EXISTS meal_plans (
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    source_record_id INTEGER NOT NULL,
    source_risk_score REAL NOT NULL,
    source_risk_category TEXT NOT NULL,
    diet_style TEXT NOT NULL,
    budget TEXT NOT NULL,
    include_snack INTEGER NOT NULL CHECK (include_snack IN (0, 1)),
    avoided_allergens_json TEXT NOT NULL,
    priorities_json TEXT NOT NULL,
    reminders_json TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TEXT NOT NULL,
    FOREIGN KEY (source_record_id) REFERENCES screening_records(record_id)
);
"""

CREATE_MEAL_PLAN_ITEMS_TABLE = """
CREATE TABLE IF NOT EXISTS meal_plan_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    day_index INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    meal_order INTEGER NOT NULL,
    meal_type TEXT NOT NULL,
    menu_name TEXT NOT NULL,
    components TEXT NOT NULL,
    notes TEXT NOT NULL,
    FOREIGN KEY (plan_id) REFERENCES meal_plans(plan_id) ON DELETE CASCADE,
    UNIQUE (plan_id, day_index, meal_order)
);
"""

CREATE_MEAL_PLAN_USER_INDEX = """
CREATE INDEX IF NOT EXISTS idx_meal_plans_user_created
ON meal_plans (user_id, created_at);
"""

CREATE_MEAL_PLAN_ACTIVE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_meal_plans_user_active
ON meal_plans (user_id, is_active);
"""

DAY_INDEX = {
    "Senin": 1,
    "Selasa": 2,
    "Rabu": 3,
    "Kamis": 4,
    "Jumat": 5,
    "Sabtu": 6,
    "Minggu": 7,
}

MEAL_ORDER_INDEX = {
    "Sarapan": 1,
    "Makan siang": 2,
    "Makan malam": 3,
    "Camilan": 4,
}

REQUIRED_PLAN_COLUMNS = {
    "Hari",
    "Waktu makan",
    "Menu",
    "Susunan",
    "Catatan",
}


def initialize_meal_plan_database(
    database_path: str | Path = DATABASE_PATH,
) -> None:
    """Membuat tabel meal plan tanpa menghapus data lama."""
    initialize_database(database_path)

    with get_connection(database_path) as connection:
        connection.execute(CREATE_MEAL_PLANS_TABLE)
        connection.execute(CREATE_MEAL_PLAN_ITEMS_TABLE)
        connection.execute(CREATE_MEAL_PLAN_USER_INDEX)
        connection.execute(CREATE_MEAL_PLAN_ACTIVE_INDEX)
        connection.commit()


def _validate_plan(plan: dict[str, Any]) -> pd.DataFrame:
    required_keys = {
        "plan_table",
        "priorities",
        "reminders",
        "diet_style",
        "budget",
        "avoided_allergens",
        "include_snack",
        "source_record_id",
        "source_risk_score",
        "source_risk_category",
    }

    missing_keys = sorted(required_keys.difference(plan))
    if missing_keys:
        raise ValueError(
            f"Data meal plan belum lengkap. Key yang hilang: {missing_keys}"
        )

    plan_table = plan["plan_table"]
    if not isinstance(plan_table, pd.DataFrame):
        raise TypeError("plan_table harus berupa pandas DataFrame.")

    missing_columns = sorted(
        REQUIRED_PLAN_COLUMNS.difference(plan_table.columns)
    )
    if missing_columns:
        raise ValueError(
            f"Kolom meal plan belum lengkap: {missing_columns}"
        )

    if plan_table.empty:
        raise ValueError("Meal plan kosong dan tidak dapat disimpan.")

    unknown_days = sorted(
        set(plan_table["Hari"]).difference(DAY_INDEX)
    )
    if unknown_days:
        raise ValueError(f"Nama hari tidak dikenali: {unknown_days}")

    unknown_meal_types = sorted(
        set(plan_table["Waktu makan"]).difference(MEAL_ORDER_INDEX)
    )
    if unknown_meal_types:
        raise ValueError(
            f"Jenis waktu makan tidak dikenali: {unknown_meal_types}"
        )

    return plan_table.copy()


def save_active_meal_plan(
    plan: dict[str, Any],
    user_id: str = DEFAULT_USER_ID,
    database_path: str | Path = DATABASE_PATH,
    created_at: datetime | None = None,
) -> int:
    """Simpan plan baru dan jadikan satu-satunya plan aktif user."""
    initialize_meal_plan_database(database_path)
    plan_table = _validate_plan(plan)

    current_time = created_at or datetime.now().astimezone()
    created_at_text = current_time.isoformat(timespec="seconds")

    values = {
        "user_id": user_id,
        "source_record_id": int(plan["source_record_id"]),
        "source_risk_score": float(plan["source_risk_score"]),
        "source_risk_category": str(plan["source_risk_category"]),
        "diet_style": str(plan["diet_style"]),
        "budget": str(plan["budget"]),
        "include_snack": int(bool(plan["include_snack"])),
        "avoided_allergens_json": json.dumps(
            plan["avoided_allergens"],
            ensure_ascii=False,
            sort_keys=True,
        ),
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
            "UPDATE meal_plans SET is_active = 0 WHERE user_id = ?",
            (user_id,),
        )

        cursor = connection.execute(
            """
            INSERT INTO meal_plans (
                user_id,
                source_record_id,
                source_risk_score,
                source_risk_category,
                diet_style,
                budget,
                include_snack,
                avoided_allergens_json,
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
                :diet_style,
                :budget,
                :include_snack,
                :avoided_allergens_json,
                :priorities_json,
                :reminders_json,
                1,
                :created_at
            )
            """,
            values,
        )

        plan_id = int(cursor.lastrowid)
        item_rows = []

        for _, row in plan_table.iterrows():
            item_rows.append(
                {
                    "plan_id": plan_id,
                    "day_index": DAY_INDEX[str(row["Hari"])],
                    "day_name": str(row["Hari"]),
                    "meal_order": MEAL_ORDER_INDEX[
                        str(row["Waktu makan"])
                    ],
                    "meal_type": str(row["Waktu makan"]),
                    "menu_name": str(row["Menu"]),
                    "components": str(row["Susunan"]),
                    "notes": str(row["Catatan"]),
                }
            )

        connection.executemany(
            """
            INSERT INTO meal_plan_items (
                plan_id,
                day_index,
                day_name,
                meal_order,
                meal_type,
                menu_name,
                components,
                notes
            )
            VALUES (
                :plan_id,
                :day_index,
                :day_name,
                :meal_order,
                :meal_type,
                :menu_name,
                :components,
                :notes
            )
            """,
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
            """
            SELECT
                day_name AS "Hari",
                meal_type AS "Waktu makan",
                menu_name AS "Menu",
                components AS "Susunan",
                notes AS "Catatan"
            FROM meal_plan_items
            WHERE plan_id = ?
            ORDER BY day_index ASC, meal_order ASC
            """,
            (plan_id,),
        ).fetchall()

    return pd.DataFrame([dict(row) for row in rows])


def get_active_meal_plan(
    user_id: str = DEFAULT_USER_ID,
    database_path: str | Path = DATABASE_PATH,
) -> dict[str, Any] | None:
    initialize_meal_plan_database(database_path)

    with get_connection(database_path) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM meal_plans
            WHERE user_id = ? AND is_active = 1
            ORDER BY created_at DESC, plan_id DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

    if row is None:
        return None

    data = dict(row)
    plan_id = int(data["plan_id"])

    return {
        "plan_id": plan_id,
        "plan_table": _load_plan_items(plan_id, database_path),
        "priorities": json.loads(data["priorities_json"]),
        "reminders": json.loads(data["reminders_json"]),
        "diet_style": data["diet_style"],
        "budget": data["budget"],
        "avoided_allergens": json.loads(
            data["avoided_allergens_json"]
        ),
        "include_snack": bool(data["include_snack"]),
        "source_record_id": int(data["source_record_id"]),
        "source_risk_score": float(data["source_risk_score"]),
        "source_risk_category": data["source_risk_category"],
        "created_at": data["created_at"],
        "is_saved": True,
    }


def list_meal_plans(
    user_id: str = DEFAULT_USER_ID,
    database_path: str | Path = DATABASE_PATH,
) -> pd.DataFrame:
    initialize_meal_plan_database(database_path)

    with get_connection(database_path) as connection:
        rows = connection.execute(
            """
            SELECT
                p.plan_id,
                p.created_at,
                p.source_record_id,
                p.source_risk_score,
                p.source_risk_category,
                p.diet_style,
                p.budget,
                p.include_snack,
                p.is_active,
                COUNT(i.item_id) AS item_count
            FROM meal_plans AS p
            LEFT JOIN meal_plan_items AS i
              ON i.plan_id = p.plan_id
            WHERE p.user_id = ?
            GROUP BY p.plan_id
            ORDER BY p.created_at DESC, p.plan_id DESC
            """,
            (user_id,),
        ).fetchall()

    return pd.DataFrame([dict(row) for row in rows])


def activate_meal_plan(
    plan_id: int,
    user_id: str = DEFAULT_USER_ID,
    database_path: str | Path = DATABASE_PATH,
) -> bool:
    initialize_meal_plan_database(database_path)

    with get_connection(database_path) as connection:
        exists = connection.execute(
            """
            SELECT 1
            FROM meal_plans
            WHERE plan_id = ? AND user_id = ?
            """,
            (plan_id, user_id),
        ).fetchone()

        if exists is None:
            return False

        connection.execute(
            "UPDATE meal_plans SET is_active = 0 WHERE user_id = ?",
            (user_id,),
        )
        connection.execute(
            """
            UPDATE meal_plans
            SET is_active = 1
            WHERE plan_id = ? AND user_id = ?
            """,
            (plan_id, user_id),
        )
        connection.commit()

    return True
