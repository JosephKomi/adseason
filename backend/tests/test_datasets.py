import io

import pandas as pd
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


def _make_csv(rows: int = 50) -> bytes:
    df = pd.DataFrame({
        "price": [round(i * 1.5, 2) for i in range(rows)],
        "payment_value": [round(i * 1.8, 2) for i in range(rows)],
        "review_score": [((i % 5) + 1) for i in range(rows)],
        "month": [(i % 12) + 1 for i in range(rows)],
        "customer_unique_id": [f"cust_{i}" for i in range(rows)],
    })
    buf = io.BytesIO()
    df.to_csv(buf, index=False, sep=";")
    return buf.getvalue()


async def test_upload_valid_csv(client: AsyncClient, auth_headers: dict):
    content = _make_csv()
    res = await client.post(
        "/api/datasets/upload",
        headers=auth_headers,
        files={"file": ("data.csv", content, "text/csv")},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "processed"
    assert data["row_count"] == 50
    assert data["original_name"] == "data.csv"


async def test_upload_missing_column(client: AsyncClient, auth_headers: dict):
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    buf = io.BytesIO()
    df.to_csv(buf, index=False, sep=";")

    res = await client.post(
        "/api/datasets/upload",
        headers=auth_headers,
        files={"file": ("bad.csv", buf.getvalue(), "text/csv")},
    )
    assert res.status_code == 201
    assert res.json()["status"] == "error"
    assert res.json()["error_msg"] is not None


async def test_list_datasets(client: AsyncClient, auth_headers: dict):
    content = _make_csv()
    await client.post(
        "/api/datasets/upload",
        headers=auth_headers,
        files={"file": ("data.csv", content, "text/csv")},
    )
    res = await client.get("/api/datasets/", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) == 1


async def test_upload_wrong_extension(client: AsyncClient, auth_headers: dict):
    res = await client.post(
        "/api/datasets/upload",
        headers=auth_headers,
        files={"file": ("data.json", b'{"a":1}', "application/json")},
    )
    assert res.status_code == 400


async def test_delete_dataset(client: AsyncClient, auth_headers: dict):
    content = _make_csv()
    upload = await client.post(
        "/api/datasets/upload",
        headers=auth_headers,
        files={"file": ("data.csv", content, "text/csv")},
    )
    dataset_id = upload.json()["id"]
    res = await client.delete(f"/api/datasets/{dataset_id}", headers=auth_headers)
    assert res.status_code == 204

    res = await client.get("/api/datasets/", headers=auth_headers)
    assert len(res.json()) == 0


async def test_unauthenticated_upload(client: AsyncClient):
    content = _make_csv()
    res = await client.post(
        "/api/datasets/upload",
        files={"file": ("data.csv", content, "text/csv")},
    )
    assert res.status_code == 401
