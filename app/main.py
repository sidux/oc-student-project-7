import csv
import hashlib
import logging
import os
import pickle
import re
import time
from pathlib import Path
from typing import Dict, Optional, List

import tensorflow as tf
from tf_keras.preprocessing.text import Tokenizer
from tf_keras.preprocessing.sequence import pad_sequences
from nltk.corpus import stopwords
from snowballstemmer import stemmer as snowball_stemmer
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
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
import tensorflow_hub as hub

load_dotenv()

APP_DIR = Path(__file__).resolve().parent
MODEL_BASE_DIR = APP_DIR / "model"
TOKENIZER_PATH = MODEL_BASE_DIR / "tokenizer_stem.pkl"
TESTING = os.getenv("TESTING", "").lower() in ("1", "true", "yes")

FEEDBACK_FILE = APP_DIR / "feedback.csv"
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "bilstm")
APP_INSIGHTS_CONNECTION = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
TELEMETRY_ENABLED = bool(APP_INSIGHTS_CONNECTION and track_event and configure_azure_monitor)

VOCAB_SIZE = 10000
MAX_LENGTH = 30

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("tweet_app")

if TELEMETRY_ENABLED:
    configure_azure_monitor()
else:
    logger.warning("Application Insights connection string not set; telemetry disabled.")

if not FEEDBACK_FILE.exists():
    with open(FEEDBACK_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["text", "predicted_label", "confidence", "correct", "model"])

stop_words = set(stopwords.words('english'))
stemmer = snowball_stemmer("english")


def clean_text(text: str) -> str:
    """Preprocess text using stemming (same as training)."""
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in stop_words]
    tokens = stemmer.stemWords(tokens)
    return " ".join(tokens)


# Model registry to store loaded models
models: Dict[str, dict] = {}


def load_bilstm_model():
    """Load BiLSTM model and its tokenizer."""
    model_path = MODEL_BASE_DIR / "bilstm_stem_random"
    if not (model_path / "saved_model.pb").exists():
        return None
    
    print(f"Loading BiLSTM model from {model_path} ...")
    model = tf.saved_model.load(str(model_path))
    
    if TOKENIZER_PATH.exists():
        with open(TOKENIZER_PATH, 'rb') as f:
            tokenizer = pickle.load(f)
    else:
        return None
    
    return {"model": model, "tokenizer": tokenizer, "type": "bilstm"}


def load_bert_model():
    """Load BERT model and its tokenizer."""
    model_path = MODEL_BASE_DIR / "my_bert_model"
    if not model_path.exists():
        return None
    
    print(f"Loading BERT model from {model_path} ...")
    tokenizer = AutoTokenizer.from_pretrained(str(model_path))
    model = TFAutoModelForSequenceClassification.from_pretrained(str(model_path))
    
    return {"model": model, "tokenizer": tokenizer, "type": "bert"}


def load_use_model():
    """Load USE encoder and Dense classifier."""
    model_path = MODEL_BASE_DIR / "use_stem"
    if not (model_path / "saved_model.pb").exists():
        return None
    
    print("Loading USE encoder from TensorFlow Hub...")
    use_encoder = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
    
    print(f"Loading USE classifier from {model_path} ...")
    classifier = tf.saved_model.load(str(model_path))
    
    return {"model": classifier, "encoder": use_encoder, "type": "use"}


# Load all available models at startup
if not TESTING:
    bilstm = load_bilstm_model()
    if bilstm:
        models["bilstm"] = bilstm
        print("BiLSTM model loaded successfully")
    
    bert = load_bert_model()
    if bert:
        models["bert"] = bert
        print("BERT model loaded successfully")
    
    use = load_use_model()
    if use:
        models["use"] = use
        print("USE model loaded successfully")
    
    if not models:
        raise FileNotFoundError("No models found in app/model directory")

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


