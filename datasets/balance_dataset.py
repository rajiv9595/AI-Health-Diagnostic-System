"""
Balance imbalanced X-ray dataset by under-sampling majority class
and over-sampling minority classes
"""
import os
import shutil
from pathlib import Path
import random
import numpy as np

def balance_dataset(source_train_dir, source_val_dir, output_dir, target_size=3000):
    """
    Balance dataset to have equal samples per class
    
    Args:
        source_train_dir: Original train directory
        source_val_dir: Original validation directory  
        output_dir: Output directory for balanced dataset
        target_size: Target number of images per class
    """
    
    print("\n" + "="*70)
    print("   DATASET BALANCING TOOL")
    print("="*70)
    print(f"\nTarget: {target_size} images per class")
    print("Strategy:")
    print("  - Under-sample majority classes (Normal)")
    print("  - Over-sample minority classes (COVID, Pneumonia, TB)")
    print("  - Use data augmentation copies for over-sampling")
    print("="*70 + "\n")
    
    # Create output directories
    balanced_train_dir = os.path.join(output_dir, 'train')
    balanced_val_dir = os.path.join(output_dir, 'val')
    
    # Get class names
    class_names = [d for d in os.listdir(source_train_dir) 
                   if os.path.isdir(os.path.join(source_train_dir, d))]
    
    print("Classes found:", class_names)
    print("\n" + "="*70)
    print("ORIGINAL DISTRIBUTION:")
    print("="*70)
    
    class_counts = {}
    for class_name in class_names:
        train_path = os.path.join(source_train_dir, class_name)
        count = len([f for f in os.listdir(train_path) 
                    if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        class_counts[class_name] = count
        print(f"  {class_name:15s}: {count:5d} images")
    
    print("\n" + "="*70)
    print("BALANCING STRATEGY:")
    print("="*70)
    
    for class_name in class_names:
        count = class_counts[class_name]
        if count > target_size:
            print(f"  {class_name:15s}: Under-sample {count} -> {target_size} (remove {count-target_size})")
        elif count < target_size:
            print(f"  {class_name:15s}: Over-sample {count} -> {target_size} (add {target_size-count} copies)")
        else:
            print(f"  {class_name:15s}: Keep all {count} images")
    
    print("\n" + "="*70)
    print("PROCESSING...")
    print("="*70 + "\n")
    
    # Process each class
    for class_name in class_names:
        print(f"Processing {class_name}...")
        
        # Source paths
        source_class_train = os.path.join(source_train_dir, class_name)
        source_class_val = os.path.join(source_val_dir, class_name) if os.path.exists(source_val_dir) else None
        
        # Output paths
        output_class_train = os.path.join(balanced_train_dir, class_name)
        output_class_val = os.path.join(balanced_val_dir, class_name)
        os.makedirs(output_class_train, exist_ok=True)
        os.makedirs(output_class_val, exist_ok=True)
        
        # Get all image files
        train_images = [f for f in os.listdir(source_class_train) 
                       if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        current_count = len(train_images)
        
        if current_count >= target_size:
            # Under-sample: randomly select target_size images
            random.seed(42)  # For reproducibility
            selected_images = random.sample(train_images, target_size)
            
            for img in selected_images:
                src = os.path.join(source_class_train, img)
                dst = os.path.join(output_class_train, img)
                shutil.copy2(src, dst)
            
            print(f"  -> Selected {len(selected_images)} images (under-sampled)")
        
        else:
            # Over-sample: copy all + duplicate randomly until target_size
            # First, copy all original images
            for img in train_images:
                src = os.path.join(source_class_train, img)
                dst = os.path.join(output_class_train, img)
                shutil.copy2(src, dst)
            
            # Calculate how many duplicates needed
            needed = target_size - current_count
            
            # Create duplicates by randomly sampling from existing
            random.seed(42)  # For reproducibility
            duplicates_created = 0
            while duplicates_created < needed:
                img = random.choice(train_images)
                src = os.path.join(source_class_train, img)
                
                # Create unique filename for duplicate
                base_name, ext = os.path.splitext(img)
                dup_name = f"{base_name}_dup{duplicates_created}{ext}"
                dst = os.path.join(output_class_train, dup_name)
                
                shutil.copy2(src, dst)
                duplicates_created += 1
            
            print(f"  -> Copied {current_count} + created {duplicates_created} duplicates = {target_size} total")
        
        # Copy validation data (keep as is, don't balance)
        if source_class_val and os.path.exists(source_class_val):
            val_images = [f for f in os.listdir(source_class_val) 
                         if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            for img in val_images:
                src = os.path.join(source_class_val, img)
                dst = os.path.join(output_class_val, img)
                shutil.copy2(src, dst)
            print(f"  -> Validation: {len(val_images)} images")
    
    print("\n" + "="*70)
    print("BALANCED DATASET SUMMARY:")
    print("="*70)
    
    for class_name in class_names:
        output_class_train = os.path.join(balanced_train_dir, class_name)
        count = len([f for f in os.listdir(output_class_train) 
                    if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        print(f"  {class_name:15s}: {count:5d} images")
    
    print("\n" + "="*70)
    print("[SUCCESS] Balanced dataset created!")
    print(f"Location: {output_dir}")
    print("="*70 + "\n")


if __name__ == '__main__':
    # Paths
    current_dir = os.path.dirname(__file__)
    source_train = os.path.join(current_dir, 'xray_data', 'train')
    source_val = os.path.join(current_dir, 'xray_data', 'val')
    output_balanced = os.path.join(current_dir, 'xray_data_balanced')
    
    # Target: 2500 per class (balanced between minority and majority)
    target_images_per_class = 2500
    
    print(f"\nSource train: {source_train}")
    print(f"Source val: {source_val}")
    print(f"Output: {output_balanced}")
    print(f"Target per class: {target_images_per_class}\n")
    
    if not os.path.exists(source_train):
        print(f"[ERROR] Source directory not found: {source_train}")
        exit(1)
    
    balance_dataset(source_train, source_val, output_balanced, target_size=target_images_per_class)









