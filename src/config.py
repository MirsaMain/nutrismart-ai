from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REFERENCE_DATA_DIR = DATA_DIR / "reference"

ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "best_model_pipeline.joblib"
MODEL_METADATA_PATH = ARTIFACTS_DIR / "model_metadata.json"
MODEL_METRICS_PATH = ARTIFACTS_DIR / "model_metrics.json"

DATABASE_PATH = DATA_DIR / "nutrismart.db"
DEFAULT_USER_ID = "local-user"

APP_NAME = "NutriSmart AI"
DEFAULT_CLASSIFICATION_THRESHOLD = 0.50

LOW_RISK_MAX = 40.0
MEDIUM_RISK_MAX = 70.0
