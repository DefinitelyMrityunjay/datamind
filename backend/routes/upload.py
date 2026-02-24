from fastapi import APIRouter, UploadFile, File, HTTPException
import sys
import os
import shutil

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, os.path.join(BASE_DIR, "layers/layer1_ingestion"))
sys.path.insert(0, os.path.join(BASE_DIR, "layers/layer2_sql"))
sys.path.insert(0, BASE_DIR)

from ingestion import ingest_file
from sql_engine import push_to_postgres

router = APIRouter()

UPLOAD_DIR = "../../uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Accepts any file, runs it through Layer 1 + Layer 2,
    returns table metadata to the frontend.
    """
    allowed_types = ["csv", "xlsx", "xls", "pdf", "png", "jpg", "jpeg"]
    extension = file.filename.rsplit(".", 1)[-1].lower()

    if extension not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {extension}")

    # Save file temporarily
    temp_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Layer 1 — Ingest
    try:
        df = ingest_file(temp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

    # Layer 2 — Push to PostgreSQL
    try:
        metadata = push_to_postgres(df, file_name=file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    return {
        "success": True,
        "upload_id": metadata["upload_id"],
        "table_name": metadata["table_name"],
        "file_name": metadata["file_name"],
        "rows": metadata["rows"],
        "columns": metadata["columns"],
        "column_names": metadata["column_names"]
    }