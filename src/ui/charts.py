import pandas as pd
import plotly.graph_objects as go


def create_risk_history_chart(
    daily_history: pd.DataFrame,
) -> go.Figure:
    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=daily_history["recorded_date"],
            y=daily_history["risk_score"],
            mode="lines",
            name="Skor harian",
            customdata=daily_history[
                [
                    "data_status",
                    "risk_category",
                    "bmi",
                    "bmi_category",
                ]
            ],
            hovertemplate=(
                "<b>%{x|%d %b %Y}</b><br>"
                "Skor: %{y:.1f}/100<br>"
                "Status data: %{customdata[0]}<br>"
                "Kategori skor: %{customdata[1]}<br>"
                "BMI: %{customdata[2]:.2f}<br>"
                "Kategori BMI: %{customdata[3]}"
                "<extra></extra>"
            ),
        )
    )

    actual_rows = daily_history.loc[
        daily_history["is_actual"]
    ]

    figure.add_trace(
        go.Scatter(
            x=actual_rows["recorded_date"],
            y=actual_rows["risk_score"],
            mode="markers",
            name="Pembaruan aktual",
            marker={"size": 10, "symbol": "circle"},
            hovertemplate=(
                "<b>Pembaruan aktual</b><br>"
                "%{x|%d %b %Y}<br>"
                "Skor: %{y:.1f}/100"
                "<extra></extra>"
            ),
        )
    )

    carried_rows = daily_history.loc[
        ~daily_history["is_actual"]
    ]

    if not carried_rows.empty:
        figure.add_trace(
            go.Scatter(
                x=carried_rows["recorded_date"],
                y=carried_rows["risk_score"],
                mode="markers",
                name="Nilai diteruskan",
                marker={
                    "size": 6,
                    "symbol": "circle-open",
                },
                hovertemplate=(
                    "<b>Tidak ada pembaruan</b><br>"
                    "%{x|%d %b %Y}<br>"
                    "Skor diteruskan: %{y:.1f}/100"
                    "<extra></extra>"
                ),
            )
        )

    figure.add_hline(
        y=40,
        line_dash="dot",
        annotation_text="Batas sedang",
    )
    figure.add_hline(
        y=70,
        line_dash="dot",
        annotation_text="Batas tinggi",
    )

    figure.update_layout(
        title="Riwayat Harian Skor Pola Hidup",
        xaxis_title="Tanggal",
        yaxis_title="Skor pola hidup",
        yaxis={"range": [0, 100]},
        hovermode="x unified",
        legend_title_text="Jenis data",
    )

    return figure
