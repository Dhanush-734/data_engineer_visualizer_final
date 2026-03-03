import pandas as pd
import os

def run_etl(file_path):

    if file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    elif file_path.endswith(".csv"):
        try:
            df = pd.read_csv(file_path)
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="latin1")
    else:
        raise ValueError("Unsupported file format")

    original_rows = df.shape[0]

    # 🔥 Clean generically (no hardcoded column names)
    df = df.dropna()
    df = df.drop_duplicates()

    cleaned_rows = df.shape[0]

    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", "cleaned_data.csv")
    df.to_csv(output_path, index=False)

    preview_data = df.head(5).to_dict(orient="records")
    missing_values = int(df.isnull().sum().sum())

    return {
        "original_rows": original_rows,
        "cleaned_rows": cleaned_rows,
        "columns": list(df.columns),
        "preview": preview_data,
        "missing_values": missing_values
    }