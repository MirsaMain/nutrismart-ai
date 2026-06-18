import base64
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TITLE_ICON_PATH = (
    PROJECT_ROOT
    / "assets"
    / "celerates_nutrismart_icon.png"
)

TITLE_ICON_BASE64 = base64.b64encode(
    TITLE_ICON_PATH.read_bytes()
).decode("utf-8")



st.markdown(
    """
    <style>
        .hero-brand {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 0.5rem;
        }

        .hero-logo {
            width: 74px;
            height: 74px;
            object-fit: contain;
            flex-shrink: 0;
        }

        .hero-title {
            font-size: 3.15rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 0.5rem;
            color: #1f2937;
        }

        .hero-subtitle {
            font-size: 1.75rem;
            font-weight: 700;
            margin-top: 1.75rem;
            margin-bottom: 0.85rem;
            color: #111827;
        }

        .hero-description {
            font-size: 1.08rem;
            line-height: 1.75;
            color: #374151;
            margin-bottom: 1.25rem;
        }

        .feature-section-title {
            font-size: 1.65rem;
            font-weight: 750;
            margin-top: 2.2rem;
            margin-bottom: 0.35rem;
            color: #1f2937;
        }

        .feature-section-description {
            font-size: 1rem;
            color: #6b7280;
            margin-bottom: 1.2rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            min-height: 245px;
            border-radius: 18px;
            border: 1px solid #dfe8df;
            background: #ffffff;
            box-shadow: 0 6px 18px rgba(31, 41, 55, 0.06);
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #a9c8ad;
            box-shadow: 0 10px 24px rgba(31, 41, 55, 0.10);
            transition: 0.2s ease-in-out;
        }

        .card-icon {
            font-size: 2rem;
            margin-bottom: 0.4rem;
        }

        .card-title {
            font-size: 1.25rem;
            font-weight: 750;
            color: #1f2937;
            margin-bottom: 0.45rem;
        }

        .card-description {
            font-size: 0.98rem;
            line-height: 1.6;
            color: #4b5563;
            min-height: 92px;
        }

        .disclaimer-box {
            background: #eaf3ff;
            border: 1px solid #d7e8ff;
            border-radius: 14px;
            padding: 1rem 1.15rem;
            color: #135ca8;
            font-size: 1.02rem;
            margin-top: 1.25rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    f"""
    <div class="hero-brand">
        <img
            class="hero-logo"
            src="data:image/png;base64,{TITLE_ICON_BASE64}"
            alt="Celerates NutriSmart"
        />
        <div class="hero-title">Celerates NutriSmart</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-subtitle">Skrining risiko pola hidup terhadap obesitas</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-description">
        Aplikasi ini dirancang untuk membantu pengguna memahami apakah pola makan
        dan aktivitas fisiknya cenderung mendukung pengendalian berat badan atau
        meningkatkan risiko obesitas.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="disclaimer-box">
        Hasil aplikasi merupakan skrining dan edukasi, bukan diagnosis medis.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="feature-section-title">Jelajahi Fitur Celerates NutriSmart</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="feature-section-description">
        Gunakan fitur berikut untuk melakukan skrining, memantau perkembangan,
        dan mendapatkan rekomendasi pola makan serta aktivitas.
    </div>
    """,
    unsafe_allow_html=True,
)


row_one = st.columns(3, gap="large")

with row_one[0]:
    with st.container(border=True):
        st.markdown('<div class="card-icon">📋</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Skrining</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="card-description">
                Isi data tubuh dan kebiasaan hidup untuk mengetahui BMI,
                skor risiko pola hidup terhadap obesitas, serta interpretasi
                hasil secara ringkas.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "app_pages/screening.py",
            label="Buka Skrining",
            icon="➡️",
            use_container_width=True,
        )

with row_one[1]:
    with st.container(border=True):
        st.markdown('<div class="card-icon">📈</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Riwayat</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="card-description">
                Pantau perubahan skor pola hidup dan BMI dari waktu ke waktu
                melalui grafik harian serta tabel pembaruan skrining yang
                tersimpan.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "app_pages/history.py",
            label="Buka Riwayat",
            icon="➡️",
            use_container_width=True,
        )

with row_one[2]:
    with st.container(border=True):
        st.markdown('<div class="card-icon">🍽️</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Meal Plan</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="card-description">
                Buat rencana makan tujuh hari berdasarkan hasil skrining,
                preferensi pola makan, anggaran, serta bahan makanan yang
                perlu dihindari.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "app_pages/meal_plan.py",
            label="Buka Meal Plan",
            icon="➡️",
            use_container_width=True,
        )


row_two = st.columns(2, gap="large")

with row_two[0]:
    with st.container(border=True):
        st.markdown('<div class="card-icon">🏃</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Workout Plan</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="card-description">
                Susun jadwal aktivitas tujuh hari sesuai tingkat kebugaran,
                waktu yang tersedia, lokasi latihan, peralatan, dan kebutuhan
                dukungan gerak.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "app_pages/workout_plan.py",
            label="Buka Workout Plan",
            icon="➡️",
            use_container_width=True,
        )

with row_two[1]:
    with st.container(border=True):
        st.markdown('<div class="card-icon">📷</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Food Scanner</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="card-description">
                Unggah foto makanan untuk membantu mengenali jenis makanan
                menggunakan model klasifikasi gambar dan melihat hasil
                prediksi secara cepat.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "app_pages/5_Food_Scanner.py",
            label="Buka Food Scanner",
            icon="➡️",
            use_container_width=True,
        )
