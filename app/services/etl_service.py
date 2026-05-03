import pandas as pd
import os
from sqlalchemy import create_engine


def run_etl(file_path: str, user_id="default"):

    """
    Load, clean, process and save dataset
    for a specific user.
    """

    # ---------------------------------------------------
    # LOAD DATA
    # ---------------------------------------------------

    if file_path.endswith(".xlsx"):

        df = pd.read_excel(file_path)

    else:

        df = pd.read_csv(
            file_path,
            encoding="latin1"
        )

    # ---------------------------------------------------
    # MAKE DUPLICATE COLUMN NAMES UNIQUE
    # ---------------------------------------------------

    cols = []
    counts = {}

    for col in df.columns:

        if col in counts:

            counts[col] += 1
            cols.append(f"{col}_{counts[col]}")

        else:

            counts[col] = 0
            cols.append(col)

    df.columns = cols

    # ---------------------------------------------------
    # DATA QUALITY METRICS
    # ---------------------------------------------------

    original_rows = len(df)

    duplicate_count = df.duplicated().sum()

    missing_before = df.isnull().sum().sum()

    # ---------------------------------------------------
    # CLEANING
    # ---------------------------------------------------

    for col in df.columns:

        if df[col].dtype == object:

            cleaned = (
                df[col]
                .astype(str)
                .str.replace(r'[\$,]', '', regex=True)
                .str.strip()
            )

            converted = pd.to_numeric(
                cleaned,
                errors='coerce'
            )

            # Convert only if majority numeric
            if converted.notna().mean() > 0.5:

                df[col] = converted

            else:

                df[col] = cleaned

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    # Fill missing values
    for col in df.columns:

        if df[col].dtype == object:

            df[col] = df[col].fillna("Unknown")

        else:

            df[col] = df[col].fillna(0)

    missing_after = df.isnull().sum().sum()

    final_rows = len(df)

    # ---------------------------------------------------
    # QUALITY REPORT
    # ---------------------------------------------------

    quality_report = {

        "original_rows": int(original_rows),

        "duplicate_count": int(duplicate_count),

        "missing_before": int(missing_before),

        "missing_after": int(missing_after),

        "final_rows": int(final_rows)

    }

    # ---------------------------------------------------
    # SAVE DATA TO POSTGRESQL
    # ---------------------------------------------------

    database_url = os.getenv(
        "SQLALCHEMY_DATABASE_URI"
    )

    if database_url:

        engine = create_engine(database_url)

        df.to_sql(
            "cleaned_data",
            engine,
            if_exists="replace",
            index=False
        )

        print("[ETL] Data saved to PostgreSQL")

    # ---------------------------------------------------
    # SAVE CLEANED CSV
    # ---------------------------------------------------

    os.makedirs("outputs", exist_ok=True)

    output_path = os.path.join(
        "outputs",
        f"cleaned_data_{user_id}.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"[ETL] Saved cleaned data → {output_path}"
    )

    print(
        f"[ETL] Rows: {len(df)} | Columns: {len(df.columns)}"
    )

    # ---------------------------------------------------
    # RETURN
    # ---------------------------------------------------

    return output_path, quality_report