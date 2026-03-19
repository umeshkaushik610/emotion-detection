
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import json

class EmotionClassifier:
    """Production-ready emotion classifier"""
    
    def __init__(self, model_path, tokenizer_path, model_info_path, device='cpu'):
        # Load model info
        with open(model_info_path, 'r') as f:
            self.info = json.load(f)
        
        self.emotions = self.info['emotions']
        self.device = device
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        
        # Load model
        self.model = AutoModelForSequenceClassification.from_pretrained(
            'distilbert-base-uncased',
            num_labels=len(self.emotions)
        )
        self.model.load_state_dict(torch.load(model_path, map_location=device))
        self.model.to(device)
        self.model.eval()
    
    def predict(self, text):
        """Predict emotion for a single text"""
        encoding = self.tokenizer(
            text,
            padding='max_length',
            truncation=True,
            max_length=128,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, 
                               attention_mask=attention_mask)
            probs = torch.softmax(outputs.logits, dim=1)
            confidence, prediction = torch.max(probs, dim=1)
        
        emotion = self.emotions[prediction.item()]
        confidence = confidence.item()
        
        return emotion, confidence
    
    def predict_top_k(self, text, k=3):
        """Get top k emotion predictions"""
        encoding = self.tokenizer(
            text,
            padding='max_length',
            truncation=True,
            max_length=128,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, 
                               attention_mask=attention_mask)
            probs = torch.softmax(outputs.logits, dim=1)[0]
        
        top_k = torch.topk(probs, k)
        results = [(self.emotions[idx.item()], score.item()) 
                   for score, idx in zip(top_k.values, top_k.indices)]
        
        return results
