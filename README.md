
# AdversarialCompiler

### Robust Compiler Design Against Adversarial Source Code

## Overview
AdversarialCompiler is a research prototype for analyzing C source code using static security analysis, machine-learning classification, GCC compilation checks, and robustness testing.

## Features
- Detect selected risky coding patterns using static analysis.
- Classify source code using a trained machine-learning model.
- Check C compilation with GCC.
- Test whether simple formatting changes affect model predictions.
- Display results in a web dashboard.

## Technologies
- Python
- FastAPI
- HTML, CSS, JavaScript
- scikit-learn
- TF-IDF
- Logistic Regression
- GCC
- Git and GitHub

## Project Structure
- `backend/` — FastAPI backend and analysis services
- `frontend/` — Web dashboard
- `ml/` — Model training, saved model, and evaluation metrics
- `tests/` — Automated tests
- `data/` — Dataset files, if included

## Run Locally
Install the required Python packages, ensure GCC is available, and start the backend:

```bash
python -m uvicorn backend.app.main:app --reload
```

In another terminal, start the frontend:

```bash
python -m http.server 5500 --directory frontend
```

Open `http://127.0.0.1:5500` in your browser.

API documentation: `http://127.0.0.1:8000/docs`

## Limitations
This is an experimental research prototype. Its static rules cover selected patterns, its ML predictions depend on the training data, and successful compilation does not guarantee security.

## Disclaimer
Do not treat the model's predictions as proof that code is safe or vulnerable.
