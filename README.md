# 🌿 Emotional Intelligence Companion

A full-stack emotional journaling application that uses a **custom-trained DistilBERT model** to classify emotions from journal entries in real-time, with a glassmorphism UI and interactive analytics dashboard.

> **No external AI APIs.** The emotion detection model was trained from scratch as part of this project — no OpenAI, Google, or any third-party AI service is used. The entire ML pipeline (data processing, model training, inference) is self-contained.

**🔗 [Live Demo](https://emotion-detection-kki5h6c3numuk8syg4zlvf.streamlit.app/)**

---

## What It Does

Write a journal entry → the app analyzes your emotions using a custom-trained NLP model → view insights, trends, and patterns over time through interactive visualizations.

The app detects **17 emotions** including joy, sadness, anger, anxiety, gratitude, excitement, fear, and more — going beyond simple positive/negative sentiment analysis.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit, Plotly, Custom CSS (Glassmorphism) |
| **ML Model** | DistilBERT (fine-tuned), PyTorch, Hugging Face Transformers |
| **Database** | PostgreSQL (Supabase) |
| **ETL Pipeline** | Python (Medallion Architecture — Bronze/Silver/Gold) |
| **Deployment** | Streamlit Community Cloud |
| **Model Hosting** | Hugging Face Hub |

---

## Architecture

```
User Input (Journal Entry)
        │
        ▼
┌─────────────────────┐
│   Streamlit App      │  ← Glassmorphism UI with light/dark mode
│   (dashboard/app.py) │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   ETL Pipeline       │  ← Text cleaning, validation, quality scoring
│   (src/etl/)         │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   DistilBERT Model   │  ← Fine-tuned on 59K samples (GoEmotions + Emotion datasets)
│   (src/ml/)          │     17 emotions, ~63% test accuracy
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   PostgreSQL         │  ← Medallion architecture (Bronze → Silver → Gold)
│   (Supabase Cloud)   │     Raw entries → Processed → Predictions → Analytics
└─────────────────────┘
```

---

## Features

### 📝 Reflect
- Journal entry input with emotion analysis
- Real-time emotion prediction with confidence scores
- AI-generated reflections based on detected emotions
- Emotional Intelligence score (0–100) based on balance, clarity, and consistency
- Journaling streak tracker

### 📊 Snapshot
- Emotion distribution (donut chart)
- Sentiment timeline (positive/negative/neutral trends)
- Confidence distribution histogram
- Top emotions bar chart

### 🔍 Insights
- Positive/Negative/Neutral ratio breakdown
- Writing patterns scatter plot
- Activity heatmap (day × hour)
- Emotion deep dive with per-emotion stats
- Key takeaways with dominant emotion, streak, and trend analysis

### 📖 History
- Full journal history with filters (emotion, date, sort order)
- Per-entry emotion tags with confidence percentages

### 🎨 UI
- Glassmorphism design with backdrop blur effects
- Light/Dark mode toggle
- Responsive glass cards with hover animations
- Custom color palette per emotion

---

## Model Performance

The emotion classifier is a **self-trained model** — no external AI APIs (OpenAI, Google, etc.) are used anywhere in this project. The model was fine-tuned from scratch on a combined dataset and handles 17 distinct emotions.

**Overall Metrics:**
- **Overall Accuracy:** ~63% across all 17 emotion classes
- **Training Data:** ~59,000 samples (GoEmotions + Emotion datasets combined)
- **Base Model:** `distilbert-base-uncased` fine-tuned for sequence classification
- **Training:** 3 epochs on Google Colab (T4 GPU), PyTorch
- **Hosted on:** [Hugging Face Hub](https://huggingface.co/umeshkaushik610/emotion-classifier)

**Performance by Emotion Category:**

| Tier | Accuracy Range | Emotions |
|------|---------------|----------|
| **Strong** | 80–90% | Joy, Sadness, Anger, Fear, Excitement, Gratitude |
| **Moderate** | 60–70% | Anxiety, Disappointment, Optimism, Pride/Proud |
| **Weaker** | 40–50% | Embarrassment, Guilt, Confusion, Neutral, Annoyance |

The model performs best on commonly expressed, well-represented emotions in the training data. Rarer and more nuanced emotions (embarrassment, guilt) have fewer training samples and are inherently harder to distinguish from neighboring emotions, which is consistent with published benchmarks on the GoEmotions dataset. The overall accuracy of ~63% across 17 classes is competitive — for context, random guessing on 17 classes would yield ~6%, and even state-of-the-art models on GoEmotions report 60–70% macro F1.

---

## Database Schema (Medallion Architecture)

- **Bronze Layer** — `raw_journal_entries`: Raw text as entered by user
- **Silver Layer** — `processed_entries`: Cleaned text, word count, quality score
- **Gold Layer** — `emotion_predictions`: Predicted emotion, confidence, model version
- **Analytics** — `daily_emotion_summary`, `emotion_trends`: Aggregated insights

---

## Project Structure

```
├── dashboard/
│   └── app.py                 # Main Streamlit application
├── src/
│   ├── database/
│   │   ├── connection.py      # PostgreSQL connection (Supabase/local)
│   │   ├── operations.py      # CRUD operations
│   │   └── schema.sql         # Database schema
│   ├── etl/
│   │   ├── pipeline.py        # End-to-end ETL pipeline
│   │   └── transform.py       # Text cleaning and validation
│   ├── ml/
│   │   ├── inference.py       # Model loading and prediction (HF Hub/local)
│   │   └── batch_predict.py   # Batch prediction utilities
│   └── reporting/
│       ├── aggregations.py    # Data aggregation logic
│       └── report_gen.py      # Report generation
├── data/
│   └── models/                # Model config and tokenizer (weights on HF Hub)
├── requirements.txt
└── README.md
```

---

## Run Locally

```bash
# Clone the repo
git clone https://github.com/umeshkaushik610/emotion-detection.git
cd emotion-detection

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create a .env file with:
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=emotion_detection_db
# DB_USER=postgres
# DB_PASSWORD=your_password

# Set up the database
psql -U postgres -d emotion_detection_db -f src/database/schema.sql

# Run the app
streamlit run dashboard/app.py
```

---

## Screenshots

| Light Mode | Dark Mode |
|-----------|----------|
| Glassmorphism cards with gradient background | Starfield background with frosted glass effect |

---

## What I Learned

- Fine-tuning transformer models (DistilBERT) for multi-class classification with PyTorch
- Building end-to-end ETL pipelines with a medallion architecture
- Deploying ML models via Hugging Face Hub for cloud inference
- Cloud PostgreSQL setup with Supabase
- Streamlit deployment with secrets management
- Custom CSS injection for glassmorphism UI in Streamlit

---

## Roadmap

Planned improvements for future iterations:

- **User Authentication** — Add proper login/signup with password hashing so users can securely access their data across devices, replacing the current name-based identity system
- **Model Retraining with User Feedback** — Allow users to correct misclassified emotions, collect that feedback, and use it to fine-tune the model for improved accuracy over time
- **Weekly/Monthly Email Reports** — Automated emotional wellness summaries delivered via email, with trend analysis and personalized recommendations
- **Multilingual Support** — Extend emotion detection to Hindi and Hinglish journal entries using multilingual transformer models (XLM-RoBERTa)
- **Export & Data Portability** — Let users export their journal history and analytics as PDF reports or CSV files for personal records or therapist sharing

---

## Author

**Umesh Kaushik**

Built as a portfolio project demonstrating full-stack data engineering and applied ML skills.
