import sqlite3

DB_FILE = "sensor_data.db"

def read_latest_5():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, timestamp, temperature, humidity, synced
            FROM readings
            ORDER BY id ASC
        """)

        rows = cursor.fetchall()

        for row in rows:
            print(row)

if __name__ == "__main__":
    read_latest_5()
