"""
Training script for AI Health Diagnostic System models
"""
import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.ml_models.symptom_model import SymptomChecker


def train_symptom_model():
    """Train symptom checker model"""
    print("\n" + "="*60)
    print("Training Symptom Checker Model")
    print("="*60)
    
    # Download required NLTK data
    import nltk
    try:
        nltk.download('punkt_tab', quiet=True)
    except:
        pass
    
    # Load dataset
    csv_path = os.path.join(os.path.dirname(__file__), 'disease_symptom.csv')
    df = pd.read_csv(csv_path)
    
    print(f"\nLoaded {len(df)} samples")
    print(f"Diseases: {df['disease'].nunique()}")
    
    # Prepare data
    symptoms = df['symptoms'].values
    diseases = df['disease'].values
    
    # Initialize model
    model = SymptomChecker()
    
    # Train model
    print("\nTraining model...")
    model.train(symptoms, diseases)
    
    # Test predictions
    print("\nTesting predictions...")
    test_cases = [
        "fever, cough, breathlessness, fatigue",
        "continuous sneezing, watering from eyes, chills",
        "chest pain, shortness of breath, sweating",
        "headache, blurred vision, stiff neck"
    ]
    
    for test_case in test_cases:
        result = model.predict(test_case)
        print(f"\nSymptoms: {test_case}")
        print(f"Predicted: {result['predicted_disease']} ({result['confidence']:.2%})")
        print(f"Urgency: {result['urgency_level']}")
    
    # Save model
    save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'saved_models')
    os.makedirs(save_dir, exist_ok=True)
    
    model_path = os.path.join(save_dir, 'symptom_model.pkl')
    vectorizer_path = os.path.join(save_dir, 'symptom_vectorizer.pkl')
    encoder_path = os.path.join(save_dir, 'symptom_label_encoder.pkl')
    
    model.save_model(model_path, vectorizer_path, encoder_path)
    
    print(f"\n[SUCCESS] Model saved successfully!")
    print(f"   - {model_path}")
    print(f"   - {vectorizer_path}")
    print(f"   - {encoder_path}")


def train_xray_model():
    """
    Train X-ray model on real dataset
    Expected structure:
    datasets/xray_data/
    ├── train/
    │   ├── Normal/
    │   ├── Pneumonia/
    │   ├── Tuberculosis/
    │   └── COVID-19/
    └── val/
        ├── Normal/
        ├── Pneumonia/
        ├── Tuberculosis/
        └── COVID-19/
    """
    print("\n" + "="*60)
    print("Training X-ray Model")
    print("="*60)
    
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
    from backend.models.ml_models.xray_model import XRayAnalyzer
    
    # Check if dataset exists - using BALANCED dataset
    train_dir = os.path.join(os.path.dirname(__file__), 'xray_data_balanced', 'train')
    val_dir = os.path.join(os.path.dirname(__file__), 'xray_data_balanced', 'val')
    
    if not os.path.exists(train_dir):
        print("\n[ERROR] X-ray training data not found!")
        print(f"   Expected location: {train_dir}")
        print("\nPlease organize your dataset as:")
        print("   datasets/xray_data/")
        print("   ├── train/")
        print("   │   ├── Normal/")
        print("   │   ├── Pneumonia/")
        print("   │   ├── Tuberculosis/")
        print("   │   └── COVID-19/")
        print("   └── val/")
        print("       └── (same structure)")
        print("\nSkipping X-ray training...")
        return
    
    print(f"\nFound training data at: {train_dir}")
    if os.path.exists(val_dir):
        print(f"Found validation data at: {val_dir}")
    else:
        print("⚠️  No validation data found, using training data only")
        val_dir = None
    
    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True,
        zoom_range=0.1,
        shear_range=0.1,
        fill_mode='nearest'
    )
    
    # Only rescaling for validation
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    # Load training data
    print("\nLoading training images...")
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        shuffle=True
    )
    
    print(f"Found {train_generator.samples} training images")
    print(f"Classes: {list(train_generator.class_indices.keys())}")
    
    # Load validation data if available
    validation_generator = None
    if val_dir:
        print("\nLoading validation images...")
        validation_generator = val_datagen.flow_from_directory(
            val_dir,
            target_size=(224, 224),
            batch_size=32,
            class_mode='categorical',
            shuffle=False
        )
        print(f"Found {validation_generator.samples} validation images")
    
    # Initialize model
    print("\nInitializing DenseNet121 model...")
    analyzer = XRayAnalyzer()
    
    # Save directory
    save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'saved_models')
    os.makedirs(save_dir, exist_ok=True)
    model_path = os.path.join(save_dir, 'xray_model.keras')
    
    # Callbacks
    callbacks = [
        ModelCheckpoint(
            model_path,
            monitor='val_accuracy' if validation_generator else 'accuracy',
            save_best_only=True,
            verbose=0  # Silent to avoid encoding issues
        ),
        EarlyStopping(
            monitor='val_loss' if validation_generator else 'loss',
            patience=5,
            restore_best_weights=True,
            verbose=0  # Silent to avoid encoding issues
        ),
        ReduceLROnPlateau(
            monitor='val_loss' if validation_generator else 'loss',
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=0  # Silent to avoid encoding issues
        )
    ]
    
    # Dataset is already balanced, no need for class weights!
    print("\n" + "="*60)
    print("Class Distribution (BALANCED):")
    print("="*60)
    class_counts = {}
    for class_name in train_generator.class_indices.keys():
        class_idx = train_generator.class_indices[class_name]
        class_counts[class_idx] = sum(train_generator.classes == class_idx)
        print(f"  {class_name}: {class_counts[class_idx]} images")
    
    # Train model
    print("\n" + "="*60)
    print("Starting Training with BALANCED Dataset...")
    print("="*60)
    print("\nAll classes have equal representation!")
    print("Training with data augmentation for better generalization.\n")
    
    history = analyzer.model.fit(
        train_generator,
        epochs=20,  # Adjust based on your needs
        validation_data=validation_generator,
        callbacks=callbacks,
        verbose=2  # Use 2 to avoid progress bar encoding issues on Windows
    )
    
    # Save final model
    analyzer.save_model(model_path)
    
    # Print training summary
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)
    
    if validation_generator:
        final_train_acc = history.history['accuracy'][-1]
        final_val_acc = history.history['val_accuracy'][-1]
        print(f"\nFinal Training Accuracy: {final_train_acc*100:.2f}%")
        print(f"Final Validation Accuracy: {final_val_acc*100:.2f}%")
    else:
        final_train_acc = history.history['accuracy'][-1]
        print(f"\nFinal Training Accuracy: {final_train_acc*100:.2f}%")
    
    print(f"\n[SUCCESS] Model saved to: {model_path}")
    print("   Ready for production use!")
    
    return history


