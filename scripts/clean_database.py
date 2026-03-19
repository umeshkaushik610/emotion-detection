"""
Delete all unprocessed entries
"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.database.connection import get_db_connection, init_connection_pool

init_connection_pool()

print("="*60)
print("CLEANING UNPROCESSED ENTRIES")
print("="*60)
print()

with get_db_connection() as conn:
    cursor = conn.cursor()
    
    # Count entries to delete
    cursor.execute("""
        SELECT COUNT(*) 
        FROM raw_journal_entries r
        LEFT JOIN processed_entries p ON r.entry_id = p.entry_id
        WHERE p.entry_id IS NULL;
    """)
    
    count = cursor.fetchone()[0]
    print(f"Found {count} unprocessed entries to delete")
    
    if count == 0:
        print("✅ Nothing to delete!")
    else:
        response = input(f"\n⚠️  Delete {count} unprocessed entries? (yes/no): ")
        
        if response.lower() == 'yes':
            # Delete entries without processing
            cursor.execute("""
                DELETE FROM raw_journal_entries
                WHERE entry_id IN (
                    SELECT r.entry_id 
                    FROM raw_journal_entries r
                    LEFT JOIN processed_entries p ON r.entry_id = p.entry_id
                    WHERE p.entry_id IS NULL
                );
            """)
            
            conn.commit()
            print(f"✅ Deleted {count} unprocessed entries!")
            
            # Show what's left
            cursor.execute("SELECT COUNT(*) FROM raw_journal_entries;")
            remaining = cursor.fetchone()[0]
            print(f"📊 Remaining entries: {remaining}")
        else:
            print("❌ Cancelled")

print()
print("="*60)