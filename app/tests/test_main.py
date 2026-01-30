import csv
import sys
from importlib import util as importlib_util
from pathlib import Path

import pytest
import tensorflow as tf
from fastapi.testclient import TestClient


class _DummyTokenizer:
    def texts_to_sequences(self, texts):
        return [[1, 2, 3, 4, 5] for _ in texts]


class _DummyInfer:
    def __init__(self):
        self.structured_input_signature = (None, {"embedding_input": None})
    
    def __call__(self, **kwargs):
        probs = tf.constant([[0.1, 0.2, 0.7]], dtype=tf.float32)
        return {"dense_1": probs}


class _DummyModel:
    def __init__(self):
        self.signatures = {"serving_default": _DummyInfer()}


@pytest.fixture
def app_module(monkeypatch, tmp_path):
    """Reload app.main with lightweight tokenizer/model stubs."""
    sys.modules.pop("app.main", None)
    monkeypatch.setenv("TESTING", "1")

    module_path = Path(__file__).resolve().parents[1] / "main.py"
    spec = importlib_util.spec_from_file_location("app.main", module_path)
    assert spec and spec.loader, "Could not build spec for app.main"
    app_main = importlib_util.module_from_spec(spec)
    spec.loader.exec_module(app_main)

    app_main.models = {
        "bilstm": {
            "model": _DummyModel(),
            "tokenizer": _DummyTokenizer(),
            "type": "bilstm"
        }
    }
    app_main.DEFAULT_MODEL = "bilstm"
    app_main.FEEDBACK_FILE = tmp_path / "feedback.csv"
    return app_main


def test_hash_text_is_deterministic(app_module):
    first = app_module.hash_text("hello world")
    second = app_module.hash_text("hello world")
    different = app_module.hash_text("other")

    assert first == second
    assert first != different


def test_classify_tweet_returns_positive_label(app_module):
    label, confidence = app_module.classify_tweet("Great service!", "bilstm")

    assert label == "Positive"
    assert 0 <= confidence <= 1


def test_models_endpoint_returns_available_models(app_module):
    with TestClient(app_module.app) as client:
        response = client.get("/models")

    assert response.status_code == 200
    body = response.json()
    assert "models" in body
    assert "bilstm" in body["models"]
    assert body["default"] == "bilstm"


def test_predict_endpoint_uses_mocked_model(app_module):
    with TestClient(app_module.app) as client:
        response = client.post("/predict", json={"text": "Great company!"})

    assert response.status_code == 200
    body = response.json()
    assert body["label"] == "Positive"
    assert 0 <= body["confidence"] <= 1
    assert body["model"] == "bilstm"


def test_predict_endpoint_with_model_selection(app_module):
    with TestClient(app_module.app) as client:
        response = client.post("/predict", json={"text": "Great!", "model": "bilstm"})

    assert response.status_code == 200
    body = response.json()
    assert body["model"] == "bilstm"


def test_feedback_endpoint_persists_rows(app_module):
    app_module.FEEDBACK_FILE.write_text("text,predicted_label,confidence,correct,model\n")

    payload = {
        "text": "Great company!",
        "label": "Positive",
        "confidence": 0.95,
        "correct": True,
        "model": "bilstm"
    }
    with TestClient(app_module.app) as client:
        response = client.post("/feedback", json=payload)

    assert response.status_code == 200

    with app_module.FEEDBACK_FILE.open() as handle:
        reader = list(csv.DictReader(handle))

    assert len(reader) == 1
    assert reader[0]["text"] == payload["text"]
    assert reader[0]["predicted_label"] == payload["label"]
    assert reader[0]["model"] == payload["model"]
