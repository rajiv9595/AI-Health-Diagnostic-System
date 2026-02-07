# Symptom Baseline Evaluation (TF-IDF + Logistic Regression)

- Accuracy: 0.444
- Precision (weighted): 0.444
- Recall (weighted): 0.444
- F1 (weighted): 0.444

## Classification Report

```
                         precision    recall  f1-score   support

                   AIDS       0.00      0.00      0.00         1
                   Acne       0.00      0.00      0.00         2
                Allergy       1.00      1.00      1.00         2
             Bronchitis       0.00      0.00      0.00         1
               COVID-19       0.00      0.00      0.00         0
    Chronic cholestasis       0.00      0.00      0.00         1
            Common Cold       0.00      0.00      0.00         1
               Diabetes       1.00      1.00      1.00         1
  Dimorphic hemmorhoids       1.00      1.00      1.00         1
          Drug Reaction       0.00      0.00      0.00         0
       Fungal infection       1.00      1.00      1.00         1
                   GERD       0.00      0.00      0.00         0
            Hepatitis E       0.00      0.00      0.00         1
           Hypertension       0.00      0.00      0.00         2
                Malaria       0.00      0.00      0.00         0
               Migraine       1.00      1.00      1.00         1
         Osteoarthritis       1.00      1.00      1.00         1
              Pneumonia       0.00      0.00      0.00         0
           Tuberculosis       0.00      0.00      0.00         1
Urinary tract infection       1.00      1.00      1.00         1

               accuracy                           0.44        18
              macro avg       0.35      0.35      0.35        18
           weighted avg       0.44      0.44      0.44        18
```

## Top Confusions

| True | Pred | Count |
|---|---|---:|
| Hypertension | COVID-19 | 2 |
| Acne | Pneumonia | 1 |
| Bronchitis | Common Cold | 1 |
| Chronic cholestasis | GERD | 1 |
| Tuberculosis | Malaria | 1 |
| AIDS | Malaria | 1 |
| Acne | Drug Reaction | 1 |
| Common Cold | Tuberculosis | 1 |
| Hepatitis E | COVID-19 | 1 |

_Note: This evaluates the baseline model only; the running backend model remains unchanged._
