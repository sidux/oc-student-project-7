# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     notebook_metadata_filter: all
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.12.12
# ---

# %%
import re
import shutil
import warnings

# For data
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# For NLP
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from snowballstemmer import stemmer

# For ML
from sklearn.model_selection import train_test_split, StratifiedShuffleSplit
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# For LSTM
import tensorflow as tf
from tf_keras.models import Sequential
from tf_keras.layers import Embedding, Bidirectional, LSTM, Dropout, Dense
from tf_keras.optimizers.legacy import Adam
from tf_keras.preprocessing.text import Tokenizer
from tf_keras.preprocessing.sequence import pad_sequences
from tf_keras.callbacks import EarlyStopping, Callback


# For BERT
from transformers import BertTokenizer, TFBertForSequenceClassification
from transformers import create_optimizer

# For MLflow
import mlflow
import mlflow.sklearn
import mlflow.tensorflow

# For Word2Vec & GloVe
import gensim.downloader as api

# For USE (Universal Sentence Encoder)
import tensorflow_hub as hub

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")
np.random.seed(42)
tf.random.set_seed(42)

# Download required NLTK data
nltk.download('stopwords')
nltk.download('wordnet')

# Store MLflow runs inside the project result directory.
RESULT_DIR = Path("result")
PLOTS_DIR = RESULT_DIR / "plots"
REPORTS_DIR = RESULT_DIR / "reports"
MLFLOW_TRACKING_DIR = RESULT_DIR / "mlruns"
MODEL_EXPORT_DIR = RESULT_DIR / "my_bert_model"
APP_MODEL_DIR = Path("app") / "model" / "my_bert_model"

for directory in (RESULT_DIR, PLOTS_DIR, REPORTS_DIR, MLFLOW_TRACKING_DIR):
    directory.mkdir(parents=True, exist_ok=True)

APP_MODEL_DIR.parent.mkdir(parents=True, exist_ok=True)

mlflow.set_tracking_uri("http://127.0.0.1:5000")


# %%
# Part 2: Data Exploration

path = "data/training.1600000.processed.noemoticon.csv"

# 2. Load into DataFrame
columns = ['target', 'id', 'date', 'flag', 'user', 'text']
data = pd.read_csv(path, names=columns, encoding='ISO-8859-1')
print("Data loaded. Shape:", data.shape)

data.head()

# %%
# 3. Quick Info
data.info()

# %%
# 4. Basic Stats
data.describe(include='all')

# %%
# 5. Duplicates
print("Number of duplicates by `id`  :", data.duplicated("id").sum())
print("Number of duplicates by `text`:", data.duplicated("text").sum())

# %% [markdown]
# **Observations**:
# - We have **1.6 million** tweets in total.
# - There are some duplicate `text` entries, which is not uncommon for Twitter data.
# - We'll primarily focus on the **target** and **text** columns for sentiment modeling.

# %% [markdown]
# ### **2.1 Class Distribution**
# Let’s see how many tweets belong to each sentiment category:
# - **0** = Negative
# - **2** = Neutral
# - **4** = Positive

# %%
# 6. Distribution of targets
plt.figure(figsize=(6,4))
sns.countplot(data=data, x='target', order=[0,2,4], palette='viridis')
plt.title("Distribution of Sentiment Labels")
plt.xlabel("Sentiment (0=Neg, 2=Neutral, 4=Pos)")
plt.ylabel("Count")
plt.show()

# %% [markdown]
# **Observation**:
# - The dataset is roughly balanced between `negative (0)` and `positive (4)`.
# - There are no `neutral (2)` tweets.

# %%
from functools import partial

# Part 3: Text Cleaning (Lemma & Stem)
stop_words = set(stopwords.words('english'))
wordnet_lemmatizer = WordNetLemmatizer()
snowball_stemmer = stemmer("english")

def clean_text(text: str, mode: str):
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text) # remove URLs
    text = re.sub(r'@\w+', '', text)                  # remove @mentions
    text = re.sub(r'[^a-z0-9\s]', '', text)           # remove non-alphanumeric
    tokens = text.split() # Tokenize (split on whitespace)
    tokens = [t for t in tokens if t not in stop_words]
    
    if mode == "lemma":
        tokens = [wordnet_lemmatizer.lemmatize(t) for t in tokens]
    elif mode == "stem":
       tokens = snowball_stemmer.stemWords(tokens)
    
    return " ".join(tokens)


