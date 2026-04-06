import pandas as pd
import os

def run_etl(file_path: str, user_id="default"):
    """Load, clean, and save dataset for a given user."""

    # ── Load ──────────────────────────────────────────────────────────────────
    if file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path, encoding="latin1")

    # ── Clean ─────────────────────────────────────────────────────────────────
    # Strip currency / comma characters then try numeric conversion
    for col in df.columns:
        if df[col].dtype == object:
            cleaned = df[col].astype(str).str.replace(r'[\$,]', '', regex=True).str.strip()
            converted = pd.to_numeric(cleaned, errors='coerce')
            # Only replace column if most values converted successfully (>50 %)
            if converted.notna().mean() > 0.5:
                df[col] = converted
            else:
                df[col] = cleaned   # keep as clean string

    df.drop_duplicates(inplace=True)
    df.fillna(0, inplace=True)

    # ── Save ──────────────────────────────────────────────────────────────────
    os.makedirs("outputs", exist_ok=True)
    out_path = os.path.join("outputs", f"cleaned_data_{user_id}.csv")
    df.to_csv(out_path, index=False)
    print(f"[ETL] Saved cleaned data → {out_path}  ({len(df)} rows, {len(df.columns)} cols)")