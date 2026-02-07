"""
Dataset Splitting Utility
Splits your X-ray dataset into train/val folders (80/20 split)
"""
import os
import shutil
from pathlib import Path
import random


def split_dataset(source_dir, output_dir='xray_data', split_ratio=0.8, seed=42):
    """
    Split dataset into train/val folders
    
    Args:
        source_dir: Path to your dataset folder containing class folders
                   e.g., 'path/to/dataset' with subdirectories: Normal/, Pneumonia/, etc.
        output_dir: Output directory name (default: 'xray_data')
        split_ratio: Train/val split ratio (default: 0.8 for 80/20 split)
        seed: Random seed for reproducibility
    
    Expected source structure:
        source_dir/
        ├── Normal/
        │   ├── img1.jpg
        │   ├── img2.jpg
        ├── Pneumonia/
        ├── Tuberculosis/
        └── COVID-19/
    
    Output structure:
        output_dir/
        ├── train/
        │   ├── Normal/
        │   ├── Pneumonia/
        │   ├── Tuberculosis/
        │   └── COVID-19/
        └── val/
            └── (same structure)
    """
    random.seed(seed)
    
    # Get absolute paths
    source_path = Path(source_dir).resolve()
    output_path = Path(os.path.dirname(__file__)) / output_dir
    
    print("="*60)
    print("Dataset Splitting Utility")
    print("="*60)
    print(f"\nSource: {source_path}")
    print(f"Output: {output_path}")
    print(f"Split ratio: {split_ratio*100:.0f}% train, {(1-split_ratio)*100:.0f}% val\n")
    
    if not source_path.exists():
        print(f"❌ Error: Source directory not found!")
        print(f"   {source_path}")
        return
    
    # Get class folders
    class_folders = [d for d in source_path.iterdir() if d.is_dir()]
    
    if not class_folders:
        print("❌ Error: No class folders found in source directory!")
        return
    
    print(f"Found {len(class_folders)} classes:")
    for folder in class_folders:
        print(f"  - {folder.name}")
    print()
    
    # Process each class
    total_train = 0
    total_val = 0
    
    for class_folder in class_folders:
        class_name = class_folder.name
        print(f"Processing {class_name}...")
        
        # Get all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        images = [
            f for f in class_folder.iterdir() 
            if f.is_file() and f.suffix.lower() in image_extensions
        ]
        
        if not images:
            print(f"  ⚠️  No images found in {class_name}, skipping...")
            continue
        
        # Shuffle images
        random.shuffle(images)
        
        # Split
        split_idx = int(len(images) * split_ratio)
        train_images = images[:split_idx]
        val_images = images[split_idx:]
        
        # Create output directories
        train_class_dir = output_path / 'train' / class_name
        val_class_dir = output_path / 'val' / class_name
        train_class_dir.mkdir(parents=True, exist_ok=True)
        val_class_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy training images
        for img in train_images:
            shutil.copy2(img, train_class_dir / img.name)
        
        # Copy validation images
        for img in val_images:
            shutil.copy2(img, val_class_dir / img.name)
        
        print(f"  ✅ {len(train_images)} train, {len(val_images)} val")
        
        total_train += len(train_images)
        total_val += len(val_images)
    
    print("\n" + "="*60)
    print("Split Complete!")
    print("="*60)
    print(f"\nTotal images:")
    print(f"  Training: {total_train}")
    print(f"  Validation: {total_val}")
    print(f"  Total: {total_train + total_val}")
    print(f"\nDataset saved to: {output_path}")
    print("\nYou can now run: python train_models.py")


if __name__ == '__main__':
    import sys
    
    print("\n🔄 X-ray Dataset Splitter\n")
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python split_dataset.py <path_to_your_dataset>")
        print("\nExample:")
        print("  python split_dataset.py C:/Downloads/chest_xray_dataset")
        print("\nExpected structure of your dataset:")
        print("  your_dataset/")
        print("  ├── Normal/")
        print("  ├── Pneumonia/")
        print("  ├── Tuberculosis/")
        print("  └── COVID-19/")
        print("\nThis will create:")
        print("  datasets/xray_data/")
        print("  ├── train/ (80% of images)")
        print("  └── val/ (20% of images)")
        sys.exit(1)
    
    source_directory = sys.argv[1]
    split_dataset(source_directory)