SAMPLE_SIZE = 50_000
stratified_sampler = StratifiedShuffleSplit(
    n_splits=1,
    train_size=SAMPLE_SIZE,
    random_state=42,
)
sample_indices, _ = next(stratified_sampler.split(data, data["target"]))
data_sampled = data.iloc[sample_indices].reset_index(drop=True)

# Create columns for lemma vs stem
data_sampled["cleaned_text_lemma"] = data_sampled["text"].apply(partial(clean_text, mode="lemma"))
data_sampled["cleaned_text_stem"] = data_sampled["text"].apply(partial(clean_text, mode="stem"))

print(f"Completed cleaning (both lemma & stem) on {len(data_sampled):,} stratified sample. New columns added.")
data_sampled.head()

# %%
data_sampled.shape

# %%
# Check distribution in the sampled dataset
target_counts_sampled = data_sampled['target'].value_counts()
target_counts_sampled

# %% [markdown]
# ### **3.1 Quick EDA on Cleaned Text**
# Let’s look at the length (number of words) of tweets after cleaning:

# %%
# Part 4: Train/Val/Test Split

# We'll do an 80/10/10 split, stratified on the target.
train_data, temp_data = train_test_split(
    data_sampled,
    test_size=0.2,
    stratify=data_sampled['target'],
    random_state=42
)
val_data, test_data = train_test_split(
    temp_data,
    test_size=0.5,
    stratify=temp_data['target'],
    random_state=42
)

print("Train:", train_data.shape)
print("Val:  ", val_data.shape)
print("Test: ", test_data.shape)

# Extract X/y for lemma
X_train_lemma = train_data["cleaned_text_lemma"].values
X_val_lemma   = val_data["cleaned_text_lemma"].values
X_test_lemma  = test_data["cleaned_text_lemma"].values

# Extract X/y for stem
X_train_stem = train_data["cleaned_text_stem"].values
X_val_stem   = val_data["cleaned_text_stem"].values
X_test_stem  = test_data["cleaned_text_stem"].values

# The raw labels are 0,2,4. We'll keep them as y_train, etc. for baseline logistic
y_train = train_data["target"].values
y_val   = val_data["target"].values
y_test  = test_data["target"].values


# %%
# Part 5: Modeling Helpers & MLflow Callback

# Map (0 -> 0, 2 -> 1, 4 -> 2) for 3-class classification
def map_target(t):
    if t == 0:
        return 0
    elif t == 2:
        return 1
    else:
        return 2

y_train_mapped = np.array([map_target(i) for i in y_train])
y_val_mapped   = np.array([map_target(i) for i in y_val])
y_test_mapped  = np.array([map_target(i) for i in y_test])

class LogToMLflow(Callback):
    """
    Keras Callback that logs train/val metrics to MLflow after every epoch.
    """
    def on_epoch_end(self, epoch, logs=None):
        mlflow.log_metric("train_loss", logs.get("loss"), step=epoch)
        mlflow.log_metric("val_loss", logs.get("val_loss"), step=epoch)
        mlflow.log_metric("train_accuracy", logs.get("accuracy"), step=epoch)
        mlflow.log_metric("val_accuracy", logs.get("val_accuracy"), step=epoch)

print("Helper functions and MLflow callback set up.")


