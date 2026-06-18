import pandas as pd
import streamlit as st

from src.database.meal_plan_repository import (
    activate_meal_plan,
    get_active_meal_plan,
    initialize_meal_plan_database,
    list_meal_plans,
    save_active_meal_plan,
)
from src.database.repository import (
    get_screening_history,
    initialize_database,
)
from src.recommendations.meal_plan_service import (
    DAY_NAMES,
    generate_meal_plan,
    plan_to_csv_bytes,
)
from src.services.history_service import get_latest_actual_record

initialize_database()
initialize_meal_plan_database()

st.title("🍽️ Meal Plan")
st.write(
    "Buat dan simpan rencana makan tujuh hari berdasarkan hasil "
    "skrining terbaru serta preferensi pengguna."
)

st.warning(
    "Meal plan ini bersifat edukasi untuk orang dewasa umum. "
    "Rencana bukan diet terapeutik, tidak menghitung kebutuhan "
    "kalori individual, dan tidak menggantikan dokter atau ahli gizi."
)

history = get_screening_history()
if history.empty:
    st.info(
        "Belum ada hasil skrining. Buka halaman **Skrining**, "
        "proses dan simpan hasil terlebih dahulu."
    )
    st.stop()

latest_record = get_latest_actual_record(history)

# Muat kembali plan aktif dari database setelah aplikasi dibuka ulang.
if "active_meal_plan" not in st.session_state:
    saved_plan = get_active_meal_plan()
    if saved_plan is not None:
        st.session_state["active_meal_plan"] = saved_plan

col_1, col_2, col_3 = st.columns(3)
col_1.metric(
    "Skor terbaru",
    f"{float(latest_record['risk_score']):.1f}/100",
)
col_2.metric(
    "Kategori skor",
    str(latest_record["risk_category"]),
)
col_3.metric(
    "Kategori BMI",
    str(latest_record["bmi_category"]),
)

st.caption(
    f"Skrining terbaru memiliki ID {int(latest_record['record_id'])}."
)

with st.form("meal_plan_preferences"):
    st.subheader("Preferensi rencana")
    pref_col_1, pref_col_2 = st.columns(2)

    with pref_col_1:
        diet_style = st.selectbox(
            "Pola makan",
            ["Umum", "Vegetarian"],
        )
        budget = st.selectbox(
            "Anggaran bahan makanan",
            ["Hemat", "Sedang"],
        )
        include_snack = st.checkbox(
            "Sertakan satu camilan terencana per hari",
            value=True,
        )

    with pref_col_2:
        avoided_allergens = st.multiselect(
            "Bahan yang perlu dihindari",
            [
                "Telur",
                "Susu",
                "Kacang",
                "Ikan/seafood",
                "Kedelai",
            ],
            help="Filter tidak menjamin bebas kontaminasi silang.",
        )
        special_diet_needed = st.selectbox(
            "Apakah Anda memerlukan diet medis khusus?",
            ["Tidak", "Ya atau tidak yakin"],
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
            "Gunakan bantuan dokter atau ahli gizi."
        )
    else:
        try:
            generated_plan = generate_meal_plan(
                latest_record=latest_record,
                diet_style=diet_style,
                budget=budget,
                avoided_allergens=avoided_allergens,
                include_snack=include_snack,
            )
        except ValueError as error:
            st.error(str(error))
        else:
            generated_plan["is_saved"] = False
            generated_plan["plan_id"] = None
            st.session_state["active_meal_plan"] = generated_plan

plan = st.session_state.get("active_meal_plan")

if plan:
    if int(plan["source_record_id"]) != int(latest_record["record_id"]):
        st.info(
            "Meal plan yang sedang tampil dibuat dari skrining lama. "
            "Buat plan baru untuk memakai hasil skrining terbaru."
        )

    if plan.get("is_saved"):
        st.success(
            f"Meal plan aktif tersimpan di database dengan ID "
            f"{plan['plan_id']}."
        )
    else:
        st.warning(
            "Meal plan ini belum tersimpan permanen. Klik tombol "
            "**Simpan sebagai meal plan aktif**."
        )

    st.divider()
    st.subheader("Prioritas dari skrining")

    for index, priority in enumerate(plan["priorities"], start=1):
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
                st.markdown(f"### {row['Waktu makan']}")
                st.write(f"**{row['Menu']}**")
                st.write(row["Susunan"])
                st.caption(row["Catatan"])

    st.subheader("Tabel lengkap")
    st.dataframe(
        plan["plan_table"],
        use_container_width=True,
        hide_index=True,
    )

    action_col_1, action_col_2 = st.columns(2)

    with action_col_1:
        save_button = st.button(
            "Simpan sebagai meal plan aktif",
            type="primary",
            use_container_width=True,
            disabled=bool(plan.get("is_saved")),
        )

    with action_col_2:
        st.download_button(
            "Unduh meal plan sebagai CSV",
            data=plan_to_csv_bytes(plan["plan_table"]),
            file_name="nutrismart_meal_plan_7_hari.csv",
            mime="text/csv",
            use_container_width=True,
        )

    if save_button:
        try:
            plan_id = save_active_meal_plan(plan)
        except Exception as error:
            st.error("Meal plan gagal disimpan.")
            st.exception(error)
        else:
            st.session_state["active_meal_plan"] = (
                get_active_meal_plan()
            )
            st.success(
                f"Meal plan berhasil disimpan sebagai plan aktif "
                f"dengan ID {plan_id}."
            )
            st.rerun()

    st.subheader("Pengingat umum")
    for reminder in plan["reminders"]:
        st.write(f"• {reminder}")

    with st.expander("Informasi teknis rencana"):
        st.write(
            {
                "plan_id": plan.get("plan_id"),
                "saved": bool(plan.get("is_saved")),
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
                "created_at": plan.get("created_at"),
            }
        )

st.divider()

with st.expander("Riwayat meal plan tersimpan"):
    plans = list_meal_plans()

    if plans.empty:
        st.caption("Belum ada meal plan yang tersimpan.")
    else:
        plans_display = plans.copy()
        plans_display["created_at"] = pd.to_datetime(
            plans_display["created_at"],
            errors="coerce",
        ).dt.strftime("%d-%m-%Y %H:%M:%S")

        plans_display["include_snack"] = (
            plans_display["include_snack"]
            .astype(bool)
            .map({True: "Ya", False: "Tidak"})
        )
        plans_display["is_active"] = (
            plans_display["is_active"]
            .astype(bool)
            .map({True: "Aktif", False: "Tidak aktif"})
        )

        plans_display = plans_display.rename(
            columns={
                "plan_id": "ID Plan",
                "created_at": "Dibuat",
                "source_record_id": "ID Skrining",
                "source_risk_score": "Skor sumber",
                "source_risk_category": "Kategori sumber",
                "diet_style": "Pola makan",
                "budget": "Anggaran",
                "include_snack": "Camilan",
                "is_active": "Status",
                "item_count": "Jumlah item",
            }
        )

        st.dataframe(
            plans_display,
            use_container_width=True,
            hide_index=True,
        )

        selected_plan_id = st.selectbox(
            "Pilih ID plan yang ingin dijadikan aktif",
            options=plans["plan_id"].astype(int).tolist(),
        )

        if st.button(
            "Jadikan plan terpilih sebagai aktif",
            use_container_width=True,
        ):
            if activate_meal_plan(int(selected_plan_id)):
                st.session_state["active_meal_plan"] = (
                    get_active_meal_plan()
                )
                st.success(
                    f"Meal plan ID {selected_plan_id} sekarang aktif."
                )
                st.rerun()
            else:
                st.error("Meal plan tidak ditemukan.")
