import sqlite3
import os

db_path = os.path.join("instance", "zenvora.db")

print("Database path:")
print(os.path.abspath(db_path))
print()

if not os.path.exists(db_path):
    print("❌ Database file NOT FOUND")
else:
    print("✅ Database file found")

    connection = sqlite3.connect(db_path)

    tables = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()

    print()
    print("Tables found:")
    for table in tables:
        print("-", table[0])

    connection.close()