# %%
# Part 6: Logistic Regression with TF-IDF (Lemma vs Stem)
def run_logistic_regression(X_train, y_train, X_val, y_val, X_test, y_test, preprocessing_label="lemma"):
    """
    Train & evaluate Logistic Regression with TF-IDF features.
    Logs metrics/artifacts to MLflow.
    """
    max_features = 10000
    ngram_range = (1,2)
    C_value = 1.0
    max_iter = 200

    with mlflow.start_run(run_name=f"LogReg_{preprocessing_label}_Experiment"):
        # Log hyperparams
        mlflow.log_param("model_type", "LogisticRegression")
        mlflow.log_param("preprocessing", preprocessing_label)
        mlflow.log_param("tfidf_max_features", max_features)
        mlflow.log_param("tfidf_ngram_range", ngram_range)
        mlflow.log_param("C_value", C_value)
        mlflow.log_param("max_iter", max_iter)

        # TF-IDF
        tfidf = TfidfVectorizer(max_features=max_features, ngram_range=ngram_range)
        tfidf.fit(X_train)

        X_train_tfidf = tfidf.transform(X_train)
        X_val_tfidf   = tfidf.transform(X_val)
        X_test_tfidf  = tfidf.transform(X_test)

        # Train LR
        log_reg = LogisticRegression(C=C_value, max_iter=max_iter)
        log_reg.fit(X_train_tfidf, y_train)

        # Validation & test metrics
        val_preds  = log_reg.predict(X_val_tfidf)
        test_preds = log_reg.predict(X_test_tfidf)

        val_acc  = accuracy_score(y_val, val_preds)
        test_acc = accuracy_score(y_test, test_preds)

        mlflow.log_metric("val_accuracy", val_acc)
        mlflow.log_metric("test_accuracy", test_acc)

        # Confusion matrix on test
        cm = confusion_matrix(y_test, test_preds, labels=[0,2,4])
        plt.figure(figsize=(5,4))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title(f"LogReg ({preprocessing_label}) - Confusion Matrix (Test)")
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.tight_layout()
        fig_name = f"logreg_cm_{preprocessing_label}.png"
        fig_path = PLOTS_DIR / fig_name
        plt.savefig(fig_path)
        plt.close()
        mlflow.log_artifact(str(fig_path), artifact_path="plots")

        # Classification report
        cls_report = classification_report(y_test, test_preds, digits=4)
        report_path = REPORTS_DIR / f"logreg_cr_{preprocessing_label}.txt"
        with open(report_path, "w") as f:
            f.write(cls_report)
        mlflow.log_artifact(str(report_path), artifact_path="reports")

        # Log model
        mlflow.sklearn.log_model(log_reg, artifact_path=f"logreg_model_{preprocessing_label}")

        print(f"[LogReg ({preprocessing_label})] Val Acc: {val_acc:.4f}, Test Acc: {test_acc:.4f}")
        print(cls_report)

# Run for lemma
run_logistic_regression(
    X_train_lemma, y_train, X_val_lemma, y_val, X_test_lemma, y_test,
    preprocessing_label="lemma"
)

# Run for stem
run_logistic_regression(
    X_train_stem, y_train, X_val_stem, y_val, X_test_stem, y_test,
    preprocessing_label="stem"
)

# %%
# Part 7: LSTM (Lemma vs Stem) with Random Embeddings

def prepare_sequences(texts_train, texts_val, texts_test, vocab_size=10000, max_length=30):
    """
    Tokenize the text data and create padded sequences.
    Returns: (tokenizer, X_train_pad, X_val_pad, X_test_pad)
    """
    tokenizer = Tokenizer(num_words=vocab_size, oov_token='<OOV>')
    tokenizer.fit_on_texts(texts_train)

    seq_train = tokenizer.texts_to_sequences(texts_train)
    seq_val   = tokenizer.texts_to_sequences(texts_val)
    seq_test  = tokenizer.texts_to_sequences(texts_test)

    X_train_pad = pad_sequences(seq_train, maxlen=max_length, padding='post', truncating='post')
    X_val_pad   = pad_sequences(seq_val,   maxlen=max_length, padding='post', truncating='post')
    X_test_pad  = pad_sequences(seq_test,  maxlen=max_length, padding='post', truncating='post')

    return tokenizer, X_train_pad, X_val_pad, X_test_pad

