# Air Paradis - Détection de Bad Buzz Twitter

Système de classification de sentiments en temps réel pour anticiper les bad buzz sur les réseaux sociaux.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.19-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![Azure](https://img.shields.io/badge/Azure-App%20Service-blue)

## Aperçu du Projet

Ce projet implémente un pipeline MLOps complet pour la détection de sentiments sur Twitter :

- **4 familles de modèles** comparées (TF-IDF, BiLSTM, BERT, USE)
- **API REST** pour les prédictions en temps réel
- **Monitoring** avec Azure Application Insights
- **CI/CD** avec GitHub Actions et déploiement Azure

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Notebook   │ →  │   MLflow     │ →  │   Model      │       │
│  │ Experiments  │    │   Tracking   │    │   Registry   │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                 │               │
│                                                 ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   GitHub     │ →  │   Docker     │ →  │   Azure      │       │
│  │   Actions    │    │   Build      │    │   App Service│       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                 │               │
│                                                 ▼               │
│                                          ┌──────────────┐       │
│                                          │  Application │       │
│                                          │   Insights   │       │
│                                          └──────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Structure du Projet

```
project-7/
├── app/                      # API FastAPI
│   ├── main.py              # Endpoints /predict, /feedback
│   ├── model/               # Modèle BERT fine-tuné
│   ├── static/              # Assets web
│   ├── templates/           # Templates HTML
│   └── tests/               # Tests unitaires
│
├── infra/                    # Infrastructure as Code (Pulumi)
│   ├── __main__.py          # Ressources Azure
│   └── Pulumi.yaml          # Configuration
│
├── data/                     # Dataset Sentiment140
│
├── result/                   # Outputs du notebook
│   ├── plots/               # Confusion matrices
│   ├── reports/             # Classification reports
│   └── mlruns/              # MLflow tracking
│
├── .github/workflows/        # CI/CD
│   ├── ci.yaml              # Tests & lint
│   └── deploy.yaml          # Déploiement Azure
│
├── notebook.py              # Expérimentation (source Jupytext)
├── notebook.ipynb           # Notebook généré
├── presentation.md          # Slides Marp
├── blog.md                  # Documentation technique
├── pyproject.toml           # Dépendances Python
├── Dockerfile               # Image Docker API
└── README.md                # Ce fichier
```

## Installation

### Prérequis

- Python 3.12
- [uv](https://github.com/astral-sh/uv) (gestionnaire de packages)
- Docker (optionnel, pour le déploiement)

### Installation locale

```bash
# Cloner le repository
git clone <repository-url>
cd project-7

# Installer les dépendances avec uv
uv sync

# Ou avec pip
pip install -e .
```

### Télécharger le dataset

```bash
# Le dataset Sentiment140 (1.6M tweets) doit être placé dans data/
# Téléchargement via Kaggle ou manuellement
```

## Utilisation

### 1. Expérimentation (Notebook)

```bash
# Lancer JupyterLab
uv run jupyter lab

# Ou exécuter le notebook en script
uv run python notebook.py
```

Le notebook entraîne et compare :
- TF-IDF + Régression Logistique (baseline)
- BiLSTM + Embeddings (Word2Vec, GloVe)
- BERT fine-tuné
- Universal Sentence Encoder (USE)

### 2. MLflow Tracking

```bash
# Démarrer le serveur MLflow
uv run mlflow ui --port 5000

# Accéder à http://localhost:5000
```

### 3. API FastAPI

```bash
# Lancer l'API en local
uv run uvicorn app.main:app --reload --port 8000

# Accéder à http://localhost:8000
# Documentation API: http://localhost:8000/docs
```

### 4. Tests

```bash
# Exécuter les tests unitaires
uv run pytest app/tests/ -v

# Avec couverture
uv run pytest app/tests/ --cov=app
```

## API Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Interface web |
| `/predict` | POST | Prédiction de sentiment |
| `/feedback` | POST | Feedback utilisateur |
| `/docs` | GET | Documentation Swagger |

### Exemple de requête

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "This flight was terrible!"}'
```

**Réponse** :
```json
{
  "label": "Negative",
  "confidence": 0.94
}
```

## Déploiement

### Docker

```bash
# Build l'image
docker build -t air-paradis-api .

# Run le conteneur
docker run -p 8000:8000 air-paradis-api
```

### Azure (avec Pulumi)

```bash
# Se connecter à Azure
az login

# Déployer l'infrastructure
cd infra
pulumi up

# Ou utiliser le script de déploiement
./script/deploy.sh
```

### CI/CD

Le pipeline GitHub Actions :
1. **CI** : Lint, tests, build Docker
2. **Deploy** : Push vers Azure Container Registry, déploiement App Service

## Modèles Comparés

| Modèle | Accuracy | Recall Négatif | Latence |
|--------|----------|----------------|---------|
| TF-IDF + LogReg | 0.774 | 0.757 | < 10ms |
| BiLSTM (Random) | 0.774 | **0.772** | ~35ms |
| BiLSTM + Word2Vec | 0.776 | 0.741 | ~40ms |
| BiLSTM + GloVe | 0.776 | 0.747 | ~40ms |
| BERT fine-tuné | 0.762 | 0.694 | ~160ms |
| USE | ~0.77 | ~0.75 | ~50ms |

**Recommandation** : BiLSTM avec embeddings aléatoires (meilleur recall négatif).

## Monitoring

Azure Application Insights collecte :
- Traces de prédictions (latence, confiance)
- Feedbacks utilisateurs
- Alertes automatiques (3+ feedbacks négatifs en 5 min)

## Technologies

| Catégorie | Technologies |
|-----------|--------------|
| ML/DL | TensorFlow, Keras, Transformers, Gensim |
| NLP | NLTK, BERT, USE, Word2Vec, GloVe |
| API | FastAPI, Uvicorn |
| MLOps | MLflow, Docker, GitHub Actions |
| Cloud | Azure App Service, Container Registry, Application Insights |
| IaC | Pulumi |
| Tests | pytest |

## Documentation

- `presentation.md` - Slides de présentation (Marp)
- `blog.md` - Article technique détaillé
- `project.md` - Cahier des charges original

## Auteur

Projet réalisé dans le cadre de la formation Data Science - OpenClassrooms

## Licence

Ce projet est à usage éducatif.
