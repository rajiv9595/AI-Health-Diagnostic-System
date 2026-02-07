"""
Lightweight symptom parser that accepts free text or comma-separated keywords.

Design goals:
- Zero external runtime requirements (spaCy optional).
- Robust synonym normalization and simple negation handling.
- Safe default that will not break existing project.
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple


SYMPTOM_SYNONYMS: Dict[str, List[str]] = {
    # Respiratory
    "fever": ["pyrexia", "high temperature", "temperature", "temp", "hot body", "raised temp", "feverish"],
    "cough": ["coughing", "dry cough", "wet cough", "productive cough"],
    "shortness of breath": ["sob", "breathlessness", "dyspnea", "difficulty breathing", "labored breathing"],
    "chest pain": ["chest tightness", "pressure in chest", "chest pressure", "pain in chest"],
    "wheezing": ["whistling chest"],
    "sore throat": ["throat pain", "throat irritation", "pharyngitis"],
    "runny nose": ["rhinorrhea", "running nose", "nasal discharge"],
    "nasal congestion": ["stuffy nose", "blocked nose", "nasal blockage"],

    # Neuro / general
    "headache": ["head pain", "migraine", "aching head"],
    "fatigue": ["tired", "tiredness", "exhaustion", "lethargy", "low energy"],
    "dizziness": ["lightheaded", "vertigo"],
    "chills": ["shivering", "rigors"],
    "body aches": ["myalgia", "muscle pain", "aches", "body pain"],

    # GI
    "nausea": ["queasy"],
    "vomiting": ["emesis", "throwing up", "vomitted"],
    "diarrhea": ["loose stools", "loose motions"],
    "abdominal pain": ["stomach pain", "belly pain", "tummy pain", "gastric pain"],

    # ENT / sensory
    "loss of smell": ["anosmia", "no smell", "reduced smell"],
    "loss of taste": ["ageusia", "no taste", "reduced taste"],

    # Cardio
    "palpitations": ["racing heart", "fast heartbeat", "heart racing"],
    "swelling legs": ["leg swelling", "pedal edema", "ankle swelling"],
}


def _build_inverse_synonyms() -> Dict[str, str]:
    inv: Dict[str, str] = {}
    for canonical, alts in SYMPTOM_SYNONYMS.items():
        inv[canonical] = canonical
        for alt in alts:
            inv[alt] = canonical
    return inv


INVERSE_SYNONYM = _build_inverse_synonyms()


NEGATION_PAT = re.compile(r"\b(no|not|denies|without|absent)\b", re.I)
NUMBER_PAT = re.compile(r"\b(\d+)(\s*)(day|days|week|weeks|month|months|hr|hour|hours)\b", re.I)
TEMP_PAT = re.compile(r"\b(\d{2,3}(?:\.\d+)?)\s*(f|c)\b", re.I)


def normalize_text(text: str) -> str:
    text = text.lower()
    # Remove non-word characters but keep spaces and commas
    text = re.sub(r"[^a-z0-9,\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_duration(text: str):
    """Return (label, hours) or (None, None)."""
    m = NUMBER_PAT.search(text)
    if not m:
        return None, None
    num = float(m.group(1))
    unit = m.group(3).lower()
    if unit.startswith('day'):
        hours = num * 24
    elif unit.startswith('week'):
        hours = num * 7 * 24
    elif unit.startswith('month'):
        hours = num * 30 * 24
    else:  # hr/hour/hours
        hours = num
    return f"{int(num)} {unit}", hours


def parse_symptoms(input_text: str | List[str]) -> Dict:
    """
    Parse symptoms from free text or list of keywords.

    Returns a dict with:
      - extracted: list of canonical symptom strings (negated removed)
      - negated: list of symptoms explicitly negated
      - duration: optional extracted duration string
      - severity_hint: 'mild'|'moderate'|'severe' (heuristic)
    """
    if isinstance(input_text, list):
        raw = ", ".join(input_text)
    else:
        raw = input_text or ""

    text = normalize_text(raw)
    duration_label, duration_hours = extract_duration(text)

    # Split on commas or semicolons into phrases
    phrases = [p.strip() for p in re.split(r"[,;]", text) if p.strip()]
    found: List[str] = []
    negated: List[str] = []

    def map_to_canonical(token: str) -> str | None:
        token = token.strip()
        if not token:
            return None
        # direct match
        if token in INVERSE_SYNONYM:
            return INVERSE_SYNONYM[token]
        # partial heuristic match
        for k in INVERSE_SYNONYM:
            if token == k or token in k or k in token:
                return INVERSE_SYNONYM[k]
        return None

    for phrase in phrases or [text]:
        is_neg = bool(NEGATION_PAT.search(phrase))
        tokens = [t.strip() for t in phrase.split()]
        window = []
        for t in tokens:
            window.append(t)
            # Check bigrams/trigrams first
            for n in (3, 2, 1):
                if len(window) >= n:
                    cand = " ".join(window[-n:])
                    canonical = map_to_canonical(cand)
                    if canonical:
                        if is_neg:
                            if canonical not in negated:
                                negated.append(canonical)
                        else:
                            if canonical not in found:
                                found.append(canonical)
                        break

    # Heuristic severity
    severe_markers = {"shortness of breath", "chest pain", "wheezing", "palpitations"}
    moderate_markers = {"fever", "cough", "vomiting", "diarrhea", "abdominal pain"}
    severity = "mild"
    # Temperature-based escalation
    t = TEMP_PAT.search(text)
    if t:
        val = float(t.group(1))
        unit = t.group(2).lower()
        if (unit == 'f' and val >= 102) or (unit == 'c' and val >= 38.9):
            severity = "severe"
    if any(s in found for s in severe_markers):
        severity = "severe"
    elif any(s in found for s in moderate_markers):
        severity = "moderate"

    return {
        "extracted": found,
        "negated": negated,
        "duration": duration_label,
        "duration_hours": duration_hours,
        "severity_hint": severity,
        "raw": raw,
    }


__all__ = ["parse_symptoms", "SYMPTOM_SYNONYMS"]