def build_lstm_model(
        vocab_size=10000,
        embedding_dim=128,
        max_length=30,
        lstm_units=64,
        dropout_rate=0.3,
        learning_rate=1e-3,
        pretrained_embedding_matrix=None,
        trainable_emb=True
):
    """
    Build a sequential LSTM model.
    If pretrained_embedding_matrix is provided, use that as weights.
    """
    model = Sequential()
    if pretrained_embedding_matrix is not None:
        emb_layer = Embedding(
            input_dim=pretrained_embedding_matrix.shape[0],
            output_dim=pretrained_embedding_matrix.shape[1],
            weights=[pretrained_embedding_matrix],
            input_length=max_length,
            trainable=trainable_emb
        )
        model.add(emb_layer)
    else:
        # random embeddings
        model.add(Embedding(
            input_dim=vocab_size,
            output_dim=embedding_dim,
            input_length=max_length
        ))

    model.add(Bidirectional(LSTM(lstm_units, return_sequences=False)))
    model.add(Dropout(dropout_rate))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(dropout_rate))
    model.add(Dense(3, activation='softmax'))  # 3 classes

    model.compile(
        loss='sparse_categorical_crossentropy',
        optimizer=Adam(learning_rate=learning_rate),
        metrics=['accuracy']
    )
    return model

def run_lstm_experiment(
        texts_train, texts_val, texts_test,
        y_train_mapped, y_val_mapped, y_test_mapped,
        preprocessing_label="lemma_random"
):
    """
    Build, train, evaluate LSTM with random embeddings on provided text data.
    """
    # Hyperparams
    vocab_size     = 10000
    max_length     = 30
    embedding_dim  = 128
    lstm_units     = 64
    dropout_rate   = 0.3
    learning_rate  = 1e-3
    epochs         = 10
    batch_size     = 256
    patience       = 3

    with mlflow.start_run(run_name=f"LSTM_{preprocessing_label}_Experiment"):
        mlflow.log_param("preprocessing", preprocessing_label)
        mlflow.log_param("vocab_size", vocab_size)
        mlflow.log_param("max_length", max_length)
        mlflow.log_param("embedding_dim", embedding_dim)
        mlflow.log_param("lstm_units", lstm_units)
        mlflow.log_param("dropout_rate", dropout_rate)
        mlflow.log_param("learning_rate", learning_rate)
        mlflow.log_param("epochs", epochs)
        mlflow.log_param("batch_size", batch_size)

        # Prepare sequences
        tokenizer, X_train_pad, X_val_pad, X_test_pad = prepare_sequences(
            texts_train, texts_val, texts_test,
            vocab_size=vocab_size, max_length=max_length
        )

        model = build_lstm_model(
            vocab_size=vocab_size,
            embedding_dim=embedding_dim,
            max_length=max_length,
            lstm_units=lstm_units,
            dropout_rate=dropout_rate,
            learning_rate=learning_rate,
            pretrained_embedding_matrix=None,  # random
            trainable_emb=True
        )

        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=patience,
            restore_best_weights=True,
            verbose=1
        )

        history = model.fit(
            X_train_pad, y_train_mapped,
            validation_data=(X_val_pad, y_val_mapped),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[LogToMLflow(), early_stop]
        )

        # Evaluate
        preds = model.predict(X_test_pad)
        pred_labels = np.argmax(preds, axis=1)
        test_acc = accuracy_score(y_test_mapped, pred_labels)
        mlflow.log_metric("test_accuracy", test_acc)

        # Confusion Matrix
        cm = confusion_matrix(y_test_mapped, pred_labels, labels=[0,1,2])
        plt.figure(figsize=(5,4))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=["0","1","2"], yticklabels=["0","1","2"])
        plt.title(f"LSTM ({preprocessing_label}) - CM (Test)")
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.tight_layout()
        fig_name = f"lstm_cm_{preprocessing_label}.png"
        fig_path = PLOTS_DIR / fig_name
        plt.savefig(fig_path)
        plt.close()
        mlflow.log_artifact(str(fig_path), artifact_path="plots")

        # Classification report
        cls_report = classification_report(y_test_mapped, pred_labels, digits=4)
        report_path = REPORTS_DIR / f"lstm_cr_{preprocessing_label}.txt"
        with open(report_path, "w") as f:
            f.write(cls_report)
        mlflow.log_artifact(str(report_path), artifact_path="reports")

        # Log model
        mlflow.tensorflow.log_model(model, artifact_path=f"lstm_model_{preprocessing_label}")

        print(f"[LSTM {preprocessing_label}] Test Acc: {test_acc:.4f}")
        print(cls_report)

# Run LSTM with random embeddings for lemma
run_lstm_experiment(X_train_lemma, X_val_lemma, X_test_lemma,
                    y_train_mapped, y_val_mapped, y_test_mapped,
                    preprocessing_label="lemma_random")

