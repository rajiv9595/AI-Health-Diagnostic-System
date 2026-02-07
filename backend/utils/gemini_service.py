import google.generativeai as genai
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def configure_gemini():
    """Configure Gemini with API key from environment variables"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.warning("GEMINI_API_KEY not found in environment variables")
        return False
    genai.configure(api_key=api_key)
    return True

def analyze_symptoms_with_gemini(symptoms_text):
    """
    Analyze symptoms using Gemini model and return structured data.
    
    Args:
        symptoms_text (str): Description of symptoms
        
    Returns:
        dict: Structured prediction data or None if analysis fails
    """
    if not configure_gemini():
        return None
        
    try:
        # Use Gemini 2.5 Flash as requested
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        Act as an expert medical AI assistant. Analyze the following symptoms and provide a preliminary diagnosis.
        
        Symptoms: "{symptoms_text}"
        
        Return the analysis strictly in the following JSON format:
        {{
            "predicted_disease": "Name of the most likely condition",
            "confidence": 0.85,  # Float between 0 and 1 representing confidence level
            "urgency_level": "mild", # One of: "mild", "moderate", "severe"
            "top_predictions": [
                {{ "disease": "Most likely condition", "confidence": 0.85, "urgency": "mild" }},
                {{ "disease": "Second likely condition", "confidence": 0.10, "urgency": "mild" }},
                {{ "disease": "Third likely condition", "confidence": 0.05, "urgency": "moderate" }}
            ],
            "recommendations": [
                "Detailed recommendation 1",
                "Detailed recommendation 2",
                "Detailed recommendation 3"
            ]
        }}
        
        IMPORTANT:
        1. "confidence" must be a float between 0.0 and 1.0.
        2. "urgency_level" must be strictly one of: "mild", "moderate", "severe".
        3. Provide 3-5 practical, actionable recommendations.
        4. If the symptoms are vague or insufficient, predict "Undetermined" with low confidence but provide general health advice.
        5. DO NOT include markdown formatting (like ```json). Return ONLY the raw JSON string.
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.replace('```json', '').replace('```', '').strip()
        
        try:
            prediction = json.loads(response_text)
            
            # Helper to ensure correct types
            if 'confidence' in prediction:
                prediction['confidence'] = float(prediction['confidence'])
            
            # Ensure top_predictions exists and is a list
            if 'top_predictions' not in prediction or not isinstance(prediction['top_predictions'], list):
                prediction['top_predictions'] = []
            
            # Ensure recommendations exists and is a list
            if 'recommendations' not in prediction or not isinstance(prediction['recommendations'], list):
                prediction['recommendations'] = []
                
            return prediction
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Raw response: {response_text}")
            return None
            
    except Exception as e:
        logger.error(f"Gemini analysis failed: {e}")
        return None
