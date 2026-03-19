"""
Generate sample journal entries for testing
"""

import sys
import os
from datetime import datetime, timedelta
import random

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.etl.pipeline import process_journal_entry
from src.database.connection import init_connection_pool

# same journal entries
SAMPLE_ENTRIES = {
    'joy' : [
        "Had an amazing day today! Everything went perfectly.",
        "Spent wonderful time with family, feeling blessed.",
        "Got great news at work, feeling on top of the world!",
        "Beautiful weather today, went for a lovely walk",
        "Laughed so much with friends today, best day ever!",
    ],
    'sadness' : [
        "Feeling down today, everything seems grey",
        "Missing my old friends, feeling lonely",
        "Bad day at work, feeling disappointed",
        "Struggling with motivation today",
        "Feeling overwhelmed and sad about everything.",
    ],
    'gratitude' : [
        "So grateful for my supportive family",
        "Thankful for all the opportunities I have",
        "Appreciating the small things in life today",
        "Feeling blessed to have such good friends.",
        "Grateful for my health and happiness."
    ],
    'excitement': [
        "Can't wait for the trip next week!",
        "So excited about the new project starting!",
        "Looking forward to the concert tonight!",
        "Thrilled about the new opportunity!",
        "Pumped up for the challenge ahead!",
    ],
    'anger': [
        "So frustrated with how things turned out.",
        "Angry about the unfair treatment.",
        "Really annoyed by what happened today.",
        "Fed up with all the problems.",
        "Irritated by the lack of support.",
    ],
    'fear': [
        "Scared about the future and what it holds.",
        "Afraid of failing at this important task.",
        "Worried something bad might happen.",
        "Feeling fearful about the changes ahead.",
        "Terrified of making the wrong decision.",
    ],
    'proud': [
        "Really proud of what I accomplished today!",
        "Feeling great about finishing the project.",
        "Proud of myself for pushing through.",
        "Achieved my goal, feeling accomplished!",
        "Did something I'm really proud of today.",
    ]
}

def generate_entries(num_days=30, entries_per_day=2):
    """
    Generate sample journal entries over the past N days
    """
    print("="*60)
    print(f"GENERATING SAMPLE DATA")
    print(f"Days: {num_days}, Avg entries/day: {entries_per_day}")
    print("="*60)

    init_connection_pool()

    total_generated = 0

    for day in range(num_days):
        # vary entries per day
        num_entries = random.randint(1, entries_per_day + 2)
        
        # calculate date (going backwards from today)
        entry_date = datetime.now() - timedelta(days=day)

        for _ in range(num_entries):
            # pick random emotion category
            emotion_category = random.choice(list(SAMPLE_ENTRIES.keys()))

            # pick random entry
            text = random.choice(SAMPLE_ENTRIES[emotion_category])

            variations = [
                f"{text} #{random.randint(1, 999)}",
                f"Day {day}: {text}",
                text,
                f"{text} Feeling this strongly today."
            ]
            text = random.choice(variations)

            #process entry
            print(f"\n Day --{day}: {text[:50]}...")
            result = process_journal_entry('sample_user', text, 'generated')

            if result['success']:
                print(f" Emotion: {result['emotion']} ({result['confidence']:.1%})")
                total_generated += 1
            else:
                print(f" Failed: {result.get('error', 'Unkown error')}")

    print("\n" + "="*60)
    print(f" GENERATED {total_generated} SAMPLE ENTIRES!")
    print("="*60)
    print("\n Refresh your dashboard to see the new data!")

if __name__ == "__main__":
    print("How many days of data would you like?")
    print(" 1. 7 days (quick test)")
    print(" 2. 30 days (recommended)")
    print(" 3. 90 days (extensive)")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        generate_entries(num_days=7, entries_per_day=2)
    elif choice == "2":
        generate_entries(num_days=30, entries_per_day=2)
    elif choice == "3":
        generate_entries(num_days=90, entries_per_day=1)
    else:
        print("Invalid choice. Running default (30 days)...")
        generate_entries(num_days=30, entries_per_day=2)