import sqlite3
from pathlib import Path


def get_connection(database_path: str | Path = "nutrismart.db"):
    return sqlite3.connect(database_path)
