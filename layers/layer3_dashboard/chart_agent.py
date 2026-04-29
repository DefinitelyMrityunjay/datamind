import os
import json
import re
import pandas as pd
from dotenv import load_dotenv

load_dotenv()



# ─────────────────────────────────────────────
# CHART TYPES your frontend supports
# Only Gemini can pick from this list
# ─────────────────────────────────────────────

SUPPORTED_CHARTS = [
    "bar",          # categorical vs numeric  (e.g. product vs sales)
    "line",         # time series or ordered  (e.g. date vs revenue)
    "scatter",      # numeric vs numeric      (e.g. age vs salary)
    "pie",          # distribution of a category (e.g. region share)
    "histogram",    # distribution of a single numeric column
    "heatmap",      # correlation between many numeric columns
    "box",          # spread/outliers of a numeric column per category
]


# ─────────────────────────────────────────────
# STEP 1 — Build a column profile for Gemini
# ─────────────────────────────────────────────

def build_column_profile(df: pd.DataFrame) -> list[dict]:
    """
    Builds a lightweight profile of each column.
    We send this to Gemini — not the raw data.
    """
    profile = []

    for col in df.columns:
        series = df[col]

        # Detect if an "object" column is actually dates
        is_datetime = False
        if series.dtype == "object":
            try:
                pd.to_datetime(series.dropna().head(5), infer_datetime_format=True)
                is_datetime = True
            except Exception:
                pass

        # Categorize dtype simply
        if is_datetime or pd.api.types.is_datetime64_any_dtype(series):
            col_type = "datetime"
        elif pd.api.types.is_numeric_dtype(series):
            col_type = "numeric"
        else:
            col_type = "categorical"

        profile.append({
            "name": col,
            "type": col_type,
            "unique_count": int(series.nunique()),
            "null_percent": round(series.isnull().mean() * 100, 1),
            "sample_values": [str(v) for v in series.dropna().head(4).tolist()]
        })

    return profile


# ─────────────────────────────────────────────
# STEP 2 — Ask Gemini which charts to show
# ─────────────────────────────────────────────

