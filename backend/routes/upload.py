from fastapi import APIRouter, UploadFile, File, HTTPException
import sys, os, shutil, traceback

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from layers.layer1_ingestion.cleaner import clean_dataframe

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, os.path.join(BASE_DIR, "layers/layer1_ingestion"))
sys.path.insert(0, os.path.join(BASE_DIR, "layers/layer2_sql"))
sys.path.insert(0, BASE_DIR)

from ingestion import ingest_file
from sql_engine import push_to_postgres

router = APIRouter()

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        print("==== UPLOAD START ====")
        print("Filename:", file.filename)

        allowed_types = ["csv", "xlsx", "xls", "pdf", "png", "jpg", "jpeg"]
        extension = file.filename.rsplit(".", 1)[-1].lower()
        print("Extension:", extension)

        if extension not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {extension}")

        temp_path = os.path.join(UPLOAD_DIR, file.filename)
        print("Saving file to:", temp_path)

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print("File saved successfully")

        print("Running ingestion...")
        df = ingest_file(temp_path)
        print("Ingestion done")
        print("DF shape:", df.shape)
        print("DF columns:", df.columns.tolist())

        print("Running cleaner...")
        result = clean_dataframe(df, use_ai=False)
        print("Cleaner done")
        print("Cleaning log:", result["log"])

        df = result["dataframe"]
        cleaning_log = result["log"]
        cleaning_issues = result["issues"]

        print("Pushing to PostgreSQL...")
        metadata = push_to_postgres(df, file_name=file.filename)
        print("Database push done")
        print("Metadata:", metadata)

        print("==== UPLOAD SUCCESS ====")

        return {
            "success": True,
            "upload_id": metadata["upload_id"],
            "table_name": metadata["table_name"],
            "file_name": metadata["file_name"],
            "rows": metadata["rows"],
            "columns": metadata["columns"],
            "column_names": metadata["column_names"],
            "message": "File uploaded and processed successfully",
            "cleaning_log": cleaning_log,
            "cleaning_issues": cleaning_issues,
        }

    except HTTPException:
        raise

    except Exception as e:
        print("==== UPLOAD ERROR ====")
        print(str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")