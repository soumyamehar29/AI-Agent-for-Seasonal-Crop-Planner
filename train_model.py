"""
train_model.py
==============
Train the Random Forest Classifier on the Crop Recommendation Dataset.

Usage:
    python train_model.py

This script:
1. Loads data/Crop_recommendation.csv
2. Validates required columns
3. Handles missing values
4. Trains a Random Forest model
5. Evaluates the model and prints metrics
6. Saves the trained model to model/crop_model.pkl
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, classification_report, confusion_matrix
)
import joblib

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
DATA_PATH  = os.path.join("data", "Crop_recommendation.csv")
MODEL_DIR  = "model"
MODEL_PATH = os.path.join(MODEL_DIR, "crop_model.pkl")

REQUIRED_COLUMNS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall", "label"]
FEATURE_COLS     = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
TARGET_COL       = "label"

RF_PARAMS = {
    "n_estimators": 200,
    "random_state": 42,
    "n_jobs": -1,
}

TEST_SIZE    = 0.20
RANDOM_STATE = 42


def print_banner():
    print("=" * 60)
    print("  AI Agent for Seasonal Crop Planning")
    print("  Model Training Script")
    print("=" * 60)


def load_and_validate_data(path: str) -> pd.DataFrame:
    """Load CSV and check for required columns."""
    if not os.path.exists(path):
        print(f"\n[ERROR] Dataset not found at: {path}")
        print("\nPlease follow these steps:")
        print("  1. Download the Crop Recommendation Dataset.")
        print("  2. Place the CSV file at:  data/Crop_recommendation.csv")
        print("     The file MUST contain these columns:")
        print(f"     {REQUIRED_COLUMNS}")
        print("\n  Popular source: https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset")
        sys.exit(1)

    print(f"\n[INFO] Loading dataset from: {path}")
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"[ERROR] Failed to read CSV: {e}")
        sys.exit(1)

    print(f"[INFO] Dataset loaded: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"[INFO] Columns found: {list(df.columns)}")

    # Column name normalisation (strip whitespace, lowercase)
    df.columns = [c.strip() for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        print(f"\n[ERROR] Missing required columns: {missing}")
        print(f"  Expected: {REQUIRED_COLUMNS}")
        print(f"  Found:    {list(df.columns)}")
        sys.exit(1)

    return df


def preprocess_data(df: pd.DataFrame):
    """Handle missing values and extract features/target."""
    initial_rows = len(df)

    # Drop rows where target is missing
    df = df.dropna(subset=[TARGET_COL])

    # Fill numeric NaN with column median
    for col in FEATURE_COLS:
        if df[col].isna().sum() > 0:
            median_val = df[col].median()
            print(f"[WARN] Column '{col}' has {df[col].isna().sum()} missing values. "
                  f"Filling with median ({median_val:.2f}).")
            df[col] = df[col].fillna(median_val)

    cleaned_rows = len(df)
    if initial_rows != cleaned_rows:
        print(f"[INFO] Removed {initial_rows - cleaned_rows} rows with missing target values.")

    # Use .to_numpy() to get a plain NumPy array.
    # pandas 3.0+ may use a PyArrow-backed ArrowExtensionArray by default,
    # which scikit-learn's _safe_indexing cannot index. Explicit conversion avoids this.
    X = df[FEATURE_COLS].to_numpy(dtype=float)
    y = df[TARGET_COL].to_numpy(dtype=str)

    print(f"\n[INFO] Feature matrix shape : {X.shape}")
    print(f"[INFO] Target vector shape  : {y.shape}")
    print(f"[INFO] Unique crops (classes): {len(np.unique(y))}")
    print(f"[INFO] Crops: {sorted(np.unique(y).tolist())}")

    return X, y


def train_model(X_train, y_train):
    """Train a Random Forest Classifier."""
    print(f"\n[INFO] Training RandomForestClassifier with params: {RF_PARAMS}")
    model = RandomForestClassifier(**RF_PARAMS)
    model.fit(X_train, y_train)
    print("[INFO] Training complete.")
    return model


def evaluate_model(model, X_test, y_test):
    """Print evaluation metrics."""
    y_pred = model.predict(X_test)

    acc  = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    rec  = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1   = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    print("\n" + "=" * 60)
    print("  MODEL EVALUATION RESULTS")
    print("=" * 60)
    print(f"  Accuracy  : {acc  * 100:.2f}%")
    print(f"  Precision : {prec * 100:.2f}%")
    print(f"  Recall    : {rec  * 100:.2f}%")
    print(f"  F1-Score  : {f1   * 100:.2f}%")
    print("=" * 60)

    print("\n[INFO] Detailed Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    # Condensed confusion matrix summary
    cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
    correct = cm.diagonal().sum()
    total   = cm.sum()
    print(f"[INFO] Confusion Matrix: {correct}/{total} correctly classified samples.")

    return acc


def save_model(model, path: str):
    """Save the trained model using joblib."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model, path)
    print(f"\n[INFO] Model saved to: {path}")
    size_kb = os.path.getsize(path) / 1024
    print(f"[INFO] Model file size: {size_kb:.1f} KB")


def main():
    print_banner()

    # 1. Load & validate
    df = load_and_validate_data(DATA_PATH)

    # 2. Preprocess
    X, y = preprocess_data(df)

    # 3. Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    print(f"\n[INFO] Train samples : {len(X_train)}")
    print(f"[INFO] Test  samples : {len(X_test)}")

    # 4. Train
    model = train_model(X_train, y_train)

    # 5. Evaluate
    evaluate_model(model, X_test, y_test)

    # 6. Save
    save_model(model, MODEL_PATH)

    print("\n[OK] Model training complete!")
    print("[OK] Run the application with:  python app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
