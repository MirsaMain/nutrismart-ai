CREATE_SCREENING_RECORDS_TABLE = '''
CREATE TABLE IF NOT EXISTS screening_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    recorded_date TEXT NOT NULL,
    height_cm REAL NOT NULL,
    weight_kg REAL NOT NULL,
    bmi REAL NOT NULL,
    bmi_category TEXT NOT NULL,
    predicted_class INTEGER NOT NULL,
    obesity_probability REAL NOT NULL,
    risk_score REAL NOT NULL,
    risk_category TEXT NOT NULL,
    fcvc REAL,
    ncp REAL,
    ch2o REAL,
    faf REAL,
    tue REAL,
    favc TEXT,
    caec TEXT,
    scc TEXT,
    calc TEXT,
    mtrans TEXT,
    input_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
'''

CREATE_USER_DATE_INDEX = '''
CREATE INDEX IF NOT EXISTS idx_screening_user_date
ON screening_records (user_id, recorded_date);
'''

CREATE_USER_DATETIME_INDEX = '''
CREATE INDEX IF NOT EXISTS idx_screening_user_datetime
ON screening_records (user_id, recorded_at);
'''

# Digunakan untuk memperbarui database lama dari starter project.
OPTIONAL_MIGRATION_COLUMNS = {
    "recorded_date": "TEXT",
    "bmi_category": "TEXT",
    "predicted_class": "INTEGER",
    "obesity_probability": "REAL",
    "fcvc": "REAL",
    "ncp": "REAL",
    "ch2o": "REAL",
    "faf": "REAL",
    "tue": "REAL",
    "favc": "TEXT",
    "caec": "TEXT",
    "scc": "TEXT",
    "calc": "TEXT",
    "mtrans": "TEXT",
    "input_json": "TEXT",
}
