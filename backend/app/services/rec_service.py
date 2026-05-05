import pandas as pd

# Mapping cluster → profil client selon les centroïdes K-means
CLUSTER_PROFILES = {
    0: {"client_type": "Nouveau client", "description": "Faible panier, satisfaction neutre"},
    1: {"client_type": "Client régulier", "description": "Panier moyen, bonne satisfaction"},
    2: {"client_type": "Client premium", "description": "Panier élevé, haute satisfaction"},
    3: {"client_type": "Client à risque", "description": "Panier moyen, satisfaction faible"},
    4: {"client_type": "Grand public", "description": "Volume élevé, panier modéré"},
}

SEASON_CATEGORIES = {
    "printemps": ["jardin_outils", "sport_loisirs", "beaute_sante"],
    "ete":       ["sport_loisirs", "electronique", "mode_vetements"],
    "automne":   ["maison_decoration", "electronique", "livres"],
    "hiver":     ["jouets", "maison_decoration", "mode_vetements"],
}

SEASON_CHANNELS = {
    "printemps": ["Email", "Social Media", "SEA"],
    "ete":       ["Social Media", "Influenceurs", "Display"],
    "automne":   ["Email", "SEA", "Display"],
    "hiver":     ["Email", "SEA", "Social Media", "SMS"],
}

OFFER_TYPES = {
    "Nouveau client":   "Code promo bienvenue (-15%)",
    "Client régulier":  "Programme fidélité — points doublés",
    "Client premium":   "Offre exclusive VIP + livraison offerte",
    "Client à risque":  "Offre de rétention (-20%) + email personnalisé",
    "Grand public":     "Pack spécial saison — bundle 3 articles",
}


def generate(df_with_clusters: pd.DataFrame, season: str, total_budget: float, currency: str) -> list[dict]:
    season_key = season.lower().replace("é", "e").replace("è", "e")
    cluster_counts = df_with_clusters["cluster"].value_counts().to_dict()
    total_clients = len(df_with_clusters)

    recos = []
    active_clusters = sorted(cluster_counts.keys())

    budget_per_cluster = total_budget / len(active_clusters) if active_clusters else 0
    categories = SEASON_CATEGORIES.get(season_key, ["electronique", "mode_vetements"])
    channels = SEASON_CHANNELS.get(season_key, ["Email", "SEA"])

    for i, cluster_id in enumerate(active_clusters):
        profile = CLUSTER_PROFILES.get(int(cluster_id), CLUSTER_PROFILES[0])
        target_size = cluster_counts[cluster_id]
        budget = round(budget_per_cluster, 2)
        roi = _estimate_roi(profile["client_type"], season_key)

        recos.append({
            "cluster_id": int(cluster_id),
            "client_type": profile["client_type"],
            "description": profile["description"],
            "product_category": categories[i % len(categories)],
            "offer_type": OFFER_TYPES.get(profile["client_type"], "Promotion saisonnière"),
            "channels": channels,
            "budget": budget,
            "currency": currency,
            "roi_estimate": roi,
            "target_size": target_size,
            "target_pct": round(target_size / total_clients * 100, 1),
        })

    return recos


def _estimate_roi(client_type: str, season: str) -> float:
    base = {"Client premium": 3.5, "Client régulier": 2.8, "Grand public": 2.2,
            "Nouveau client": 1.8, "Client à risque": 1.5}
    season_bonus = {"hiver": 0.4, "printemps": 0.2, "ete": 0.1, "automne": 0.15}
    return round(base.get(client_type, 2.0) + season_bonus.get(season, 0), 2)
