"""
Check what's actually in the database
"""
import sys
import os
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.database.connection import get_db_connection, init_connection_pool
import pandas as pd

init_connection_pool()

print("="*80)
print("DATABASE INVESTIGATION")
print("="*80)
print()

with get_db_connection() as conn:
    # Total entries
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM raw_journal_entries;")
    total = cursor.fetchone()[0]
    print(f"📊 TOTAL ENTRIES: {total}")
    print()
    
    # Entries with word count
    df = pd.read_sql("""
        SELECT 
            r.entry_id,
            r.created_at,
            r.raw_text,
            p.word_count,
            e.emotion,
            e.confidence
        FROM raw_journal_entries r
        LEFT JOIN processed_entries p ON r.entry_id = p.entry_id
        LEFT JOIN emotion_predictions e ON r.entry_id = e.entry_id
        ORDER BY r.created_at DESC
        LIMIT 20;
    """, conn)
    
    print("📝 LAST 20 ENTRIES:")
    print("-"*80)
    for idx, row in df.iterrows():
        date = pd.to_datetime(row['created_at']).strftime('%Y-%m-%d %H:%M')
        text = row['raw_text'][:60] + "..." if len(row['raw_text']) > 60 else row['raw_text']
        wc = int(row['word_count']) if pd.notna(row['word_count']) else 'NULL'
        em = row['emotion'] if pd.notna(row['emotion']) else 'NULL'
        conf = f"{row['confidence']:.0%}" if pd.notna(row['confidence']) else 'NULL'
        
        print(f"{date} | Words: {wc:>3} | {em:>12} {conf:>4} | {text}")
    
    print()
    print("-"*80)
    print()
    
    # Word count distribution
    cursor.execute("""
        SELECT 
            CASE 
                WHEN word_count < 10 THEN '< 10 words'
                WHEN word_count < 20 THEN '10-19 words'
                WHEN word_count < 30 THEN '20-29 words'
                WHEN word_count >= 30 THEN '30+ words'
                ELSE 'No word count'
            END as range,
            COUNT(*) as count
        FROM raw_journal_entries r
        LEFT JOIN processed_entries p ON r.entry_id = p.entry_id
        GROUP BY range
        ORDER BY range;
    """)
    
    print("📊 WORD COUNT DISTRIBUTION:")
    print("-"*80)
    for row in cursor.fetchall():
        print(f"  {row[0]:20} : {row[1]:>4} entries")
    
    print()
    
    # Emotion distribution
    cursor.execute("""
        SELECT 
            COALESCE(emotion, 'NULL/Missing') as emotion,
            COUNT(*) as count
        FROM raw_journal_entries r
        LEFT JOIN emotion_predictions e ON r.entry_id = e.entry_id
        GROUP BY emotion
        ORDER BY count DESC;
    """)
    
    print("😊 EMOTION DISTRIBUTION:")
    print("-"*80)
    for row in cursor.fetchall():
        print(f"  {row[0]:20} : {row[1]:>4} entries")
    
    print()
    
    # Date range
    cursor.execute("""
        SELECT 
            MIN(created_at) as first_entry,
            MAX(created_at) as last_entry
        FROM raw_journal_entries;
    """)
    
    dates = cursor.fetchone()
    print("📅 DATE RANGE:")
    print("-"*80)
    print(f"  First entry: {dates[0]}")
    print(f"  Last entry:  {dates[1]}")
    
    print()
    
    # Entries without emotions
    cursor.execute("""
        SELECT COUNT(*) 
        FROM raw_journal_entries r
        LEFT JOIN emotion_predictions e ON r.entry_id = e.entry_id
        WHERE e.emotion IS NULL;
    """)
    
    no_emotion = cursor.fetchone()[0]
    print("⚠️  MISSING DATA:")
    print("-"*80)
    print(f"  Entries WITHOUT emotion: {no_emotion}")
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM raw_journal_entries r
        LEFT JOIN processed_entries p ON r.entry_id = p.entry_id
        WHERE p.word_count IS NULL;
    """)
    
    no_processed = cursor.fetchone()[0]
    print(f"  Entries WITHOUT processing: {no_processed}")
    
    print()
    print("="*80)
    print()
    
    # Sample entries with issues
    if no_emotion > 0:
        print("🔍 SAMPLE ENTRIES WITHOUT EMOTIONS:")
        print("-"*80)
        
        df_issues = pd.read_sql("""
            SELECT r.entry_id, r.created_at, r.raw_text, p.word_count
            FROM raw_journal_entries r
            LEFT JOIN processed_entries p ON r.entry_id = p.entry_id
            LEFT JOIN emotion_predictions e ON r.entry_id = e.entry_id
            WHERE e.emotion IS NULL
            ORDER BY r.created_at DESC
            LIMIT 10;
        """, conn)
        
        for idx, row in df_issues.iterrows():
            date = pd.to_datetime(row['created_at']).strftime('%Y-%m-%d %H:%M')
            text = row['raw_text'][:70] + "..." if len(row['raw_text']) > 70 else row['raw_text']
            wc = int(row['word_count']) if pd.notna(row['word_count']) else 'NULL'
            print(f"  {date} | Words: {wc:>3} | {text}")

print()
print("💡 RECOMMENDATION:")
print("-"*80)
print("Based on the data above, you can decide:")
print("1. Delete ALL data and regenerate from scratch")
print("2. Delete only problematic entries (< 20 words)")
print("3. Keep everything and just add more good data")