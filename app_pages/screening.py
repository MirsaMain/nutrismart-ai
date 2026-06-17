import streamlit as st

from src.config import MODEL_PATH
from src.database.repository import (
    initialize_database,
    save_screening_record,
)
from src.features.input_schema import (
    ACTIVITY_SCORE_MAPPING,
    ALCOHOL_MAPPING,
    BETWEEN_MEALS_MAPPING,
    TECHNOLOGY_SCORE_MAPPING,
    TRANSPORT_MAPPING,
    VEGETABLE_SCORE_MAPPING,
    WATER_SCORE_MAPPING,
    YES_NO_MAPPING,
)
from src.models.inference import load_model
from src.services.screening_service import process_screening

initialize_database()

st.title("📋 Skrining Risiko Pola Hidup")
st.write(
    "Masukkan data tubuh dan kebiasaan hidup Anda. BMI digunakan untuk "
    "menampilkan kondisi berat badan saat ini, sedangkan model AI menilai "
    "pola makan dan aktivitas fisik."
)

st.info(
    "Hasil ini merupakan skrining berbasis data, bukan diagnosis medis. "
    "Setiap hasil yang berhasil diproses akan disimpan ke riwayat lokal."
)

if not MODEL_PATH.exists():
    st.error(
        "File model belum ditemukan. Pastikan file "
        "`artifacts/best_model_pipeline.joblib` tersedia."
    )
    st.stop()

try:
    model = load_model()
except Exception as error:
    st.error("Model tidak dapat dimuat.")
    st.exception(error)
    st.stop()

with st.form("screening_form", clear_on_submit=False):
    st.subheader("1. Data tubuh")
    body_col_1, body_col_2 = st.columns(2)

    with body_col_1:
        height_cm = st.number_input(
            "Tinggi badan (cm)",
            min_value=100.0,
            max_value=230.0,
            value=165.0,
            step=0.1,
        )

    with body_col_2:
        weight_kg = st.number_input(
            "Berat badan (kg)",
            min_value=25.0,
            max_value=300.0,
            value=65.0,
            step=0.1,
        )

    st.subheader("2. Pola makan")
    food_col_1, food_col_2 = st.columns(2)

    with food_col_1:
        favc_label = st.selectbox(
            "Sering mengonsumsi makanan tinggi kalori?",
            list(YES_NO_MAPPING.keys()),
        )
        fcvc_label = st.selectbox(
            "Tingkat konsumsi sayuran",
            list(VEGETABLE_SCORE_MAPPING.keys()),
            index=1,
        )
        ncp = st.slider(
            "Jumlah makanan utama per hari",
            1,
            4,
            3,
        )
        caec_label = st.selectbox(
            "Kebiasaan makan di antara waktu makan",
            list(BETWEEN_MEALS_MAPPING.keys()),
            index=1,
        )

    with food_col_2:
        water_label = st.selectbox(
            "Tingkat konsumsi air harian",
            list(WATER_SCORE_MAPPING.keys()),
            index=1,
        )
        scc_label = st.selectbox(
            "Apakah Anda memantau asupan kalori?",
            list(YES_NO_MAPPING.keys()),
        )
        calc_label = st.selectbox(
            "Frekuensi konsumsi alkohol",
            list(ALCOHOL_MAPPING.keys()),
        )

    st.subheader("3. Aktivitas dan perilaku")
    activity_col_1, activity_col_2 = st.columns(2)

    with activity_col_1:
        faf_label = st.selectbox(
            "Tingkat aktivitas fisik",
            list(ACTIVITY_SCORE_MAPPING.keys()),
            index=1,
        )
        tue_label = st.selectbox(
            "Tingkat penggunaan perangkat teknologi",
            list(TECHNOLOGY_SCORE_MAPPING.keys()),
            index=1,
        )

    with activity_col_2:
        transport_label = st.selectbox(
            "Moda transportasi utama",
            list(TRANSPORT_MAPPING.keys()),
            index=3,
        )

    submitted = st.form_submit_button(
        "Proses dan simpan skrining",
        type="primary",
        use_container_width=True,
    )

if submitted:
    lifestyle_input = {
        "FCVC": VEGETABLE_SCORE_MAPPING[fcvc_label],
        "NCP": float(ncp),
        "CH2O": WATER_SCORE_MAPPING[water_label],
        "FAF": ACTIVITY_SCORE_MAPPING[faf_label],
        "TUE": TECHNOLOGY_SCORE_MAPPING[tue_label],
        "FAVC": YES_NO_MAPPING[favc_label],
        "CAEC": BETWEEN_MEALS_MAPPING[caec_label],
        "SCC": YES_NO_MAPPING[scc_label],
        "CALC": ALCOHOL_MAPPING[calc_label],
        "MTRANS": TRANSPORT_MAPPING[transport_label],
    }

    try:
        result = process_screening(
            model=model,
            height_cm=height_cm,
            weight_kg=weight_kg,
            lifestyle_input=lifestyle_input,
        )

        record_id = save_screening_record(
            height_cm=height_cm,
            weight_kg=weight_kg,
            screening_result=result,
            lifestyle_input=lifestyle_input,
        )

        result["record_id"] = record_id
    except Exception as error:
        st.error("Data tidak dapat diproses atau disimpan.")
        st.exception(error)
    else:
        st.session_state["last_screening_result"] = result
        st.success(
            f"Hasil skrining berhasil disimpan ke riwayat "
            f"dengan ID {record_id}."
        )

result = st.session_state.get("last_screening_result")

if result:
    st.divider()
    st.subheader("Hasil skrining")

    col_1, col_2, col_3 = st.columns(3)
    col_1.metric("BMI", f"{result['bmi']:.2f}")
    col_2.metric("Kategori BMI", result["bmi_category"])
    col_3.metric(
        "Skor pola hidup",
        f"{result['risk_score']:.1f}/100",
    )

    st.progress(
        min(max(int(round(result["risk_score"])), 0), 100),
        text=f"Kategori skor: {result['risk_category']}",
    )

    if result["risk_category"] == "Tinggi":
        st.warning(result["interpretation"])
    elif result["risk_category"] == "Sedang":
        st.info(result["interpretation"])
    else:
        st.success(result["interpretation"])

    st.caption(
        "Skor berasal dari keluaran model dan bukan probabilitas klinis. "
        "Data hasil skrining disimpan di database SQLite lokal."
    )

    with st.expander("Lihat input yang dikirim ke model"):
        st.json(result["lifestyle_input"])

    with st.expander("Lihat keluaran teknis model"):
        st.write(
            {
                "record_id": result.get("record_id"),
                "predicted_class": result["predicted_class"],
                "obesity_probability": round(
                    result["obesity_probability"],
                    6,
                ),
                "risk_score": round(
                    result["risk_score"],
                    2,
                ),
                "risk_category": result["risk_category"],
            }
        )
