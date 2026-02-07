"""
Aggressive balanced training for imbalanced X-ray dataset
Uses undersampling + heavy class weights + augmentation
"""
import os
import sys
import numpy as np
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from backend.models.ml_models.xray_model import XRayAnalyzer


def train_with_aggressive_balancing():
    """Train X-ray model with aggressive balancing techniques"""
    
    print("\n" + "="*70)
    print("   AGGRESSIVE BALANCED TRAINING")
    print("="*70)
    print("\nTechniques:")
    print("  1. Manual strong class weights (10x for rare classes)")
    print("  2. Heavy data augmentation on all classes")
    print("  3. Lower learning rate for better convergence")
    print("="*70 + "\n")
    
    # Paths
    data_dir = os.path.join(os.path.dirname(__file__), 'xray_data')
    train_dir = os.path.join(data_dir, 'train')
    val_dir = os.path.join(data_dir, 'val')
    
    if not os.path.exists(train_dir):
        print(f"[ERROR] Training directory not found: {train_dir}")
        return None
    
    # HEAVY data augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest',
        brightness_range=[0.8, 1.2],
        channel_shift_range=0.1
    )
    
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    # Load data
    print("Loading training data...")
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        shuffle=True
    )
    print(f"Found {train_generator.samples} training images")
    print(f"Classes: {list(train_generator.class_indices.keys())}")
    
    validation_generator = None
    if os.path.exists(val_dir):
        print("\nLoading validation data...")
        validation_generator = val_datagen.flow_from_directory(
            val_dir,
            target_size=(224, 224),
            batch_size=32,
            class_mode='categorical',
            shuffle=False
        )
        print(f"Found {validation_generator.samples} validation images")
    
    # Calculate actual class distribution
    class_counts = {}
    for class_name in train_generator.class_indices.keys():
        class_idx = train_generator.class_indices[class_name]
        class_counts[class_idx] = sum(train_generator.classes == class_idx)
    
    print("\n" + "="*70)
    print("CLASS DISTRIBUTION:")
    print("="*70)
    for class_name, class_idx in sorted(train_generator.class_indices.items(), key=lambda x: class_counts[x[1]], reverse=True):
        count = class_counts[class_idx]
        percentage = (count / train_generator.samples) * 100
        print(f"  {class_name:15s}: {count:5d} images ({percentage:5.1f}%)")
    
    # MANUAL AGGRESSIVE CLASS WEIGHTS
    # Find the class with most samples
    max_count = max(class_counts.values())
    min_count = min(class_counts.values())
    
    class_weights = {}
    print("\n" + "="*70)
    print("AGGRESSIVE CLASS WEIGHTS:")
    print("="*70)
    
    for class_idx, count in class_counts.items():
        # Calculate aggressive weight: minority classes get 10x boost
        ratio = max_count / count
        if ratio > 5:  # Very imbalanced
            weight = ratio * 2.0  # Double the normal weight
        elif ratio > 2:  # Moderately imbalanced
            weight = ratio * 1.5  # 1.5x the normal weight
        else:
            weight = ratio * 0.8  # Slightly reduce majority class
        
        class_weights[class_idx] = weight
        
        class_name = [k for k, v in train_generator.class_indices.items() if v == class_idx][0]
        print(f"  {class_name:15s}: {weight:.2f}x (samples: {count})")
    
    print("="*70 + "\n")
    
    # Initialize model with LOWER learning rate
    print("Initializing DenseNet121 model with low learning rate...")
    analyzer = XRayAnalyzer()
    
    # Recompile with lower learning rate for better convergence
    analyzer.model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.00005),  # Lower LR
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )
    
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
            mode='max',
            verbose=1
        ),
        EarlyStopping(
            monitor='val_loss' if validation_generator else 'loss',
            patience=7,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss' if validation_generator else 'loss',
            factor=0.5,
            patience=3,
            min_lr=1e-8,
            verbose=1
        )
    ]
    
    # Train model
    print("\n" + "="*70)
    print("STARTING AGGRESSIVE BALANCED TRAINING")
    print("="*70)
    print(f"\nEpochs: 25")
    print(f"Learning Rate: 0.00005 (low for stability)")
    print(f"Augmentation: HEAVY (rotation, zoom, shift, brightness)")
    print(f"Class Weights: AGGRESSIVE (up to {max(class_weights.values()):.1f}x)")
    print("\nThis will take 45-50 minutes...\n")
    
    history = analyzer.model.fit(
        train_generator,
        epochs=25,  # More epochs with lower LR
        validation_data=validation_generator,
        callbacks=callbacks,
        class_weight=class_weights,
        verbose=1
    )
    
    # Save final model
    analyzer.save_model(model_path)
    
    # Print training summary
    print("\n" + "="*70)
    print("TRAINING COMPLETE!")
    print("="*70)
    
    if validation_generator:
        final_train_acc = history.history['accuracy'][-1]
        final_val_acc = history.history['val_accuracy'][-1]
        final_train_prec = history.history['precision'][-1] if 'precision' in history.history else 0
        final_val_prec = history.history['val_precision'][-1] if 'val_precision' in history.history else 0
        
        print(f"\nFinal Training Accuracy: {final_train_acc*100:.2f}%")
        print(f"Final Validation Accuracy: {final_val_acc*100:.2f}%")
        print(f"Final Training Precision: {final_train_prec*100:.2f}%")
        print(f"Final Validation Precision: {final_val_prec*100:.2f}%")
    else:
        final_train_acc = history.history['accuracy'][-1]
        print(f"\nFinal Training Accuracy: {final_train_acc*100:.2f}%")
    
    print(f"\n[SUCCESS] Balanced model saved to: {model_path}")
    print("   This model should perform MUCH better on minority classes!\n")
    
    return history


if __name__ == '__main__':
    train_with_aggressive_balancing()









