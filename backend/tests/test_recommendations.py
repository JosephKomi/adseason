import io
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


def _make_csv(rows: int = 100) -> bytes:
    df = pd.DataFrame({
        "price": [round(i * 2.5, 2) for i in range(rows)],
        "payment_value": [round(i * 3.0, 2) for i in range(rows)],
        "review_score": [((i % 5) + 1) for i in range(rows)],
        "month": [(i % 12) + 1 for i in range(rows)],
        "customer_unique_id": [f"cust_{i}" for i in range(rows)],
        "cluster": [i % 5 for i in range(rows)],
    })
    buf = io.BytesIO()
    df.to_csv(buf, index=False, sep=";")
    return buf.getvalue()


async def _upload_dataset(client: AsyncClient, headers: dict) -> str:
    content = _make_csv()
    res = await client.post(
        "/api/datasets/upload",
        headers=headers,
        files={"file": ("data.csv", content, "text/csv")},
    )
    return res.json()["id"]


async def test_generate_recommendations(client: AsyncClient, auth_headers: dict):
    dataset_id = await _upload_dataset(client, auth_headers)

    # Mock predict_batch car pas de modèle .pkl en test
    with patch("app.routers.recommendations.predict_batch") as mock_predict:
        df = pd.read_csv(io.BytesIO(_make_csv()), sep=";")
        df["cluster"] = df.index % 5
        mock_predict.return_value = df

        res = await client.post(
            "/api/recommendations/generate",
            headers=auth_headers,
            json={
                "dataset_id": dataset_id,
                "season": "hiver",
                "currency": "EUR",
                "total_budget": 5000.0,
                "channels": ["Email", "SEA"],
            },
        )

    assert res.status_code == 201
    data = res.json()
    assert data["season"] == "hiver"
    assert data["currency"] == "EUR"
    assert "clusters" in data
    assert len(data["clusters"]["items"]) > 0


async def test_list_recommendations(client: AsyncClient, auth_headers: dict):
    res = await client.get("/api/recommendations/", headers=auth_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_get_recommendation_not_found(client: AsyncClient, auth_headers: dict):
    fake_id = "00000000-0000-0000-0000-000000000000"
    res = await client.get(f"/api/recommendations/{fake_id}", headers=auth_headers)
    assert res.status_code == 404


async def test_generate_invalid_dataset(client: AsyncClient, auth_headers: dict):
    fake_id = "00000000-0000-0000-0000-000000000000"
    res = await client.post(
        "/api/recommendations/generate",
        headers=auth_headers,
        json={
            "dataset_id": fake_id,
            "season": "ete",
            "currency": "EUR",
            "total_budget": 1000.0,
        },
    )
    assert res.status_code == 404
