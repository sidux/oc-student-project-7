# Anticiper les bad buzz pour Air Paradis : 3 modèles et une chaîne MLOps opérationnelle

Lorsque Air Paradis nous a demandé un prototype capable d'anticiper les bad buzz sur X/Twitter, l'enjeu était double : atteindre une performance métier fiable sur un problème de classification binaire (négatif vs non négatif) et démontrer qu'une approche MLOps complète pouvait être déployée rapidement à coût maîtrisé. Nous avons donc construit trois familles de modèles (« modèle sur mesure simple », « modèle sur mesure avancé » et « modèle avancé BERT ») tout en outillant chaque étape de la chaîne de valeur : tracking des expériences, stockage et versioning des modèles, tests, déploiement automatisé sur Azure et monitoring proactif. Cet article (environ 1 700 mots) synthétise les enseignements et s'appuie sur les captures d'écran produites dans le dossier `result/`.

## 1. Données, prétraitements et instrumentation de l'expérimentation

Nous sommes partis du corpus open source de 1,6 million de tweets (`data/training.1600000.processed.noemoticon.csv`). Pour réduire les coûts d'entraînement tout en conservant la diversité lexicale, le notebook (`notebook.py`) échantillonne 200 000 tweets stratifiés, applique deux variantes de nettoyage (`lemma` et `stem`) via la fonction `clean_text` (suppression des URLs, mentions, normalisation, stop words, puis lemmatisation WordNet ou stemming Snowball) et construit un split 80/10/10 strictement séparé (`train_test_split` avec `stratify`).

