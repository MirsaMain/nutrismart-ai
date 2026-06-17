import pandas as pd
import streamlit as st

from src.database.repository import (
    count_screening_records,
    get_screening_history,
    initialize_database,
)
from src.services.history_service import (
    build_daily_history,
    filter_daily_history,
    get_latest_actual_record,
)
from src.ui.charts import create_risk_history_chart

initialize_database()

st.title("📈 Riwayat Harian")
st.write(
    "Halaman ini menampilkan perkembangan skor pola hidup berdasarkan "
    "hasil skrining yang tersimpan."
)

st.caption(
    "Database hanya menyimpan pembaruan yang benar-benar dilakukan. "
    "Pada tanggal tanpa pembaruan, grafik meneruskan skor terakhir agar "
    "tren harian tetap terbaca."
)

history = get_screening_history()

if history.empty:
    st.info(
        "Belum ada riwayat skrining. Buka halaman Skrining, isi form, "
        "kemudian klik **Proses dan simpan skrining**."
    )
    st.stop()

latest_record = get_latest_actual_record(history)
total_records = count_screening_records()

metric_col_1, metric_col_2, metric_col_3, metric_col_4 = st.columns(4)

metric_col_1.metric(
    "Jumlah pembaruan",
    total_records,
)
metric_col_2.metric(
    "Skor terbaru",
    f"{float(latest_record['risk_score']):.1f}/100",
)
metric_col_3.metric(
    "Kategori terbaru",
    str(latest_record["risk_category"]),
)
metric_col_4.metric(
    "BMI terbaru",
    f"{float(latest_record['bmi']):.2f}",
)

period_label = st.selectbox(
    "Periode grafik",
    options=[
        "7 hari terakhir",
        "30 hari terakhir",
        "90 hari terakhir",
        "Semua riwayat",
    ],
    index=1,
)

period_mapping = {
    "7 hari terakhir": 7,
    "30 hari terakhir": 30,
    "90 hari terakhir": 90,
    "Semua riwayat": None,
}

daily_history = build_daily_history(history)
displayed_history = filter_daily_history(
    daily_history,
    period_mapping[period_label],
)

if displayed_history.empty:
    st.warning("Tidak ada data pada periode yang dipilih.")
    st.stop()

figure = create_risk_history_chart(displayed_history)
st.plotly_chart(
    figure,
    use_container_width=True,
)

actual_count = int(displayed_history["is_actual"].sum())
carried_count = int((~displayed_history["is_actual"]).sum())

st.caption(
    f"Periode ini memuat {actual_count} pembaruan aktual dan "
    f"{carried_count} tanggal dengan nilai yang diteruskan."
)

st.subheader("Data harian")

daily_table = displayed_history[
    [
        "recorded_date",
        "risk_score",
        "risk_category",
        "bmi",
        "bmi_category",
        "data_status",
    ]
].copy()

daily_table["recorded_date"] = pd.to_datetime(
    daily_table["recorded_date"]
).dt.strftime("%d-%m-%Y")

daily_table = daily_table.rename(
    columns={
        "recorded_date": "Tanggal",
        "risk_score": "Skor",
        "risk_category": "Kategori skor",
        "bmi": "BMI",
        "bmi_category": "Kategori BMI",
        "data_status": "Status data",
    }
)

daily_table["Skor"] = daily_table["Skor"].round(2)
daily_table["BMI"] = daily_table["BMI"].round(2)

st.dataframe(
    daily_table,
    use_container_width=True,
    hide_index=True,
)

with st.expander("Lihat seluruh pembaruan aktual"):
    actual_table = history[
        [
            "record_id",
            "recorded_at",
            "height_cm",
            "weight_kg",
            "bmi",
            "bmi_category",
            "risk_score",
            "risk_category",
        ]
    ].copy()

    actual_table["recorded_at"] = pd.to_datetime(
        actual_table["recorded_at"]
    ).dt.strftime("%d-%m-%Y %H:%M:%S")

    actual_table = actual_table.sort_values(
        "record_id",
        ascending=False,
    )

    actual_table = actual_table.rename(
        columns={
            "record_id": "ID",
            "recorded_at": "Waktu",
            "height_cm": "Tinggi (cm)",
            "weight_kg": "Berat (kg)",
            "bmi": "BMI",
            "bmi_category": "Kategori BMI",
            "risk_score": "Skor",
            "risk_category": "Kategori skor",
        }
    )

    actual_table["BMI"] = actual_table["BMI"].round(2)
    actual_table["Skor"] = actual_table["Skor"].round(2)

    st.dataframe(
        actual_table,
        use_container_width=True,
        hide_index=True,
    )