# Run LSTM with random embeddings for stem
run_lstm_experiment(X_train_stem, X_val_stem, X_test_stem,
                    y_train_mapped, y_val_mapped, y_test_mapped,
                    preprocessing_label="stem_random")


# %%
# Part 8: LSTM + Word2Vec / GloVe for both Lemma & Stem

# 1. Download pretrained models from gensim.downloader
print("Downloading Word2Vec (GoogleNews-300)... This may be ~1.5GB in RAM!")
w2v_model = api.load("word2vec-google-news-300")

print("Downloading GloVe (wiki-gigaword-100)...")
glove_model = api.load("glove-wiki-gigaword-100")

def build_embedding_matrix_from_gensim(gensim_model, word_index, vocab_size, embed_dim):
    """
    Create an embedding matrix for the top 'vocab_size' words in 'word_index',
    using vectors from a Gensim KeyedVectors model.
    Missing words stay as zero vectors.
    """
    embedding_matrix = np.zeros((vocab_size, embed_dim), dtype=np.float32)
    for word, i in word_index.items():
        if i < vocab_size:
            if word in gensim_model.key_to_index:
                embedding_matrix[i] = gensim_model[word]
    return embedding_matrix

def run_lstm_pretrained(
        texts_train, texts_val, texts_test,
        y_train_mapped, y_val_mapped, y_test_mapped,
        gensim_model, embed_dim, experiment_name="w2v_lemma",
        freeze_emb=False
):
    """
    Build, train, evaluate LSTM with a Gensim KeyedVectors pretrained embedding.
    experiment_name helps name the MLflow run.
    freeze_emb=False => fine-tune embeddings
    """
    vocab_size = 10000
    max_length = 30
    lstm_units = 64
    dropout_rate = 0.3
    learning_rate = 1e-3
    epochs = 10
    batch_size = 256
    patience = 3

    with mlflow.start_run(run_name=f"LSTM_{experiment_name}_Experiment"):
        mlflow.log_param("embedding_source", experiment_name)
        mlflow.log_param("embedding_dim", embed_dim)
        mlflow.log_param("freeze_emb", freeze_emb)

        # Prepare sequences
        tokenizer, X_train_pad, X_val_pad, X_test_pad = prepare_sequences(
            texts_train, texts_val, texts_test, vocab_size=vocab_size, max_length=max_length
        )
        # Build embedding matrix
        word_index = tokenizer.word_index
        embedding_matrix = build_embedding_matrix_from_gensim(
            gensim_model, word_index, vocab_size, embed_dim
        )

        # Build LSTM with this matrix
        model = build_lstm_model(
            vocab_size=vocab_size,
            embedding_dim=embed_dim,
            max_length=max_length,
            lstm_units=lstm_units,
            dropout_rate=dropout_rate,
            learning_rate=learning_rate,
            pretrained_embedding_matrix=embedding_matrix,
            trainable_emb=not freeze_emb
        )

        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=patience,
            restore_best_weights=True,
            verbose=1
        )

        history = model.fit(
            X_train_pad, y_train_mapped,
            validation_data=(X_val_pad, y_val_mapped),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[LogToMLflow(), early_stop]
        )

        # Evaluate
        preds = model.predict(X_test_pad)
        pred_labels = np.argmax(preds, axis=1)
        test_acc = accuracy_score(y_test_mapped, pred_labels)
        mlflow.log_metric("test_accuracy", test_acc)

        # Confusion Matrix
        cm = confusion_matrix(y_test_mapped, pred_labels, labels=[0,1,2])
        plt.figure(figsize=(5,4))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=["0","1","2"], yticklabels=["0","1","2"])
        plt.title(f"LSTM ({experiment_name}) - CM (Test)")
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.tight_layout()
        fig_name = f"lstm_cm_{experiment_name}.png"
        fig_path = PLOTS_DIR / fig_name
        plt.savefig(fig_path)
        plt.close()
        mlflow.log_artifact(str(fig_path), artifact_path="plots")

        # Classification report
        cls_report = classification_report(y_test_mapped, pred_labels, digits=4)
        report_path = REPORTS_DIR / f"lstm_cr_{experiment_name}.txt"
        with open(report_path, "w") as f:
            f.write(cls_report)
        mlflow.log_artifact(str(report_path), artifact_path="reports")

        # Log model
        mlflow.tensorflow.log_model(model, artifact_path=f"lstm_model_{experiment_name}")

        print(f"[LSTM {experiment_name}] Test Acc: {test_acc:.4f}")
        print(cls_report)

