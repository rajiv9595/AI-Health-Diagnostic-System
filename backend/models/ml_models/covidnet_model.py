"""
COVID-Net: Advanced pre-trained model for COVID-19 detection
Based on COVID-Net architecture for chest X-ray analysis
Uses TensorFlow/Keras implementation
"""
import numpy as np
import cv2
import os

# Try to import TFLite runtime (for Render/Production)
try:
    import tflite_runtime.interpreter as tflite
    print("[INFO] Using tflite_runtime")
    TFLITE_RUNTIME = True
except ImportError:
    try:
        import tensorflow as tf
        from tensorflow import keras
        from tensorflow.keras.models import Model, load_model
        from tensorflow.keras.applications import EfficientNetB4
        from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, Input
        from tensorflow.keras.utils import load_img, img_to_array
        print("[INFO] Using full TensorFlow")
        TFLITE_RUNTIME = False
    except ImportError:
        print("[ERROR] Neither tflite_runtime nor tensorflow found!")
        TFLITE_RUNTIME = None

class COVIDNetAnalyzer:
    """
    COVID-Net analyzer for X-ray image classification
    Supports both Keras (Dev) and TFLite (Production) models.
    """
    
    def __init__(self, model_path=None, input_shape=(224, 224, 3), num_classes=4):
        """
        Initialize COVID-Net analyzer
        """
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.class_names = ['COVID-19', 'Normal', 'Pneumonia', 'Tuberculosis']
        self.use_tflite = False
        self.model = None  # Ensure attribute exists for TFLite mode
        
        # 1. Try TFLite Model first (Preferred for Production)
        tflite_path = model_path.replace('.keras', '.tflite') if model_path else None
        if tflite_path and os.path.exists(tflite_path):
             print(f"[INFO] Found TFLite model at {tflite_path}")
             try:
                 if TFLITE_RUNTIME:
                     self.interpreter = tflite.Interpreter(model_path=tflite_path)
                 else:
                     self.interpreter = tf.lite.Interpreter(model_path=tflite_path)
                 
                 self.interpreter.allocate_tensors()
                 
                 # Get input and output details
                 self.input_details = self.interpreter.get_input_details()
                 self.output_details = self.interpreter.get_output_details()
                 
                 self.use_tflite = True
                 print("[SUCCESS] Loaded TFLite model")
                 return
             except Exception as e:
                 print(f"[WARNING] Failed to load TFLite model: {e}")

        # 2. Fallback to Keras Model (Development)
        if TFLITE_RUNTIME:
            print("[ERROR] Cannot load Keras model with tflite-runtime. Please ensure .tflite model exists.")
            # In production without TFLite model, we are stuck.
            self.model = None 
            return

        if model_path and os.path.exists(model_path):
            try:
                self.model = load_model(model_path)
                print(f"[SUCCESS] Loaded COVID-Net model from {model_path}")
            except Exception as e:
                print(f"[WARNING] Failed to load model: {e}")
                print("[INFO] Creating new EfficientNetB4 model...")
                self.model = self._build_model()
        else:
            print("[INFO] Building new EfficientNetB4-based model...")
            self.model = self._build_model()
    
    def _build_model(self):
        """Build EfficientNetB4-based model (Keras Only)"""
        inputs = Input(shape=self.input_shape)
        base_model = EfficientNetB4(weights='imagenet', include_top=False, input_tensor=inputs)
        
        for layer in base_model.layers[:-30]:
            layer.trainable = False
        
        x = base_model.output
        x = GlobalAveragePooling2D(name='global_avg_pool')(x)
        x = Dropout(0.5, name='dropout_1')(x)
        x = Dense(512, activation='relu', name='dense_512')(x)
        x = Dropout(0.3, name='dropout_2')(x)
        x = Dense(256, activation='relu', name='dense_256')(x)
        x = Dropout(0.2, name='dropout_3')(x)
        predictions = Dense(self.num_classes, activation='softmax', name='predictions')(x)
        
        model = Model(inputs=inputs, outputs=predictions, name='COVIDNet_EfficientB4')
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.0001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        return model
    
    def preprocess_image(self, img_path):
        """Preprocess image for model input"""
        # Load image using OpenCV to avoid Keras dependency in TFLite mode
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (self.input_shape[0], self.input_shape[1]))
        
        # Apply CLAHE
        img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        img_enhanced = clahe.apply(img_gray)
        img_array = cv2.cvtColor(img_enhanced, cv2.COLOR_GRAY2RGB)
        
        # Normalize
        img_array = img_array.astype(np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    def predict(self, img_path):
        """Predict disease from X-ray image"""
        img_array = self.preprocess_image(img_path)
        
        if self.use_tflite:
            # TFLite Inference
            # 1. Prediction on original
            self.interpreter.set_tensor(self.input_details[0]['index'], img_array)
            self.interpreter.invoke()
            pred_original = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
            
            # 2. Prediction on flipped (TTA)
            img_flipped = np.flip(img_array, axis=2)
            self.interpreter.set_tensor(self.input_details[0]['index'], img_flipped)
            self.interpreter.invoke()
            pred_flipped = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
            
            predictions = (pred_original + pred_flipped) / 2.0
            print(f"[DEBUG] TFLite TTA - Avg: {predictions}")
            
        else:
            # Keras Inference
            pred_original = self.model.predict(img_array, verbose=0)[0]
            img_flipped = np.flip(img_array, axis=2)
            pred_flipped = self.model.predict(img_flipped, verbose=0)[0]
            predictions = (pred_original + pred_flipped) / 2.0
            print(f"[DEBUG] Keras TTA - Avg: {predictions}")
        
        # Get predicted class
        predicted_idx = np.argmax(predictions)
        predicted_class = self.class_names[predicted_idx]
        confidence = float(predictions[predicted_idx])
        
        # Create predictions dictionary
        pred_dict = {
            self.class_names[i]: float(predictions[i])
            for i in range(len(self.class_names))
        }
        
        # Determine if abnormal (anything except Normal)
        is_abnormal = predicted_class != 'Normal'
        
        # Calculate urgency based on disease and confidence
        urgency = self._calculate_urgency(predicted_class, confidence)
        
        result = {
            'predicted_class': predicted_class,
            'confidence': confidence,
            'predictions': pred_dict,
            'is_abnormal': is_abnormal,
            'urgency': urgency,
            'model': 'COVID-Net (EfficientNetB4)'
        }
        
        return result
    
    def _calculate_urgency(self, disease, confidence):
        """Calculate medical urgency level"""
        if disease == 'Normal':
            return 'low'
        elif disease == 'COVID-19' and confidence > 0.7:
            return 'high'
        elif disease == 'Pneumonia' and confidence > 0.8:
            return 'high'
        elif disease == 'Tuberculosis' and confidence > 0.7:
            return 'high'
        else:
            return 'medium'
    
    def generate_gradcam(self, img_path, output_path=None, layer_name=None):
        """
        Generate Grad-CAM visualization for interpretability
        
        Args:
            img_path: Path to input image
            output_path: Path to save heatmap
            layer_name: Layer name for Grad-CAM (default: last conv layer)
            
        Returns:
            Path to saved heatmap image
        """
        if self.use_tflite:
            print("[INFO] Grad-CAM not supported in TFLite mode")
            return None
            
        # Find last convolutional layer if not specified
        if layer_name is None:
            # For EfficientNet, use the last block's output
            for layer in reversed(self.model.layers):
                if 'block' in layer.name and hasattr(layer, 'output'):
                    try:
                        if len(layer.output.shape) == 4:
                            layer_name = layer.name
                            break
                    except:
                        continue
            
            # Fallback to any 4D layer
            if layer_name is None:
                for layer in reversed(self.model.layers):
                    if hasattr(layer, 'output'):
                        try:
                            if len(layer.output.shape) == 4:
                                layer_name = layer.name
                                break
                        except:
                            continue
        
        if layer_name is None:
            print("[WARNING] Could not find suitable layer for Grad-CAM")
            return None
        
        # Create grad model
        try:
            grad_model = Model(
                inputs=[self.model.inputs],
                outputs=[self.model.get_layer(layer_name).output, self.model.output]
            )
        except Exception as e:
            print(f"[WARNING] Grad-CAM model creation failed: {e}")
            return None
        
        # Preprocess image
        img_array = self.preprocess_image(img_path)
        
        # Get gradients
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)
            predicted_idx = tf.argmax(predictions[0])
            class_channel = predictions[:, predicted_idx]
        
        # Compute gradients
        grads = tape.gradient(class_channel, conv_outputs)
        
        # Pool gradients
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        # Weight conv outputs by gradients
        conv_outputs = conv_outputs[0].numpy()
        pooled_grads = pooled_grads.numpy()
        heatmap = conv_outputs @ pooled_grads[..., np.newaxis]
        heatmap = np.squeeze(heatmap)
        
        # Normalize heatmap
        heatmap = np.maximum(heatmap, 0)
        heatmap /= (np.max(heatmap) + 1e-10)
        
        # Load original image
        original_img = cv2.imread(img_path)
        if original_img is None:
            print(f"[WARNING] Could not load image: {img_path}")
            return None
            
        original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
        
        # Resize heatmap to match image
        heatmap = cv2.resize(heatmap, (original_img.shape[1], original_img.shape[0]))
        heatmap = np.uint8(255 * heatmap)
        
        # Apply colormap
        heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        
        # Superimpose heatmap on image
        superimposed = cv2.addWeighted(original_img, 0.6, heatmap, 0.4, 0)
        
        # Save if output path provided
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cv2.imwrite(output_path, cv2.cvtColor(superimposed, cv2.COLOR_RGB2BGR))
            return output_path
        
        return superimposed
    
    def save_model(self, path):
        """Save model to file"""
        if not path.endswith('.keras'):
            path = path.replace('.h5', '.keras')
        self.model.save(path)
        print(f"[SUCCESS] Model saved to {path}")
    
    def get_model_summary(self):
        """Get model architecture summary"""
        return self.model.summary()


# Utility function for batch prediction
def batch_predict(model, image_paths):
    """
    Predict multiple images at once
    
    Args:
        model: COVIDNetAnalyzer instance
        image_paths: List of image paths
        
    Returns:
        List of prediction results
    """
    results = []
    for img_path in image_paths:
        try:
            result = model.predict(img_path)
            result['image_path'] = img_path
            results.append(result)
        except Exception as e:
            results.append({
                'image_path': img_path,
                'error': str(e)
            })
    
    return results









