import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("Error: GEMINI_API_KEY not found in backend/.env")
    exit(1)

genai.configure(api_key=api_key)

print(f"Checking available models for API Key: {api_key[:5]}...{api_key[-5:]}")
print("-" * 50)

try:
    models = genai.list_models()
    found_any = False
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            found_any = True
            
    if not found_any:
        print("No models found that support 'generateContent'.")
        
except Exception as e:
    print(f"Error listing models: {e}")
