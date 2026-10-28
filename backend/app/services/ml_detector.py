
from pathlib import Path
import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "ml" / "code_classifier.joblib"

_model = None


def predict_source(source_code: str) -> dict:
    global _model

    if not MODEL_PATH.exists():
        return {
            "available": False,
            "message": "Trained model not found. Run python ml/train_model.py",
        }

    try:
        if _model is None:
            _model = joblib.load(MODEL_PATH)

        prediction = int(_model.predict([source_code])[0])
        probabilities = _model.predict_proba([source_code])[0]

        return {
            "available": True,
            "predicted_label": prediction,
            "predicted_class": (
                "vulnerable_example"
                if prediction == 1
                else "non_vulnerable_example"
            ),
            "class_probabilities": {
                "label_0": round(float(probabilities[0]), 4),
                "label_1": round(float(probabilities[1]), 4),
            },
            "model_type": "Character TF-IDF + Logistic Regression",
            "warning": (
                "Experimental prediction based on dataset labels; "
                "not proof that code is safe or vulnerable."
            ),
        }
    except Exception as exc:
        return {
            "available": False,
            "message": f"Model prediction failed: {type(exc).__name__}: {exc}",
        }
