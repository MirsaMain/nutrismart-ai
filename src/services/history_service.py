import pandas as pd


def forward_fill_daily_history(
    history: pd.DataFrame,
    date_column: str = "recorded_at",
    score_column: str = "risk_score",
) -> pd.DataFrame:
    if history.empty:
        return history.copy()

    result = history.copy()
    result[date_column] = pd.to_datetime(result[date_column])
    result = result.sort_values(date_column).set_index(date_column)

    daily_index = pd.date_range(
        result.index.min(),
        result.index.max(),
        freq="D",
    )

    result = result.reindex(daily_index)
    result[score_column] = result[score_column].ffill()
    result["data_status"] = result["record_id"].apply(
        lambda value: "actual" if pd.notna(value) else "carried_forward"
    )
    result.index.name = date_column
    return result.reset_index()
