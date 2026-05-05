"""
Script d'entraînement standalone.
Usage : python -m app.ml.train --data path/to/data.csv --clusters 5
"""
import argparse
from pathlib import Path

import pandas as pd

from app.services.ml_service import FEATURES, train


def main():
    parser = argparse.ArgumentParser(description="Entraîner le modèle K-means AdSeason")
    parser.add_argument("--data", required=True, help="Chemin vers le CSV source")
    parser.add_argument("--clusters", type=int, default=5, help="Nombre de clusters (défaut: 5)")
    parser.add_argument("--sep", default=";", help="Séparateur CSV (défaut: ;)")
    parser.add_argument("--encoding", default="latin1", help="Encodage CSV (défaut: latin1)")
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"Erreur : fichier introuvable → {data_path}")
        return

    print(f"Chargement des données : {data_path}")
    df = pd.read_csv(data_path, sep=args.sep, encoding=args.encoding)
    print(f"  {len(df):,} lignes, {len(df.columns)} colonnes")

    missing = [f for f in FEATURES if f not in df.columns]
    if missing:
        print(f"Erreur : colonnes manquantes → {missing}")
        print(f"Colonnes disponibles : {list(df.columns)}")
        return

    print(f"Entraînement K-means avec k={args.clusters}...")
    result = train(df, n_clusters=args.clusters)

    print("\n✓ Modèle sauvegardé avec succès !")
    print(f"  Clusters      : {result['n_clusters']}")
    print(f"  Features      : {result['features']}")
    print(f"  Silhouette    : {result['silhouette_score']}")
    print(f"  Lignes train  : {result['training_rows']:,}")


if __name__ == "__main__":
    main()
