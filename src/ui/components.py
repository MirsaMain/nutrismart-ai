import streamlit as st


def show_disclaimer() -> None:
    st.info(
        "Hasil merupakan skrining berbasis data dan tidak menggantikan "
        "pemeriksaan tenaga kesehatan."
    )
