import streamlit as st

from src.features.bmi import calculate_bmi, classify_bmi

st.title("📋 Skrining")

with st.form("screening_form"):
    col1, col2 = st.columns(2)

    with col1:
        height_cm = st.number_input(
            "Tinggi badan (cm)",
            min_value=100.0,
            max_value=230.0,
            value=165.0,
            step=0.1,
        )
        weight_kg = st.number_input(
            "Berat badan (kg)",
            min_value=25.0,
            max_value=300.0,
            value=65.0,
            step=0.1,
        )

    with col2:
        physical_activity = st.selectbox(
            "Aktivitas fisik",
            ["Rendah", "Sedang", "Tinggi"],
        )
        high_calorie_food = st.selectbox(
            "Konsumsi makanan tinggi kalori",
            ["Jarang", "Kadang-kadang", "Sering"],
        )

    submitted = st.form_submit_button("Proses skrining")

if submitted:
    bmi = calculate_bmi(weight_kg, height_cm)
    bmi_category = classify_bmi(bmi)

    st.success("Data berhasil diproses.")
    metric1, metric2 = st.columns(2)
    metric1.metric("BMI", f"{bmi:.2f}")
    metric2.metric("Kategori BMI", bmi_category)

    st.warning(
        "Prediksi model AI belum diaktifkan. Model akan dihubungkan setelah "
        "eksperimen klasifikasi selesai."
    )
