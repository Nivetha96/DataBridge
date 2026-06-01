import sqlite3
import json


def query_connections(db_path="connections.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("SELECT name, type, config FROM connections").fetchall()

    if not rows:
        print("No connections found.")
        return

    print(f"{'NAME':<20} {'TYPE':<10} CONFIG")
    print(f"{'-'*20} {'-'*10} {'-'*40}")
    for row in rows:
        print(f"{row['name']:<20} {row['type']:<10} {row['config']}")

    conn.close()


if __name__ == "__main__":
    query_connections()
