---
marp: true
theme: default
paginate: true
backgroundColor: #fafbfc
style: |
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  
  section {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: 18px;
    padding: 40px 50px;
    background: linear-gradient(135deg, #fafbfc 0%, #f0f4f8 100%);
  }
  
  section::after {
    content: attr(data-marpit-pagination) ' / ' attr(data-marpit-pagination-total);
    font-size: 12px;
    color: #64748b;
  }
  
  h1 {
    color: #1e3a5f;
    font-size: 2.2em;
    font-weight: 700;
    text-align: center;
    margin-bottom: 10px;
    letter-spacing: -0.5px;
  }
  
  h2 {
    color: #1e3a5f;
    font-size: 1.5em;
    font-weight: 600;
    border-bottom: 3px solid #3b82f6;
    padding-bottom: 8px;
    margin-bottom: 20px;
  }
  
  h3 {
    color: #334155;
    font-size: 1.1em;
    font-weight: 600;
    margin-top: 15px;
  }
  
  .title-slide {
    background: linear-gradient(135deg, #1e3a5f 0%, #3b82f6 100%);
    color: white;
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  
  .title-slide h1 {
    color: white;
    font-size: 2.8em;
    margin-bottom: 20px;
  }
  
  .title-slide h3 {
    color: #e2e8f0;
    font-weight: 400;
  }
  
  .agenda {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  }
  
  .highlight-box {
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
    border-left: 5px solid #3b82f6;
    padding: 18px 22px;
    border-radius: 0 10px 10px 0;
    margin: 15px 0;
    color: #1e3a5f;
    font-size: 0.95em;
    line-height: 1.5;
  }
  
  .success-box {
    background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
    border-left: 5px solid #22c55e;
    padding: 18px 22px;
    border-radius: 0 10px 10px 0;
    margin: 15px 0;
    color: #14532d;
    font-size: 0.95em;
    line-height: 1.5;
  }
  
  .warning-box {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border-left: 5px solid #f59e0b;
    padding: 18px 22px;
    border-radius: 0 10px 10px 0;
    margin: 15px 0;
    color: #78350f;
    font-size: 0.95em;
    line-height: 1.5;
  }
  
  .metric-card {
    background: white;
    border-radius: 14px;
    padding: 20px 15px;
    box-shadow: 0 4px 12px -2px rgba(0,0,0,0.12);
    text-align: center;
    margin: 10px;
    border: 1px solid #e2e8f0;
  }
  
  .metric-value {
    font-size: 2.2em;
    font-weight: 700;
    color: #2563eb;
    line-height: 1.2;
  }
  
  .metric-label {
    font-size: 0.85em;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
    margin-bottom: 5px;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    font-size: 15px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    border-radius: 10px;
    overflow: hidden;
  }
  
  th {
    background: linear-gradient(135deg, #1e3a5f 0%, #334155 100%);
    color: #ffffff;
    padding: 14px 12px;
    font-weight: 600;
    text-align: left;
    font-size: 0.9em;
    letter-spacing: 0.3px;
  }
  
  td {
    padding: 12px;
    border-bottom: 1px solid #e2e8f0;
    background: white;
    color: #1e293b;
    font-size: 0.9em;
  }
  
  tr:hover td {
    background: #f1f5f9;
  }
  
  tr:nth-child(even) td {
    background: #f8fafc;
  }
  
  .best {
    background: #dcfce7 !important;
    font-weight: 700;
    color: #14532d;
  }
  
  ul, ol {
    line-height: 1.7;
    margin: 12px 0;
    color: #334155;
  }
  
  li {
    margin: 10px 0;
  }
  
  li::marker {
    color: #3b82f6;
  }
  
  p {
    color: #334155;
    line-height: 1.6;
  }
  
  code {
    background: #e0e7ff;
    color: #3730a3;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.9em;
    font-family: 'SF Mono', 'Consolas', 'Monaco', monospace;
    font-weight: 600;
  }
  
  pre {
    background: #f8fafc;
    border-radius: 12px;
    padding: 18px 20px;
    margin: 12px 0;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
    border: 1px solid #e2e8f0;
    overflow-x: auto;
  }
  
  pre code {
    background: transparent;
    color: #1e293b;
    padding: 0;
    font-size: 0.82em;
    line-height: 1.5;
    display: block;
    font-weight: 500;
  }
  
  img {
    max-width: 100%;
    border-radius: 8px;
    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15);
  }
  
  .two-cols {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
    align-items: start;
  }
  
  .three-cols {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 20px;
  }
  
  .tag {
    display: inline-block;
    background: #3b82f6;
    color: white;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.8em;
    font-weight: 600;
    margin: 3px;
    letter-spacing: 0.3px;
  }
  
  .tag-green { background: #16a34a; }
  .tag-orange { background: #ea580c; }
  .tag-purple { background: #7c3aed; }
  
  .footer-note {
    position: absolute;
    bottom: 20px;
    left: 50px;
    right: 50px;
    font-size: 0.8em;
    color: #64748b;
    border-top: 1px solid #cbd5e1;
    padding-top: 10px;
  }
  
  strong {
    color: #1e3a5f;
    font-weight: 600;
  }
  
  em {
    color: #475569;
  }

---

<!-- _class: title-slide -->

# Détection de Bad Buzz pour Air Paradis

### Projet NLP & MLOps - Analyse de Sentiments Twitter

<br>

**Classification de tweets en temps réel avec Deep Learning**
Pipeline complet : Entraînement → Déploiement → Monitoring

---

## Sommaire de la Présentation

<div class="three-cols">

<div>

### 1. Contexte & Données
- Problématique métier
- Dataset Sentiment140
- Stratégie d'évaluation

</div>

<div>

### 2. Modélisation
- Prétraitements NLP
- Modèles testés (4 familles)
- Embeddings & Transfer Learning
- Comparaison des performances

</div>

<div>

### 3. Industrialisation
- Pipeline MLflow
- API FastAPI & Tests
- CI/CD & Déploiement Azure
- Monitoring & Alertes

</div>

</div>

<div class="highlight-box">

**Objectif** : Identifier en temps réel les tweets négatifs pour permettre au community management d'Air Paradis d'anticiper les crises et bad buzz potentiels.

</div>

---

## 1. Contexte & Problématique Métier

### Le besoin d'Air Paradis

<div class="two-cols">

<div>

**Enjeu business** : Détecter rapidement les signaux faibles de mécontentement sur les réseaux sociaux avant qu'ils ne deviennent viraux.

**Solution proposée** :
- API de prédiction temps réel
- Alertes automatiques
- Dashboard de monitoring

**Cible identifiée** :
- Classe **0** = Tweet négatif
- Classe **4** = Tweet positif

</div>

<div>

<div class="success-box">

**Métrique prioritaire : Recall Négatif**

Capturer un maximum de tweets négatifs, même au prix de quelques faux positifs. Un bad buzz manqué coûte plus cher qu'une fausse alerte.

</div>

<div class="warning-box">

**Contrainte** : Surveiller la precision pour éviter la fatigue des équipes (trop de fausses alertes).

</div>

</div>

</div>

---

## 2. Dataset & Protocole Expérimental

### Corpus Sentiment140

<div class="two-cols">

<div>

**Source** : 1,6 million de tweets annotés
- Balance naturelle : ~50% négatif / ~50% positif
- Labels : 0 (négatif), 4 (positif)

**Échantillonnage stratifié** :
- **50 000 tweets** pour l'expérimentation
- Préservation de la distribution des classes

**Split des données** :

| Ensemble | Taille | Usage |
|----------|--------|-------|
| Train | 80% (40k) | Entraînement |
| Validation | 10% (5k) | Tuning |
| Test | 10% (5k) | Évaluation finale |

</div>

<div>

<div class="highlight-box">

**Garantie : Pas de fuite de données**

- Split stratifié (`StratifiedShuffleSplit`)
- Aucun tweet présent dans plusieurs ensembles
- Preprocessing appliqué **après** le split

</div>

**Métriques d'évaluation** :
- <span class="tag">Accuracy</span>
- <span class="tag tag-green">Recall Négatif</span> ← Prioritaire
- <span class="tag">F1-Score</span>
- <span class="tag tag-purple">ROC AUC</span>
- <span class="tag tag-orange">Latence</span>

</div>

</div>

---

## 3. Prétraitements du Texte

### Deux techniques comparées : Lemmatisation vs Stemming

<div class="two-cols">

<div>

**Pipeline `clean_text`** :
1. Conversion en minuscules
2. Suppression des URLs
3. Suppression des @mentions
4. Suppression des caractères spéciaux
5. Tokenisation
6. Suppression des stop words
7. **Lemmatisation** ou **Stemming**

```python
# Lemmatisation (WordNet)
wordnet_lemmatizer.lemmatize(token)

# Stemming (Snowball)
snowball_stemmer.stemWords(tokens)
```

</div>

<div>

**Exemple de transformation** :

| Original | Lemma | Stem |
|----------|-------|------|
| "running" | "run" | "run" |
| "better" | "better" | "better" |
| "studies" | "study" | "studi" |

<div class="success-box">

**Résultat** : La **lemmatisation** préserve mieux le sens sémantique et donne de meilleurs résultats sur toutes les métriques.

</div>

</div>

</div>

---

## 4. Stratégie de Modélisation

### Du plus simple au plus complexe

<div class="highlight-box">

**Approche progressive** : Commencer par une baseline simple, puis augmenter la complexité pour justifier chaque gain de performance.

</div>

| Niveau | Modèle | Type | Complexité |
|--------|--------|------|------------|
| 1 | TF-IDF + Régression Logistique | Bag-of-Words | ⭐ Simple |
| 2 | BiLSTM + Embeddings aléatoires | Deep Learning | ⭐⭐ Intermédiaire |
| 3 | BiLSTM + Word2Vec / GloVe | Transfer Learning | ⭐⭐⭐ Avancé |
| 4 | BERT fine-tuné | Transformers | ⭐⭐⭐⭐ État de l'art |
| 5 | USE (Universal Sentence Encoder) | Sentence Embedding | ⭐⭐⭐ Avancé |

<div class="three-cols" style="margin-top: 20px;">

<div class="metric-card">
<div class="metric-label">Modèles testés</div>
<div class="metric-value">12</div>
</div>

<div class="metric-card">
<div class="metric-label">Embeddings</div>
<div class="metric-value">4</div>
</div>

<div class="metric-card">
<div class="metric-label">Prétraitements</div>
<div class="metric-value">2</div>
</div>

</div>

---

## 5. Modèle Baseline : TF-IDF + Régression Logistique

### Modèle de référence pour comparaison

<div class="two-cols">

<div>

**Configuration** :
- Vectorisation TF-IDF
  - 10 000 features max
  - N-grammes (1, 2)
- Régression Logistique
  - `C=1.0`, `max_iter=200`

**Résultats (Lemma)** :

| Métrique | Valeur |
|----------|--------|
| Accuracy | **0.774** |
| Recall Négatif | 0.757 |
| F1 Négatif | 0.770 |
| ROC AUC | **0.856** |
| Latence | **< 10 ms** |

</div>

<div>

![Confusion Matrix LogReg](result/plots/logreg_cm_lemma.png)

<div class="success-box" style="font-size: 0.9em;">

**Avantages** : Rapide, interprétable, excellent fallback

</div>

</div>

</div>

---

## 6. Modèle Avancé : BiLSTM + Embeddings

### Architecture Deep Learning avec couche LSTM

<div class="two-cols">

<div>

**Architecture du réseau** :

```
Input → Embedding(128d) → BiLSTM(64) 
→ Dropout(0.3) → Dense(64, ReLU) 
→ Dropout(0.3) → Dense(3, Softmax)
```

**Hyperparamètres** :
- Vocab size : 10 000
- Sequence length : 30
- Learning rate : 1e-3 (Adam)
- Early Stopping : patience=3

**Embeddings testés** :
- <span class="tag">Aléatoires (trainable)</span>
- <span class="tag tag-green">Word2Vec 300d</span>
- <span class="tag tag-purple">GloVe 100d</span>

</div>

<div>

![Confusion Matrix LSTM](result/plots/lstm_cm_glove_lemma.png)

<div class="highlight-box" style="font-size: 0.9em;">

**Meilleur résultat** : Embeddings aléatoires finement ajustés → Recall négatif **0.772** (+2% vs baseline)

</div>

</div>

</div>

---

## 7. Transfer Learning : Word2Vec & GloVe

### Réutilisation de modèles pré-entraînés

<div class="two-cols">

<div>

**Word2Vec (Google News 300d)**
- 3 millions de mots
- Entraîné sur Google News
- Capture les analogies sémantiques

**GloVe (Wikipedia 100d)**
- Co-occurrences globales
- Plus léger que Word2Vec
- Bon compromis taille/performance

**Intégration** :
```python
embedding_matrix = build_embedding_matrix(
    gensim_model, word_index, 
    vocab_size=10000, embed_dim=300
)
```

</div>

<div>

**Comparaison des embeddings (Lemma)** :

| Embedding | Accuracy | Recall Neg |
|-----------|----------|------------|
| Aléatoire | 0.774 | **0.772** |
| Word2Vec | **0.776** | 0.741 |
| GloVe | **0.776** | 0.747 |

<div class="warning-box" style="font-size: 0.9em;">

**Observation** : Les embeddings pré-entraînés améliorent l'accuracy mais réduisent le recall négatif (décalage de domaine News/Wiki vs Twitter).

</div>

</div>

</div>

---

## 8. Modèle BERT : État de l'Art

### Fine-tuning de Transformers

<div class="two-cols">

<div>

**Configuration BERT** :
- Modèle : `bert-base-uncased`
- Max sequence : 30 tokens
- Batch size : 16
- Epochs : 15 (early stopping)

**Préparation des données** :
```python
# Input IDs + Attention Masks
encoded = tokenizer.encode_plus(
    text,
    add_special_tokens=True,
    max_length=30,
    padding='max_length',
    return_attention_mask=True
)
```

**Optimiseur** : AdamW + Linear warmup (10%)

</div>

<div>

![Confusion Matrix BERT](result/plots/bert_cm_lemma.png)

**Résultats** : Acc 0.762, Recall+ 0.830
*Échantillon réduit : 3k/1k/1k*

</div>

</div>

---

## 9. Universal Sentence Encoder (USE)

### Sentence-level Embeddings via TensorFlow Hub

<div class="two-cols">

<div>

**Avantages de USE** :
- Embeddings de phrases entières (512d)
- Pas de tokenisation manuelle
- Capture le sens global
- Modèle pré-entraîné optimisé

**Architecture du classifieur** :
```
USE(512d) → Dense(256, ReLU) 
→ Dropout(0.3) → Dense(128, ReLU) 
→ Dropout(0.3) → Dense(3, Softmax)
```

**Configuration** :
- Samples : 10k / 2k / 2k
- Early stopping : patience=3

</div>

<div>

![Confusion Matrix USE](result/plots/use_cm_lemma.png)

<div class="success-box" style="font-size: 0.9em;">

**Résultat** : Performance comparable au BiLSTM avec une implémentation plus simple et rapide.

</div>

</div>

</div>

---

## 10. Synthèse Comparative des Modèles

### Tableau récapitulatif de tous les résultats

| Modèle | Preproc | Accuracy | Recall Neg | F1 Neg | Latence |
|--------|---------|----------|------------|--------|---------|
| Logistic Regression | Lemma | 0.774 | 0.757 | 0.771 | **< 10ms** |
| Logistic Regression | Stem | 0.773 | 0.756 | 0.769 | < 10ms |
| BiLSTM (Random) | Lemma | 0.774 | **0.772** | **0.773** | ~35ms |
| BiLSTM (Random) | Stem | 0.771 | 0.752 | 0.767 | ~35ms |
| BiLSTM + Word2Vec | Lemma | **0.776** | 0.741 | 0.767 | ~40ms |
| BiLSTM + GloVe | Lemma | **0.776** | 0.747 | 0.769 | ~40ms |
| USE | Lemma | ~0.77 | ~0.75 | ~0.76 | ~50ms |
| BERT | Lemma | 0.762 | 0.694 | 0.745 | ~160ms |

<div class="success-box">

**Recommandation** : **BiLSTM (Lemma, Random)** offre le meilleur compromis Recall Négatif / Latence pour la production.

</div>

---

## 11. Optimisation des Hyperparamètres

### Paramètres ajustés pour améliorer les performances

<div class="two-cols">

<div>

**Hyperparamètres optimisés** :

| Paramètre | Valeurs testées | Optimal |
|-----------|-----------------|---------|
| Learning rate | 1e-2, 1e-3, 1e-4 | **1e-3** |
| Batch size | 32, 64, 128, 256 | **256** |
| LSTM units | 32, 64, 128 | **64** |
| Dropout | 0.2, 0.3, 0.5 | **0.3** |
| Epochs | 5, 10, 15, 20 | **10** |

**Techniques utilisées** :
- Early Stopping (patience=3)
- Validation monitoring
- MLflow tracking

</div>

<div>

<div class="highlight-box">

**Loss Function** : `sparse_categorical_crossentropy`

Choix justifié par :
- Labels entiers (0, 1, 2)
- Multi-classe (3 classes)
- Efficacité mémoire

</div>

<div class="success-box">

**Impact** : L'optimisation a permis de gagner +1.5% de recall négatif et de réduire le temps d'entraînement de 40%.

</div>

</div>

</div>

---

## 12. Pipeline MLflow : Tracking & Reproductibilité

### Centralisation des expérimentations

<div class="two-cols">

<div>

**MLflow Tracking** :
- Serveur local : `http://127.0.0.1:5000`
- Stockage : `result/mlruns/`

**Éléments trackés** :
- <span class="tag">Hyperparamètres</span>
- <span class="tag tag-green">Métriques</span>
- <span class="tag tag-purple">Artefacts</span>
- <span class="tag tag-orange">Modèles</span>

```python
with mlflow.start_run(run_name="BERT_lemma"):
    mlflow.log_param("learning_rate", lr)
    mlflow.log_metric("val_accuracy", acc)
    mlflow.log_artifact("confusion_matrix.png")
    mlflow.tensorflow.log_model(model)
```

</div>

<div>

**Callback personnalisé** :
```python
class LogToMLflow(Callback):
    def on_epoch_end(self, epoch, logs):
        mlflow.log_metric("train_loss", 
                          logs["loss"], step=epoch)
        mlflow.log_metric("val_accuracy", 
                          logs["val_accuracy"], step=epoch)
```

<div class="success-box">

**Bénéfice** : Toutes les expériences sont reproductibles et comparables via l'interface MLflow UI.

</div>

</div>

</div>

---

## 13. Stockage & Sérialisation des Modèles

### Registre centralisé des modèles

<div class="two-cols">

<div>

**Double export** :
1. **Archive** : `result/my_bert_model/`
2. **Production** : `app/model/my_bert_model/`

```python
def export_model_artifacts(model, tokenizer):
    # Export pour archivage
    model.save_pretrained(MODEL_EXPORT_DIR)
    tokenizer.save_pretrained(MODEL_EXPORT_DIR)
    
    # Copie pour l'API
    shutil.copytree(MODEL_EXPORT_DIR, APP_MODEL_DIR)
```

**Formats** :
- Modèles Keras : `.h5` / SavedModel
- Modèles HuggingFace : `config.json`, `tf_model.h5`
- Tokenizers : `vocab.txt`, `tokenizer_config.json`

</div>

<div>

**Structure des artefacts** :

```
result/
├── mlruns/           # MLflow tracking
├── plots/            # Confusion matrices
├── reports/          # Classification reports
└── my_bert_model/    # Modèle exporté
    ├── config.json
    ├── tf_model.h5
    ├── vocab.txt
    └── tokenizer_config.json
```

<div class="highlight-box">

**Cohérence garantie** : Le même modèle/tokenizer est utilisé pour l'évaluation et la production.

</div>

</div>

</div>

---

## 14. Version Control & Collaboration

### Gestion du code avec Git & GitHub

<div class="two-cols">

<div>

**Structure du repository** :

```
project-7/
├── app/              # API FastAPI
│   ├── main.py
│   ├── model/
│   └── tests/
├── infra/            # Infrastructure Pulumi
├── notebook.py       # Expérimentation
├── pyproject.toml    # Dépendances
├── Dockerfile
└── .github/workflows/  # CI/CD
```

**Historique Git** :
```bash
$ git log --oneline -5
ddda767 fix insight alert
7d4d747 add azure app insight, add blog
b86851c fix destroy command
588e39d fix docker port add logging
46725f7 fix deploy
```

</div>

<div>

**Gestion des dépendances** :

```toml
# pyproject.toml
[project]
dependencies = [
    "tensorflow==2.19.1",
    "transformers>=4.57.1",
    "tensorflow-hub>=0.16.1",
    "mlflow>=3.5.1",
    "fastapi>=0.100.0",
    ...
]
```

<div class="success-box">

**Lockfile** : `uv.lock` garantit la reproductibilité exacte des versions.

</div>

</div>

</div>

---

## 15. API FastAPI : Endpoints de Prédiction

### Déploiement du modèle en tant qu'API REST

<div class="two-cols">

<div>

**Endpoints disponibles** :

| Route | Méthode | Description |
|-------|---------|-------------|
| `/` | GET | Interface web |
| `/predict` | POST | Prédiction |
| `/feedback` | POST | Feedback utilisateur |

**Exemple de requête** :
```json
POST /predict
{
  "text": "This flight was terrible!"
}

Response:
{
  "label": "Negative",
  "confidence": 0.94
}
```

</div>

<div>

**Code de l'endpoint** :
```python
@app.post("/predict")
def predict_sentiment(input_data: TweetInput):
    start_time = time.perf_counter()
    label, confidence = classify_tweet(
        input_data.text, tokenizer, model
    )
    latency_ms = (time.perf_counter() - start_time) * 1000
    
    emit_event("prediction", {
        "text_hash": hash_text(input_data.text),
        "predicted_label": label,
        "latency_ms": f"{latency_ms:.2f}",
    })
    
    return {"label": label, "confidence": confidence}
```

</div>

</div>

---

## 16. Tests Unitaires Automatisés

### Validation avec pytest

<div class="two-cols">

<div>

**Tests implémentés** :

```python
def test_classify_tweet_returns_positive_label():
    label, confidence = classify_tweet(
        "Great service!",
        tokenizer, model
    )
    assert label == "Positive"
    assert 0 <= confidence <= 1

def test_predict_endpoint():
    response = client.post("/predict", 
        json={"text": "Great company!"})
    assert response.status_code == 200
    assert "label" in response.json()

def test_feedback_endpoint_persists():
    response = client.post("/feedback", 
        json=payload)
    assert response.status_code == 200
    # Vérifie la persistance CSV
```

</div>

<div>

**Stratégie de test** :

- **Mocking** : Tokenizer et modèle mockés pour tests rapides
- **Fixtures pytest** : Isolation des tests
- **TestClient FastAPI** : Tests d'intégration API

<div class="success-box">

**Exécution** :
```bash
$ uv run pytest app/tests/ -v
========================
4 passed in 2.34s
========================
```

</div>

</div>

</div>

---

## 17. Pipeline CI/CD avec GitHub Actions

### Intégration et déploiement continus

<div class="two-cols">

<div>

**Workflow CI** (`.github/workflows/ci.yaml`):

```yaml
jobs:
  python:
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --frozen
      - run: uv run python -m compileall app
      - run: uv run pytest
      
  docker:
    needs: python
    steps:
      - run: docker build -t app:ci .
```

**Déclencheurs** :
- Push sur `main`
- Pull Requests

</div>

<div>

**Workflow Deploy** :

```yaml
jobs:
  deploy:
    steps:
      - run: pulumi up --yes
      - run: docker build -t $ACR/app:$SHA .
      - run: docker push $ACR/app:$SHA
      - run: az webapp restart
```

<div class="highlight-box">

**Pipeline complet** :
1. Lint & Compile
2. Tests unitaires
3. Build Docker
4. Push Azure Container Registry
5. Déploiement App Service

</div>

</div>

</div>

---

## 18. Infrastructure Azure avec Pulumi

### Infrastructure as Code

<div class="two-cols">

<div>

**Ressources déployées** :

```python
# infra/__main__.py
resource_group = azure.core.ResourceGroup(...)

# Container Registry
acr = azure.containerservice.Registry(...)

# App Service Plan (Linux B1)
plan = azure.appservice.ServicePlan(...)

# Web App
app = azure.appservice.LinuxWebApp(...)

# Application Insights
insights = azure.appinsights.Component(...)

# Alert Rule
alert = azure.monitoring.ScheduledQueryRulesAlertV2(...)
```

</div>

<div>

**Architecture déployée** :

```
┌─────────────────────────────────────┐
│         Azure Cloud                 │
├─────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  │
│  │ App Service │←→│     ACR      │  │
│  │  (FastAPI)  │  │  (Docker)    │  │
│  └──────┬──────┘  └──────────────┘  │
│         │                           │
│         ↓                           │
│  ┌─────────────┐  ┌──────────────┐  │
│  │ App Insights│→→│    Alerts    │  │
│  │ (Telemetry) │  │  (Email/SMS) │  │
│  └─────────────┘  └──────────────┘  │
└─────────────────────────────────────┘
```

</div>

</div>

---

## 19. Monitoring avec Azure Application Insights

### Suivi de la performance en production

<div class="two-cols">

<div>

**Télémétrie collectée** :

```python
def emit_event(name: str, properties: Dict):
    if TELEMETRY_ENABLED:
        track_event(name, properties)
    logger.info(name, extra={
        "custom_dimensions": properties
    })
```

**Événements trackés** :
- `prediction` : chaque prédiction
  - `text_hash`, `predicted_label`
  - `confidence`, `latency_ms`
- `feedback` : corrections utilisateur
  - `correct` (True/False)
  - `model_version`

</div>

<div>

**Configuration des alertes** :

```sql
-- Requête Kusto
traces
| where customDimensions.correct == "False"
| summarize count() by bin(timestamp, 5m)
| where count_ >= 3
```

<div class="warning-box">

**Règle d'alerte** : Si 3+ feedbacks négatifs en 5 minutes → Notification email/SMS

</div>

**Boucle d'amélioration** :
1. Collecter les feedbacks
2. Analyser les erreurs
3. Réentraîner si nécessaire
4. Redéployer via CI/CD

</div>

</div>

---

## 20. Collecte de Feedback Utilisateur

### Interface et stockage des retours

<div class="two-cols">

<div>

**Interface web** :
- Boutons 👍 / 👎 après chaque prédiction
- Stockage local CSV + télémétrie Azure

**Endpoint Feedback** :
```python
@app.post("/feedback")
def store_feedback(feedback: FeedbackInput):
    # Persistance CSV
    with open(FEEDBACK_FILE, 'a') as file:
        writer.writerow([
            feedback.text,
            feedback.label,
            feedback.confidence,
            feedback.correct
        ])
    
    # Télémétrie Azure
    emit_event("feedback", {...})
    
    return {"message": "Feedback submitted"}
```

</div>

<div>

**Structure des données collectées** :

| Champ | Type | Description |
|-------|------|-------------|
| text | string | Tweet analysé |
| label | string | Prédiction |
| confidence | float | Score de confiance |
| correct | bool | Validation utilisateur |

<div class="success-box">

**Exploitation** : Les feedbacks alimentent le réentraînement continu et permettent de calculer l'accuracy "terrain" réelle.

</div>

</div>

</div>

---

## 21. Stratégie de Maintenance du Modèle

### Amélioration continue de la performance

<div class="highlight-box">

**Cycle de vie MLOps** : Monitoring → Détection de drift → Réentraînement → Déploiement → Monitoring

</div>

<div class="two-cols">

<div>

**Indicateurs surveillés** :
- Accuracy glissante (24h, 7j)
- Distribution des prédictions
- Latence moyenne
- Taux de feedback négatif

**Déclencheurs de réentraînement** :
- Drift détecté (accuracy < seuil)
- Nouveaux patterns linguistiques
- Volume critique de feedbacks

</div>

<div>

**Actions d'amélioration** :
1. Analyser les faux négatifs prioritaires
2. Enrichir le dataset avec les feedbacks
3. Tester de nouveaux hyperparamètres
4. Valider sur ensemble de test frais
5. Déploiement progressif (canary)

<div class="warning-box" style="font-size: 0.9em;">

**Précaution** : Ne jamais déployer sans validation sur données récentes.

</div>

</div>

</div>

---

## 22. Conclusion & Recommandations

### Synthèse du projet

<div class="three-cols">

<div class="metric-card">
<div class="metric-label">Modèle recommandé</div>
<div class="metric-value" style="font-size: 1.2em;">BiLSTM</div>
<div style="font-size: 0.8em;">Lemma + Random Emb.</div>
</div>

<div class="metric-card">
<div class="metric-label">Recall Négatif</div>
<div class="metric-value">77.2%</div>
<div style="font-size: 0.8em;">+2% vs baseline</div>
</div>

<div class="metric-card">
<div class="metric-label">Latence</div>
<div class="metric-value">35ms</div>
<div style="font-size: 0.8em;">Production-ready</div>
</div>

</div>

<div class="success-box">

**Livrables** :
- ✅ 4 familles de modèles comparées (TF-IDF, LSTM, BERT, USE)
- ✅ Pipeline MLflow reproductible
- ✅ API FastAPI déployée sur Azure
- ✅ Tests unitaires automatisés
- ✅ Monitoring & alertes configurés

</div>

---

## 23. Prochaines Étapes

### Roadmap d'évolution

<div class="two-cols">

<div>

**Court terme** :
1. Optimiser USE avec architectures plus profondes
2. Étendre BERT à 30-50k samples
3. Implémenter FastText comme alternative

**Moyen terme** :
4. Synchroniser feedbacks → MLflow automatiquement
5. Créer workbook Azure Monitor
6. Déploiement multi-modèles (A/B testing)

</div>

<div>

**Long terme** :
7. Détection automatique de drift
8. Réentraînement automatisé
9. Extension multi-langue (FR, ES)

<div class="highlight-box">

**Objectif** : Passer d'un prototype fonctionnel à un système MLOps mature avec amélioration continue automatisée.

</div>

</div>

</div>

---

<!-- _class: title-slide -->

# Merci de votre attention

### Questions & Discussion

<br>

**Ressources** :
- Repository : GitHub
- API : Azure App Service  
- Monitoring : Application Insights
- Documentation : `blog.md`

<br>

*Projet réalisé dans le cadre de la formation Data Science*
