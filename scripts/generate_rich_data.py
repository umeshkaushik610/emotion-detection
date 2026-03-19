"""
STEP 2: Generate rich sample data across ~60 days
Uses your ACTUAL ETL pipeline (process_journal_entry) so every entry
goes through: raw_journal_entries → processed_entries → emotion_predictions

Run reset_database.py FIRST, then run this.
"""
import sys
import os
from datetime import datetime, timedelta
import random
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.chdir(project_root)  # CRITICAL: so relative paths like 'data\models\tokenizer' work

from src.database.connection import get_db_connection, init_connection_pool
from src.etl.pipeline import process_journal_entry

init_connection_pool()

# ─────────────────────────────────────────────────────────────
# Rich journal templates — diverse, realistic, 30-80 words each
# The model will detect emotions naturally from the text
# ─────────────────────────────────────────────────────────────
ENTRIES = [
    # JOY / HAPPINESS
    "Today was one of those rare perfect days. The sun was warm, my coffee was just right, and I had the best conversation with an old friend I hadn't spoken to in years. We laughed until our stomachs hurt remembering college days. I feel so alive and content right now.",
    "My daughter took her first steps today! I was recording a video when she just stood up and walked three steps toward me. The look of surprise on her own face was priceless. I cried happy tears. This is what life is all about.",
    "Cooked a new recipe from scratch and it turned out incredible. My family went back for seconds and thirds. There's something deeply satisfying about nourishing the people you love with food you made with your own hands.",
    "Went for a morning walk in the park and everything felt magical. The birds were singing, the flowers were blooming, and a stranger smiled and waved at me. Sometimes the simplest things bring the greatest happiness.",
    "Had the most wonderful surprise birthday party. My friends decorated the entire apartment while I was at work. Walking through that door and seeing everyone I love gathered together made my heart so full.",

    # EXCITEMENT
    "Just got accepted into the program I've been dreaming about for two years! I can barely contain myself. My hands are literally shaking as I type this. All those late nights studying and preparing were absolutely worth it.",
    "Booked flights to Japan for next month! I've wanted to visit Tokyo and Kyoto since I was a teenager watching anime. The anticipation is killing me in the best way possible. Already planning which ramen shops to visit.",
    "Started my own side business today. The website is live, the first product is listed, and I already got two inquiries. The entrepreneurial energy is electrifying. I know there's a long road ahead but I'm thrilled to begin.",
    "Got the keys to my new apartment today! Walking through the empty rooms imagining where everything will go. The view from the balcony is incredible. I can't wait to make this space truly mine over the coming weeks.",
    "My team won the championship game in the final seconds! The crowd erupted and we all jumped and hugged each other. Pure adrenaline and disbelief. I'll never forget this incredible moment.",

    # GRATITUDE
    "My mentor stayed an extra hour after work just to help me prepare for my interview. She didn't have to do that. People like her remind me that genuine kindness still exists in this competitive world. I'm so thankful for her guidance.",
    "My parents sent me a care package with homemade food and a handwritten letter. Reading their words of encouragement thousands of miles from home brought tears to my eyes. I'm so grateful for their unconditional love and support.",
    "A stranger helped me change my flat tire in the pouring rain today. Refused to take any money and just said to pay it forward. Moments like this restore my faith in humanity and make me want to be a better person.",
    "Reflecting on this year, I realize how much I've grown. The struggles I faced taught me resilience. The friends who stayed showed me loyalty. The opportunities I received showed me grace. I'm thankful for every single experience.",
    "My therapist helped me see something about myself that I'd been blind to for years. That moment of clarity was worth every session. I'm grateful for professionals who dedicate their lives to helping others heal.",

    # PRIDE / ACCOMPLISHMENT
    "Finished my first marathon today! My legs are screaming but my spirit is soaring. Six months ago I couldn't run a mile without stopping. The discipline and consistency paid off beyond my wildest expectations.",
    "Presented my research to a room of two hundred people and absolutely nailed it. I spoke clearly, handled tough questions with confidence, and received a standing ovation. Months of preparation led to this proud moment.",
    "My code review came back with zero issues for the first time ever. My senior engineer said my architecture was elegant and well-thought-out. After years of learning and improving, I finally feel like a real professional developer.",
    "Got promoted to team lead today! My manager said it was my ability to both deliver results and uplift my teammates that stood out. I've worked so hard to develop both my technical and leadership skills.",
    "Published my first article and it got featured on the homepage. People are commenting with thoughtful responses and sharing it with their networks. Seeing my ideas resonate with strangers feels incredibly validating.",

    # SADNESS
    "My best friend is moving to another country next week. We've been inseparable since kindergarten. I know this is a great opportunity for her, but the thought of not having her nearby makes my chest ache with sadness.",
    "Found my grandfather's old watch while cleaning the attic. He passed away three years ago but holding something he wore every day made it feel like yesterday. I sat there crying, missing his stories and his warm laugh.",
    "Another rejection letter today. That's the fifteenth this month. I know I should keep trying but each one chips away at my confidence a little more. Some days it's hard to see any light at the end of this tunnel.",
    "Visited my childhood home and found it completely renovated by the new owners. The tree I used to climb is gone. My room is now a storage space. Those memories feel further away than ever and it makes me deeply sad.",
    "My pet had to be put down today after fourteen years together. She was there through every breakup, every move, every late night. The house feels unbearably empty without her. I keep expecting to hear her footsteps.",

    # ANGER
    "My coworker took full credit for the project I spent three months building. In the meeting, they presented MY work as entirely theirs while I sat there in shock. The injustice makes my blood absolutely boil.",
    "Found out the contractor overcharged me by thousands and did substandard work on purpose. When I confronted him, he was dismissive and rude. I'm furious at the dishonesty and the complete lack of accountability.",
    "Someone vandalized my car overnight for no apparent reason. Keyed the entire side and smashed a mirror. The senseless destruction of something I worked hard to afford makes me incredibly angry and frustrated.",
    "My landlord refuses to fix the broken heating despite multiple written requests over two months. It's freezing in the apartment. The negligence and disregard for tenant rights is absolutely infuriating.",
    "Got into an argument with a family member who constantly dismisses my career choices. Every holiday they make passive-aggressive comments about my decisions. I'm tired of defending my life to people who should support me.",

    # ANXIETY
    "Can't sleep because I keep replaying tomorrow's job interview in my head. What if I blank on a question? What if they don't like me? My stomach is in knots and my mind won't stop racing through worst-case scenarios.",
    "The doctor said they found something unusual in my blood work and need to run more tests. The waiting is absolute torture. My mind keeps jumping to the worst possible conclusions even though it might be nothing.",
    "My savings are running dangerously low and rent is due next week. I've applied to dozens of jobs with no callbacks. The financial pressure is crushing and I wake up every morning with this heavy weight of worry on my chest.",
    "Presenting to the board of directors tomorrow and I'm terrified of failing in front of everyone. I've practiced a hundred times but the stakes feel impossibly high. My hands are sweating just thinking about it.",
    "My relationship feels like it's on shaky ground and I don't know how to fix it. Every conversation turns into an argument. The uncertainty about our future together keeps me up at night filled with dread.",

    # FEAR
    "Heard strange noises downstairs at three in the morning while home alone. My heart was pounding so hard I could hear it in my ears. Called a friend to stay on the phone with me while I checked every room.",
    "Almost got into a serious car accident on the highway today. A truck swerved into my lane and I had to slam the brakes. My whole body was trembling for an hour afterward. Life felt incredibly fragile in that moment.",
    "The earthquake warning went off on my phone and the building started shaking. Those ten seconds of not knowing if the ceiling would hold felt like an eternity. Even after it stopped, the fear lingered for hours.",
    "Walking through the dark parking garage after my night shift when I heard footsteps behind me getting faster. Pure terror shot through my body. Turned out to be another employee rushing to their car but the fear was real.",
    "Got a call from the hospital about my mother. Those seconds between the phone ringing and hearing it wasn't serious were the most terrifying of my life. The vulnerability of loving someone so much is frightening.",

    # DISAPPOINTMENT
    "The vacation I planned for months was ruined by terrible weather every single day. Hotels were mediocre, the food was overpriced, and nothing went as expected. I feel deflated after looking forward to this trip for so long.",
    "My friend cancelled our plans for the fifth time in a row with a vague excuse. I'm starting to realize that maybe this friendship isn't as important to them as it is to me. That realization stings deeply.",
    "Didn't get the apartment I had my heart set on. Someone offered above asking price and I simply couldn't compete. I had already imagined my whole life there. Starting the search over feels defeating.",
    "The movie everyone recommended turned out to be incredibly mediocre. But more than the movie, I'm disappointed in myself for once again setting expectations too high based on other people's enthusiasm.",
    "My team lost the deal we've been working on for six months. The client went with a competitor despite our superior proposal. All those late nights and weekends feel like they were for nothing.",

    # OPTIMISM
    "Despite all the setbacks this year, I genuinely believe next year will be different. I've learned from every mistake, built better habits, and surrounded myself with supportive people. The future looks bright.",
    "Had a great brainstorming session today where everything clicked. New ideas are flowing and I can see a clear path forward for the project. When things align like this, it reminds me why I love what I do.",
    "The interview went better than expected and they seemed genuinely impressed with my portfolio. Even if I don't get this one, I now know I can perform well under pressure. Things are looking up for my career.",
    "Started therapy last week and already feel a shift in perspective. It's early days but I'm hopeful that working through these patterns will lead to real lasting change. Investing in myself feels empowering.",
    "My savings finally hit the milestone I've been working toward for two years. It proves that small consistent actions compound over time. I'm excited about what this financial cushion will enable me to do next.",

    # LOVE
    "Watching my partner sleep this morning, I was overwhelmed by how much I love this person. The way they scrunch their nose while dreaming, the warmth of their hand on mine. I'm so lucky to share my life with them.",
    "My child drew a picture of our family today with a big sun and wrote 'I love you mommy' in wobbly letters. I'm going to frame it and keep it forever. The pure unconditional love of a child is the most beautiful thing.",
    "Long phone call with my sister today. Even though we live in different countries now, our bond hasn't weakened at all. Family love transcends distance and time. She always knows exactly what to say.",
    "Adopted a rescue dog today. The moment he put his head on my lap in the shelter, I knew he was coming home with me. Already can't imagine life without this little furry companion by my side.",
    "Anniversary dinner with my spouse tonight. Fifteen years and somehow I love them more than the day we met. We've weathered storms together and come out stronger every time. True love is a daily choice.",

    # CONFUSION
    "Got conflicting advice from two managers today about the project direction. One wants agile, the other wants waterfall. I'm stuck in the middle with no clear path forward and a deadline approaching fast.",
    "Received a cryptic message from a friend that I've been overanalyzing for hours. Can't tell if they're upset with me or just having a bad day. The ambiguity is driving me crazy and I don't want to make it worse.",
    "The new company policy changes were announced but the communication was so unclear that nobody in the office knows what's actually changing. We spent the whole day speculating instead of working productively.",
    "Trying to understand this new framework and the documentation is contradictory in several places. One section says do X, another says never do X. I'm going in circles and getting more confused with each attempt.",
    "My feelings about this relationship are a tangled mess. Some days I'm completely in love, other days I feel suffocated. I can't figure out if this ambivalence is normal or a sign that something is fundamentally wrong.",

    # EMBARRASSMENT
    "Called my teacher 'mom' in front of the entire class today. I'm twenty-five. The silence that followed was deafening before everyone burst out laughing. I wanted the earth to swallow me whole.",
    "Tripped and fell in the middle of a crowded restaurant while carrying a tray of food. Everything went flying. The entire place went quiet and stared. My face was burning red as I cleaned up the mess.",
    "Accidentally sent a personal text meant for my partner to my entire work group chat. It wasn't inappropriate but it was definitely too affectionate for professional eyes. I want to disappear from this planet.",
    "Realized halfway through a confident presentation that my slides had several embarrassing typos that completely changed the meaning of key points. The audience noticed before I did based on their confused expressions.",
    "Waved enthusiastically at someone I thought was my friend across the street. It was a complete stranger who looked at me like I was insane. Then my actual friend saw the whole thing and won't stop teasing me.",

    # GUILT
    "Forgot my mother's birthday yesterday. She didn't say anything which somehow makes it worse. She does so much for me and I couldn't even remember to make a simple phone call. The guilt is eating me alive.",
    "Snapped at my partner over something trivial after a long stressful day at work. The hurt in their eyes haunts me. They didn't deserve that. I need to do better at separating work stress from my home life.",
    "Ate an entire cake that my roommate baked for a party tomorrow. I was stress-eating and before I knew it, the whole thing was gone. Now I have to confess and find a way to replace it before the guests arrive.",
    "Told a white lie to avoid a social event and then got caught when someone posted photos of me somewhere else. The disappointment in my friend's face was crushing. Honesty would have been so much simpler.",
    "Didn't visit my grandmother in the hospital because I was too busy with work. She passed away two days later. I'll never forgive myself for prioritizing a deadline over spending those final precious moments with her.",

    # ANNOYANCE
    "My neighbor's dog has been barking non-stop for three hours straight. I've asked them politely twice. I've left notes. Nothing changes. The constant noise is fraying my last nerve and ruining my ability to focus.",
    "Stuck behind someone in the express checkout lane with forty items. The sign clearly says fifteen or fewer. Then they decided to pay with a check and had to hunt for a pen. Some people are truly oblivious.",
    "The Wi-Fi has dropped for the fourth time today during important video calls. My internet provider keeps giving me the same scripted troubleshooting steps that never actually fix anything. Beyond frustrating.",
    "Coworker keeps eating my clearly labeled lunch from the shared fridge. I've written my name on it. I've sent emails. I've even tried hiding it behind other items. The blatant disregard is maddening.",
    "Every single app on my phone wants to send notifications about things I don't care about. I spend more time dismissing alerts than actually using the apps. Technology was supposed to make life simpler.",

    # NEUTRAL / REFLECTIVE
    "Spent the afternoon organizing my bookshelf and reflecting on how my reading tastes have changed over the years. It's interesting to see my intellectual journey mapped out in book spines. Not good or bad, just observing.",
    "Quiet Sunday with nothing planned. Did laundry, made lunch, watched the rain. Sometimes uneventful days are exactly what you need. No emotional highs or lows, just peaceful existence.",
    "Commute to work was the same as always. Coffee from the usual place, same playlist, same route. There's a comfort in routine even if it's not exciting. Predictability has its own kind of value.",
    "Reorganized my desk today. Everything has a place now. Cleaned out old files, sharpened pencils, wiped down the monitor. The mundane act of tidying felt meditative rather than like a chore.",
    "Read an article about how different cultures process emotions differently. Fascinating from an academic perspective. Made me think about my own cultural conditioning and how it shapes my emotional responses.",

    # SURPRISE
    "Ran into my childhood best friend at a coffee shop across the country! Neither of us knew the other lived here. What are the odds? We talked for three hours catching up on twenty years of life. Absolutely surreal.",
    "Got a completely unexpected bonus at work today. Had no idea it was coming. Apparently the leadership team wanted to recognize effort on the last quarter's project. A pleasant shock to start the week.",
    "Opened my email to find a message from a publisher interested in my blog posts. They want to discuss turning them into a book! I never imagined anyone besides my friends actually read my writing.",
    "My plant that I thought was completely dead somehow sprouted new leaves after I was about to throw it out. Life finds a way. This little plant just became my symbol of resilience and unexpected comebacks.",
    "Discovered that my quiet introverted coworker is actually an incredible singer when I stumbled upon their YouTube channel with thousands of followers. You truly never know the hidden talents people carry.",
]