def create_sample_readme():
    """Create a README for the datasets folder"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    
    content = """# Datasets

This folder contains sample datasets and model training scripts for the AI Health Diagnostic System.

## Files

### disease_symptom.csv
Sample symptom-disease dataset for training the symptom checker model.
- Contains symptom descriptions and corresponding diseases
- Used by the NLP symptom checker

### train_models.py
Training script for both symptom checker and X-ray analysis models.

## Usage

### Train Symptom Checker

```bash
cd datasets
python train_models.py
```

This will:
1. Load the symptom-disease dataset
2. Train a Naive Bayes classifier
3. Save the trained model to `backend/saved_models/`

### X-ray Model Training

For X-ray analysis, you'll need to:

1. Download a real chest X-ray dataset:
   - **NIH Chest X-ray Dataset**: https://www.nih.gov/news-events/news-releases/nih-clinical-center-provides-one-largest-publicly-available-chest-x-ray-datasets-scientific-community
   - **COVID-19 Radiography Database**: https://www.kaggle.com/tawsifurrahman/covid19-radiography-database
   - **ChestX-ray14**: https://nihcc.app.box.com/v/ChestXray-NIHCC

2. Organize images into folders by class:
   ```
   datasets/xray_data/
   ├── train/
   │   ├── Normal/
   │   ├── Pneumonia/
   │   ├── Tuberculosis/
   │   └── COVID-19/
   └── val/
       ├── Normal/
       ├── Pneumonia/
       ├── Tuberculosis/
       └── COVID-19/
   ```

3. Modify `train_models.py` to include X-ray training code

## Sample X-rays

For testing purposes, you can place sample X-ray images in:
```
datasets/sample_xrays/
```

## Model Files

Trained models are saved to:
```
backend/saved_models/
├── symptom_model.pkl
├── symptom_vectorizer.pkl
├── symptom_label_encoder.pkl
└── xray_model.h5
```

## Notes

- The symptom checker model trains quickly on CPU
- X-ray model training requires GPU for reasonable speed
- For production use, collect more diverse symptom-disease pairs
- Consider data augmentation for X-ray training

## Medical Disclaimer

These models are for educational purposes only and should not be used for actual medical diagnosis.
"""
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n[SUCCESS] Created dataset README: {readme_path}")


if __name__ == '__main__':
    print("\n=== AI Health Diagnostic System - Model Training ===")
    print("="*60)
    
    # Train symptom checker
    try:
        train_symptom_model()
    except Exception as e:
        print(f"\n[ERROR] Error training symptom model: {e}")
    
    # Train X-ray model
    try:
        train_xray_model()
    except Exception as e:
        print(f"\n[ERROR] Error training X-ray model: {e}")
        import traceback
        traceback.print_exc()
    
    # Create README
    try:
        create_sample_readme()
    except Exception as e:
        print(f"\n[ERROR] Error creating README: {e}")
    
    print("\n" + "="*60)
    print("[SUCCESS] Model training complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start the backend: cd backend && python app.py")
    print("2. Start the frontend: cd frontend && npm start")
    print("3. Access the app at http://localhost:3000")
    print("="*60 + "\n")

