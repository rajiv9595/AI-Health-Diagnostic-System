
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.ml_models.covidnet_model import COVIDNetAnalyzer

print("Testing TFLite model loading...")
try:
    # Point to the TFLite model explicitly (Absolute Path)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, 'backend', 'saved_models', 'xray_model.keras') # Pass .keras path, let it find .tflite
    print(f"Testing with model path: {model_path}")
    
    if not os.path.exists(model_path):
        print("ERROR: Keras model file not found at path!")
    tflite_path_check = model_path.replace('.keras', '.tflite')
    if not os.path.exists(tflite_path_check):
         print(f"ERROR: TFLite model file not found at {tflite_path_check}!")

    analyzer = COVIDNetAnalyzer(model_path=model_path)
    
    if analyzer.use_tflite:
        print("SUCCESS: TFLite model loaded and active!")
    else:
        print("WARNING: Fallback to Keras model (or TFLite failed).")
        
except Exception as e:
    print(f"FAILED: {e}")