# Shuffle for natural variety
random.shuffle(ENTRIES)

print("=" * 60)
print("  GENERATING RICH JOURNAL DATA")
print("=" * 60)
print()

# Verify tables are empty first
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM raw_journal_entries;")
    existing = cursor.fetchone()[0]
    if existing > 0:
        print(f"⚠️  Database has {existing} existing entries.")
        resp = input("Continue anyway? (yes/no): ")
        if resp.strip().lower() != "yes":
            print("Run reset_database.py first.")
            sys.exit(0)

# ─────────────────────────────────────────────────────────────
# Generate entries spread across 60 days ending today
# 1-3 entries per day for realistic variety
# ─────────────────────────────────────────────────────────────
today = datetime.now().replace(hour=20, minute=0, second=0, microsecond=0)
start_date = today - timedelta(days=59)

entry_index = 0
created = 0
failed = 0
total_planned = len(ENTRIES)

print(f"📝 {total_planned} entries to create across 60 days")
print(f"📅 Date range: {start_date.strftime('%Y-%m-%d')} → {today.strftime('%Y-%m-%d')}")
print()

for day_offset in range(60):
    current_day = start_date + timedelta(days=day_offset)

    # 1-3 entries per day (weighted toward 1-2)
    entries_today = random.choices([1, 2, 3], weights=[3, 5, 2])[0]

    for e in range(entries_today):
        if entry_index >= total_planned:
            break

        # Random hour for this entry (morning, afternoon, or evening)
        hour = random.choice([7, 8, 9, 10, 14, 15, 16, 20, 21, 22])
        minute = random.randint(0, 59)
        entry_time = current_day.replace(hour=hour, minute=minute)

        text = ENTRIES[entry_index]

        # Process through the real pipeline
        try:
            result = process_journal_entry("Parth", text, "manual")

            if result.get("success"):
                # Update timestamp to the backdated time
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE raw_journal_entries SET created_at = %s WHERE entry_id = %s;",
                        (entry_time, result["entry_id"]),
                    )
                    conn.commit()

                created += 1
                emotion = result.get("emotion", "?")
                conf = result.get("confidence", 0)

                if created % 10 == 0 or created <= 3:
                    print(f"  ✓ [{created}/{total_planned}] {entry_time.strftime('%b %d %H:%M')} → "
                          f"{emotion} ({int(conf * 100)}%)")
            else:
                failed += 1
                err = result.get("error", "unknown")
                print(f"  ✗ FAILED: {err}")
                print(f"    Text: {text[:80]}...")
        except Exception as ex:
            failed += 1
            print(f"  ✗ EXCEPTION: {ex}")
            print(f"    Text: {text[:80]}...")

        entry_index += 1

    if entry_index >= total_planned:
        break

