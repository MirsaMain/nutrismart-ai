import io
import sys
import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image


ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from utils.food_scanner import (
    load_nutrition_data,
    load_food_model,
    predict_food_from_image,
    get_nutrition_by_label,
)


DATA_PATH = ROOT_DIR / "data" / "nutrition.csv"
MODEL_PATH = ROOT_DIR / "models" / "food_model.pth"


st.set_page_config(
    page_title="Food Scanner",
    page_icon="📷",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def cached_load_nutrition(path: str):
    return load_nutrition_data(path)


@st.cache_resource(show_spinner=False)
def cached_food_model(path: str):
    return load_food_model(path)


def format_number(value, suffix):
    try:
        return f"{float(value):g} {suffix}"
    except Exception:
        return f"- {suffix}"


def show_nutrition_card(nutrition):
    st.subheader(f"🍽️ {nutrition['name']}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Calories", format_number(nutrition["calories"], "kcal"))

    with col2:
        st.metric("Protein", format_number(nutrition["proteins"], "g"))

    with col3:
        st.metric("Carbohydrate", format_number(nutrition["carbohydrate"], "g"))

    with col4:
        st.metric("Fat", format_number(nutrition["fat"], "g"))


st.title("📷 Food Scanner")

st.write(
    "Kamera → Food Recognition → Nama Makanan → nutrition.csv → Tampilkan Nutrisi"
)

if not DATA_PATH.exists():
    st.error(f"File nutrition.csv tidak ditemukan di: {DATA_PATH}")
    st.stop()

if not MODEL_PATH.exists():
    st.error(
        "Model Food Scanner belum ditemukan. "
        "Pastikan file models/food_model.pth sudah ada."
    )
    st.stop()

try:
    nutrition_df = cached_load_nutrition(str(DATA_PATH))
except Exception as e:
    st.error(f"Gagal membaca nutrition.csv: {e}")
    st.stop()

try:
    model, class_names, image_size, device = cached_food_model(str(MODEL_PATH))
except Exception as e:
    st.error(f"Gagal memuat model: {e}")
    st.stop()

st.success(f"Model Food Scanner aktif menggunakan device: {device}")

st.info(
    "Catatan: scanner ini mengenali jenis makanan dari foto. "
    "Nutrisi diambil dari nutrition.csv, bukan dihitung otomatis dari berat atau porsi makanan."
)

left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("1. Input Foto Makanan")

    input_mode = st.radio(
        "Pilih sumber gambar:",
        ["Kamera", "Upload Gambar"],
        horizontal=True,
    )

    image_file = None

    if input_mode == "Kamera":
        image_file = st.camera_input("Arahkan kamera ke makanan, lalu ambil foto")
    else:
        image_file = st.file_uploader(
            "Upload foto makanan",
            type=["jpg", "jpeg", "png"],
        )

    image = None
    image_key = None

    if image_file is not None:
        image_bytes = image_file.getvalue()
        image_key = hashlib.md5(image_bytes).hexdigest()

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        st.image(image, caption="Foto yang akan discan", use_container_width=True)


with right_col:
    st.subheader("2. Hasil Food Recognition")

    if image is None:
        st.warning("Ambil foto atau upload gambar terlebih dahulu.")
    else:
        scan_button = st.button(
            "🔍 Scan Makanan",
            type="primary",
            use_container_width=True,
        )

        if scan_button:
            with st.spinner("Model sedang mengenali makanan..."):
                results = predict_food_from_image(
                    image=image,
                    model=model,
                    class_names=class_names,
                    image_size=image_size,
                    device=device,
                    top_k=5,
                )

            st.session_state["food_scan_results"] = results
            st.session_state["food_scan_image_key"] = image_key

        if (
            "food_scan_results" in st.session_state
            and st.session_state.get("food_scan_image_key") == image_key
        ):
            results = st.session_state["food_scan_results"]

            score_map = {
                item["label"]: item["confidence"]
                for item in results
            }

            label_options = [item["label"] for item in results]

            selected_label = st.selectbox(
                "Pilih hasil prediksi yang paling sesuai:",
                label_options,
                format_func=lambda label: f"{label} ({score_map[label] * 100:.1f}%)",
            )

            nutrition = get_nutrition_by_label(nutrition_df, selected_label)

            if nutrition is not None:
                show_nutrition_card(nutrition)
            else:
                st.error(
                    f"Data nutrisi untuk label '{selected_label}' tidak ditemukan di nutrition.csv."
                )

            with st.expander("Lihat Top 5 Prediksi Model"):
                results_df = pd.DataFrame(results)
                results_df["confidence"] = (results_df["confidence"] * 100).round(2)

                results_df = results_df.rename(
                    columns={
                        "label": "Label Model",
                        "nutrition_name": "Nama di nutrition.csv",
                        "confidence": "Confidence (%)",
                    }
                )

                st.dataframe(results_df, use_container_width=True)


st.divider()

st.subheader("3. Makanan yang Bisa Dikenali Model")

st.write(
    """
    Model Food Scanner saat ini mendukung 5 makanan:

    - ayam
    - bakso
    - belut_goreng
    - mie_ayam
    - nasi_goreng
    """
)