# Run Word2Vec + Lemma
run_lstm_pretrained(
    X_train_lemma, X_val_lemma, X_test_lemma,
    y_train_mapped, y_val_mapped, y_test_mapped,
    w2v_model, embed_dim=300, experiment_name="w2v_lemma"
)

# Run Word2Vec + Stem
run_lstm_pretrained(
    X_train_stem, X_val_stem, X_test_stem,
    y_train_mapped, y_val_mapped, y_test_mapped,
    w2v_model, embed_dim=300, experiment_name="w2v_stem"
)

# Run GloVe + Lemma
run_lstm_pretrained(
    X_train_lemma, X_val_lemma, X_test_lemma,
    y_train_mapped, y_val_mapped, y_test_mapped,
    glove_model, embed_dim=100, experiment_name="glove_lemma"
)

# Run GloVe + Stem
run_lstm_pretrained(
    X_train_stem, X_val_stem, X_test_stem,
    y_train_mapped, y_val_mapped, y_test_mapped,
    glove_model, embed_dim=100, experiment_name="glove_stem"
)

# %%
# Part 9: BERT (Lemma vs Stem)
# We'll sample smaller subsets because BERT is expensive.

def bert_encode(texts, tokenizer, max_len=30):
    input_ids = []
    attention_masks = []
    for txt in texts:
        encoded = tokenizer.encode_plus(
            txt,
            add_special_tokens=True,
            max_length=max_len,
            truncation=True,
            padding='max_length',
            return_attention_mask=True,
            return_tensors='tf'
        )
        input_ids.append(encoded['input_ids'])
        attention_masks.append(encoded['attention_mask'])
    return (tf.concat(input_ids, axis=0), tf.concat(attention_masks, axis=0))


def run_bert_experiment(
        texts_train, texts_val, texts_test,
        y_train_mapped, y_val_mapped, y_test_mapped,
        preprocessing_label="lemma",
        export_for_app=False,
):
    MODEL_NAME = "bert-base-uncased"
    EPOCHS = 15
    BATCH_SIZE = 16
    MAX_LEN = 30
    patience = 5

    # We'll pick smaller sample sizes
    train_sample_size = 3000
    val_sample_size = 1000
    test_sample_size = 1000

    with mlflow.start_run(run_name=f"BERT_{preprocessing_label}_Experiment"):
        mlflow.log_param("model_name", MODEL_NAME)
        mlflow.log_param("preprocessing", preprocessing_label)
        mlflow.log_param("train_sample_size", train_sample_size)
        mlflow.log_param("val_sample_size", val_sample_size)
        mlflow.log_param("test_sample_size", test_sample_size)
        mlflow.log_param("max_seq_length", MAX_LEN)
        mlflow.log_param("epochs", EPOCHS)
        mlflow.log_param("batch_size", BATCH_SIZE)

        bert_tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)

        train_ids, train_masks = bert_encode(texts_train[:train_sample_size], bert_tokenizer, max_len=MAX_LEN)
        val_ids, val_masks     = bert_encode(texts_val[:val_sample_size],   bert_tokenizer, max_len=MAX_LEN)
        test_ids, test_masks   = bert_encode(texts_test[:test_sample_size], bert_tokenizer, max_len=MAX_LEN)

        y_train_sample = y_train_mapped[:train_sample_size]
        y_val_sample   = y_val_mapped[:val_sample_size]
        y_test_sample  = y_test_mapped[:test_sample_size]

        bert_model = TFBertForSequenceClassification.from_pretrained(
            MODEL_NAME, 
            num_labels=3,
            use_safetensors=False,
        )

        num_train_steps = (train_sample_size // BATCH_SIZE) * EPOCHS
        num_warmup_steps = int(0.1 * num_train_steps)

        optimizer, schedule = create_optimizer(
            init_lr=2e-5,
            num_warmup_steps=num_warmup_steps,
            num_train_steps=num_train_steps,
            weight_decay_rate=0.01
        )

        bert_model.compile(
            optimizer=optimizer,
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            metrics=['accuracy']
        )

        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=patience,
            restore_best_weights=True,
            verbose=1
        )

        history = bert_model.fit(
            [train_ids, train_masks],
            y_train_sample,
            validation_data=([val_ids, val_masks], y_val_sample),
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            callbacks=[early_stop]
        )

        # Evaluate
        preds = bert_model.predict([test_ids, test_masks]).logits
        pred_labels = np.argmax(preds, axis=1)
        test_acc = accuracy_score(y_test_sample, pred_labels)
        mlflow.log_metric("test_accuracy", test_acc)

        cm = confusion_matrix(y_test_sample, pred_labels, labels=[0,1,2])
        plt.figure(figsize=(5,4))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=["0","1","2"], yticklabels=["0","1","2"])
        plt.title(f"BERT ({preprocessing_label}) - CM (Test)")
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.tight_layout()
        fig_name = f"bert_cm_{preprocessing_label}.png"
        fig_path = PLOTS_DIR / fig_name
        plt.savefig(fig_path)
        plt.close()
        mlflow.log_artifact(str(fig_path), artifact_path="plots")

        cls_report = classification_report(y_test_sample, pred_labels, digits=4)
        report_path = REPORTS_DIR / f"bert_cr_{preprocessing_label}.txt"
        with open(report_path, "w") as f:
            f.write(cls_report)
        mlflow.log_artifact(str(report_path), artifact_path="reports")

        mlflow.tensorflow.log_model(bert_model, artifact_path=f"bert_model_{preprocessing_label}")

        if export_for_app:
            export_model_artifacts(bert_model, bert_tokenizer)

        print(f"[BERT {preprocessing_label}] Test Acc: {test_acc:.4f}")
        print(cls_report)

