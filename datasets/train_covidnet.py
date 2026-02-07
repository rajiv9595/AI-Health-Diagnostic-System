"""
Train COVID-Net (EfficientNetB4) model with balanced dataset
"""
import os
import sys
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from backend.models.ml_models.covidnet_model import COVIDNetAnalyzer


def train_covidnet():
    """Train COVID-Net model with balanced dataset"""
    
    print("\n" + "="*70)
    print("   COVID-NET TRAINING (EfficientNetB4)")
    print("="*70)
    print("\nModel: EfficientNetB4 + Custom Medical Head")
    print("Dataset: Balanced (2,500 images per class)")
    print("Optimizer: Adam with learning rate 0.0001")
    print("="*70 + "\n")
    
    # Paths - use balanced dataset
    data_dir = os.path.join(os.path.dirname(__file__), 'xray_data_balanced')
    train_dir = os.path.join(data_dir, 'train')
    val_dir = os.path.join(data_dir, 'val')
    
    if not os.path.exists(train_dir):
        print(f"[ERROR] Balanced training data not found: {train_dir}")
        print("\nPlease run balance_dataset.py first!")
        return None
    
    # Data augmentation with medical imaging best practices
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        shear_range=0.1,
        zoom_range=0.1,
        horizontal_flip=True,
        fill_mode='nearest'
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
    
    # Display class distribution
    print("\n" + "="*70)
    print("CLASS DISTRIBUTION (BALANCED):")
    print("="*70)
    class_counts = {}
    for class_name in train_generator.class_indices.keys():
        class_idx = train_generator.class_indices[class_name]
        class_counts[class_idx] = sum(train_generator.classes == class_idx)
        print(f"  {class_name:15s}: {class_counts[class_idx]:5d} images")
    print("="*70 + "\n")
    
    # Initialize COVID-Net analyzer
    print("Initializing COVID-Net (EfficientNetB4)...")
    analyzer = COVIDNetAnalyzer()
    
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
    print("STARTING COVID-NET TRAINING")
    print("="*70)
    print(f"\nEpochs: 15")
    print(f"Learning Rate: 0.0001")
    print(f"Model: EfficientNetB4 (Medical-grade)")
    print(f"Expected time: ~25-30 minutes\n")
    
    history = analyzer.model.fit(
        train_generator,
        epochs=15,  # Fewer epochs needed with EfficientNet
        validation_data=validation_generator,
        callbacks=callbacks,
        verbose=1
    )
    
    # Save final model
    analyzer.save_model(model_path)
    
    # Print training summary
    print("\n" + "="*70)
    print("COVID-NET TRAINING COMPLETE!")
    print("="*70)
    
    if validation_generator:
        final_train_acc = history.history['accuracy'][-1]
        final_val_acc = history.history['val_accuracy'][-1]
        final_train_prec = history.history['precision'][-1]
        final_val_prec = history.history['val_precision'][-1]
        final_train_rec = history.history['recall'][-1]
        final_val_rec = history.history['val_recall'][-1]
        
        print(f"\nFinal Training Metrics:")
        print(f"  Accuracy:  {final_train_acc*100:.2f}%")
        print(f"  Precision: {final_train_prec*100:.2f}%")
        print(f"  Recall:    {final_train_rec*100:.2f}%")
        
        print(f"\nFinal Validation Metrics:")
        print(f"  Accuracy:  {final_val_acc*100:.2f}%")
        print(f"  Precision: {final_val_prec*100:.2f}%")
        print(f"  Recall:    {final_val_rec*100:.2f}%")
    else:
        final_train_acc = history.history['accuracy'][-1]
        print(f"\nFinal Training Accuracy: {final_train_acc*100:.2f}%")
    
    print(f"\n[SUCCESS] COVID-Net model saved to: {model_path}")
    print("   Medical-grade model ready for deployment!\n")
    
    return history


if __name__ == '__main__':
    train_covidnet()