def ask_mistral_for_charts(profile: list[dict], dataset_name: str = "") -> list[dict]:
    import requests

    profile_json = json.dumps(profile, indent=2)
    supported = ", ".join(SUPPORTED_CHARTS)

    prompt = f"""
You are a data visualization expert.

Dataset name: "{dataset_name}"

Column profiles:
{profile_json}

Supported chart types: {supported}

STRICT RULES:
- Return ONLY JSON array
- No explanation
- No markdown
- 3 to 6 charts
- Follow chart rules strictly

Format:
[
  {{
    "chart_type": "...",
    "x": "...",
    "y": "...",
    "title": "...",
    "reason": "..."
  }}
]
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",   # 🔥 USING MISTRAL
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )

        response.raise_for_status()
        result = response.json()

        raw = result.get("response", "").strip()

        # Remove markdown if any
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"^```\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        raw = raw.strip()

        charts = json.loads(raw)

        if not isinstance(charts, list):
            return []

        return charts

    except Exception as e:
        print("Mistral error:", e)
        return []




# ─────────────────────────────────────────────
# STEP 3 — Validate recommendations
# Make sure columns Gemini picked actually exist
# ─────────────────────────────────────────────

def validate_recommendations(charts: list[dict], df: pd.DataFrame) -> list[dict]:
    """
    Filters out any chart recommendations where the columns
    Gemini suggested don't actually exist in the DataFrame.
    """
    valid = []
    existing_cols = set(df.columns)

    for chart in charts:
        x = chart.get("x")
        y = chart.get("y")
        chart_type = chart.get("chart_type", "")

        # Must be a supported type
        if chart_type not in SUPPORTED_CHARTS:
            continue

        # For histogram and heatmap, x/y columns are optional
        if chart_type == "heatmap":
            valid.append(chart)
            continue

        if chart_type == "histogram":
            if x and x in existing_cols:
                valid.append(chart)
            elif y and y in existing_cols:
                # Some models put the column in y — normalise to x
                chart["x"] = y
                chart["y"] = None
                valid.append(chart)
            continue

        # All other charts need at least x to exist
        if x and x not in existing_cols:
            continue
        if y and y not in existing_cols:
            continue

        valid.append(chart)

    return valid


# ─────────────────────────────────────────────
# STEP 4 — Fallback if Gemini fails or returns nothing
# ─────────────────────────────────────────────

def fallback_charts(df: pd.DataFrame) -> list[dict]:
    """
    Simple rule-based chart selection used when Gemini fails.
    Guarantees at least something useful is shown.
    """
    charts = []
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = [
        c for c in df.select_dtypes(include="object").columns
        if df[c].nunique() <= 20
    ]
    datetime_cols = df.select_dtypes(include="datetime").columns.tolist()

    # Also check object columns that look like dates
    for col in df.select_dtypes(include="object").columns:
        try:
            pd.to_datetime(df[col].dropna().head(5))
            if col not in datetime_cols:
                datetime_cols.append(col)
        except Exception:
            pass

    # Histogram for first numeric column
    if numeric_cols:
        charts.append({
            "chart_type": "histogram",
            "x": numeric_cols[0],
            "y": None,
            "title": f"Distribution of {numeric_cols[0]}",
            "reason": "Shows how values are spread across this numeric column."
        })

    # Bar chart if we have categorical + numeric
    if categorical_cols and numeric_cols:
        charts.append({
            "chart_type": "bar",
            "x": categorical_cols[0],
            "y": numeric_cols[0],
            "title": f"{numeric_cols[0]} by {categorical_cols[0]}",
            "reason": "Compares numeric values across categories."
        })

    # Line chart if datetime is present
    if datetime_cols and numeric_cols:
        charts.append({
            "chart_type": "line",
            "x": datetime_cols[0],
            "y": numeric_cols[0],
            "title": f"{numeric_cols[0]} over time",
            "reason": "Shows trend of a numeric value over time."
        })

    # Scatter if two numeric columns exist
    if len(numeric_cols) >= 2:
        charts.append({
            "chart_type": "scatter",
            "x": numeric_cols[0],
            "y": numeric_cols[1],
            "title": f"{numeric_cols[0]} vs {numeric_cols[1]}",
            "reason": "Shows relationship between two numeric values."
        })

    # Heatmap if 3+ numeric columns
    if len(numeric_cols) >= 3:
        charts.append({
            "chart_type": "heatmap",
            "x": None,
            "y": None,
            "title": "Correlation heatmap",
            "reason": "Shows how all numeric columns relate to each other."
        })

    return charts


# ─────────────────────────────────────────────
# MAIN FUNCTION — call this from your dashboard route
# ─────────────────────────────────────────────

def select_charts(df: pd.DataFrame, dataset_name: str = "", use_ai: bool = True) -> dict:
    """
    Main entry point. Call this from your dashboard backend route.

    Parameters:
        df           — the cleaned DataFrame (from Layer 1 + Layer 2)
        dataset_name — optional, used to give Gemini context
        use_ai       — set False to skip Gemini and use fallback only

    Returns:
        {
          "charts":     list of chart recommendation dicts,
          "ai_used":    bool,
          "fallback":   bool (True if Gemini failed and fallback was used),
          "profile":    the column profile that was analysed
        }
    """
    profile = build_column_profile(df)

    if use_ai:
        try:
            raw_charts = ask_mistral_for_charts(profile, dataset_name)
            validated = validate_recommendations(raw_charts, df)

            # If Gemini gave us something usable, return it
            if validated:
                return {
                    "charts": validated,
                    "ai_used": True,
                    "fallback": False,
                    "profile": profile
                }

        except Exception:
            pass  # Fall through to fallback below

    # Fallback — rule-based, always works
    fallback = fallback_charts(df)
    return {
        "charts": fallback,
        "ai_used": False,
        "fallback": True,
        "profile": profile
    }