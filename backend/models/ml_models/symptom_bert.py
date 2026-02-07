"""
Optional DistilBERT-based classifier for free-text symptom paragraphs.
This module is safe: if transformers/torch are unavailable, it degrades gracefully.
Uses zero-shot classification to map text to disease labels.
"""
from __future__ import annotations

from typing import List, Dict

try:
    from transformers import pipeline
    _TRANSFORMERS_AVAILABLE = True
except Exception:
    _TRANSFORMERS_AVAILABLE = False


DEFAULT_DISEASES = [
    'Common Cold', 'Flu', 'Pneumonia', 'COVID-19', 'Tuberculosis',
    'Bronchitis', 'Asthma', 'Allergies', 'Sinusitis', 'Migraine',
    'Gastroenteritis', 'Food Poisoning', 'GERD', 'Diabetes',
    'Hypertension', 'Heart Disease', 'Stroke', 'Urinary Tract Infection'
]


class SymptomBERT:
    def __init__(self, labels: List[str] | None = None):
        if not _TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers is not installed.")
        self.labels = labels or DEFAULT_DISEASES
        # Zero-shot classification pipeline; will download model first time
        self.classifier = pipeline('zero-shot-classification', model='valhalla/distilbart-mnli-12-1')

    def predict(self, text: str, top_k: int = 3) -> Dict:
        result = self.classifier(text, self.labels, multi_label=True)
        # Build score dict
        scores = dict(zip(result['labels'], result['scores']))
        # Sort by score desc
        top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        top_predictions = [
            { 'disease': d, 'confidence': float(s), 'urgency': self._urgency_hint(d) }
            for d, s in top
        ]
        return {
            'predicted_disease': top_predictions[0]['disease'],
            'confidence': top_predictions[0]['confidence'],
            'top_predictions': top_predictions,
        }

    @staticmethod
    def _urgency_hint(disease: str) -> str:
        severe = {'Pneumonia', 'COVID-19', 'Tuberculosis', 'Heart Disease', 'Stroke'}
        moderate = {'Hypertension', 'Asthma', 'Urinary Tract Infection', 'Gastroenteritis'}
        if disease in severe:
            return 'severe'
        if disease in moderate:
            return 'moderate'
        return 'mild'










