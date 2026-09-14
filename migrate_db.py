import sqlite3
import os

DB_PATH = os.path.join("instance", "zenvora.db")

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

print("Updating Zenvora database...")
print()

# Columns that were added to the newer version of the application.
columns_to_add = {
    "user": {
        "created_at": "DATETIME"
    },
    "admin": {
        "created_at": "DATETIME"
    },
    "property": {
        "created_at": "DATETIME"
    },
    "cart": {
        "created_at": "DATETIME"
    },
    "wishlist": {
        "created_at": "DATETIME"
    },
    "inquiry": {
        "created_at": "DATETIME"
    },
    "deal": {
        "created_at": "DATETIME"
    }
}

for table, columns in columns_to_add.items():

    existing_columns = {
        row[1]
        for row in cursor.execute(f"PRAGMA table_info({table})").fetchall()
    }

    if not existing_columns:
        print(f"⚠️ Table '{table}' not found.")
        continue

    for column, data_type in columns.items():

        if column not in existing_columns:
            cursor.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} {data_type}"
            )
            print(f"✅ Added {table}.{column}")

        else:
            print(f"✔ {table}.{column} already exists")

connection.commit()
connection.close()

print()
print("===================================")
print("Zenvora database migration complete")
print("Existing data was NOT deleted.")
print("===================================")