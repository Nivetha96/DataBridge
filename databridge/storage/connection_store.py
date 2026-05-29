import json
import sqlite3


class ConnectionStore:

    def __init__(self, db_path="connections.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS connections (
                name TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                config TEXT NOT NULL
            )
        """)

        self.conn.commit()

    def save_connection(
        self,
        name: str,
        connection_type: str,
        config: dict
    ):
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO connections(name, type, config)
                VALUES (?, ?, ?)
            """, (name,connection_type,json.dumps(config)))
            self.conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Connection '{name}' already exists")

    def get_connection(self, name: str):
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT name, type, config
            FROM connections
            WHERE name = ?
        """, (name,))

        row = cursor.fetchone()

        if not row:
            return None

        return {
            "name": row[0],
            "type": row[1],
            "config": json.loads(row[2])
        }
