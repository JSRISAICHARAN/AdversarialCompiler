
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "c_vulnerability" / "dataset.csv"
MODEL_PATH = ROOT / "ml" / "code_classifier.joblib"
METRICS_PATH = ROOT / "ml" / "model_metrics.json"

NEGATIVE_LIMIT = 36_000
POSITIVE_LIMIT = 18_000
CHUNK_SIZE = 10_000
RANDOM_STATE = 42


def load_balanced_sample():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    negatives = []
    positives = []
    rng = np.random.default_rng(RANDOM_STATE)

    reader = pd.read_csv(
        DATA_PATH,
        usecols=["func", "target"],
        chunksize=CHUNK_SIZE,
    )

    for chunk in reader:
        chunk = chunk.dropna(subset=["func", "target"])
        chunk["target"] = pd.to_numeric(chunk["target"], errors="coerce")
        chunk = chunk.dropna(subset=["target"])
        chunk = chunk[chunk["target"].isin([0, 1])]

        for label, limit, bucket in [
            (0, NEGATIVE_LIMIT, negatives),
            (1, POSITIVE_LIMIT, positives),
        ]:
            remaining = limit - sum(len(part) for part in bucket)
            if remaining <= 0:
                continue

            candidates = chunk.loc[
                chunk["target"] == label, ["func", "target"]
            ]

            if len(candidates) > remaining:
                candidates = candidates.sample(
                    n=remaining,
                    random_state=int(rng.integers(0, 2**31 - 1)),
                )

            bucket.append(candidates)

        if (
            sum(len(part) for part in negatives) >= NEGATIVE_LIMIT
            and sum(len(part) for part in positives) >= POSITIVE_LIMIT
        ):
            break

    negative_df = pd.concat(negatives, ignore_index=True)
    positive_df = pd.concat(positives, ignore_index=True)
    data = pd.concat([negative_df, positive_df], ignore_index=True)

    data["func"] = data["func"].astype(str)
    data = data[data["func"].str.strip().ne("")]
    data = data.drop_duplicates(subset=["func"])

    if data["target"].nunique() != 2:
        raise ValueError("Both labels must be present in the training sample.")

    return data["func"].to_numpy(), data["target"].astype(int).to_numpy()


def main():
    print("Loading a memory-conscious sample from the real dataset...")
    X, y = load_balanced_sample()

    print(f"Usable functions: {len(X):,}")
    print("Class counts:", dict(zip(*np.unique(y, return_counts=True))))

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    model = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                analyzer="char",
                ngram_range=(3, 5),
                max_features=100_000,
                min_df=2,
                dtype=np.float32,
                sublinear_tf=True,
            ),
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=300,
                class_weight="balanced",
                random_state=RANDOM_STATE,
            ),
        ),
    ])

    print("Training TF-IDF + Logistic Regression...")
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print("\nClassification report:")
    print(classification_report(
        y_test,
        predictions,
        target_names=["label_0", "label_1"],
        zero_division=0,
    ))

    metrics = {
        "dataset": "Kaggle vulnerable C functions dataset",
        "sample_count": int(len(X)),
        "train_count": int(len(X_train)),
        "test_count": int(len(X_test)),
        "label_convention": {
            "0": "non-vulnerable (dataset label)",
            "1": "vulnerable (dataset label)",
        },
        "positive_class": 1,
        "precision_label_1": float(
            precision_score(y_test, predictions, zero_division=0)
        ),
        "recall_label_1": float(
            recall_score(y_test, predictions, zero_division=0)
        ),
        "f1_label_1": float(
            f1_score(y_test, predictions, zero_division=0)
        ),
        "confusion_matrix_labels_0_then_1": confusion_matrix(
            y_test, predictions, labels=[0, 1]
        ).tolist(),
        "model": "Character TF-IDF + Logistic Regression",
        "split": "random stratified split; not project-independent",
        "warning": (
            "Experimental classifier. Random splitting can cause "
            "project or duplicate leakage. Predictions do not prove "
            "that code is safe or vulnerable."
        ),
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    METRICS_PATH.write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )

    print(f"\nSaved model: {MODEL_PATH}")
    print(f"Saved metrics: {METRICS_PATH}")
    print("\nEvaluation metrics:")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
