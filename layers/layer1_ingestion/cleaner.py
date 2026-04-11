import os
import json
import re
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")


# ─────────────────────────────────────────────
# STEP 1 — Build a safe summary of the DataFrame
# (We never send raw data to Gemini, only metadata)
# ─────────────────────────────────────────────

def build_dataframe_profile(df: pd.DataFrame) -> dict:
    """
    Creates a lightweight profile of the DataFrame.
    This is what we send to Gemini — NOT the raw rows.
    """
    profile = {
        "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "columns": []
    }

    for col in df.columns:
        series = df[col]
        col_info = {
            "name": col,
            "dtype": str(series.dtype),
            "null_count": int(series.isnull().sum()),
            "null_percent": round(series.isnull().mean() * 100, 1),
            "unique_count": int(series.nunique()),
            "sample_values": []
        }

        # Grab up to 5 non-null sample values as strings
        samples = series.dropna().head(5).tolist()
        col_info["sample_values"] = [str(v) for v in samples]

        # Extra stats for numeric columns
        if pd.api.types.is_numeric_dtype(series):
            col_info["min"] = float(series.min()) if not series.isnull().all() else None
            col_info["max"] = float(series.max()) if not series.isnull().all() else None
            col_info["mean"] = round(float(series.mean()), 2) if not series.isnull().all() else None

        profile["columns"].append(col_info)

    return profile


# ─────────────────────────────────────────────
# STEP 2 — Ask Gemini to detect issues
# ─────────────────────────────────────────────

def detect_issues_with_gemini(profile: dict) -> list[dict]:
    """
    Sends the DataFrame profile to Gemini and gets back a list of
    detected data quality issues with suggested fixes.
    """

    prompt = f"""
You are a data quality expert. Analyze this dataset profile and identify data quality issues.

Dataset profile (JSON):
{json.dumps(profile, indent=2)}

Your job:
1. Look at each column's name, dtype, null count, unique count, and sample values.
2. Identify real problems — don't make up issues that aren't there.
3. For each real issue found, return a JSON fix instruction.

Types of issues to look for:
- Columns with a name like "Unnamed: 0" or "Column1" or just a number (meaningless names)
- Columns where null_percent is above 80% (mostly empty — consider dropping)
- Columns whose dtype is "object" but sample values look like numbers or dates
- Column names with spaces, special characters, or mixed case (should be snake_case)
- Columns with only 1 unique value (useless constant columns)

Return ONLY a JSON array of fix objects. No explanation, no markdown, no code blocks.
Each fix object must have exactly these fields:
{{
  "column": "original column name",
  "issue": "short description of the problem",
  "fix_type": one of ["rename", "drop", "convert_to_numeric", "convert_to_datetime", "fill_nulls"],
  "fix_value": "the new name if renaming, or null for other types"
}}

If there are no issues, return an empty array: []

JSON array:
"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Strip markdown code fences if Gemini accidentally adds them
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    try:
        issues = json.loads(raw)
        if not isinstance(issues, list):
            return []
        return issues
    except json.JSONDecodeError:
        # If Gemini returns something unparseable, return empty — don't crash
        return []


# ─────────────────────────────────────────────
# STEP 3 — Apply the fixes to the DataFrame
# ─────────────────────────────────────────────

def apply_fixes(df: pd.DataFrame, fixes: list[dict]) -> tuple[pd.DataFrame, list[str]]:
    """
    Applies each fix instruction to the DataFrame.
    Returns the cleaned DataFrame and a human-readable log of what was done.
    """
    df = df.copy()
    log = []

    for fix in fixes:
        col = fix.get("column")
        fix_type = fix.get("fix_type")
        fix_value = fix.get("fix_value")
        issue = fix.get("issue", "")

        # Safety check — skip if column doesn't exist
        if col not in df.columns:
            continue

        try:
            if fix_type == "rename" and fix_value:
                df.rename(columns={col: fix_value}, inplace=True)
                log.append(f"✅ Renamed column '{col}' → '{fix_value}' ({issue})")

            elif fix_type == "drop":
                df.drop(columns=[col], inplace=True)
                log.append(f"🗑️ Dropped column '{col}' ({issue})")

            elif fix_type == "convert_to_numeric":
                df[col] = pd.to_numeric(df[col], errors="coerce")
                log.append(f"🔢 Converted '{col}' to numeric ({issue})")

            elif fix_type == "convert_to_datetime":
                df[col] = pd.to_datetime(df[col], errors="coerce")
                log.append(f"📅 Converted '{col}' to datetime ({issue})")

            elif fix_type == "fill_nulls":
                if pd.api.types.is_numeric_dtype(df[col]):
                    fill_val = df[col].median()
                    df[col].fillna(fill_val, inplace=True)
                    log.append(f"🔧 Filled nulls in '{col}' with median {round(fill_val, 2)} ({issue})")
                else:
                    df[col].fillna("Unknown", inplace=True)
                    log.append(f"🔧 Filled nulls in '{col}' with 'Unknown' ({issue})")

        except Exception as e:
            log.append(f"⚠️ Could not fix '{col}': {str(e)}")

    return df, log


# ─────────────────────────────────────────────
# STEP 4 — Always-on basic cleaning
# (runs regardless of Gemini, fast and safe)
# ─────────────────────────────────────────────

def basic_clean(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Fast, rule-based cleaning that always runs.
    No AI needed. Handles the obvious stuff.
    """
    df = df.copy()
    log = []
    original_cols = list(df.columns)

    # 1. Strip whitespace from all string values
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].str.strip()

    # 2. Clean column names: lowercase, replace spaces/special chars with underscore
    new_cols = []
    for col in df.columns:
        clean = str(col).strip().lower()
        clean = re.sub(r"[^a-z0-9]+", "_", clean)  # replace non-alphanumeric with _
        clean = re.sub(r"_+", "_", clean)            # collapse multiple underscores
        clean = clean.strip("_")                      # remove leading/trailing underscores
        if not clean:
            clean = f"column_{len(new_cols)}"
        new_cols.append(clean)

    # Only log if something actually changed
    renamed = {o: n for o, n in zip(original_cols, new_cols) if o != n}
    if renamed:
        df.columns = new_cols
        for old, new in renamed.items():
            log.append(f"✅ Cleaned column name: '{old}' → '{new}'")
    else:
        df.columns = new_cols

    # 3. Drop fully empty rows
    before = len(df)
    df.dropna(how="all", inplace=True)
    after = len(df)
    if before != after:
        log.append(f"🗑️ Dropped {before - after} fully empty row(s)")

    # 4. Drop fully duplicate rows
    before = len(df)
    df.drop_duplicates(inplace=True)
    after = len(df)
    if before != after:
        log.append(f"🗑️ Removed {before - after} duplicate row(s)")

    # 5. Reset index cleanly
    df.reset_index(drop=True, inplace=True)

    return df, log


