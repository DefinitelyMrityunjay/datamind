import google.generativeai as genai
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# -----------------------------------------------
# MAIN — Generate AI insights from a DataFrame
# -----------------------------------------------

def generate_insights(df: pd.DataFrame, table_name: str) -> str:
    """
    Sends a summary of the DataFrame to Gemini
    and gets back a written analysis of key insights.
    """
    try:
        summary = build_data_summary(df)

        prompt = f"""
You are a senior data analyst. Analyze this dataset and provide:
1. 3-5 key insights from the data
2. Any trends you notice
3. Any anomalies or interesting patterns
4. One business recommendation based on the data

Dataset summary:
{summary}

Be concise, specific, and use numbers where possible.
Write in clear bullet points.
"""
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"⚠️ AI insights unavailable: {e}"


# -----------------------------------------------
# HELPER — Build a text summary of the DataFrame
# -----------------------------------------------

def build_data_summary(df: pd.DataFrame) -> str:
    lines = []
    lines.append(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    lines.append(f"Column names: {list(df.columns)}")
    lines.append(f"\nData types:\n{df.dtypes.to_string()}")

    numeric_cols = df.select_dtypes(include="number")
    if not numeric_cols.empty:
        lines.append(f"\nNumeric summary:\n{numeric_cols.describe().to_string()}")

    lines.append(f"\nFirst 5 rows:\n{df.head().to_string()}")

    return "\n".join(lines)