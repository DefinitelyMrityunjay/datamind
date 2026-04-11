import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

import requests
import re


def get_table_schema(table_name: str) -> str:
    """Fetches the column names and types from the database table."""
    engine = create_engine(os.getenv("DATABASE_URL"))
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = :table_name
            ORDER BY ordinal_position
        """), {"table_name": table_name})
        rows = result.fetchall()

    if not rows:
        raise ValueError(f"Table '{table_name}' not found or has no columns.")

    schema_str = f"Table name: {table_name}\nColumns:\n"
    for row in rows:
        schema_str += f"  - {row[0]} ({row[1]})\n"

    return schema_str


def generate_sql(user_question: str, table_name: str) -> str:
    """Uses Ollama (local LLM) to convert English → SQL."""
    schema = get_table_schema(table_name)

    prompt = f"""
You are a PostgreSQL expert.

VERY STRICT RULES:
- Output ONLY ONE SQL query
- NO explanation
- NO extra text
- NO markdown
- Query MUST end with semicolon ;
- ONLY SELECT queries allowed
- Use exact column names from schema

{schema}

Question: {user_question}

SQL:
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "tinyllama",
            "prompt": prompt,
            "stream": False
        }
    )

    raw_output = result.get("response", "").strip()

    # Remove markdown
    raw_output = raw_output.replace("```sql", "").replace("```", "").strip()

    # 🔥 Extract ONLY the first SELECT query
    match = re.search(r"(SELECT[\s\S]+?;)", raw_output, re.IGNORECASE)

    if match:
        sql = match.group(1)
    else:
        # fallback: take first line
        sql = raw_output.split("\n")[0]

    sql = sql.strip()

    return sql

    

def run_query(sql: str) -> dict:
    """Runs the SQL query and returns results."""
    engine = create_engine(os.getenv("DATABASE_URL"))
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        rows = result.fetchall()

    data = [dict(zip(columns, row)) for row in rows]
    return {
        "columns": columns,
        "rows": data,
        "row_count": len(data)
    }


def chat_with_data(user_question: str, table_name: str) -> dict:
    """Main function used by FastAPI."""
    try:
        sql = generate_sql(user_question, table_name)
        results = run_query(sql)

        return {
            "success": True,
            "question": user_question,
            "sql": sql,
            "data": results
        }

    except Exception as e:
        return {
            "success": False,
            "question": user_question,
            "sql": None,
            "error": str(e)
        }