# ─────────────────────────────────────────────
# MAIN FUNCTION — call this from your upload route
# ─────────────────────────────────────────────

def clean_dataframe(df: pd.DataFrame, use_ai: bool = True) -> dict:
    """
    Full cleaning pipeline. Call this after ingestion, before saving to DB.

    Parameters:
        df         — the raw DataFrame from ingestion.py
        use_ai     — set False to skip Gemini (faster, for testing)

    Returns a dict with:
        "dataframe"   — the cleaned DataFrame
        "log"         — list of strings describing every change made
        "issues"      — raw list of issues Gemini detected (for display in frontend)
        "ai_used"     — bool, whether Gemini was called
    """
    full_log = []
    ai_issues = []

    # Stage 1: Basic rule-based cleaning (always runs)
    df, basic_log = basic_clean(df)
    full_log.extend(basic_log)

    # Stage 2: AI-powered cleaning (runs if use_ai=True)
    if use_ai:
        try:
            profile = build_dataframe_profile(df)
            ai_issues = detect_issues_with_gemini(profile)

            if ai_issues:
                df, ai_log = apply_fixes(df, ai_issues)
                full_log.extend(ai_log)
            else:
                full_log.append("🤖 AI scan complete — no additional issues found.")

        except Exception as e:
            # If Gemini fails for any reason, don't crash the upload
            full_log.append(f"⚠️ AI cleaning skipped (Gemini error): {str(e)}")

    return {
        "dataframe": df,
        "log": full_log,
        "issues": ai_issues,
        "ai_used": use_ai
    }