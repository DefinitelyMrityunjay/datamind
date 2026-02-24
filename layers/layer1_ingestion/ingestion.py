import pandas as pd
import pdfplumber
import pytesseract
from PIL import Image
import easyocr
import os
import re

# -----------------------------------------------
# MAIN FUNCTION — Entry point for all file types
# -----------------------------------------------

def ingest_file(file_path: str) -> pd.DataFrame:
    """
    Accepts any file path and returns a clean Pandas DataFrame.
    Supports: CSV, Excel, PDF, Image (PNG/JPG)
    """
    extension = get_extension(file_path)

    if extension == "csv":
        return ingest_csv(file_path)
    
    elif extension in ["xlsx", "xls"]:
        return ingest_excel(file_path)
    
    elif extension == "pdf":
        return ingest_pdf(file_path)
    
    elif extension in ["png", "jpg", "jpeg"]:
        return ingest_image(file_path)
    
    else:
        raise ValueError(f"Unsupported file type: {extension}")


# -----------------------------------------------
# HELPER — Get file extension
# -----------------------------------------------

def get_extension(file_path: str) -> str:
    return file_path.rsplit(".", 1)[-1].lower()


# -----------------------------------------------
# LAYER 1A — CSV Ingestion
# -----------------------------------------------

def ingest_csv(file_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path)
        df = clean_dataframe(df)
        print(f"[CSV] Loaded {df.shape[0]} rows x {df.shape[1]} columns")
        return df
    except Exception as e:
        raise RuntimeError(f"CSV ingestion failed: {e}")


# -----------------------------------------------
# LAYER 1B — Excel Ingestion
# -----------------------------------------------

def ingest_excel(file_path: str) -> pd.DataFrame:
    try:
        # Read first sheet by default
        df = pd.read_excel(file_path, sheet_name=0)
        df = clean_dataframe(df)
        print(f"[Excel] Loaded {df.shape[0]} rows x {df.shape[1]} columns")
        return df
    except Exception as e:
        raise RuntimeError(f"Excel ingestion failed: {e}")


# -----------------------------------------------
# LAYER 1C — PDF Ingestion
# -----------------------------------------------

def ingest_pdf(file_path: str) -> pd.DataFrame:
    """
    Extracts tables from PDF using pdfplumber.
    Falls back to text extraction if no tables found.
    """
    try:
        all_tables = []

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                
                if tables:
                    for table in tables:
                        # First row becomes headers
                        headers = table[0]
                        rows = table[1:]
                        df = pd.DataFrame(rows, columns=headers)
                        all_tables.append(df)
                        print(f"[PDF] Table found on page {page_num + 1}")

        if all_tables:
            combined = pd.concat(all_tables, ignore_index=True)
            return clean_dataframe(combined)
        else:
            raise RuntimeError("No tables found in PDF. Try uploading as an image.")

    except Exception as e:
        raise RuntimeError(f"PDF ingestion failed: {e}")


# -----------------------------------------------
# LAYER 1D — Image Ingestion (OCR)
# -----------------------------------------------

def ingest_image(file_path: str) -> pd.DataFrame:
    """
    Uses EasyOCR to extract text from image,
    then attempts to parse it into a DataFrame.
    """
    try:
        reader = easyocr.Reader(['en'], gpu=False)
        results = reader.readtext(file_path, detail=0)  # detail=0 = text only
        
        # Join all detected text
        raw_text = "\n".join(results)
        print(f"[Image OCR] Extracted text:\n{raw_text}\n")

        # Parse the text into a table structure
        df = parse_text_to_dataframe(raw_text)
        return clean_dataframe(df)

    except Exception as e:
        raise RuntimeError(f"Image ingestion failed: {e}")


# -----------------------------------------------
# PARSER — Convert raw OCR text → DataFrame
# -----------------------------------------------

def parse_text_to_dataframe(raw_text: str) -> pd.DataFrame:
    """
    Tries to parse raw OCR text into a structured DataFrame.
    Assumes first line = headers, remaining lines = rows.
    """
    lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip()]

    if len(lines) < 2:
        raise RuntimeError("Not enough data extracted from image to form a table.")

    # Split each line by common delimiters
    def split_line(line):
        # Try tab, pipe, comma, or multiple spaces
        for delimiter in ["\t", "|", ","]:
            if delimiter in line:
                return [cell.strip() for cell in line.split(delimiter)]
        # fallback: split by 2+ spaces
        return re.split(r'\s{2,}', line)

    headers = split_line(lines[0])
    rows = [split_line(line) for line in lines[1:]]

    # Normalize row lengths
    num_cols = len(headers)
    normalized_rows = []
    for row in rows:
        if len(row) == num_cols:
            normalized_rows.append(row)
        elif len(row) < num_cols:
            # Pad short rows
            normalized_rows.append(row + [""] * (num_cols - len(row)))
        else:
            # Trim long rows
            normalized_rows.append(row[:num_cols])

    df = pd.DataFrame(normalized_rows, columns=headers)
    return df


# -----------------------------------------------
# CLEANER — Standardize any DataFrame
# -----------------------------------------------

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes a DataFrame:
    - Strips whitespace from column names
    - Lowercases column names
    - Replaces spaces in column names with underscores
    - Drops fully empty rows and columns
    - Strips whitespace from string values
    """
    # Clean column names
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w]", "", regex=True)
    )

    # Drop completely empty rows and columns
    df.dropna(how="all", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)

    # Strip whitespace from string cells
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    # Reset index
    df.reset_index(drop=True, inplace=True)

    return df