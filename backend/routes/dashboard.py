from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import pandas as pd
import os
import numpy as np

def convert_numpy(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, os.path.join(BASE_DIR, "layers/layer1_ingestion"))
sys.path.insert(0, os.path.join(BASE_DIR, "layers/layer2_sql"))
sys.path.insert(0, os.path.join(BASE_DIR, "layers/layer3_dashboard"))
sys.path.insert(0, BASE_DIR)

from sql_engine import run_query, get_table_schema
from insights import generate_insights

router = APIRouter()

# -----------------------------------------------
# GET — Full dashboard data for a table
# -----------------------------------------------

@router.get("/dashboard/{table_name}")
def get_dashboard(table_name: str):
    """
    Returns everything the React frontend needs
    to render the full dashboard for a given table.
    """
    try:
        # Fetch all data from the table
        df = run_query(f"SELECT * FROM {table_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

    # Schema
    try:
        schema = get_table_schema(table_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema fetch failed: {e}")

    # Identify column types
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    date_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

    # Key metrics
    # Key metrics
    metrics = {}
    for col in numeric_cols:
        metrics[col] = {
            "sum": convert_numpy(round(float(df[col].sum()), 2)),
            "mean": convert_numpy(round(float(df[col].mean()), 2)),
            "min": convert_numpy(round(float(df[col].min()), 2)),
            "max": convert_numpy(round(float(df[col].max()), 2))
        }

    # Chart data — bar chart
    bar_chart = None
    if categorical_cols and numeric_cols:
        cat, num = categorical_cols[0], numeric_cols[0]
        grouped = df.groupby(cat)[num].sum().reset_index()
        bar_chart = {
            "labels": grouped[cat].tolist(),
            "values": [convert_numpy(v) for v in grouped[num].tolist()],
            "x_label": cat,
            "y_label": num
        }

    # Chart data — line chart
    line_chart = None
    if date_cols and numeric_cols:
        date_col = date_cols[0]
        num_col = numeric_cols[0]
        df[date_col] = df[date_col].astype(str)
        line_data = df.groupby(date_col)[num_col].sum().reset_index()
        line_chart = {
            "labels": line_data[date_col].tolist(),
            "values": [convert_numpy(v) for v in line_data[num_col].tolist()],
            "x_label": date_col,
            "y_label": num_col
        }

    # Raw data (first 100 rows for preview)
    raw_data = df.head(100).fillna("").to_dict(orient="records")

    # AI Insights
    insights = generate_insights(df, table_name)

    return {
        "table_name": table_name,
        "schema": schema,
        "metrics": metrics,
        "bar_chart": bar_chart,
        "line_chart": line_chart,
        "raw_data": raw_data,
        "insights": insights,
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols
    }