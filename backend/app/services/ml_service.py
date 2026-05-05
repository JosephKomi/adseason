from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

MODELS_DIR = Path(__file__).parent.parent / "ml" / "models"
FEATURES = ["price", "payment_value", "review_score", "month"]


def load_model() -> tuple:
    model_path = MODELS_DIR / "kmeans_model.pkl"
    scaler_path = MODELS_DIR / "scaler.pkl"
    if not model_path.exists():
        raise FileNotFoundError("Modèle ML non trouvé. Lancez d'abord l'entraînement.")
    return joblib.load(model_path), joblib.load(scaler_path)


def predict_cluster(data: dict) -> int:
    kmeans, scaler = load_model()
    row = pd.DataFrame([{f: data.get(f, 0) for f in FEATURES}])
    scaled = scaler.transform(row)
    return int(kmeans.predict(scaled)[0])


def predict_batch(df: pd.DataFrame) -> pd.DataFrame:
    kmeans, scaler = load_model()
    cols = [c for c in FEATURES if c in df.columns]
    X = df[cols].fillna(df[cols].median())
    scaled = scaler.transform(X)
    df = df.copy()
    df["cluster"] = kmeans.predict(scaled)
    return df


def train(df: pd.DataFrame, n_clusters: int = 5) -> dict:
    cols = [c for c in FEATURES if c in df.columns]
    X = df[cols].dropna()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(X_scaled)

    score = silhouette_score(X_scaled, kmeans.labels_)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(kmeans, MODELS_DIR / "kmeans_model.pkl")
    joblib.dump(scaler, MODELS_DIR / "scaler.pkl")

    return {
        "n_clusters": n_clusters,
        "features": cols,
        "silhouette_score": round(float(score), 4),
        "training_rows": len(X),
    }
