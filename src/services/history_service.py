from datetime import date

import numpy as np
import pandas as pd


DAILY_HISTORY_COLUMNS = [
    "recorded_date",
    "record_id",
    "recorded_at",
    "risk_score",
    "risk_category",
    "bmi",
    "bmi_category",
    "weight_kg",
    "data_status",
    "is_actual",
    "actual_score",
]


def build_daily_history(
    history: pd.DataFrame,
    end_date: date | str | None = None,
) -> pd.DataFrame:
    if history.empty:
        return pd.DataFrame(columns=DAILY_HISTORY_COLUMNS)

    result = history.copy()
    result["recorded_at"] = pd.to_datetime(
        result["recorded_at"],
        errors="coerce",
    )
    result["recorded_date"] = pd.to_datetime(
        result["recorded_date"],
        errors="coerce",
    ).dt.normalize()

    result = result.dropna(
        subset=["recorded_at", "recorded_date", "risk_score"]
    )
    result = result.sort_values(
        ["recorded_at", "record_id"]
    )

    # Jika ada beberapa skrining pada hari yang sama,
    # grafik harian memakai hasil paling akhir pada hari tersebut.
    latest_per_day = (
        result.groupby("recorded_date", as_index=False)
        .tail(1)
        .set_index("recorded_date")
        .sort_index()
    )

    first_date = latest_per_day.index.min()

    if end_date is None:
        final_date = max(
            latest_per_day.index.max(),
            pd.Timestamp(date.today()),
        )
    else:
        final_date = pd.Timestamp(end_date).normalize()
        final_date = max(final_date, latest_per_day.index.max())

    daily_index = pd.date_range(
        start=first_date,
        end=final_date,
        freq="D",
    )

    daily = latest_per_day.reindex(daily_index)
    daily.index.name = "recorded_date"

    daily["is_actual"] = daily["record_id"].notna()

    columns_to_forward_fill = [
        "record_id",
        "recorded_at",
        "risk_score",
        "risk_category",
        "bmi",
        "bmi_category",
        "weight_kg",
        "predicted_class",
        "obesity_probability",
    ]

    available_columns = [
        column
        for column in columns_to_forward_fill
        if column in daily.columns
    ]

    daily[available_columns] = daily[
        available_columns
    ].ffill()

    daily["data_status"] = np.where(
        daily["is_actual"],
        "Aktual",
        "Diteruskan dari pembaruan terakhir",
    )

    daily["actual_score"] = daily["risk_score"].where(
        daily["is_actual"]
    )

    return daily.reset_index()


def filter_daily_history(
    daily_history: pd.DataFrame,
    period_days: int | None,
) -> pd.DataFrame:
    if daily_history.empty or period_days is None:
        return daily_history.copy()

    last_date = daily_history["recorded_date"].max()
    start_date = last_date - pd.Timedelta(days=period_days - 1)

    return daily_history.loc[
        daily_history["recorded_date"] >= start_date
    ].reset_index(drop=True)


def get_latest_actual_record(
    history: pd.DataFrame,
) -> pd.Series | None:
    if history.empty:
        return None

    result = history.copy()
    result["recorded_at"] = pd.to_datetime(
        result["recorded_at"],
        errors="coerce",
    )
    result = result.dropna(subset=["recorded_at"])
    result = result.sort_values(
        ["recorded_at", "record_id"]
    )

    if result.empty:
        return None

    return result.iloc[-1]
