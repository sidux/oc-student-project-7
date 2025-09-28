import csv
import sys
from importlib import util as importlib_util
from pathlib import Path
from types import SimpleNamespace

import pytest
import tensorflow as tf
from fastapi.testclient import TestClient


class _DummyTokenizer:
    def encode_plus(self, text, **kwargs):
        max_length = kwargs.get("max_length", 30)
        padding_length = max_length - 1
        token_ids = [101] + [100] * padding_length
        mask = [1] * max_length
        return {
            "input_ids": tf.constant([token_ids], dtype=tf.int32),
            "attention_mask": tf.constant([mask], dtype=tf.int32),
        }


class _DummyModel:
    def __call__(self, input_ids, attention_mask=None):
        logits = tf.constant([[0.1, 0.2, 3.0]], dtype=tf.float32)
        return SimpleNamespace(logits=logits)


@pytest.fixture
def app_module(monkeypatch, tmp_path):
    """Reload app.main with lightweight tokenizer/model stubs."""
    import transformers

    sys.modules.pop("app.main", None)

    dummy_tokenizer = _DummyTokenizer()
    dummy_model = _DummyModel()

    monkeypatch.setattr(
        transformers.BertTokenizer,
        "from_pretrained",
        lambda *args, **kwargs: dummy_tokenizer,
    )
    monkeypatch.setattr(
        transformers.TFBertForSequenceClassification,
        "from_pretrained",
        lambda *args, **kwargs: dummy_model,
    )

    module_path = Path(__file__).resolve().parents[1] / "main.py"
    spec = importlib_util.spec_from_file_location("app.main", module_path)
    assert spec and spec.loader, "Could not build spec for app.main"
    app_main = importlib_util.module_from_spec(spec)
    spec.loader.exec_module(app_main)
    app_main.FEEDBACK_FILE = tmp_path / "feedback.csv"
    return app_main


def test_hash_text_is_deterministic(app_module):
    first = app_module.hash_text("hello world")
    second = app_module.hash_text("hello world")
    different = app_module.hash_text("other")

    assert first == second
    assert first != different


def test_classify_tweet_returns_positive_label(app_module):
    label, confidence = app_module.classify_tweet(
        "Great service!",
        app_module.tokenizer,
        app_module.model,
    )

    assert label == "Positive"
    assert 0 <= confidence <= 1


def test_predict_endpoint_uses_mocked_model(app_module):
    with TestClient(app_module.app) as client:
        response = client.post("/predict", json={"text": "Great company!"})

    assert response.status_code == 200
    body = response.json()
    assert body["label"] == "Positive"
    assert 0 <= body["confidence"] <= 1


def test_feedback_endpoint_persists_rows(app_module):
    app_module.FEEDBACK_FILE.write_text("text,predicted_label,confidence,correct\n")

    payload = {
        "text": "Great company!",
        "label": "Positive",
        "confidence": 0.95,
        "correct": True,
    }
    with TestClient(app_module.app) as client:
        response = client.post("/feedback", json=payload)

    assert response.status_code == 200

    with app_module.FEEDBACK_FILE.open() as handle:
        reader = list(csv.DictReader(handle))

    assert len(reader) == 1
    assert reader[0]["text"] == payload["text"]
    assert reader[0]["predicted_label"] == payload["label"]