# Run BERT lemma
run_bert_experiment(X_train_lemma, X_val_lemma, X_test_lemma,
                    y_train_mapped, y_val_mapped, y_test_mapped,
                    preprocessing_label="lemma",
                    export_for_app=True)

# Run BERT stem
run_bert_experiment(X_train_stem, X_val_stem, X_test_stem,
                    y_train_mapped, y_val_mapped, y_test_mapped,
                    preprocessing_label="stem")

# %%
# Part 10: Universal Sentence Encoder (USE)
# USE provides sentence-level embeddings directly from TensorFlow Hub

print("Loading Universal Sentence Encoder from TensorFlow Hub...")
use_model = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
print("USE model loaded successfully.")


def get_use_embeddings(texts, use_model):
    """
    Generate USE embeddings for a list of texts.
    Returns a numpy array of shape (len(texts), 512).
    """
    embeddings = use_model(texts)
    return embeddings.numpy()


def run_use_experiment(
        texts_train, texts_val, texts_test,
        y_train_mapped, y_val_mapped, y_test_mapped,
        preprocessing_label="lemma"
):
    """
    Train a Dense classifier on top of USE embeddings.
    """
    train_sample_size = 10000
    val_sample_size = 2000
    test_sample_size = 2000
    
    EPOCHS = 15
    BATCH_SIZE = 64
    patience = 3

    with mlflow.start_run(run_name=f"USE_{preprocessing_label}_Experiment"):
        mlflow.log_param("model_type", "USE_Dense")
        mlflow.log_param("preprocessing", preprocessing_label)
        mlflow.log_param("train_sample_size", train_sample_size)
        mlflow.log_param("val_sample_size", val_sample_size)
        mlflow.log_param("test_sample_size", test_sample_size)
        mlflow.log_param("embedding_dim", 512)
        mlflow.log_param("epochs", EPOCHS)
        mlflow.log_param("batch_size", BATCH_SIZE)

        # Sample the data
        train_texts = list(texts_train[:train_sample_size])
        val_texts = list(texts_val[:val_sample_size])
        test_texts = list(texts_test[:test_sample_size])

        y_train_sample = y_train_mapped[:train_sample_size]
        y_val_sample = y_val_mapped[:val_sample_size]
        y_test_sample = y_test_mapped[:test_sample_size]

        # Generate USE embeddings
        print(f"Generating USE embeddings for {len(train_texts)} train samples...")
        X_train_use = get_use_embeddings(train_texts, use_model)
        print(f"Generating USE embeddings for {len(val_texts)} val samples...")
        X_val_use = get_use_embeddings(val_texts, use_model)
        print(f"Generating USE embeddings for {len(test_texts)} test samples...")
        X_test_use = get_use_embeddings(test_texts, use_model)

        # Build a simple Dense classifier on top of USE embeddings
        use_classifier = Sequential([
            Dense(256, activation='relu', input_shape=(512,)),
            Dropout(0.3),
            Dense(128, activation='relu'),
            Dropout(0.3),
            Dense(3, activation='softmax')
        ])

        use_classifier.compile(
            loss='sparse_categorical_crossentropy',
            optimizer=Adam(learning_rate=1e-3),
            metrics=['accuracy']
        )

        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=patience,
            restore_best_weights=True,
            verbose=1
        )

        history = use_classifier.fit(
            X_train_use, y_train_sample,
            validation_data=(X_val_use, y_val_sample),
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            callbacks=[LogToMLflow(), early_stop]
        )

        # Evaluate
        preds = use_classifier.predict(X_test_use)
        pred_labels = np.argmax(preds, axis=1)
        test_acc = accuracy_score(y_test_sample, pred_labels)
        mlflow.log_metric("test_accuracy", test_acc)

        # Confusion Matrix
        cm = confusion_matrix(y_test_sample, pred_labels, labels=[0, 1, 2])
        plt.figure(figsize=(5, 4))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=["0", "1", "2"], yticklabels=["0", "1", "2"])
        plt.title(f"USE ({preprocessing_label}) - CM (Test)")
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.tight_layout()
        fig_name = f"use_cm_{preprocessing_label}.png"
        fig_path = PLOTS_DIR / fig_name
        plt.savefig(fig_path)
        plt.close()
        mlflow.log_artifact(str(fig_path), artifact_path="plots")

        # Classification report
        cls_report = classification_report(y_test_sample, pred_labels, digits=4)
        report_path = REPORTS_DIR / f"use_cr_{preprocessing_label}.txt"
        with open(report_path, "w") as f:
            f.write(cls_report)
        mlflow.log_artifact(str(report_path), artifact_path="reports")

        # Log model
        mlflow.tensorflow.log_model(use_classifier, artifact_path=f"use_model_{preprocessing_label}")

        print(f"[USE {preprocessing_label}] Test Acc: {test_acc:.4f}")
        print(cls_report)


