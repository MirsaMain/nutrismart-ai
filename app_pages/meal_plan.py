import pandas as pd
import streamlit as st

from src.database.repository import (
    get_screening_history,
    initialize_database,
)
from src.recommendations.meal_plan_service import (
    DAY_NAMES,
    generate_meal_plan,
    plan_to_csv_bytes,
)
from src.services.history_service import (
    get_latest_actual_record,
)

initialize_database()

st.title("🍽️ Meal Plan")
st.write(
    "Halaman ini membuat rencana makan tujuh hari berbasis aturan "
    "dengan menggunakan hasil skrining terbaru dan preferensi pengguna."
)

st.warning(
    "Meal plan ini bersifat edukasi untuk orang dewasa umum. "
    "Rencana ini bukan diet terapeutik, tidak menghitung kebutuhan kalori "
    "individual, dan tidak menggantikan konsultasi dokter atau ahli gizi."
)

history = get_screening_history()

if history.empty:
    st.info(
        "Belum ada hasil skrining. Buka halaman **Skrining**, "
        "proses dan simpan hasil terlebih dahulu."
    )
    st.stop()

latest_record = get_latest_actual_record(history)

metric_col_1, metric_col_2, metric_col_3 = st.columns(3)

metric_col_1.metric(
    "Skor terbaru",
    f"{float(latest_record['risk_score']):.1f}/100",
)
metric_col_2.metric(
    "Kategori skor",
    str(latest_record["risk_category"]),
)
metric_col_3.metric(
    "Kategori BMI",
    str(latest_record["bmi_category"]),
)

st.caption(
    f"Rencana menggunakan skrining dengan ID "
    f"{int(latest_record['record_id'])}."
)

with st.form("meal_plan_preferences"):
    st.subheader("Preferensi rencana")

    preference_col_1, preference_col_2 = st.columns(2)

    with preference_col_1:
        diet_style = st.selectbox(
            "Pola makan",
            options=["Umum", "Vegetarian"],
            help=(
                "Vegetarian pada prototype ini dapat tetap menggunakan "
                "telur atau susu kecuali bahan tersebut dipilih untuk dihindari."
            ),
        )

        budget = st.selectbox(
            "Anggaran bahan makanan",
            options=["Hemat", "Sedang"],
        )

        include_snack = st.checkbox(
            "Sertakan satu camilan terencana per hari",
            value=True,
        )

    with preference_col_2:
        avoided_allergens = st.multiselect(
            "Bahan yang perlu dihindari",
            options=[
                "Telur",
                "Susu",
                "Kacang",
                "Ikan/seafood",
                "Kedelai",
            ],
            help=(
                "Fitur ini menyaring bahan yang disebutkan dalam template. "
                "Aplikasi tidak dapat menjamin bebas kontaminasi silang."
            ),
        )

        special_diet_needed = st.selectbox(
            "Apakah Anda memerlukan diet medis khusus?",
            options=[
                "Tidak",
                "Ya atau tidak yakin",
            ],
            help=(
                "Contoh: diabetes dengan terapi, penyakit ginjal, "
                "penyakit hati, alergi berat, kehamilan/menyusui, "
                "atau riwayat gangguan makan."
            ),
        )

    generate_button = st.form_submit_button(
        "Buat meal plan 7 hari",
        type="primary",
        use_container_width=True,
    )

if generate_button:
    if special_diet_needed == "Ya atau tidak yakin":
        st.error(
            "Meal plan otomatis tidak dibuat karena Anda menyatakan "
            "memerlukan atau mungkin memerlukan diet khusus. "
            "Gunakan bantuan dokter atau ahli gizi agar rencana aman."
        )
    else:
        try:
            plan = generate_meal_plan(
                latest_record=latest_record,
                diet_style=diet_style,
                budget=budget,
                avoided_allergens=avoided_allergens,
                include_snack=include_snack,
            )
        except ValueError as error:
            st.error(str(error))
        else:
            st.session_state["active_meal_plan"] = plan

plan = st.session_state.get("active_meal_plan")

if plan:
    if (
        int(plan["source_record_id"])
        != int(latest_record["record_id"])
    ):
        st.info(
            "Meal plan yang sedang tampil dibuat dari skrining lama. "
            "Klik **Buat meal plan 7 hari** untuk memperbaruinya."
        )

    st.divider()
    st.subheader("Prioritas dari skrining terbaru")

    for index, priority in enumerate(
        plan["priorities"],
        start=1,
    ):
        with st.expander(
            f"{index}. {priority['title']}",
            expanded=index == 1,
        ):
            st.write(priority["reason"])
            for action in priority["actions"]:
                st.write(f"• {action}")

    st.subheader("Rencana makan tujuh hari")

    tabs = st.tabs(DAY_NAMES)

    for tab, day_name in zip(tabs, DAY_NAMES):
        with tab:
            day_table = plan["plan_table"].loc[
                plan["plan_table"]["Hari"] == day_name
            ]

            for _, row in day_table.iterrows():
                st.markdown(
                    f"### {row['Waktu makan']}"
                )
                st.write(f"**{row['Menu']}**")
                st.write(row["Susunan"])
                st.caption(row["Catatan"])

    st.subheader("Tabel lengkap")

    st.dataframe(
        plan["plan_table"],
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Unduh meal plan sebagai CSV",
        data=plan_to_csv_bytes(
            plan["plan_table"]
        ),
        file_name="nutrismart_meal_plan_7_hari.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.subheader("Pengingat umum")

    for reminder in plan["reminders"]:
        st.write(f"• {reminder}")

    st.info(
        "Menu dapat ditukar sesuai ketersediaan bahan. "
        "Hentikan atau sesuaikan rencana jika timbul keluhan, "
        "reaksi alergi, atau kondisi kesehatan berubah."
    )

    with st.expander("Informasi teknis rencana"):
        st.write(
            {
                "source_record_id": plan["source_record_id"],
                "source_risk_score": round(
                    plan["source_risk_score"],
                    2,
                ),
                "source_risk_category": plan[
                    "source_risk_category"
                ],
                "diet_style": plan["diet_style"],
                "budget": plan["budget"],
                "avoided_allergens": plan[
                    "avoided_allergens"
                ],
                "include_snack": plan["include_snack"],
            }
        )
