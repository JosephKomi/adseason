import io
import uuid
from pathlib import Path

import pandas as pd
from fastapi import HTTPException, UploadFile

from app.config import settings

REQUIRED_COLUMNS = {"price", "payment_value", "review_score", "month"}
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


async def save_and_parse(file: UploadFile) -> dict:
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Format non supporté. Utilisez : {', '.join(ALLOWED_EXTENSIONS)}")

    content = await file.read()
    size = len(content)
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if size > max_bytes:
        raise HTTPException(413, f"Fichier trop volumineux (max {settings.MAX_FILE_SIZE_MB} Mo)")

    df = _parse(content, ext)

    cols_lower = {c.lower().strip() for c in df.columns}
    missing = REQUIRED_COLUMNS - cols_lower
    missing_required = list(missing)

    unique_name = f"{uuid.uuid4().hex}{ext}"
    dest = Path(settings.UPLOAD_DIR) / unique_name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)

    return {
        "filename": unique_name,
        "file_size": size,
        "row_count": len(df),
        "columns": {c: str(df[c].dtype) for c in df.columns},
        "missing_required": missing_required,
        "status": "error" if missing_required else "processed",
        "error_msg": f"Colonnes manquantes : {missing_required}" if missing_required else None,
    }


def load_dataframe(filename: str) -> pd.DataFrame:
    path = Path(settings.UPLOAD_DIR) / filename
    ext = path.suffix.lower()
    return _parse(path.read_bytes(), ext)


def _parse(content: bytes, ext: str) -> pd.DataFrame:
    buf = io.BytesIO(content)
    if ext == ".csv":
        for sep in [";", ",", "\t"]:
            try:
                df = pd.read_csv(buf, sep=sep, encoding="utf-8")
                if len(df.columns) > 1:
                    return df
                buf.seek(0)
            except Exception:
                buf.seek(0)
        return pd.read_csv(buf, encoding="latin1")
    return pd.read_excel(buf)
