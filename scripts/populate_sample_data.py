"""
Generate realistic sample journal entries
Deletes old low-quality entries and creates proper distribution
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.database.connection import get_db_connection, init_connection_pool

# Initialize DB
init_connection_pool()


# 17 emotions with realistic 30-word entries
EMOTION_TEMPLATES = {
    'joy': [
        "Today was absolutely wonderful! I spent quality time with my family, laughing and sharing stories over dinner. These simple moments of connection fill my heart with pure happiness and gratitude.",
        "I received amazing news at work today about my promotion! All the hard work and dedication finally paid off. I'm celebrating this achievement and feeling incredibly proud of myself.",
        "The weather was perfect, so I went for a long walk in the park. The sunshine, fresh air, and beautiful scenery lifted my spirits completely. I feel rejuvenated and full of positive energy.",
        "I finished reading an inspiring book that changed my perspective on life. The insights were profound and motivating. I'm excited to apply these lessons and grow as a person.",
    ],
    'excitement': [
        "I just booked tickets for my dream vacation! I've been planning this trip for months and it's finally happening. The anticipation is making me incredibly excited and energized about the adventure ahead.",
        "Started learning a new skill today that I've always wanted to master. The first lesson was engaging and fun. I can't wait to practice more and see how much I'll improve.",
        "Got invited to an exclusive event next week! It's a fantastic networking opportunity with industry leaders. I'm thrilled about the possibilities and connections this could bring to my career.",
        "My creative project is gaining traction online! People are responding positively and sharing it widely. The momentum is building and I'm excited to see where this journey takes me.",
    ],
    'gratitude': [
        "I'm deeply thankful for the supportive friends in my life. They showed up for me today when I needed help, without hesitation. Their kindness reminds me how blessed I am to have such genuine relationships.",
        "Reflecting on my journey, I feel grateful for all the opportunities I've been given. Even the challenges taught me valuable lessons. I appreciate every experience that shaped who I am today.",
        "My health has been excellent lately and I don't take that for granted. Being able to move, think clearly, and enjoy life is a precious gift. I'm committed to maintaining this wellness.",
        "Someone thanked me today for something I did months ago. I had forgotten about it, but it clearly meant a lot to them. This reminder of positive impact fills me with gratitude.",
    ],
    'proud': [
        "I completed a challenging project that pushed me beyond my comfort zone. The final result exceeded my expectations and showcased skills I didn't know I had. I'm genuinely proud of this accomplishment.",
        "Helped a colleague solve a complex problem today using my expertise. Seeing their relief and appreciation made me realize how much I've grown professionally. My knowledge is making a real difference.",
        "Stuck to my fitness routine for three months straight without missing a day. The discipline and consistency I've built is remarkable. I'm proud of my commitment to personal health and growth.",
        "My presentation at the conference was well-received with thoughtful questions and positive feedback. I prepared thoroughly and it showed. This success validates all my hard work and preparation.",
    ],
    'confident': [
        "Faced a difficult conversation today and handled it with grace and clarity. I stated my boundaries assertively while remaining respectful. I trust my ability to navigate challenging interpersonal situations effectively.",
        "Took on a leadership role in our team project and everyone responded positively to my direction. I'm comfortable making decisions and guiding others. My confidence in my capabilities continues to grow stronger.",
        "Spoke up in the meeting with a solution that solved our biggest problem. My idea was implemented immediately. I'm learning to trust my instincts and contribute my valuable perspectives confidently.",
        "Tried something new today without fear of failure or judgment from others. I'm becoming more comfortable with uncertainty and growth. This self-assurance is transforming how I approach life's opportunities.",
    ],
    'optimism': [
        "Despite current challenges, I'm certain that things will work out for the best. I see opportunities everywhere and believe in positive outcomes. The future looks bright and full of amazing possibilities ahead.",
        "Starting a new chapter in my life with hope and excitement rather than fear. Change brings growth and I'm ready to embrace whatever comes. Good things are on the horizon.",
        "Even though the project faced setbacks, I know we'll find creative solutions together. Every obstacle is just a stepping stone. I'm looking forward to the breakthrough that's coming soon.",
        "The world feels full of potential today. I'm surrounded by opportunities to learn, grow, and make an impact. Tomorrow will bring even more chances to create something meaningful and wonderful.",
    ],
    'love': [
        "Spent a beautiful evening with my partner, just talking and being present together. These quiet moments of intimacy deepen our connection. I feel so fortunate to share my life with someone special.",
        "My heart swells with love when I think about my family's unconditional support. They accept me completely and celebrate my uniqueness. This foundation of love gives me strength to face anything life brings.",
        "Witnessed a random act of kindness today that restored my faith in humanity. Love exists everywhere if we look for it. I'm inspired to spread more compassion and care in my community.",
        "Called an old friend I haven't spoken to in months and we connected instantly. True friendship transcends time and distance. The love and understanding between us remains strong and beautiful.",
    ],
    'sadness': [
        "Feeling a deep sense of loss today after saying goodbye to someone important. The emptiness is overwhelming and tears come easily. I'm allowing myself to grieve and process these painful emotions fully.",
        "Looking at old photos made me nostalgic for times that can never return. Life moves forward relentlessly and some moments are gone forever. The weight of this realization sits heavy on my heart.",
        "Received disappointing news that crushed my hopes for something I wanted badly. The letdown feels profound and I'm struggling to find motivation. Sometimes life's rejections cut deeper than expected.",
        "The grey weather matches my melancholic mood perfectly today. Everything feels a bit slower and heavier than usual. I'm giving myself permission to feel sad without forcing positivity or rushing recovery.",
    ],
    'anger': [
        "I was treated unfairly at work and my contributions were completely overlooked. The injustice of the situation makes my blood boil. I deserve better recognition for my efforts and expertise in this field.",
        "Someone broke my trust by sharing private information I shared in confidence. The betrayal stings and I'm furious about this violation. My anger is justified and I need to address this boundary crossing.",
        "Stuck in traffic for hours due to completely preventable road planning failures. This waste of time is infuriating and disrespectful to everyone affected. The incompetence behind these decisions is absolutely maddening.",
        "Witnessed discrimination today that was blatant and harmful to someone vulnerable. The injustice ignited a fire of anger in me. I'm channeling this rage into motivation to advocate for change.",
    ],
    'annoyance': [
        "Small technical issues disrupted my workflow all day long and tested my patience. Each interruption broke my concentration and momentum. These constant minor frustrations are surprisingly draining over time.",
        "Someone kept talking during the movie despite repeated requests for quiet. The lack of basic consideration for others is irritating. Why is common courtesy so difficult for some people to practice?",
        "My plans were changed last minute without any consultation or explanation from others. The disrespect for my time is bothersome and inconsiderate. I'm annoyed by this pattern of thoughtless behavior.",
        "Dealing with inefficient processes at work that could easily be streamlined and improved. The resistance to simple changes is frustrating. These unnecessary complications waste everyone's valuable time and energy.",
    ],
    'anxiety': [
        "Can't stop worrying about the upcoming presentation even though I'm well prepared. My mind keeps imagining everything that could go wrong. The nervous energy is exhausting and difficult to manage.",
        "Financial concerns are keeping me awake at night with racing thoughts about the future. The uncertainty feels overwhelming and I can't see clear solutions. This stress is affecting my daily functioning.",
        "Waiting for important test results and the anticipation is nerve-wracking beyond words. Every possible scenario plays on repeat in my mind. The inability to control outcomes intensifies my anxious feelings.",
        "Social event tomorrow has me feeling tense and worried about interactions with people. What if I say something wrong or awkward? These intrusive thoughts are exhausting my mental energy completely.",
    ],
    'fear': [
        "Received news about health concerns that triggered deep fear about my mortality and future. The uncertainty of what comes next is terrifying. I'm trying to stay calm but the fear is overwhelming.",
        "Walking alone late at night made me hyper-aware of every sound and shadow. The vulnerability of the situation activated my fight-or-flight response. Fear kept my heart racing until I reached safety.",
        "Contemplating a major life change that could fail spectacularly and ruin everything I've built. The risk feels enormous and paralyzing. Fear of the unknown is holding me back from taking action.",
        "Someone I love is in danger and I feel powerless to protect them right now. The fear of losing them consumes my thoughts completely. This helplessness amplifies my terror to unbearable levels.",
    ],
    'disappointment': [
        "My hard work didn't lead to the outcome I expected and deserved after months of effort. The letdown is crushing and demotivating. I invested so much energy only to fall short of my goals.",
        "Someone I trusted let me down by not following through on their important promises to me. The disappointment cuts deep because I had high expectations. This failure feels like a personal betrayal.",
        "The event I looked forward to for weeks was canceled at the last minute without explanation. All my anticipation and excitement deflated instantly. Disappointment replaced what should have been joy.",
        "My performance didn't match my own standards despite giving my absolute best effort today. I'm disappointed in myself for not achieving what I thought I could. The gap between expectation and reality hurts.",
    ],
    'embarrassment': [
        "Made a factual mistake in front of colleagues and had to be corrected publicly. My face turned bright red as everyone noticed my error. The embarrassment lingered long after the moment passed by.",
        "Tripped and fell in a crowded public space with many people witnessing my clumsiness. The attention and concerned looks made my embarrassment even worse. I wished I could disappear into the ground completely.",
        "Realized I had been talking for minutes with food stuck in my teeth visibly. No one told me until much later when someone finally mentioned it kindly. The retroactive embarrassment is almost worse than immediate.",
        "Sent a message to the wrong person that was meant to be private and personal. The mistake was mortifying when I realized what happened. Embarrassment washed over me as I scrambled to explain.",
    ],
    'guilt': [
        "Forgot an important commitment to a friend and left them waiting for me alone. I feel terrible about breaking my promise and wasting their precious time. The guilt is eating at me constantly.",
        "Said something hurtful in anger that I immediately regretted but couldn't take back now. The pain I caused someone I care about weighs heavily on my conscience. I need to apologize sincerely.",
        "Should have spent more time with family instead of working late again all week long. Missing important moments makes me feel guilty about my misplaced priorities. I'm failing the people who matter most.",
        "Didn't speak up when I witnessed something wrong happening right in front of my eyes. My silence feels like complicity and the guilt is overwhelming now. I should have acted with more courage then.",
    ],
    'surprise': [
        "Received an unexpected gift from someone who remembered a small detail I mentioned months ago casually. The thoughtfulness caught me completely off guard. I'm pleasantly surprised by this touching gesture of care.",
        "Discovered a hidden talent I never knew I possessed while trying something completely new today. The revelation was shocking and exciting at the same time. Life still has the power to surprise me.",
        "Ran into an old friend in the most unlikely place imaginable after years apart. The coincidence felt almost magical and wonderfully serendipitous. We reconnected immediately like no time had passed at all.",
        "My quiet efforts were recognized publicly in a way I never anticipated or expected today. The surprise acknowledgment was humbling and deeply touching. Sometimes the universe rewards us when we least expect it.",
    ],
    'confusion': [
        "Received contradictory instructions from multiple sources and now I don't know which path to follow. The mixed messages are creating uncertainty and paralysis. I need clarity before I can move forward confidently.",
        "Trying to understand a complex concept that keeps eluding my grasp despite repeated attempts. The confusion is frustrating because I usually learn quickly. I need a different approach to breakthrough this mental block.",
        "Someone's behavior toward me changed drastically without explanation and I'm puzzled about what happened. The sudden shift doesn't make sense at all. I'm left guessing and confused about what I might have done.",
        "Looking at my life choices and feeling uncertain about the direction I'm heading in now. The confusion about my purpose and goals is unsettling. I need time to reflect and find clarity about my path.",
    ],
}


def delete_low_quality_entries():
    """Delete all entries with word count < 20"""
    print("🗑️  Deleting low-quality entries (word_count < 20)...")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get count before deletion
            cursor.execute("""
                SELECT COUNT(*) FROM raw_journal_entries r
                JOIN processed_entries p ON r.entry_id = p.entry_id
                WHERE p.word_count < 20;
            """)
            count_to_delete = cursor.fetchone()[0]
            
            if count_to_delete == 0:
                print("✅ No low-quality entries found")
                return
            
            # Delete cascading from raw_journal_entries
            cursor.execute("""
                DELETE FROM raw_journal_entries
                WHERE entry_id IN (
                    SELECT r.entry_id FROM raw_journal_entries r
                    JOIN processed_entries p ON r.entry_id = p.entry_id
                    WHERE p.word_count < 20
                );
            """)
            
            conn.commit()
            print(f"✅ Deleted {count_to_delete} low-quality entries")
            
    except Exception as e:
        print(f"❌ Error deleting entries: {e}")


def generate_sample_entries(num_days=60):
    """
    Generate sample entries with proper distribution
    
    Args:
        num_days: Number of days to generate (default 60 = 2 months)
    """
    print(f"📝 Generating sample entries for {num_days} days...")
    
    # Import AFTER adding to sys.path
    from src.etl.transform import clean_text, calculate_quality_score
    from src.ml.inference import EmotionClassifier
    
    # Initialize classifier once (reuse for all entries)
    print("Initializing emotion classifier...")
    classifier = EmotionClassifier()
    
    # Start from January 1, 2025
    start_date = datetime(2025, 1, 1, 9, 0, 0)
    
    # Get all emotions
    emotions = list(EMOTION_TEMPLATES.keys())
    
    entries_created = 0
    entries_failed = 0
    
    for day in range(num_days):
        # 2 entries per day
        for entry_num in range(2):
            # Morning entry (9 AM) or evening entry (8 PM)
            if entry_num == 0:
                entry_time = start_date + timedelta(days=day, hours=0)  # 9 AM
            else:
                entry_time = start_date + timedelta(days=day, hours=11)  # 8 PM
            
            # Pick emotion (cycle through all emotions evenly)
            emotion = emotions[(day * 2 + entry_num) % len(emotions)]
            
            # Pick random template for that emotion
            template = random.choice(EMOTION_TEMPLATES[emotion])
            
            # Add slight variation
            variations = [
                template,
                f"{template} The experience was truly memorable.",
                f"Reflecting on today: {template}",
                f"{template} I'm processing these feelings carefully.",
            ]
            
            entry_text = random.choice(variations)
            
            # Insert manually with custom timestamp
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Insert raw entry with custom created_at
                    cursor.execute("""
                        INSERT INTO raw_journal_entries (user_id, raw_text, source, created_at)
                        VALUES (%s, %s, %s, %s)
                        RETURNING entry_id;
                    """, ("Parth", entry_text, "manual", entry_time))
                    
                    entry_id = cursor.fetchone()[0]
                    
                    # Clean text
                    cleaned = clean_text(entry_text)
                    word_count = len(cleaned.split())
                    quality = calculate_quality_score(cleaned)  # Only 1 argument!
                    
                    # Insert processed entry
                    cursor.execute("""
                        INSERT INTO processed_entries 
                        (entry_id, cleaned_text, text_length, word_count, quality_score)
                        VALUES (%s, %s, %s, %s, %s);
                    """, (entry_id, cleaned, len(cleaned), word_count, quality))
                    
                    # Get emotion prediction
                    prediction = classifier.predict(cleaned)
                    
                    # Insert emotion prediction
                    cursor.execute("""
                        INSERT INTO emotion_predictions 
                        (entry_id, emotion, emotion_id, confidence, model_version)
                        VALUES (%s, %s, %s, %s, %s);
                    """, (entry_id, prediction['emotion'], prediction['emotion_id'], 
                          prediction['confidence'], prediction['model_version']))
                    
                    conn.commit()
                
                entries_created += 1
                
                if entries_created % 10 == 0:
                    print(f"  ✓ Created {entries_created} entries...")
                
            except Exception as e:
                entries_failed += 1
                print(f"  ✗ Failed to create entry: {e}")
    
    print(f"\n✅ Successfully created {entries_created} entries")
    if entries_failed > 0:
        print(f"❌ Failed to create {entries_failed} entries")


def main():
    print("=" * 60)
    print("SAMPLE DATA GENERATOR")
    print("=" * 60)
    print()
    
    # Step 1: Delete low-quality entries
    delete_low_quality_entries()
    print()
    
    # Step 2: Generate new sample entries
    # 60 days = 120 entries (2 per day)
    generate_sample_entries(num_days=60)
    
    print()
    print("=" * 60)
    print("✨ COMPLETE! Your dashboard should now have beautiful graphs!")
    print("=" * 60)
    print()
    print("📊 Refresh your Streamlit dashboard to see the results!")


if __name__ == "__main__":
    main()