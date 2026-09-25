import sqlite3
import os

DB_PATH = os.path.join("instance", "zenvora.db")

if not os.path.exists(DB_PATH):
    print("❌ Database not found:")
    print(DB_PATH)
    exit()

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

print("Updating Zenvora database...")
print()

# Columns that may be missing from older databases
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
        "deal_type": "VARCHAR(50)",
        "created_at": "DATETIME"
    }
}

for table, columns in columns_to_add.items():

    existing_columns = {
        row[1]
        for row in cursor.execute(
            f"PRAGMA table_info({table})"
        ).fetchall()
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


# Give old deals a default deal type
try:
    cursor.execute("""
        UPDATE deal
        SET deal_type = 'Sale'
        WHERE deal_type IS NULL OR deal_type = ''
    """)

    print("✅ Existing deals updated with default type: Sale")

except sqlite3.OperationalError:
    print("⚠️ Could not update deal_type")


connection.commit()
connection.close()

print()
print("===================================")
print("Zenvora database migration complete")
print("Existing data was NOT deleted.")
print("===================================")