def classify_tweet_bilstm(text: str, tokenizer, model):
    """Classify using BiLSTM model."""
    cleaned = clean_text(text)
    seq = tokenizer.texts_to_sequences([cleaned])
    padded = pad_sequences(seq, maxlen=MAX_LENGTH, padding='post', truncating='post')
    
    input_tensor = tf.constant(padded, dtype=tf.float32)
    infer = model.signatures['serving_default']
    input_name = list(infer.structured_input_signature[1].keys())[0]
    outputs = infer(**{input_name: input_tensor})
    output_key = list(outputs.keys())[0]
    probs = outputs[output_key]
    
    predicted_id = tf.argmax(probs, axis=1).numpy()[0]
    confidence = float(tf.reduce_max(probs, axis=1).numpy()[0])
    label_str = label_map[predicted_id]

    return label_str, confidence


def classify_tweet_bert(text: str, tokenizer, model):
    """Classify using BERT model."""
    cleaned = clean_text(text)
    encoded = tokenizer.encode_plus(
        cleaned,
        add_special_tokens=True,
        max_length=MAX_LENGTH,
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


def classify_tweet_use(text: str, encoder, classifier):
    """Classify using USE model."""
    cleaned = clean_text(text)
    embeddings = encoder([cleaned]).numpy()
    
    input_tensor = tf.constant(embeddings, dtype=tf.float32)
    infer = classifier.signatures['serving_default']
    input_name = list(infer.structured_input_signature[1].keys())[0]
    outputs = infer(**{input_name: input_tensor})
    output_key = list(outputs.keys())[0]
    probs = outputs[output_key]
    
    predicted_id = tf.argmax(probs, axis=1).numpy()[0]
    confidence = float(tf.reduce_max(probs, axis=1).numpy()[0])
    label_str = label_map[predicted_id]

    return label_str, confidence


def classify_tweet(text: str, model_name: str = None):
    """Classify tweet using specified model."""
    if model_name is None:
        model_name = DEFAULT_MODEL
    
    if model_name not in models:
        available = list(models.keys())
        raise ValueError(f"Model '{model_name}' not found. Available: {available}")
    
    model_data = models[model_name]
    model = model_data["model"]
    model_type = model_data["type"]
    
    if model_type == "bilstm":
        return classify_tweet_bilstm(text, model_data["tokenizer"], model)
    elif model_type == "bert":
        return classify_tweet_bert(text, model_data["tokenizer"], model)
    elif model_type == "use":
        return classify_tweet_use(text, model_data["encoder"], model)
    else:
        raise ValueError(f"Unknown model type: {model_type}")


# 3. Define FastAPI app
app = FastAPI(title="Tweet Sentiment API", version="1.0")
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])
FastAPIInstrumentor.instrument_app(app)
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")


# 4. Request Body Schema
class TweetInput(BaseModel):
    text: str
    model: Optional[str] = None


# 5. Models Endpoint
@app.get("/models", summary="List available models")
def list_models() -> Dict:
    return {
        "models": list(models.keys()),
        "default": DEFAULT_MODEL
    }


# 6. Prediction Endpoint
@app.post("/predict", summary="Predict sentiment of a tweet")
def predict_sentiment(input_data: TweetInput) -> Dict:
    model_name = input_data.model or DEFAULT_MODEL
    start_time = time.perf_counter()
    label, confidence = classify_tweet(input_data.text, model_name)
    latency_ms = (time.perf_counter() - start_time) * 1000

    emit_event(
        "prediction",
        {
            "text_hash": hash_text(input_data.text),
            "predicted_label": label,
            "predicted_confidence": f"{confidence:.4f}",
            "model_version": model_name,
            "latency_ms": f"{latency_ms:.2f}",
        },
    )

    return {
        "label": label,
        "confidence": confidence,
        "model": model_name
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
    model: Optional[str] = None


@app.post("/feedback", summary="Submit feedback on prediction")
def store_feedback(feedback_data: FeedbackInput):
    model_name = feedback_data.model or DEFAULT_MODEL
    with open(FEEDBACK_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            feedback_data.text,
            feedback_data.label,
            feedback_data.confidence,
            feedback_data.correct,
            model_name
        ])

    emit_event(
        "feedback",
        {
            "text_hash": hash_text(feedback_data.text),
            "predicted_label": feedback_data.label,
            "predicted_confidence": f"{feedback_data.confidence:.4f}",
            "model_version": model_name,
            "correct": str(feedback_data.correct),
        },
    )

    return {"message": "Feedback submitted successfully"}
