import os

import joblib
from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Create the FastAPI router
router = APIRouter(
    tags=["Task 2"],
)
templates = Jinja2Templates(directory="app/templates")


# Define request schema (Only needed for API requests)
class QueryInput(BaseModel):
    text: str


@router.get("/task2")
async def show_classification_page(request: Request):
    """Renders the classification page."""
    return templates.TemplateResponse(
        "classification.html", {"request": request}
    )


@router.post("/task2")
async def classify_text(request: Request, text: str = Form(...)):
    """Classifies the input text and returns classification + accuracy."""

    MODEL_PATH = "app/trained_models/trained_model.pkl"

    # Load the trained model and vectorizer
    if not os.path.exists(MODEL_PATH):
        return templates.TemplateResponse(
            "classification.html",
            {
                "request": request,
                "error": "Trained model not found. Please train the model first.",
            },
        )

    loaded_data = joblib.load(MODEL_PATH)
    model = loaded_data["model"]
    vectorizer = loaded_data["vectorizer"]

    try:
        # Transform the input text using the trained vectorizer
        query_vectorized = vectorizer.transform([text])

        # Ensure the input is not empty after vectorization
        if query_vectorized.shape[1] == 0:
            return templates.TemplateResponse(
                "classification.html",
                {
                    "request": request,
                    "error": "Input text contains no known words.",
                },
            )

        # Predict classification
        probs = model.predict_proba(query_vectorized)[0]
        prediction = model.predict(query_vectorized)[0]

        # Confidence: Probability of the predicted class
        confidence_index = list(model.classes_).index(prediction)
        confidence = probs[confidence_index]

        return templates.TemplateResponse(
            "classification.html",
            {
                "request": request,
                "classification": prediction,
                "accuracy": round(float(confidence * 100), 2),
                "probabilities": dict(zip(model.classes_, probs)),
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "classification.html", {"request": request, "error": str(e)}
        )
