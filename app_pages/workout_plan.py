import pandas as pd
import streamlit as st

from src.database.repository import (
    get_screening_history,
    initialize_database,
)
from src.database.workout_plan_repository import (
    activate_workout_plan,
    get_active_workout_plan,
    initialize_workout_plan_database,
    list_workout_plans,
    save_active_workout_plan,
)
from src.recommendations.workout_plan_service import (
    DAY_NAMES,
    generate_workout_plan,
    plan_to_csv_bytes,
)
from src.services.history_service import (
    get_latest_actual_record,
)

initialize_database()
initialize_workout_plan_database()

st.title("🏃 Workout Plan")
st.write(
    "Halaman ini membuat jadwal aktivitas tujuh hari berdasarkan "
    "hasil skrining terbaru, tingkat kebugaran, waktu, lokasi, "
    "peralatan, dan kebutuhan dukungan pengguna."
)

st.warning(
    "Workout plan ini bersifat edukasi untuk orang dewasa usia 18–64 "
    "tahun dan bukan program rehabilitasi atau resep medis. "
    "Jangan menggunakan plan otomatis untuk cedera akut atau gejala serius."
)

history = get_screening_history()

if history.empty:
    st.info(
        "Belum ada hasil skrining. Buka halaman **Skrining**, "
        "proses dan simpan hasil terlebih dahulu."
    )
    st.stop()

latest_record = get_latest_actual_record(history)

if "active_workout_plan" not in st.session_state:
    saved_plan = get_active_workout_plan()
    if saved_plan is not None:
        st.session_state["active_workout_plan"] = saved_plan

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
    f"Rencana menggunakan skrining terbaru dengan ID "
    f"{int(latest_record['record_id'])}."
)

with st.form("workout_plan_preferences"):
    st.subheader("Pemeriksaan keamanan")

    adult_confirmation = st.checkbox(
        "Saya berusia 18–64 tahun",
        value=False,
    )

    safety_status = st.selectbox(
        "Apakah Anda mengalami kondisi yang memerlukan pemeriksaan sebelum latihan?",
        options=[
            "Tidak",
            (
                "Ya atau tidak yakin: nyeri dada, pingsan/pusing berat, "
                "sesak tidak biasa, cedera akut, kehamilan/pascapersalinan, "
                "atau kondisi medis dengan batasan aktivitas"
            ),
        ],
    )

    st.subheader("Preferensi latihan")

    preference_col_1, preference_col_2 = st.columns(2)

    with preference_col_1:
        fitness_level = st.selectbox(
            "Tingkat kebugaran saat ini",
            options=[
                "Pemula",
                "Menengah",
                "Lanjutan",
            ],
        )

        active_days = st.selectbox(
            "Jumlah hari aktif per minggu",
            options=[3, 4, 5, 6],
            index=1,
        )

        session_minutes = st.selectbox(
            "Waktu yang tersedia per sesi",
            options=[10, 20, 30, 45],
            index=1,
            format_func=lambda value: f"{value} menit",
        )

        activity_preference = st.selectbox(
            "Aktivitas aerobik yang disukai",
            options=[
                "Jalan kaki",
                "Kardio low-impact",
                "Campuran",
            ],
        )

    with preference_col_2:
        training_location = st.selectbox(
            "Lokasi latihan",
            options=[
                "Di rumah",
                "Luar ruangan",
                "Gym",
            ],
        )

        equipment = st.selectbox(
            "Peralatan yang tersedia",
            options=[
                "Tanpa alat",
                "Resistance band",
                "Dumbbell ringan",
                "Peralatan gym",
            ],
        )

        support_option = st.selectbox(
            "Kebutuhan dukungan gerak",
            options=[
                "Tidak perlu dukungan khusus",
                "Perlu kursi atau pegangan",
            ],
            help=(
                "Pilih kursi atau pegangan bila membutuhkan latihan "
                "yang lebih stabil dan tanpa lompatan."
            ),
        )

    generate_button = st.form_submit_button(
        "Buat workout plan 7 hari",
        type="primary",
        use_container_width=True,
    )

if generate_button:
    if not adult_confirmation:
        st.error(
            "Workout plan otomatis hanya dibuat untuk pengguna yang "
            "mengonfirmasi usia 18–64 tahun."
        )
    elif safety_status != "Tidak":
        st.error(
            "Workout plan otomatis tidak dibuat karena terdapat atau "
            "mungkin terdapat kondisi yang memerlukan penilaian individual. "
            "Konsultasikan aktivitas yang aman dengan tenaga kesehatan."
        )
    else:
        try:
            generated_plan = generate_workout_plan(
                latest_record=latest_record,
                fitness_level=fitness_level,
                active_days=int(active_days),
                session_minutes=int(session_minutes),
                training_location=training_location,
                equipment=equipment,
                activity_preference=activity_preference,
                support_option=support_option,
            )
        except ValueError as error:
            st.error(str(error))
        else:
            generated_plan["is_saved"] = False
            generated_plan["plan_id"] = None
            st.session_state[
                "active_workout_plan"
            ] = generated_plan

plan = st.session_state.get("active_workout_plan")

