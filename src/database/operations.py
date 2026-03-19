"""
Database CRUD operations for journal entries
"""
import sys
import os
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.database.connection import get_db_connection


def insert_journal_entry(user_id, text, source='manual'):
    """
    Insert a new journal entry into raw_journal_entries table
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                INSERT INTO raw_journal_entries (user_id, raw_text, source)
                VALUES (%s, %s, %s)
                RETURNING entry_id;
            """
            
            cursor.execute(query, (user_id, text, source))
            entry_id = cursor.fetchone()[0]
            cursor.close()
            
            print(f" Entry inserted with ID: {entry_id}")
            return entry_id
            
    except Exception as e:
        print(f" Error inserting entry: {e}")
        return None


def get_entry_by_id(entry_id):
    """Get a journal entry by ID"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT entry_id, user_id, raw_text, created_at, source
                FROM raw_journal_entries
                WHERE entry_id = %s;
            """
            
            cursor.execute(query, (entry_id,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    'entry_id': result[0],
                    'user_id': result[1],
                    'raw_text': result[2],
                    'created_at': result[3],
                    'source': result[4]
                }
            return None
            
    except Exception as e:
        print(f" Error fetching entry: {e}")
        return None


def get_all_entries(user_id='default_user', limit=10):
    """Get all journal entries for a user"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT entry_id, user_id, raw_text, created_at, source
                FROM raw_journal_entries
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s;
            """
            
            cursor.execute(query, (user_id, limit))
            results = cursor.fetchall()
            cursor.close()
            
            entries = []
            for row in results:
                entries.append({
                    'entry_id': row[0],
                    'user_id': row[1],
                    'raw_text': row[2],
                    'created_at': row[3],
                    'source': row[4]
                })
            
            return entries
            
    except Exception as e:
        print(f" Error fetching entries: {e}")
        return []


def delete_entry(entry_id):
    """Delete a journal entry"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = "DELETE FROM raw_journal_entries WHERE entry_id = %s;"
            cursor.execute(query, (entry_id,))
            cursor.close()
            
            print(f" Entry {entry_id} deleted")
            return True
            
    except Exception as e:
        print(f" Error deleting entry: {e}")
        return False


if __name__ == "__main__":
    """Test CRUD operations"""
    print("Testing CRUD operations...")
    
    # Test 1: Insert entry
    print("\nTesting INSERT...")
    entry_id = insert_journal_entry(
        user_id='test_user',
        text='Today was amazing! I feel so grateful and happy.',
        source='test'
    )
    
    # Test 2: Get entry by ID
    print("\nTesting GET by ID...")
    entry = get_entry_by_id(entry_id)
    if entry:
        print(f"   Found entry: {entry['raw_text'][:50]}...")
    
    # Test 3: Get all entries
    print("\nTesting GET ALL...")
    entries = get_all_entries('test_user', limit=5)
    print(f"   Found {len(entries)} entries")
    
    # Test 4: Delete entry
    print("\nTesting DELETE...")
    delete_entry(entry_id)
    
    print("\nAll CRUD tests completed!")