# Datasets

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
