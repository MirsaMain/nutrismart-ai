from src.database.connection import get_connection
from src.database.schema import CREATE_SCREENING_RECORDS_TABLE


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(CREATE_SCREENING_RECORDS_TABLE)
        connection.commit()
