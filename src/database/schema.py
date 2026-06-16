CREATE_SCREENING_RECORDS_TABLE = '''
CREATE TABLE IF NOT EXISTS screening_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    height_cm REAL NOT NULL,
    weight_kg REAL NOT NULL,
    bmi REAL NOT NULL,
    risk_score REAL,
    risk_category TEXT,
    created_at TEXT NOT NULL
);
'''
