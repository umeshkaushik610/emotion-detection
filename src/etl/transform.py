"""
Text transformation and cleaning
"""
from distutils.command.clean import clean
from email import message
import enum
import re
import string

def clean_text(text):
    """
    Clean and normalize text for ML model
    """

    if not text or not isinstance(text, str):
        return ""

    text = text.lower()

    text = re.sub(r'https\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

    text = re.sub(r'\S+@\S+', '', text)

    text = ' '.join(text.split())

    text = text.strip()

    return text

def validate_text(text, min_length=5, max_length=1000):
    """
    validate text
    """       
    if not text:
        return False, "Text is empty"

    if len(text) < min_length:
        return False, f"Text too short (minimum {min_length} characters)"

    if len(text) > max_length:
        return False, f"Text too long (maximum {max_length} characters)"

    words = text.split()
    if len(words) < 2:
        return False, "Text must contain at least 2 words"

    return True, "Valid"

def extract_text_features(text):
    "Extracting features for quality scoring"
    words = text.split()

    features = {
        'text_length' : len(text),
        'word_count' : len(words),
        'avg_word_length' : sum(len(word) for word in words) / len(words) if words else 0,
        'sentence_count' : text.count('.') + text.count('!') + text.count('?'),
    } 

    return features


def calculate_quality_score(text):
    """
    Calculate quality score for text (0-1)
    """

    score = 1.0

    features = extract_text_features(text)

    # penalize if very short text
    if features['word_count'] < 5:
        score -= 0.3

    # penalize very long text
    if features['word_count'] > 200:
        score -= 0.2

    # penalize text with very short words
    if features['avg_word_length'] < 3:
        score -= 0.2

    # bonus for proper sentence structure
    if features['sentence_count'] > 0:
        score += 0.1

    score = max(0.0, min(1.0, score))

    return round(score, 2)

def process_entry(raw_text):
    """
    complete processing pipeline for journal entry
    """

    cleaned_text = clean_text(raw_text)

    is_valid, message = validate_text(cleaned_text)

    features = extract_text_features(cleaned_text)

    quality_score = calculate_quality_score(cleaned_text)

    return {
        'cleaned_text' : cleaned_text,
        'is_valid' : is_valid,
        'validation_message' : message,
        'text_length' : features['text_length'],
        'word_count' : features['word_count'],
        'quality_score' : quality_score
    }


if __name__ == "__main__":
    """ Test text processing"""
    print("Testing Text Processing Pipeline...\n")

    test_texts = [
        "Today was AMAZING! I feel so grateful and happy. Everything went perfectly!",
        "im sad :((((",
        "Check out this link: https://example.com and email me at test@tst.com",
        "I feel really overwhelmed with work today but I'm trying to stay positive",
        " a b c"
    ]    

    for i, text in enumerate(test_texts, 1):
        print(f"{'='*60}")
        print(f"Test {i}: {text[:50]}...")
        print(f"{'='*60}")

        result = process_entry(text)

        print(f"Cleaned: {result['cleaned_text']}")
        print(f"Valid: {result['is_valid']}")
        print(f"Message: {result['validation_message']}")
        print(f"Word Count: {result['word_count']}")
        print(f"Quality Score: {result['quality_score']}")
        print()

    print("All text processing test completed!")   