import json
import sqlite3
from cryptography.fernet import Fernet

class ConnectionStore:

    def __init__(self, db_path="connections.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.fernet = Fernet(encryption_key)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS connections (
                name TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                config TEXT NOT NULL
            )
        """)

        self.conn.commit()

    def _encrypt(self, value: str) -> str:
        return self.fernet.encrypt(value.encode()).decode()

    def _decrypt(self, value: str) -> str:
        return self.fernet.decrypt(value.encode()).decode()
        
    def save_connection(
        self,
        name: str,
        connection_type: str,
        config: dict
    ):
        encrypted_config = self._encrypt(json.dumps(config))
        try:
            self.conn.execute("""
                INSERT INTO connections(name, type, config)
                VALUES (?, ?, ?)
            """, (name,connection_type,json.dumps(encrypted_config)))
            self.conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Connection '{name}' already exists")

    def get_connection(self, name: str) -> dict | None:
        row = self.conn.execute("""
            SELECT name, type, config
            FROM connections
            WHERE name = ?
        """, (name,)).fetchone()

        if not row:
            return None

        return {
            "name": row["name"],
            "type": row["type"],
            "config": json.loads(self._decrypt(row["config"]))
        }
