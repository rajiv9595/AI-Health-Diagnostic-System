import google.generativeai as genai
import os
import json
import logging
from PIL import Image
from flask import current_app

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
        # Use configured Gemini model
        model_name = current_app.config.get('GEMINI_MODEL', 'gemini-1.5-flash')
        model = genai.GenerativeModel(model_name)
        
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

def verify_chest_xray(image_path):
    """
    Verify if the uploaded image is actually a chest X-ray using Gemini.
    
    Args:
        image_path (str): Path to the uploaded image file
        
    Returns:
        tuple: (is_xray, message) - Boolean and a descriptive message
    """
    if not configure_gemini():
        # If API not configured, skip verification (fail-open)
        return True, "API not configured"
        
    try:
        # Use configured Gemini model
        model_name = current_app.config.get('GEMINI_MODEL', 'gemini-1.5-flash')
        model = genai.GenerativeModel(model_name)
        
        # Load image
        img = Image.open(image_path)
        
        prompt = """
        Analyze this image. Is it a chest X-ray? 
        Answer ONLY with a JSON object in this format: 
        {"is_chest_xray": true, "reason": "Explain why"} or {"is_chest_xray": false, "reason": "Explain why this is not a chest X-ray (e.g., 'This is a selfie', 'This is a picture of a cat')"}
        
        Be strict. If it is a person's face, a landscape, or any other body part that is not a chest X-ray, mark it as false.
        """
        
        response = model.generate_content([prompt, img])
        response_text = response.text.replace('```json', '').replace('```', '').strip()
        
        result = json.loads(response_text)
        is_xray = result.get('is_chest_xray', True)
        reason = result.get('reason', 'Analysis completed')
        
        return is_xray, reason
        
    except Exception as e:
        logger.error(f"Gemini image verification failed: {e}")
        # Fail-open: if verification fails (e.g. API error), allow the upload
        return True, "Verification failed (allowed by default)"
