import pandas as pd
import uuid
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv
import os
import re

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


# -----------------------------------------------
# MAIN FUNCTION — DataFrame → PostgreSQL Table
# -----------------------------------------------

def push_to_postgres(df: pd.DataFrame, file_name: str, user_id: str = None) -> dict:
    """
    Takes a cleaned DataFrame and pushes it into PostgreSQL.
    Creates a unique table for this upload.
    Logs the upload in the uploads table.
    Returns metadata about the upload.
    """

    # Step 1 — Generate unique IDs
    upload_id = str(uuid.uuid4())
    if not user_id:
        user_id = get_or_create_default_user()

    # Step 2 — Generate a safe unique table name
    table_name = generate_table_name(file_name, upload_id)

    # Step 3 — Infer and fix data types
    df = infer_data_types(df)

    # Step 4 — Push DataFrame to PostgreSQL
    try:
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace",
            index=False,
            schema="public"
        )
        print(f"✅ Table '{table_name}' created with {df.shape[0]} rows x {df.shape[1]} columns")
    except Exception as e:
        log_upload_status(upload_id, user_id, file_name, table_name, "failed")
        raise RuntimeError(f"Failed to push data to PostgreSQL: {e}")

    # Step 5 — Log the upload
    file_type = file_name.rsplit(".", 1)[-1].lower()
    log_upload_status(upload_id, user_id, file_name, table_name, "ready", file_type)

    # Step 6 — Return metadata
    return {
        "upload_id": upload_id,
        "user_id": user_id,
        "table_name": table_name,
        "file_name": file_name,
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": list(df.columns),
        "status": "ready"
    }


# -----------------------------------------------
# QUERY FUNCTION — Run SQL on any table
# -----------------------------------------------

def run_query(sql: str) -> pd.DataFrame:
    """
    Executes any SQL query and returns result as a DataFrame.
    Used by Layer 3 (dashboard) and Layer 4 (chatbot).
    """
    try:
        with engine.connect() as conn:
            result = pd.read_sql_query(text(sql), conn)
            print(f"✅ Query returned {len(result)} rows")
            return result
    except Exception as e:
        raise RuntimeError(f"Query failed: {e}\nSQL: {sql}")


# -----------------------------------------------
# SCHEMA INSPECTOR — Get table structure
# -----------------------------------------------

def get_table_schema(table_name: str) -> dict:
    """
    Returns column names and data types for any table.
    This is fed to the LLM in Layer 4 as context.
    """
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name, schema="public")

        schema = {
            "table_name": table_name,
            "columns": [
                {
                    "name": col["name"],
                    "type": str(col["type"])
                }
                for col in columns
            ]
        }

        print(f"✅ Schema fetched for '{table_name}'")
        return schema

    except Exception as e:
        raise RuntimeError(f"Schema inspection failed: {e}")


# -----------------------------------------------
# DATA TYPE INFERENCE — Clean up column types
# -----------------------------------------------

def infer_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tries to convert columns to proper types:
    - Numeric strings → int or float
    - Date strings → datetime
    - Everything else stays as string
    """
    for col in df.columns:
        # Try numeric
        try:
            df[col] = pd.to_numeric(df[col])
            continue
        except (ValueError, TypeError):
            pass

        # Try datetime
        try:
            converted = pd.to_datetime(df[col], format="mixed", dayfirst=False)
            # Only convert if more than 50% parsed successfully
            if converted.notna().sum() > len(df) * 0.5:
                df[col] = converted
            continue
        except (ValueError, TypeError):
            pass

    return df


# -----------------------------------------------
# TABLE NAME GENERATOR
# -----------------------------------------------

def generate_table_name(file_name: str, upload_id: str) -> str:
    """
    Creates a safe PostgreSQL table name from the file name.
    Example: 'Sales Data Q3.xlsx' → 'sales_data_q3_a3f9b2c1'
    """
    base = file_name.rsplit(".", 1)[0]           # Remove extension
    base = base.lower()                           # Lowercase
    base = re.sub(r"[^\w]", "_", base)           # Replace special chars
    base = re.sub(r"_+", "_", base)              # Remove duplicate underscores
    base = base[:30]                              # Limit length
    short_id = upload_id.replace("-", "")[:8]   # Short unique suffix
    return f"{base}_{short_id}"


# -----------------------------------------------
# UPLOAD LOGGER
# -----------------------------------------------

def log_upload_status(upload_id, user_id, file_name, table_name, status, file_type="unknown"):
    """
    Logs every upload into the uploads table in PostgreSQL.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO uploads (upload_id, user_id, file_name, file_type, table_name, status)
                VALUES (:upload_id, :user_id, :file_name, :file_type, :table_name, :status)
                ON CONFLICT (upload_id) DO UPDATE SET status = :status
            """), {
                "upload_id": upload_id,
                "user_id": user_id,
                "file_name": file_name,
                "file_type": file_type,
                "table_name": table_name,
                "status": status
            })
            conn.commit()
    except Exception as e:
        print(f"⚠️ Upload logging failed (non-critical): {e}")


# -----------------------------------------------
# DEFAULT USER — For testing without auth
# -----------------------------------------------

def get_or_create_default_user() -> str:
    """
    Creates a default test user if none exists.
    Will be replaced by real auth in production.
    """
    default_email = "test@analyzeiq.com"
    default_id = str(uuid.uuid4())

    try:
        with engine.connect() as conn:
            # Check if default user exists
            result = conn.execute(text(
                "SELECT user_id FROM users WHERE email = :email"
            ), {"email": default_email})
            row = result.fetchone()

            if row:
                return str(row[0])
            else:
                # Create default user
                conn.execute(text("""
                    INSERT INTO users (user_id, email)
                    VALUES (:user_id, :email)
                """), {"user_id": default_id, "email": default_email})
                conn.commit()
                print(f"✅ Default test user created")
                return default_id

    except Exception as e:
        print(f"⚠️ Could not fetch/create user: {e}")
        return default_id