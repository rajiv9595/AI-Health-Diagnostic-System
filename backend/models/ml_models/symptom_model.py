"""
Symptom Checker Model using NLP
Predicts diseases based on symptoms
"""
import numpy as np
import pandas as pd
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
# Import relative to backend package when app runs from backend/
from models.nlp.symptom_parser import parse_symptoms


class SymptomChecker:
    """NLP-based symptom checker for disease prediction"""
    
    def __init__(self, model_path=None, vectorizer_path=None, encoder_path=None):
        """
        Initialize symptom checker
        
        Args:
            model_path: Path to saved model (.pkl)
            vectorizer_path: Path to saved TF-IDF vectorizer
            encoder_path: Path to saved label encoder
        """
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        
        # Download NLTK data if needed
        try:
            stopwords.words('english')
        except:
            nltk.download('stopwords', quiet=True)
            nltk.download('punkt', quiet=True)
        
        # Load models if paths provided
        if model_path and os.path.exists(model_path):
            self.load_model(model_path, vectorizer_path, encoder_path)
        else:
            print("Model not found - needs training")
        
        # Urgency mapping
        self.urgency_map = {
            'Common Cold': 'mild',
            'Allergy': 'mild',
            'Migraine': 'mild',
            'Gastroenteritis': 'moderate',
            'Bronchitis': 'moderate',
            'Urinary tract infection': 'moderate',
            'Pneumonia': 'severe',
            'COVID-19': 'severe',
            'Tuberculosis': 'severe',
            'Heart Attack': 'severe',
            'Stroke': 'severe',
            'Dengue': 'severe',
            'Malaria': 'severe',
            'Diabetes': 'moderate',
            'Hypertension': 'moderate',
            'Asthma': 'moderate',
            'GERD': 'mild',
            'Arthritis': 'mild',
            'Osteoporosis': 'moderate',
            'Hepatitis': 'severe',
            'Jaundice': 'severe'
        }
    
    def preprocess_text(self, text):
        """
        Preprocess symptom text
        
        Args:
            text: Raw symptom text
            
        Returns:
            Cleaned and preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]
        
        # Join back to string
        return ' '.join(tokens)
    
    def train(self, symptoms_data, disease_labels):
        """
        Train symptom checker model
        
        Args:
            symptoms_data: List of symptom strings
            disease_labels: List of corresponding disease labels
        """
        # Preprocess symptoms
        processed_symptoms = [self.preprocess_text(s) for s in symptoms_data]
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            min_df=2
        )
        
        # Transform symptoms to TF-IDF features
        X = self.vectorizer.fit_transform(processed_symptoms)
        
        # Encode labels
        self.label_encoder = LabelEncoder()
        y = self.label_encoder.fit_transform(disease_labels)
        
        # Train Naive Bayes classifier
        self.model = MultinomialNB(alpha=0.1)
        self.model.fit(X, y)
        
        print("Model trained successfully")
    
    def predict(self, symptoms_text):
        """
        Predict disease from symptoms
        
        Args:
            symptoms_text: Text description of symptoms
            
        Returns:
            Dictionary with prediction results
        """
        if not self.model or not self.vectorizer or not self.label_encoder:
            raise ValueError("Model not trained or loaded")
        
        # Normalize through parser for robust synonyms/negations
        parsed = parse_symptoms(symptoms_text)
        normalized = ", ".join(parsed.get('extracted') or [symptoms_text])
        # Preprocess symptoms
        processed = self.preprocess_text(normalized)
        
        # Transform to TF-IDF features
        X = self.vectorizer.transform([processed])
        
        # Get prediction probabilities
        proba = self.model.predict_proba(X)[0]
        
        # Get top 3 predictions
        top_indices = np.argsort(proba)[-3:][::-1]
        top_predictions = []
        
        for idx in top_indices:
            disease = self.label_encoder.inverse_transform([idx])[0]
            confidence = float(proba[idx])
            urgency = self.get_urgency_level(disease)
            
            top_predictions.append({
                'disease': disease,
                'confidence': confidence,
                'urgency': urgency
            })
        
        # Get primary prediction
        predicted_disease = top_predictions[0]['disease']
        confidence = top_predictions[0]['confidence']
        urgency_level = top_predictions[0]['urgency']
        # Rule-based urgency v2
        urgency_level = self._merge_rule_urgency(urgency_level, parsed)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(
            predicted_disease, 
            urgency_level, 
            confidence
        )
        
        result = {
            'predicted_disease': predicted_disease,
            'confidence': confidence,
            'urgency_level': urgency_level,
            'top_predictions': top_predictions,
            'recommendations': recommendations
        }
        
        return result
    
    def get_urgency_level(self, disease):
        """
        Determine urgency level for a disease
        
        Args:
            disease: Disease name
            
        Returns:
            Urgency level (mild/moderate/severe)
        """
        return self.urgency_map.get(disease, 'moderate')
    
    def generate_recommendations(self, disease, urgency, confidence):
        """
        Generate medical recommendations
        
        Args:
            disease: Predicted disease
            urgency: Urgency level
            confidence: Prediction confidence
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Base recommendation
        if urgency == 'severe':
            recommendations.append("⚠️ URGENT: Seek immediate medical attention")
            recommendations.append("Visit the emergency room or call emergency services")
        elif urgency == 'moderate':
            recommendations.append("Schedule an appointment with your doctor within 1-2 days")
            recommendations.append("Monitor your symptoms closely")
        else:
            recommendations.append("Rest and monitor your symptoms")
            recommendations.append("Consider over-the-counter medication if needed")
        
        # Confidence-based recommendation
        if confidence < 0.5:
            recommendations.append("⚠️ Low confidence prediction - please consult a doctor for accurate diagnosis")
        
        # Disease-specific recommendations
        disease_specific = {
            'COVID-19': [
                "Self-isolate immediately",
                "Get tested for COVID-19",
                "Wear a mask around others"
            ],
            'Pneumonia': [
                "Get a chest X-ray",
                "Stay hydrated",
                "Avoid smoking"
            ],
            'Diabetes': [
                "Monitor blood sugar levels",
                "Follow a healthy diet",
                "Exercise regularly"
            ],
            'Hypertension': [
                "Monitor blood pressure daily",
                "Reduce sodium intake",
                "Manage stress levels"
            ],
            'Asthma': [
                "Keep your inhaler handy",
                "Avoid triggers (dust, smoke, etc.)",
                "Monitor breathing patterns"
            ]
        }
        
        if disease in disease_specific:
            recommendations.extend(disease_specific[disease])
        
        # General recommendation
        recommendations.append("This is an AI prediction and not a substitute for professional medical advice")
        
        return recommendations

    def _merge_rule_urgency(self, model_urgency: str, parsed: dict) -> str:
        """Blend model urgency with rule-based red flags."""
        severe_set = {"shortness of breath", "chest pain", "wheezing", "palpitations"}
        moderate_set = {"fever", "cough", "vomiting", "diarrhea", "abdominal pain"}

        extracted = set(parsed.get('extracted') or [])
        duration_h = parsed.get('duration_hours') or 0

        rule = 'mild'
        # Temperature / parser severity
        if parsed.get('severity_hint') == 'severe':
            rule = 'severe'
        elif parsed.get('severity_hint') == 'moderate':
            rule = 'moderate'

        # Red flags
        if extracted & severe_set:
            rule = 'severe'
        # Persistent fever/cough beyond 48h -> at least moderate
        if duration_h and duration_h >= 48 and (extracted & {"fever", "cough"}):
            rule = 'moderate' if rule != 'severe' else 'severe'

        # Merge
        order = {'mild': 0, 'moderate': 1, 'severe': 2}
        return max([model_urgency, rule], key=lambda x: order.get(x, 1))
    
    def save_model(self, model_path, vectorizer_path, encoder_path):
        """Save model, vectorizer, and encoder"""
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        with open(encoder_path, 'wb') as f:
            pickle.dump(self.label_encoder, f)
        
        print(f"Model saved to {model_path}")
    
    def load_model(self, model_path, vectorizer_path, encoder_path):
        """Load model, vectorizer, and encoder"""
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            with open(encoder_path, 'rb') as f:
                self.label_encoder = pickle.load(f)
            
            print("Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")


# Utility function for symptom extraction
def extract_symptoms(text):
    """
    Extract individual symptoms from text
    
    Args:
        text: Symptom description
        
    Returns:
        List of extracted symptoms
    """
    # Common symptom keywords
    symptom_keywords = [
        'fever', 'cough', 'headache', 'pain', 'fatigue', 'nausea',
        'vomiting', 'diarrhea', 'rash', 'shortness of breath',
        'chest pain', 'dizziness', 'weakness', 'chills', 'sweating',
        'loss of appetite', 'weight loss', 'difficulty breathing',
        'sore throat', 'runny nose', 'congestion', 'muscle ache'
    ]
    
    text_lower = text.lower()
    found_symptoms = [s for s in symptom_keywords if s in text_lower]
    
    return found_symptoms


