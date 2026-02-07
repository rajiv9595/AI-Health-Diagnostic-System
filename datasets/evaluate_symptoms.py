"""
Evaluate TF-IDF + Logistic Regression baseline on disease_symptom.csv
Writes a concise metrics report to reports/symptom_eval.md
Safe: does not alter running backend models.
"""
import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix


def evaluate_baseline(random_state: int = 42):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(root, 'datasets', 'disease_symptom.csv')
    out_dir = os.path.join(root, 'reports')
    os.makedirs(out_dir, exist_ok=True)
    out_md = os.path.join(out_dir, 'symptom_eval.md')

    df = pd.read_csv(csv_path)
    df = df.dropna(subset=['symptoms', 'disease'])
    X = df['symptoms'].astype(str).values
    y = df['disease'].astype(str).values

    # Some classes may have only 1 sample; fall back to non-stratified split in that case
    can_stratify = True
    try:
        pd.Series(y).value_counts().min()
        if pd.Series(y).value_counts().min() < 2:
            can_stratify = False
    except Exception:
        can_stratify = False

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y if can_stratify else None, random_state=random_state
    )

    vectorizer = TfidfVectorizer(max_features=3000, ngram_range=(1, 2), min_df=1)
    Xtr = vectorizer.fit_transform(X_train)
    Xte = vectorizer.transform(X_test)

    # Logistic Regression baseline
    clf = LogisticRegression(max_iter=2000, solver='saga', n_jobs=-1)
    clf.fit(Xtr, y_train)

    y_pred = clf.predict(Xte)
    acc = accuracy_score(y_test, y_pred)
    pr, rc, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted', zero_division=0)
    cm = confusion_matrix(y_test, y_pred, labels=sorted(np.unique(y)))

    # Top confusions
    conf_df = pd.DataFrame(cm, index=sorted(np.unique(y)), columns=sorted(np.unique(y)))
    conf_df_values = conf_df.copy()
    np.fill_diagonal(conf_df_values.values, 0)
    top_conf = conf_df_values.stack().sort_values(ascending=False).head(10)

    with open(out_md, 'w', encoding='utf-8') as f:
        f.write('# Symptom Baseline Evaluation (TF-IDF + Logistic Regression)\n\n')
        f.write(f'- Accuracy: {acc:.3f}\n')
        f.write(f'- Precision (weighted): {pr:.3f}\n')
        f.write(f'- Recall (weighted): {rc:.3f}\n')
        f.write(f'- F1 (weighted): {f1:.3f}\n\n')

        f.write('## Classification Report\n\n')
        f.write('```\n')
        f.write(classification_report(y_test, y_pred, zero_division=0))
        f.write('```\n\n')

        f.write('## Top Confusions\n\n')
        if top_conf.empty:
            f.write('_No significant confusions observed._\n\n')
        else:
            f.write('| True | Pred | Count |\n|---|---|---:|\n')
            for (true_lbl, pred_lbl), cnt in top_conf.items():
                if cnt > 0:
                    f.write(f'| {true_lbl} | {pred_lbl} | {int(cnt)} |\n')

        f.write('\n_Note: This evaluates the baseline model only; the running backend model remains unchanged._\n')

    print(f"[SUCCESS] Wrote metrics -> {out_md}")


if __name__ == '__main__':
    evaluate_baseline()


