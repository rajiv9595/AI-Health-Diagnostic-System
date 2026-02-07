"""
X-ray Image Analysis Model using DenseNet121
Includes Grad-CAM visualization
"""
import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications import DenseNet121
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.utils import load_img, img_to_array
import os


class XRayAnalyzer:
    """X-ray image analyzer with Grad-CAM visualization"""
    
    def __init__(self, model_path=None, input_shape=(224, 224, 3), num_classes=4):
        """
        Initialize X-ray analyzer
        
        Args:
            model_path: Path to saved model (.h5)
            input_shape: Input image shape
            num_classes: Number of disease classes
        """
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.class_names = ['Normal', 'Pneumonia', 'Tuberculosis', 'COVID-19']
        
        if model_path and os.path.exists(model_path):
            self.model = load_model(model_path)
            print(f"Loaded model from {model_path}")
        else:
            self.model = self._build_model()
            print("Created new model - needs training")
    
    def _build_model(self):
        """Build DenseNet121 model for X-ray classification"""
        # Load pre-trained DenseNet121
        base_model = DenseNet121(
            weights='imagenet',
            include_top=False,
            input_shape=self.input_shape
        )
        
        # Freeze base model layers
        for layer in base_model.layers[:-20]:
            layer.trainable = False
        
        # Add custom classification layers
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(512, activation='relu', name='dense_512')(x)
        x = Dropout(0.5)(x)
        x = Dense(256, activation='relu', name='dense_256')(x)
        x = Dropout(0.3)(x)
        predictions = Dense(self.num_classes, activation='softmax', name='output')(x)
        
        # Create model
        model = Model(inputs=base_model.input, outputs=predictions)
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.0001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def preprocess_image(self, img_path):
        """
        Preprocess image for model input
        
        Args:
            img_path: Path to image file
            
        Returns:
            Preprocessed image array
        """
        # Load image
        img = load_img(img_path, target_size=self.input_shape[:2])
        img_array = img_to_array(img)
        
        # Normalize
        img_array = img_array / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    def predict(self, img_path):
        """
        Predict disease from X-ray image
        
        Args:
            img_path: Path to X-ray image
            
        Returns:
            Dictionary with predictions and confidence scores
        """
        # Preprocess image
        img_array = self.preprocess_image(img_path)
        
        # Make prediction
        predictions = self.model.predict(img_array, verbose=0)[0]
        
        # Get predicted class
        predicted_idx = np.argmax(predictions)
        predicted_class = self.class_names[predicted_idx]
        confidence = float(predictions[predicted_idx])
        
        # Create predictions dictionary
        pred_dict = {
            self.class_names[i]: float(predictions[i])
            for i in range(len(self.class_names))
        }
        
        result = {
            'predicted_class': predicted_class,
            'confidence': confidence,
            'predictions': pred_dict,
            'is_abnormal': predicted_class != 'Normal'
        }
        
        return result
    
    def generate_gradcam(self, img_path, output_path=None, layer_name=None):
        """
        Generate Grad-CAM visualization
        
        Args:
            img_path: Path to input image
            output_path: Path to save heatmap
            layer_name: Layer name for Grad-CAM (default: last conv layer)
            
        Returns:
            Path to saved heatmap image
        """
        # Find last convolutional layer if not specified
        if layer_name is None:
            for layer in reversed(self.model.layers):
                # Check if layer has output_shape attribute and is 4D (conv layer)
                if hasattr(layer, 'output_shape'):
                    if len(layer.output_shape) == 4:
                        layer_name = layer.name
                        break
                elif hasattr(layer, 'output'):
                    # For functional API layers
                    output_shape = layer.output.shape
                    if len(output_shape) == 4:
                        layer_name = layer.name
                        break
        
        # Create grad model
        grad_model = Model(
            inputs=[self.model.inputs],
            outputs=[self.model.get_layer(layer_name).output, self.model.output]
        )
        
        # Preprocess image
        img_array = self.preprocess_image(img_path)
        
        # Get gradients
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)
            # Convert to tensor if needed
            if isinstance(predictions, list):
                predictions = predictions[0]
            predictions = tf.convert_to_tensor(predictions)
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
            cv2.imwrite(output_path, cv2.cvtColor(superimposed, cv2.COLOR_RGB2BGR))
            return output_path
        
        return superimposed
    
    def save_model(self, path):
        """Save model to file"""
        # Ensure path ends with .keras for newer TensorFlow versions
        if not path.endswith('.keras'):
            path = path.replace('.h5', '.keras')
        self.model.save(path)
        print(f"Model saved to {path}")
    
    def get_model_summary(self):
        """Get model architecture summary"""
        return self.model.summary()


# Utility function for batch prediction
def batch_predict(model, image_paths):
    """
    Predict multiple images at once
    
    Args:
        model: XRayAnalyzer instance
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

