import streamlit as st

st.set_page_config(
    page_title="NutriSmart AI",
    page_icon="🥗",
    layout="wide",
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
        food_scanner_page,
        model_page,
    ]
)

navigation.run()