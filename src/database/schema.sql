-- ====================================================
-- EMOTION DETECTION DATABASE SCHEMA
-- ====================================================

-- Drop tables if they exists (for clean setup)
DROP TABLE IF EXISTS emotion_trends CASCADE;
DROP TABLE IF EXISTS daily_emotion_summary CASCADE;
DROP TABLE IF EXISTS emotion_predictions CASCADE;
DROP TABLE IF EXISTS processed_entries CASCADE;
DROP TABLE IF EXISTS raw_journal_entries CASCADE;

-- ====================================================
-- BRONZE LAYER : Raw journal entries
-- ====================================================

CREATE TABLE raw_journal_entries (
    entry_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL DEFAULT 'default_user',
    raw_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) DEFAULT 'manual',
    metadata JSONB,
    processed_status VARCHAR(20) DEFAULT 'pending'
);

-- ====================================================
-- SILVER LAYER : Processed/cleaned entries
-- ====================================================

CREATE TABLE processed_entries (
    processed_id SERIAL PRIMARY KEY,
    entry_id INTEGER REFERENCES raw_journal_entries(entry_id) ON DELETE CASCADE,
    cleaned_text TEXT NOT NULL,
    text_length INTEGER,
    word_count INTEGER,
    quality_score FLOAT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entry_id)
);

CREATE INDEX idx_entry_id ON processed_entries(entry_id);

-- ====================================================
-- GOLD LAYER : Emotion predictions from ML model
-- ====================================================

CREATE TABLE emotion_predictions (
    prediction_id SERIAL PRIMARY KEY,
    entry_id INTEGER REFERENCES raw_journal_entries(entry_id) ON DELETE CASCADE,
    emotion VARCHAR(50) NOT NULL,
    emotion_id INTEGER NOT NULL,
    confidence FLOAT NOT NULL,
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR(20) DEFAULT 'v1.0',
    UNIQUE(entry_id)
);

CREATE INDEX idx_entry_emotion ON emotion_predictions(entry_id, emotion);
CREATE INDEX idx_emotion ON emotion_predictions(emotion);

-- ====================================================
-- ANALYTICS : Daily emotion aggregates
-- ====================================================

CREATE TABLE daily_emotion_summary (
    summary_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    emotion VARCHAR(50) NOT NULL,
    entry_count INTEGER DEFAULT 0,
    avg_confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date, emotion)
);

CREATE INDEX idx_user_date ON daily_emotion_summary(user_id, date);

-- ====================================================
-- ANALYSTICS : Emotion trends(weekly/monthly/custom)
-- ====================================================

CREATE TABLE emotion_trends (
    trend_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    period_type VARCHAR(10) NOT NULL, -- 'week', 'month', 'custom'
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    dominant_emotion VARCHAR(50),
    total_entries INTEGER,
    emotion_distribution JSONB, --{emotion: count}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_period ON emotion_trends(user_id, period_type, start_date);

-- ====================================================
-- VIEWS
-- ====================================================

CREATE VIEW vw_entries_with_emotions AS 
SELECT 
    r.entry_id,
    r.user_id,
    r.raw_text,
    r.created_at,
    p.cleaned_text,
    p.word_count,
    e.emotion,
    e.confidence,
    e.predicted_at
FROM raw_journal_entries r
LEFT JOIN processed_entries p ON r.entry_id = p.entry_id
LEFT JOIN emotion_predictions e ON r.entry_id = e.entry_id
ORDER BY r.created_at DESC;

-- Recent emotion trends
CREATE VIEW vw_recent_trends AS 
SELECT
    user_id,
    DATE(created_at) as date,
    emotion,
    COUNT(*) AS count,
    AVG(confidence) AS avg_confidence
FROM raw_journal_entries r
JOIN emotion_predictions e ON r.entry_id = e.entry_id
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY user_id, DATE(created_at), emotion 
ORDER BY date DESC, count DESC;

SELECT 'Database schema created successfully!' AS message;