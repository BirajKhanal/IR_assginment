import re

import joblib
from fastapi import APIRouter, Depends
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import ComplementNB
from sqlmodel import Session, select

from app.database import get_db
from app.models import Prediction

router = APIRouter(
    tags=["Task 2"],
)

MODEL_PATH = "app/trained_models/trained_model.pkl"


def clean_text(text: str) -> str:
    """Preprocess text (remove special chars, convert to lowercase, etc.)."""
    text = re.sub(r"\s+", " ", text)  # Remove excessive whitespace
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    return text.lower().strip()


@router.post("/train")
def train_model(db: Session = Depends(get_db)):
    """Train the Naïve Bayes classifier and save the trained model."""

    results = db.exec(select(Prediction.content, Prediction.category)).all()
    if not results:
        return {"message": "No data available for training"}

    texts, labels = zip(*results)
    texts = [clean_text(text) for text in texts]  # Preprocess text

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3), stop_words="english", norm="l2"
    )

    X = vectorizer.fit_transform(texts)

    model = ComplementNB(alpha=0.5)

    model.fit(X, labels)

    # Calibrate probabilities
    calibrated_model = CalibratedClassifierCV(model, cv=5)
    calibrated_model.fit(X, labels)

    joblib.dump(
        {
            "model": calibrated_model,
            "vectorizer": vectorizer,
        },
        MODEL_PATH,
    )

    return {
        "message": "Model trained and saved successfully",
        "total_samples": len(texts),
    }
