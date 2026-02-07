
import tensorflow as tf
import os

def convert_to_tflite():
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, 'backend', 'saved_models', 'xray_model.keras')
    tflite_path = os.path.join(base_dir, 'backend', 'saved_models', 'xray_model.tflite')
    
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        # Try .h5
        model_path = 'backend/models/ml_models/xray_model.h5'
        if not os.path.exists(model_path):
            print("No model found.")
            return

    print(f"Loading model from {model_path}...")
    try:
        model = tf.keras.models.load_model(model_path)
        
        # Convert
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        
        # Optional: Quantization (reduces size by 4x, slightly less accuracy)
        # converter.optimizations = [tf.lite.Optimize.DEFAULT]
        
        tflite_model = converter.convert()
        
        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)
            
        print(f"Success! Model converted to {tflite_path}")
        print(f"Original Size: {os.path.getsize(model_path) / 1024 / 1024:.2f} MB")
        print(f"TFLite Size: {os.path.getsize(tflite_path) / 1024 / 1024:.2f} MB")
        
    except Exception as e:
        print(f"Error converting model: {e}")

if __name__ == "__main__":
    convert_to_tflite()
