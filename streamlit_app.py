from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent

SIDEBAR_LOGO = (
    PROJECT_ROOT
    / "assets"
    / "celerates_nutrismart_logo.png"
)

SIDEBAR_ICON = (
    PROJECT_ROOT
    / "assets"
    / "celerates_nutrismart_icon.png"
)


st.set_page_config(
    page_title="Celerates NutriSmart",
    page_icon="🥗",
    layout="wide",
)


st.logo(
    str(SIDEBAR_LOGO),
    icon_image=str(SIDEBAR_ICON),
    size="large",
)


# CSS shadow header Anda dapat tetap berada di sini
st.markdown(
    """
    <style>
        /* Sembunyikan logo horizontal saat sidebar terbuka.
           icon_image tetap tersedia ketika sidebar ditutup. */
        [data-testid="stSidebar"][aria-expanded="true"]
        [data-testid="stSidebarHeader"] img,
        [data-testid="stSidebar"][aria-expanded="true"]
        [data-testid="stSidebarHeader"] a,
        [data-testid="stSidebar"][aria-expanded="true"]
        [data-testid="stLogo"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            width: 0 !important;
            height: 0 !important;
            min-width: 0 !important;
            min-height: 0 !important;
            max-width: 0 !important;
            max-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Sisakan ruang kecil hanya untuk tombol collapse sidebar. */
        [data-testid="stSidebar"][aria-expanded="true"]
        [data-testid="stSidebarHeader"] {
            height: 48px !important;
            min-height: 48px !important;
            padding: 8px 14px 4px 14px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
        }

        header[data-testid="stHeader"],
        header[data-testid="stHeader"] > div {
            background: #ffffff !important;
            background-color: #ffffff !important;
            background-image: none !important;
            opacity: 1 !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
        }

        header[data-testid="stHeader"] {
            border-bottom: 1px solid rgba(31, 41, 55, 0.16);

            box-shadow:
                0 5px 10px rgba(31, 41, 55, 0.18),
                0 14px 28px rgba(31, 41, 55, 0.16);

            z-index: 999999 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


home_page = st.Page(
    "app_pages/home.py",
    title="Beranda",
    icon="🏠",
)

screening_page = st.Page(
    "app_pages/screening.py",
    title="Skrining",
    icon="📋",
)

# Halaman lainnya dilanjutkan seperti sebelumnya

history_page = st.Page(
    "app_pages/history.py",
    title="Riwayat",
    icon="📈",
)

meal_plan_page = st.Page(
    "app_pages/meal_plan.py",
    title="Meal Plan",
    icon="🍽️",
)

workout_plan_page = st.Page(
    "app_pages/workout_plan.py",
    title="Workout Plan",
    icon="🏃",
)

food_scanner_page = st.Page(
    "app_pages/5_Food_Scanner.py",
    title="Food Scanner",
    icon="📸",
)

model_page = st.Page(
    "app_pages/model_information.py",
    title="Informasi Model",
    icon="🤖",
)

navigation = st.navigation(
    [
        home_page,
        screening_page,
        history_page,
        meal_plan_page,
        workout_plan_page,
        food_scanner_page,
        model_page,
    ]
)

navigation.run()