# ─────────────────────────────────────────────────────────────
# Verification
# ─────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("  VERIFICATION")
print("=" * 60)
print()

with get_db_connection() as conn:
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM raw_journal_entries;")
    raw = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM processed_entries;")
    proc = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM emotion_predictions;")
    emo = cursor.fetchone()[0]

    print(f"  raw_journal_entries:  {raw}")
    print(f"  processed_entries:    {proc}")
    print(f"  emotion_predictions:  {emo}")
    print()

    if raw == proc == emo:
        print(f"  ✅ All {raw} entries fully processed!")
    else:
        print(f"  ⚠️  Mismatch! {raw - emo} entries missing emotions.")

    # Emotion distribution
    cursor.execute("""
        SELECT emotion, COUNT(*) as cnt
        FROM emotion_predictions
        GROUP BY emotion
        ORDER BY cnt DESC;
    """)

    print()
    print("  Emotion distribution:")
    for row in cursor.fetchall():
        bar = "█" * (row[1] * 2)
        print(f"    {row[0]:>16}: {row[1]:>3} {bar}")

    # Date range
    cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM raw_journal_entries;")
    dates = cursor.fetchone()
    print()
    print(f"  Date range: {dates[0]} → {dates[1]}")

print()
print("=" * 60)
print(f"  ✅ Created: {created}  |  ❌ Failed: {failed}")
print("=" * 60)
print()
print("🎉 Refresh your dashboard to see the new data!")