# Run USE with lemma preprocessing
run_use_experiment(
    X_train_lemma, X_val_lemma, X_test_lemma,
    y_train_mapped, y_val_mapped, y_test_mapped,
    preprocessing_label="lemma"
)

# Run USE with stem preprocessing
run_use_experiment(
    X_train_stem, X_val_stem, X_test_stem,
    y_train_mapped, y_val_mapped, y_test_mapped,
    preprocessing_label="stem"
)

# %%
# Part 11: Conclusion & Next Steps

"""
We have now compared:
1. Logistic Regression (TF-IDF) with Lemma vs Stem
2. LSTM with:
   - Random Embeddings (Lemma vs Stem)
   - Word2Vec (Lemma vs Stem)
   - GloVe (Lemma vs Stem)
3. BERT (Lemma vs Stem)
4. USE (Universal Sentence Encoder) with Lemma vs Stem

All results are logged in MLflow. 
"""
def export_model_artifacts(model, tokenizer):
    """
    Persist the fine-tuned BERT model for both offline analysis and the FastAPI app.
    """
    MODEL_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(MODEL_EXPORT_DIR)
    tokenizer.save_pretrained(MODEL_EXPORT_DIR)

    if APP_MODEL_DIR.exists():
        shutil.rmtree(APP_MODEL_DIR)
    shutil.copytree(MODEL_EXPORT_DIR, APP_MODEL_DIR)
    print(f"Saved fine-tuned model to {MODEL_EXPORT_DIR} and {APP_MODEL_DIR}")
