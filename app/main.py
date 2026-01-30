import csv
import hashlib
import logging
import os
import time
from pathlib import Path
from typing import Dict

import tensorflow as tf
try:  # Optional during local/tests where Azure libs may be unavailable
    from azure.monitor.events.extension import track_event
    from azure.monitor.opentelemetry import configure_azure_monitor
except ImportError:  # pragma: no cover - fallback for lightweight environments
    track_event = None
    configure_azure_monitor = None
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from pydantic import BaseModel
from transformers import BertTokenizer, TFBertForSequenceClassification

load_dotenv()

APP_DIR = Path(__file__).resolve().parent
MODEL_DIR = APP_DIR / "model" / "my_bert_model"
FALLBACK_MODEL_DIR = APP_DIR.parent / "result" / "my_bert_model"
TESTING = os.getenv("TESTING", "").lower() in ("1", "true", "yes")
MODEL_PATH = MODEL_DIR if MODEL_DIR.exists() else FALLBACK_MODEL_DIR
if not TESTING and not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Could not find a fine-tuned BERT model in {MODEL_DIR} "
        f"or {FALLBACK_MODEL_DIR}. Run the notebook to export the model first."
    )

FEEDBACK_FILE = APP_DIR / "feedback.csv"
MODEL_VERSION = os.getenv("MODEL_VERSION", "bert-finetuned")
APP_INSIGHTS_CONNECTION = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
TELEMETRY_ENABLED = bool(APP_INSIGHTS_CONNECTION and track_event and configure_azure_monitor)

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("tweet_app")

if TELEMETRY_ENABLED:
    configure_azure_monitor()
else:
    logger.warning("Application Insights connection string not set; telemetry disabled.")

if not FEEDBACK_FILE.exists():
    with open(FEEDBACK_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["text", "predicted_label", "confidence", "correct"])

# 1. Load model and tokenizer at startup (or lazily in the endpoint)
if not TESTING:
    print(f"Loading model and tokenizer from {MODEL_PATH} ...")
    tokenizer = BertTokenizer.from_pretrained(str(MODEL_PATH))
    model = TFBertForSequenceClassification.from_pretrained(str(MODEL_PATH))
else:
    tokenizer = None  # type: ignore[assignment]
    model = None  # type: ignore[assignment]

# 2. Your classify_tweet function goes here
label_map = {0: "Negative", 1: "Neutral", 2: "Positive"}


def hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def emit_event(name: str, properties: Dict[str, str]) -> None:
    safe_properties = {k: str(v) for k, v in properties.items()}

    if TELEMETRY_ENABLED:
        try:
            track_event(name, safe_properties)
        except Exception as exc:
            logger.warning("Failed to send telemetry event %s: %s", name, exc)

    logger.info(name, extra={"custom_dimensions": safe_properties})


def classify_tweet(text: str, tokenizer, model, max_len=30):
    encoded = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=max_len,
        truncation=True,
        padding='max_length',
        return_attention_mask=True,
        return_tensors='tf'
    )

    outputs = model(encoded['input_ids'], attention_mask=encoded['attention_mask'])
    probs = tf.nn.softmax(outputs.logits, axis=-1)

    predicted_id = tf.argmax(probs, axis=1).numpy()[0]
    confidence = float(tf.reduce_max(probs, axis=1).numpy()[0])
    label_str = label_map[predicted_id]

    return label_str, confidence


# 3. Define FastAPI app
app = FastAPI(title="Tweet Sentiment API", version="1.0")
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])
FastAPIInstrumentor.instrument_app(app)
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")


# 4. Request Body Schema
class TweetInput(BaseModel):
    text: str


# 5. Prediction Endpoint
@app.post("/predict", summary="Predict sentiment of a tweet")
def predict_sentiment(input_data: TweetInput) -> Dict:
    start_time = time.perf_counter()
    label, confidence = classify_tweet(input_data.text, tokenizer, model)
    latency_ms = (time.perf_counter() - start_time) * 1000

    emit_event(
        "prediction",
        {
            "text_hash": hash_text(input_data.text),
            "predicted_label": label,
            "predicted_confidence": f"{confidence:.4f}",
            "model_version": MODEL_VERSION,
            "latency_ms": f"{latency_ms:.2f}",
        },
    )

    return {
        "label": label,
        "confidence": confidence
    }


templates = Jinja2Templates(directory=str(APP_DIR / "templates"))


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Feedback Endpoint
class FeedbackInput(BaseModel):
    text: str
    label: str
    confidence: float
    correct: bool


@app.post("/feedback", summary="Submit feedback on prediction")
def store_feedback(feedback_data: FeedbackInput):
    with open(FEEDBACK_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            feedback_data.text,
            feedback_data.label,
            feedback_data.confidence,
            feedback_data.correct
        ])

    emit_event(
        "feedback",
        {
            "text_hash": hash_text(feedback_data.text),
            "predicted_label": feedback_data.label,
            "predicted_confidence": f"{feedback_data.confidence:.4f}",
            "model_version": MODEL_VERSION,
            "correct": str(feedback_data.correct),
        },
    )

    return {"message": "Feedback submitted successfully"}
