# database.py
import sqlite3
from datetime import datetime

from holiday_price_tracker.models import Tour


class Database:
    def __init__(self, db_path="db.sqlite3"):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tracked_tours (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    chat_id INTEGER NOT NULL,
                    price TEXT NOT NULL,
                    hotel_name TEXT,
                    location TEXT,
                    last_checked TIMESTAMP NOT NULL
                )
            """
            )
            conn.commit()

    def add_tour(self, tour):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR IGNORE INTO tracked_tours
                (url, chat_id, price, hotel_name,
                location, last_checked)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    tour.url,
                    tour.chat_id,
                    tour.price,
                    tour.hotel_name,
                    tour.location,
                    datetime.now(),
                ),
            )
            conn.commit()

    def remove_tour(self, url):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tracked_tours WHERE url = ?", (url,))
        conn.commit()
        conn.close()

    def get_all_tours(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT url, chat_id, price FROM tracked_tours")
        tours = [Tour(url, chat_id, price) for url, chat_id, price in cursor.fetchall()]
        conn.close()
        return tours

    def update_price(self, url, new_price):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE tracked_tours
            SET price = ?, last_checked = ?
            WHERE url = ?
        """,
            (new_price, datetime.now(), url),
        )
        conn.commit()
