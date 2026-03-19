"""
ML MODEL INTEGRATION
Loads emotion classifier from Hugging Face Hub (cloud) or local paths (dev)
"""
import sys
import os
import json
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

# ── Hugging Face repo ID — UPDATE THIS after uploading your model ──
HF_REPO_ID = os.getenv("HF_REPO_ID", "umeshkaushik610/emotion-classifier")


class EmotionClassifier:

    def __init__(self, model_path=None, tokenizer_path=None, model_info_path=None, device='cpu'):
        """
        Initialize emotion classifier.
        If no local paths provided, loads from Hugging Face Hub.
        """
        self.device = device

        # ── Determine source: local paths or HF Hub ──
        use_hf = model_path is None and not os.path.exists(
            os.path.join(project_root, 'data', 'models', 'emotion_classifier_final.pt')
        )

        if use_hf:
            self._load_from_huggingface()
        else:
            self._load_from_local(model_path, tokenizer_path, model_info_path)

        self.model.to(self.device)
        self.model.eval()
        print(f" Model loaded successfully! ({len(self.emotions)} emotions, device={self.device})")

    def _load_from_huggingface(self):
        """Load model, tokenizer, and config from Hugging Face Hub"""
        print(f"Loading model from Hugging Face: {HF_REPO_ID}")

        from huggingface_hub import hf_hub_download

        # Download model_info.json
        info_path = hf_hub_download(repo_id=HF_REPO_ID, filename="model_info.json")
        with open(info_path, 'r') as f:
            self.info = json.load(f)
        self.emotions = self.info['emotions']

        # Load tokenizer (saved as standard HF tokenizer files in the repo)
        self.tokenizer = AutoTokenizer.from_pretrained(HF_REPO_ID)

        # Load model architecture
        self.model = AutoModelForSequenceClassification.from_pretrained(
            'distilbert-base-uncased',
            num_labels=len(self.emotions)
        )

        # Download and load trained weights
        weights_path = hf_hub_download(repo_id=HF_REPO_ID, filename="emotion_classifier_final.pt")
        self.model.load_state_dict(torch.load(weights_path, map_location=self.device))

    def _load_from_local(self, model_path=None, tokenizer_path=None, model_info_path=None):
        """Load model from local file paths (development mode)"""
        if model_path is None:
            model_path = os.path.join(project_root, 'data', 'models', 'emotion_classifier_final.pt')
        if tokenizer_path is None:
            tokenizer_path = os.path.join(project_root, 'data', 'models', 'tokenizer')
        if model_info_path is None:
            model_info_path = os.path.join(project_root, 'data', 'models', 'model_info.json')

        print(f"Loading model from local: {model_path}")

        with open(model_info_path, 'r') as f:
            self.info = json.load(f)
        self.emotions = self.info['emotions']

        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)

        self.model = AutoModelForSequenceClassification.from_pretrained(
            'distilbert-base-uncased',
            num_labels=len(self.emotions)
        )
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))

    def predict(self, text):
        """Predict emotion for single text"""
        encoding = self.tokenizer(
            text, padding='max_length', truncation=True,
            max_length=128, return_tensors='pt'
        )
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            probs = torch.softmax(outputs.logits, dim=1)
            confidence, prediction = torch.max(probs, dim=1)

        emotion = self.emotions[prediction.item()]
        return emotion, confidence.item(), prediction.item()

    def predict_top_k(self, text, k=3):
        """Get top k emotion predictions"""
        encoding = self.tokenizer(
            text, padding='max_length', truncation=True,
            max_length=128, return_tensors='pt'
        )
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            probs = torch.softmax(outputs.logits, dim=1)[0]

        top_k = torch.topk(probs, k)
        return [(self.emotions[idx.item()], score.item())
                for score, idx in zip(top_k.values, top_k.indices)]


# Global classifier instance
_classifier = None


def get_classifier():
    global _classifier
    if _classifier is None:
        _classifier = EmotionClassifier()
    return _classifier


def predict_emotion(text):
    """Convenience function to predict emotion"""
    classifier = get_classifier()
    emotion, confidence, emotion_id = classifier.predict(text)
    return {'emotion': emotion, 'emotion_id': emotion_id, 'confidence': confidence}


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING EMOTION CLASSIFIER...")
    print("=" * 60)

    test_texts = [
        "Today was amazing! I accomplished so much and feel great",
        "I'm feeling really sad and disappointed about what happened",
        "I'm so nervous about the presentation tomorrow.",
        "I love spending time with my family, feeling grateful."
    ]

    classifier = EmotionClassifier()

    for i, text in enumerate(test_texts, 1):
        emotion, confidence, _ = classifier.predict(text)
        print(f"\n{i}. {text}")
        print(f"   -> {emotion} ({confidence:.2%})")