Chaque cellule critique se termine par `save_cell_output` (`util/result.py`), ce qui exporte figures, rapports et jeux de données nettoyés dans `result/cell_X/`. En parallèle, toutes les expériences sont loggées sur un serveur MLflow local (`mlflow.set_tracking_uri("http://127.0.0.1:5000")`). Cela nous permet de tracer hyperparamètres, métriques (AUC, F1 négatif, temps d'entraînement) et artefacts (matrices de confusion, rapports de classification, modèles sérialisés) pour les trois familles de modèles.

## 2. Modèle sur mesure simple : TF-IDF + régression logistique

La baseline repose sur un pipeline scikit-learn classique (`run_logistic_regression` dans `notebook.py`). Après vectorisation TF-IDF (10 000 n-grammes, 1-2), nous entraînons une régression logistique (`C=1`, `max_iter=200`). Les performances consolidées dans `result/cell_06_logreg_summary/metrics.json` montrent :

- Accuracy test ~0,778
- Recall négatif (classe 0) : 0,756
- F1 négatif : 0,770

La matrice de confusion confirme un équilibre raisonnable entre faux positifs et faux négatifs.

![Copie d'écran 1 – Matrice de confusion du modèle sur mesure simple](result/plots/logreg_cm_lemma.png)

Cette approche présente trois atouts : une explication aisée (poids TF-IDF), une latence <10 ms en CPU (multiplication matrice x poids) et un coût de stockage infime (<150 Ko). C'est la ligne de base idéale pour challenger les approches plus lourdes. En revanche, la modélisation reste purement linéaire ; elle peine sur l'ironie, les emojis et les dépendances de longue portée caractéristiques de Twitter.

## 3. Modèle sur mesure avancé : LSTM bi-directionnel et embeddings

Pour capturer la structure linguistique, nous avons conçu un modèle Keras (`build_lstm_model`) composé d'un embedding trainable (dimension 128), d'une couche BiLSTM (64 unités) et de denses regularisées (dropout 0,3). Trois variantes d'embeddings ont été testées :

1. **Embeddings aléatoires finement ajustés** (`run_lstm_experiment`, sorties `result/lstm_cr_lemma_random.txt`).
2. **Word2Vec GoogleNews 300d** (`run_lstm_pretrained` avec `experiment_name="w2v_lemma"`).
3. **GloVe wiki-gigaword 100d** (`experiment_name="glove_lemma"`).

Les callbacks `EarlyStopping` et `LogToMLflow` assurent respectivement la régularisation et le logging d'époque en époque.

![Copie d'écran 2 – Courbes d'entraînement LSTM (accès `result/lstm_training_curves.png`)](result/lstm_training_curves.png)

La meilleure configuration métier est obtenue avec le jeu **lemma + embeddings aléatoires** : accuracy 0,774, recall négatif 0,772 et F1 négatif 0,773 (`result/cell_07_lstm_summary/metrics.json`). Les embeddings pré-entraînés GloVe/W2V apportent une légère stabilité sur la classe positive mais n'améliorent pas la sensibilité aux tweets négatifs. Côté opérationnel, le modèle pèse ~12 Mo et infère en ~35 ms sur CPU, ce qui reste compatible avec un plan Azure Web App F1/B1.

![Copie d'écran 3 – Matrice de confusion du modèle sur mesure avancé (ex. GloVe lemma)](result/plots/lstm_cm_glove_lemma.png)

## 4. Modèle avancé BERT : transfert d'apprentissage ciblé

Afin de proposer un modèle « état de l'art », nous avons fine-tuné `bert-base-uncased` (`run_bert_experiment`). Pour limiter l'empreinte GPU, l'entraînement se fait sur 3 000 tweets (train), 1 000 (val) et 1 000 (test), séquences tronquées à 30 tokens, batch size 16 et scheduler linéaire avec warmup 10 %. Un export Hugging Face (`export_model_artifacts`) alimente ensuite l'API FastAPI (`app/model/my_bert_model`).

Les métriques (fichier `result/bert_cr_lemma.txt`) indiquent une **accuracy de 0,762** et un **recall négatif de 0,694**. Cette baisse tient surtout au jeu d'entraînement réduit ; néanmoins BERT conserve un excellent rappel sur la classe positive (0,830) et restitue des probabilités bien calibrées.

![Copie d'écran 4 – Matrice de confusion du modèle BERT](result/plots/bert_cm_lemma.png)

En production, le modèle occupe ~420 Mo et nécessite ~160 ms par requête sur CPU, ce qui impose soit un pod dédié, soit une mutualisation très limitée sur App Service. L'intérêt principal réside dans sa capacité à comprendre le contexte (sarcasme léger, hashtags composés) et à servir de référence pour la recherche future.

## 5. Comparaison synthétique et arbitrage métier

| Approche | Jeu d'entraînement | Accuracy | Recall négatif | Latence CPU (estim.) | Taille modèle |
| --- | --- | --- | --- | --- | --- |
| Modèle sur mesure simple | 200k tweets (lemma) | 0,778 | 0,756 | <10 ms | ~0,15 Mo |
| Modèle sur mesure avancé (BiLSTM) | 200k tweets (lemma) | 0,774 | **0,772** | ~35 ms | ~12 Mo |
| Modèle avancé BERT | 3k tweets | 0,762 | 0,694 | ~160 ms | ~420 Mo |

Cette table montre que le BiLSTM offre le meilleur compromis pour Air Paradis : il gagne +1,6 pt de recall négatif par rapport à la baseline tout en respectant la contrainte de coût. BERT reste supérieur sur des cas linguistiques difficiles, mais son coût d'inférence multiplie par 16 la facture Web App ; nous le conservons comme modèle de référence et pour les relances de R&D. Le modèle simple, quant à lui, est idéal pour des environnements edge ou en backup si le service principal tombe.

## 6. Démarche MLOps mise en œuvre

### 6.1 Tracking, gouvernance et reproductibilité

Le notebook synchronisé via Jupytext (`notebook.ipynb` ⟷ `notebook.py`) sert d'unique source de vérité. Chaque expérience déclenche `mlflow.start_run`, loggue hyperparamètres, métriques et artefacts (cf. lignes 276+, 431+, 705+). Les modèles sont loggés via `mlflow.sklearn.log_model`, `mlflow.tensorflow.log_model` ou `mlflow.tensorflow.log_model` (BERT). Le dossier `result/mlruns` conserve l'historique pour audit, tandis que `result/plots` et `result/reports` stockent automatiquement les copies d'écran exploitées dans cet article.

### 6.2 Stockage et versioning des modèles

Les artefacts finaux sont exportés deux fois :

- `result/my_bert_model/` pour l'archivage et la promotion vers MLflow Model Registry.
- `app/model/my_bert_model/` pour l'inférence FastAPI. La fonction `export_model_artifacts` rafraîchit les deux dossiers et garantit la cohérence modèle/tokenizer.

Le code est versionné dans Git ; le script `script/ensure-project-name.sh` aligne automatiquement `pyproject.toml` et `infra/Pulumi.yaml` sur le nom du dépôt, ce qui évite les dérives entre environnements.

### 6.3 Tests unitaires et validation fonctionnelle

Avant chaque entraînement massif, nous exécutons des tests ciblés :

- Vérification du nettoyage (`clean_text`) et du mapping d'étiquettes (`map_target`) via des assertions dans le notebook.
- Tests d'API manuels automatisables (`app/test.http`) qui enchaînent `POST /predict` et `POST /feedback`.
- Validation des splits (absence de doublons) et de la signature des modèles (schema loggé dans MLflow).

Cette base sera complétée par un `uv run pytest` regroupant des tests sur `classify_tweet`, sur la présence des colonnes critiques et sur le comportement du `FeedbackInput`. L'objectif est d'intégrer ces tests dans GitHub Actions avant chaque `docker build`.

### 6.4 Déploiement automatisé et infrastructure as code

Le conteneur est construit à partir du `Dockerfile` (base `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`). `uv sync --frozen --no-dev` assure la reproductibilité des dépendances, puis FastAPI est lancé avec Uvicorn (`CMD ["uv", "run", "uvicorn", ...]`).

Le script `script/deploy.sh` orchestre la chaîne :

1. `pulumi up` (stack `dev` par défaut) crée les ressources Azure (Resource Group, App Service Plan Linux B1, Container Registry, Log Analytics + Application Insights, alerte).
2. `docker build` + `docker push` vers l'ACR.
3. Redéploiement de l'App Service et streaming automatique des logs pour détecter les erreurs.

L'infrastructure est décrite dans `infra/__main__.py` : outre les ressources précédentes, on y définit un alerting basé sur Azure Monitor (`ScheduledQueryRulesAlertV2`) qui déclenche une notification si `customDimensions.correct == "False"` apparaît au moins 3 fois en 5 minutes. Les variables d'environnement `APPINSIGHTS_INSTRUMENTATIONKEY` et `APPLICATIONINSIGHTS_CONNECTION_STRING` sont injectées dans l'App Service pour permettre la télémétrie.

## 7. Monitoring de la performance et boucle d'amélioration continue

### 7.1 Collecte de feedback utilisateur

L'interface (`app/templates/index.html` + `app/static/script.js`) propose deux boutons « 👍 / 👎 ». Chaque clic envoie une requête `POST /feedback` (classe `FeedbackInput` dans `app/main.py`) qui consigne `text`, `predicted_label`, `confidence` et `correct` dans `app/feedback.csv`. Ce fichier peut être synchronisé quotidiennement vers Azure Blob Storage et rechargé comme données labellisées fraîchement validées par les équipes marketing.

### 7.2 Télémétrie Application Insights et alertes

Pour passer à l'échelle, nous prévoyons d'ajouter le SDK `opencensus-ext-azure` ou `azure-monitor-opentelemetry` dans FastAPI : chaque prédiction et chaque feedback généreront un `track_event` enrichi de `customDimensions` (`tweet_hash`, `model_version`, `latency_ms`, `user_feedback`). Grâce aux variables d'environnement fournies par Pulumi, ces traces arrivent automatiquement dans Application Insights. L'alerte configurée (`infra/__main__.py`, requête Kusto `traces | where customDimensions.correct == "False"`) envoie e-mail/SMS dès que 3 validations négatives surviennent en 5 minutes, ce qui permet d'alerter le community management avant que le bad buzz ne s'amplifie.

Nous recommandons également de créer un Workbook Azure Monitor affichant :

- L'accuracy glissante sur 24 h et 7 jours.
- La distribution des hashtags parmi les erreurs (`extend hashtags = extract_all('(#\\w+)', 0, text)` dans Kusto).
- La latence par version de modèle.

### 7.3 Analyse des statistiques et amélioration continue

La boucle d'amélioration proposée suit quatre étapes :

1. **Consolider les feedbacks** : chaque semaine, exporter `feedback.csv` + les traces Application Insights (via `az monitor app-insights query`).
2. **Qualifier les erreurs** : détecter les faux négatifs prioritaires (tweets négatifs labellisés positifs). On peut enrichir ces tweets avec des attributs métiers (campagne, type de client) pour comprendre le contexte.
3. **Réentraîner** : réinjecter ces exemples dans MLflow, lancer de nouveaux runs LSTM/BERT et comparer via `mlflow models serve`. Le registraire MLflow permet de promouvoir `Production` → `Staging` → `Archived`.
4. **Déployer de manière sécurisée** : utiliser des slots d'App Service ou une étape canary (par exemple, rediriger 10 % du trafic vers la nouvelle image Docker avant de basculer complètement).

Cette démarche garantit que le modèle reste aligné avec l'actualité (nouvelles expressions, hashtags de crise) et que chaque itération est tracée.

## 8. Conclusion et prochaines étapes

En synthèse, le modèle sur mesure avancé (BiLSTM) constitue aujourd'hui la meilleure réponse aux besoins d'Air Paradis : il équilibre précision, coût et latence tout en restant explicable (poids d'embedding) et industrialisable (FastAPI + Docker + Pulumi). La présence du modèle sur mesure simple assure une solution de repli ultra-rapide, tandis que BERT sert de laboratoire pour capter des signaux faibles. L'ensemble est enveloppé dans une démarche MLOps complète : tracking MLflow, packaging reproductible, IaC, monitoring Application Insights et boucle de feedback utilisateur.

Les prochaines étapes consistent à automatiser les tests `pytest`, à brancher effectivement le SDK Application Insights dans l'API, puis à enrichir le pipeline de données (détection automatique du sarcasme, ingestion continue des tweets). Avec ces briques, Air Paradis disposera d'un observatoire des réseaux sociaux qui non seulement détecte les signaux faibles en temps réel, mais s'améliore de manière continue grâce aux pratiques MLOps mises en place.
