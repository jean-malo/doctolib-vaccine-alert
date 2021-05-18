import json
import sqlite3
from urllib.parse import urlparse

from src import settings


def get_centers():
    with open(get_centers_filename(), "r") as f:
        return json.load(f)


def get_centers_filename():
    comma = ","
    docto_location = urlparse(settings.DOCTOLIB_SEARCH_URL).path.split("/")[-1]
    return f"data/centers_{docto_location}{f'_{comma.join(settings.ALLOWED_ZIPCODES)}' if settings.ALLOWED_ZIPCODES else ''}.json"


def check_if_table_exists():
    conn = sqlite3.connect(settings.SQL_LITE_DB_PATH)
    try:
        cursor = conn.cursor()
        # get the count of tables with the name
        tablename = "SENT"
        cursor.execute(
            "SELECT count(name) FROM sqlite_master WHERE type='table' AND name=? ",
            (tablename,),
        )
        if cursor.fetchone()[0] == 1:
            print("Table to track messages sent exists.")
            pass
        else:
            print("Table to track messages sent does not exist. Creating it.")
            cursor.execute(
                """create table SENT (
                    profile_id INT not null, 
                    sent_at CHAR(140));"""
            )
            cursor.execute(
                """
                    create index idx_profile_sent on SENT (profile_id, sent_at);"""
            )
        conn.commit()
    finally:
        conn.close()
