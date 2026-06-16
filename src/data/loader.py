from pathlib import Path

import pandas as pd


def load_csv(path: str | Path) -> pd.DataFrame:
    csv_path = Path(path)

    if not csv_path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {csv_path}")

    return pd.read_csv(csv_path)
