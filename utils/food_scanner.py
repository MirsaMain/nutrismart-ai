from pathlib import Path
from typing import Dict, Any, List

import pandas as pd
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
from torchvision.models import efficientnet_b0


LABEL_TO_NUTRITION_NAME = {
    "ayam": "Ayam",
    "bakso": "Bakso",
    "belut_goreng": "Belut goreng",
    "mie_ayam": "Mie ayam",
    "nasi_goreng": "Nasi Goreng",
}


def normalize_text(text: str) -> str:
    return str(text).strip().lower()


def load_nutrition_data(csv_path: str | Path) -> pd.DataFrame:
    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"File nutrition.csv tidak ditemukan: {csv_path}")

    df = pd.read_csv(csv_path)

    required_columns = ["name", "calories", "proteins", "fat", "carbohydrate"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Kolom berikut tidak ada di nutrition.csv: {missing_columns}")

    df = df.copy()
    df["name"] = df["name"].astype(str).str.strip()
    df["normalized_name"] = df["name"].apply(normalize_text)

    for col in ["calories", "proteins", "fat", "carbohydrate"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


def build_model(num_classes: int):
    model = efficientnet_b0(weights=None)

    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)

    return model


def load_food_model(model_path: str | Path):
    model_path = Path(model_path)

    if not model_path.exists():
        raise FileNotFoundError(f"Model tidak ditemukan: {model_path}")

    device = "cpu"

    try:
        checkpoint = torch.load(
            model_path,
            map_location=device,
            weights_only=False
        )
    except TypeError:
        checkpoint = torch.load(model_path, map_location=device)

    class_names = checkpoint["class_names"]
    image_size = checkpoint.get("image_size", 224)

    model = build_model(num_classes=len(class_names))
    model.load_state_dict(checkpoint["model_state_dict"])

    model = model.to(device)
    model.eval()

    return model, class_names, image_size, device


def get_inference_transform(image_size: int):
    return transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
    ])


def predict_food_from_image(
    image: Image.Image,
    model,
    class_names: List[str],
    image_size: int,
    device: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:

    if image.mode != "RGB":
        image = image.convert("RGB")

    transform = get_inference_transform(image_size)
    input_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.softmax(outputs, dim=1)[0]

    k = min(top_k, len(class_names))
    values, indices = torch.topk(probabilities, k)

    results = []

    for value, index in zip(values, indices):
        label = class_names[int(index)]

        results.append({
            "label": label,
            "nutrition_name": LABEL_TO_NUTRITION_NAME.get(label, label),
            "confidence": float(value),
        })

    return results


def get_nutrition_by_label(df: pd.DataFrame, label: str):
    nutrition_name = LABEL_TO_NUTRITION_NAME.get(label, label)
    normalized_target = normalize_text(nutrition_name)

    matches = df[df["normalized_name"] == normalized_target]

    if matches.empty:
        return None

    row = matches.iloc[0]

    return {
        "label": label,
        "name": row["name"],
        "calories": row["calories"],
        "proteins": row["proteins"],
        "fat": row["fat"],
        "carbohydrate": row["carbohydrate"],
    }