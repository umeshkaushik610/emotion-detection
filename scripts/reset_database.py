"""
STEP 1: Complete database reset
Deletes ALL data from all tables in the correct order (respecting foreign keys)
Run this FIRST, then run generate_rich_data.py
"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.chdir(project_root)

from src.database.connection import get_db_connection, init_connection_pool

init_connection_pool()

print("=" * 60)
print("  COMPLETE DATABASE RESET")
print("=" * 60)
print()

with get_db_connection() as conn:
    cursor = conn.cursor()

    # Check current counts
    tables = [
        "daily_emotion_summary",
        "emotion_predictions",
        "processed_entries",
        "raw_journal_entries",
    ]

    print("Current data:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} rows")

    print()
    response = input("⚠️  DELETE ALL DATA from all tables? Type 'yes' to confirm: ")

    if response.strip().lower() != "yes":
        print("❌ Cancelled.")
        sys.exit(0)

    # Delete in order: child tables first, then parent
    for table in tables:
        cursor.execute(f"DELETE FROM {table};")
        print(f"  ✓ Cleared {table}")

    conn.commit()

    print()
    print("✅ All tables cleared!")
    print()

    # Verify
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} rows")

print()
print("=" * 60)
print("Now run: python scripts/generate_rich_data.py")
print("=" * 60)
