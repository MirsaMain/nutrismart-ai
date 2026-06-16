import plotly.express as px


def create_risk_history_chart(history):
    return px.line(
        history,
        x="recorded_at",
        y="risk_score",
        markers=True,
        labels={
            "recorded_at": "Tanggal",
            "risk_score": "Skor risiko",
        },
    )