if plan:
    latest_screening_id = int(latest_record["record_id"])
    plan_source_id = int(plan["source_record_id"])

    if plan_source_id != latest_screening_id:
        st.info(
            "Workout plan yang tampil dibuat dari skrining yang lebih lama. "
            "Buat plan baru agar menggunakan skrining terbaru."
        )

    if plan.get("is_saved"):
        st.success(
            f"Workout plan aktif tersimpan di database dengan ID "
            f"{plan['plan_id']}."
        )
    else:
        st.warning(
            "Workout plan ini belum tersimpan permanen. "
            "Klik **Simpan sebagai workout plan aktif**."
        )

    summary_col_1, summary_col_2, summary_col_3 = st.columns(3)
    summary_col_1.metric(
        "Hari aktif dipilih",
        plan["active_days"],
    )
    summary_col_2.metric(
        "Durasi per sesi",
        f"{plan['session_minutes']} menit",
    )
    summary_col_3.metric(
        "Total jadwal mingguan",
        f"{plan['planned_weekly_minutes']} menit",
    )

    if plan["planned_weekly_minutes"] < 150:
        st.info(
            "Jadwal ini masih berada di bawah sasaran umum 150 menit "
            "aktivitas aerobik sedang per minggu. Untuk pengguna pemula, "
            "jadwal lebih kecil dapat menjadi tahap awal sebelum ditingkatkan "
            "secara bertahap sesuai toleransi."
        )
    else:
        st.info(
            "Total jadwal sudah mendekati atau melampaui 150 menit. "
            "Tetap perhatikan kualitas gerak, pemulihan, dan respons tubuh."
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

    st.subheader("Jadwal tujuh hari")

    tabs = st.tabs(DAY_NAMES)

    for tab, day_name in zip(tabs, DAY_NAMES):
        with tab:
            row = plan["plan_table"].loc[
                plan["plan_table"]["Hari"] == day_name
            ].iloc[0]

            st.markdown(f"## {row['Judul']}")

            detail_col_1, detail_col_2, detail_col_3 = st.columns(3)
            detail_col_1.metric(
                "Jenis sesi",
                row["Jenis sesi"],
            )
            detail_col_2.metric(
                "Durasi",
                f"{int(row['Durasi (menit)'])} menit",
            )
            detail_col_3.metric(
                "Intensitas",
                row["Intensitas"],
            )

            st.markdown("### Pemanasan")
            st.write(row["Pemanasan"])

            st.markdown("### Latihan utama")
            st.write(row["Latihan utama"])

            st.markdown("### Pendinginan")
            st.write(row["Pendinginan"])

            st.caption(row["Catatan"])

    st.subheader("Tabel lengkap")

    display_table = plan["plan_table"].drop(
        columns=["day_index"],
        errors="ignore",
    )

    st.dataframe(
        display_table,
        use_container_width=True,
        hide_index=True,
    )

    action_col_1, action_col_2 = st.columns(2)

    with action_col_1:
        save_button = st.button(
            "Simpan sebagai workout plan aktif",
            type="primary",
            use_container_width=True,
            disabled=bool(plan.get("is_saved")),
        )

    with action_col_2:
        st.download_button(
            "Unduh workout plan sebagai CSV",
            data=plan_to_csv_bytes(
                plan["plan_table"]
            ),
            file_name="nutrismart_workout_plan_7_hari.csv",
            mime="text/csv",
            use_container_width=True,
        )

    if save_button:
        try:
            plan_id = save_active_workout_plan(plan)
        except Exception as error:
            st.error("Workout plan gagal disimpan.")
            st.exception(error)
        else:
            st.session_state[
                "active_workout_plan"
            ] = get_active_workout_plan()
            st.success(
                f"Workout plan berhasil disimpan sebagai plan aktif "
                f"dengan ID {plan_id}."
            )
            st.rerun()

    st.subheader("Pengingat keamanan")

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
                "source_bmi_category": plan[
                    "source_bmi_category"
                ],
                "fitness_level": plan["fitness_level"],
                "active_days": plan["active_days"],
                "session_minutes": plan[
                    "session_minutes"
                ],
                "training_location": plan[
                    "training_location"
                ],
                "equipment": plan["equipment"],
                "activity_preference": plan[
                    "activity_preference"
                ],
                "support_option": plan["support_option"],
                "planned_weekly_minutes": plan[
                    "planned_weekly_minutes"
                ],
                "created_at": plan.get("created_at"),
            }
        )

st.divider()

with st.expander("Riwayat workout plan tersimpan"):
    plans = list_workout_plans()

    if plans.empty:
        st.caption("Belum ada workout plan yang tersimpan.")
    else:
        plans_display = plans.copy()
        plans_display["created_at"] = pd.to_datetime(
            plans_display["created_at"],
            errors="coerce",
        ).dt.strftime("%d-%m-%Y %H:%M:%S")

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
                "source_bmi_category": "Kategori BMI",
                "fitness_level": "Tingkat kebugaran",
                "active_days": "Hari aktif",
                "session_minutes": "Menit per sesi",
                "planned_weekly_minutes": "Total menit",
                "training_location": "Lokasi",
                "equipment": "Peralatan",
                "activity_preference": "Preferensi",
                "support_option": "Dukungan",
                "is_active": "Status",
                "item_count": "Jumlah hari",
            }
        )

        st.dataframe(
            plans_display,
            use_container_width=True,
            hide_index=True,
        )

        plan_options = plans["plan_id"].astype(int).tolist()

        selected_plan_id = st.selectbox(
            "Pilih ID workout plan yang ingin dijadikan aktif",
            options=plan_options,
            index=0,
        )

        if st.button(
            "Jadikan workout plan terpilih sebagai aktif",
            use_container_width=True,
        ):
            success = activate_workout_plan(
                int(selected_plan_id)
            )

            if success:
                st.session_state[
                    "active_workout_plan"
                ] = get_active_workout_plan()
                st.success(
                    f"Workout plan ID {selected_plan_id} "
                    "sekarang menjadi plan aktif."
                )
                st.rerun()
            else:
                st.error("Workout plan tidak ditemukan.")
