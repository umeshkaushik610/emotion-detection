"""
Complete ETL pipeline
Entry -> Clean -> Predict -> Store
"""

from distutils.command.config import config
import enum
import sys
import os
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.database.connection import get_db_connection, init_connection_pool
from src.database.operations import insert_journal_entry
from src.etl.transform import process_entry
from src.ml.inference import get_classifier

def process_journal_entry(user_id, raw_text, source='manual'):
    """
    Complete pipeline process

    Steps:
    1. Insert raw entry to database
    2. Clean and valdiate text
    3. Store processed entry
    4. Predict emotion using ML model
    5. Store prediction
    6. Update daily summary
    """

    print("\n" + "="*60)
    print("PROCESSING JOURNAL ENTRY")
    print("="*60)

    # Step 1: Insert raw entry
    print("\n Inserting raw entry...")
    entry_id = insert_journal_entry(user_id, raw_text, source)
    if not entry_id:
        return {'success': False, 'error': 'Failed to insert entry'}

    # Step 2: Clean and validate text
    print("\n Cleaning and validating text...")
    processed = process_entry(raw_text)
    print(f" Cleaned text: {processed['cleaned_text'][:50]}...")
    print(f" Word count: {processed['word_count']}")
    print(f" Quality Score: {processed['quality_score']}")

    if not processed['is_valid']:
        print(f" Warning: {processed['validation_message']}")

    # Step 3: Clean and validate text
    print(f" Storing processed entry...")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                INSERT INTO processed_entries
                (entry_id, cleaned_text, text_length, word_count, quality_score)
                VALUES(%s, %s, %s, %s, %s)
                RETURNING processed_id;
            """

            params = (
                int(entry_id),
                str(processed['cleaned_text']),
                int(processed['text_length']),
                int(processed['word_count']),
                float(processed['quality_score'])
            )

            cursor.execute(query, params)

            processed_id = cursor.fetchone()[0]
            cursor.close()
            print(f" Processed entry ID: {processed_id}")
    except Exception as e:
        print(f" Error storing processed entry: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


    # Step 4: Predict emotion
    print("\n Predicting emotion...")
    try:
        classifier = get_classifier()
        emotion, confidence, emotion_id = classifier.predict(processed["cleaned_text"])
        print(f" Emotion: {emotion}")
        print(f" Confidence: {confidence:.2%}")

        # top3 for additional context
        top_3 = classifier.predict_top_k(processed['cleaned_text'], k=3)
        print(f" Top 3 emotions:")
        for i, (em, score) in enumerate(top_3, 1):
            print(f" {i}. {em}: {score:.2%}")

    except Exception as e:
        print(f" Error predicting emotion: {e}")
        return {'success': False, 'error': str(e)}


    # Step 5: Store prediction
    print(f" \n Storing emotion prediction...")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query= """
                INSERT INTO emotion_predictions
                (entry_id, emotion, emotion_id, confidence, model_version)
                VALUES(%s, %s, %s, %s, %s)
                RETURNING prediction_id;
            """
            cursor.execute(query, (entry_id, emotion, emotion_id, confidence, 'v1.0'))
            prediction_id = cursor.fetchone()[0]
            cursor.close()
            print(f" Prediction ID: {prediction_id}")

    except Exception as e:
        print(f" Error storing prediction: {e}")
        return {'success': False, 'error': str(e)}


    # Step 6: Update daily summary
    print(f" Updating daily summary...")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                INSERT INTO daily_emotion_summary
                (user_id, date, emotion, entry_count, avg_confidence)
                VALUES(%s, CURRENT_DATE, %s, 1, %s)
                ON CONFLICT (user_id, date, emotion)
                DO UPDATE SET
                    entry_count = daily_emotion_summary.entry_count + 1,
                    avg_confidence = (daily_emotion_summary.avg_confidence + %s) / 2;
            """
            cursor.execute(query, (user_id, emotion, confidence, confidence))
            cursor.close()
            print(f" Daily summary updated")
    except Exception as e:
        print(f" Error updating summary: {e}")

    print("\n" + "="*60)
    print(" PIPELINE COMPLETE !")
    print("="*60)

    return {
        'success' : True,
        'entry_id' : entry_id,
        'emotion' : emotion,
        'confidence' : confidence,
        'quality_score' : processed['quality_score'],
        'word_count' : processed['word_count']
    }


if __name__ == "__main__":
    """Test the complete pipeline"""
    print("="*60)
    print("TESTING COMPLETE ETL PIPELINE")
    print("="*60)

    init_connection_pool()

    test_entries = [
        ("test_user", "Today was absolutely wonderful! I spent quality time with my family and feel so grateful for everything.", "test"),
        ("test_user", "I'm feeling really anxious about the upcomming exam. Can't stop worrying about it.", "test"),
        ("test_user", "Everything went wrong today. I'm so frustated and dissapointed.", "test"),
    ]

    for user_id, text, source in test_entries:
        print(f"\n Entry: {text[:60]}...")
        result = process_journal_entry(user_id, text, source)

        if result['success']:
            print(f"\n SUCCESS!")
            print(f" Entry ID: {result['entry_id']}")
            print(f" Emotion: {result['emotion']}")
            print(f" Confidence: {result['confidence']:.2%}")
        else:
            print(f"\n FAILED: {result['error']}")

        input(f"\n Press Enter to continue to next entry...")

    print("\n" + "="*60)
    print(" ALL PIPELINE TESTS COMPLETED!")
    print("="*60)
