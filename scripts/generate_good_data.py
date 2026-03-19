"""
Generate sample data using the WORKING ETL pipeline
"""
import sys
import os
from datetime import datetime, timedelta
import random

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.database.connection import get_db_connection, init_connection_pool
from src.etl.pipeline import process_journal_entry

init_connection_pool()

# Same emotion templates as before
EMOTION_TEMPLATES = {
    'joy': [
        "Today was absolutely wonderful! I spent quality time with my family, laughing and sharing stories over dinner. These simple moments of connection fill my heart with pure happiness and gratitude.",
        "I received amazing news at work today about my promotion! All the hard work and dedication finally paid off. I'm celebrating this achievement and feeling incredibly proud of myself.",
    ],
    'excitement': [
        "I just booked tickets for my dream vacation! I've been planning this trip for months and it's finally happening. The anticipation is making me incredibly excited and energized about the adventure ahead.",
        "Started learning a new skill today that I've always wanted to master. The first lesson was engaging and fun. I can't wait to practice more and see how much I'll improve.",
    ],
    'gratitude': [
        "I'm deeply thankful for the supportive friends in my life. They showed up for me today when I needed help, without hesitation. Their kindness reminds me how blessed I am to have such genuine relationships.",
        "Reflecting on my journey, I feel grateful for all the opportunities I've been given. Even the challenges taught me valuable lessons. I appreciate every experience that shaped who I am today.",
    ],
    'proud': [
        "I completed a challenging project that pushed me beyond my comfort zone. The final result exceeded my expectations and showcased skills I didn't know I had. I'm genuinely proud of this accomplishment.",
        "Helped a colleague solve a complex problem today using my expertise. Seeing their relief and appreciation made me realize how much I've grown professionally. My knowledge is making a real difference.",
    ],
    'sadness': [
        "Feeling a deep sense of loss today after saying goodbye to someone important. The emptiness is overwhelming and tears come easily. I'm allowing myself to grieve and process these painful emotions fully.",
        "Looking at old photos made me nostalgic for times that can never return. Life moves forward relentlessly and some moments are gone forever. The weight of this realization sits heavy on my heart.",
    ],
    'anger': [
        "I was treated unfairly at work and my contributions were completely overlooked. The injustice of the situation makes my blood boil. I deserve better recognition for my efforts and expertise in this field.",
        "Someone broke my trust by sharing private information I shared in confidence. The betrayal stings and I'm furious about this violation. My anger is justified and I need to address this boundary crossing.",
    ],
    'anxiety': [
        "Can't stop worrying about the upcoming presentation even though I'm well prepared. My mind keeps imagining everything that could go wrong. The nervous energy is exhausting and difficult to manage.",
        "Financial concerns are keeping me awake at night with racing thoughts about the future. The uncertainty feels overwhelming and I can't see clear solutions. This stress is affecting my daily functioning.",
    ],
    'fear': [
        "Received news about health concerns that triggered deep fear about my mortality and future. The uncertainty of what comes next is terrifying. I'm trying to stay calm but the fear is overwhelming.",
        "Walking alone late at night made me hyper-aware of every sound and shadow. The vulnerability of the situation activated my fight-or-flight response. Fear kept my heart racing until I reached safety.",
    ],
}

print("="*60)
print("GENERATING WORKING SAMPLE DATA")
print("="*60)
print()

# Generate 60 days = 120 entries
start_date = datetime(2025, 1, 1, 9, 0, 0)
emotions = list(EMOTION_TEMPLATES.keys())

created = 0
failed = 0

for day in range(60):
    for entry_num in range(2):
        # Calculate entry time
        hours_offset = 0 if entry_num == 0 else 11
        entry_time = start_date + timedelta(days=day, hours=hours_offset)
        
        # Pick emotion
        emotion_key = emotions[(day * 2 + entry_num) % len(emotions)]
        template = random.choice(EMOTION_TEMPLATES[emotion_key])
        
        # Add variation
        variations = [
            template,
            f"{template} The experience was truly memorable.",
            f"Reflecting on today: {template}",
        ]
        entry_text = random.choice(variations)
        
        # Process through WORKING pipeline
        result = process_journal_entry("Parth", entry_text, "manual")
        
        if result['success']:
            # Update the created_at timestamp to backdated time
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE raw_journal_entries 
                    SET created_at = %s 
                    WHERE entry_id = %s;
                """, (entry_time, result['entry_id']))
                conn.commit()
            
            created += 1
            if created % 10 == 0:
                print(f"✓ Created {created} entries...")
        else:
            failed += 1
            print(f"✗ Failed: {result.get('error')}")

print()
print(f"✅ Successfully created {created} entries")
print(f"❌ Failed: {failed} entries")
print()
print("="*60)
print("🎉 DONE! Refresh your dashboard!")
print("="*60)