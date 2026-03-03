from flask import Flask, render_template, request, redirect, send_file
import os
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
STATIC_FOLDER = "static"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- UPLOAD ----------------
@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["file"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Detect file type
    if file.filename.endswith(".csv"):
        df = pd.read_csv(
            filepath,
            encoding="ISO-8859-1",
            on_bad_lines="skip"
        )

    elif file.filename.endswith(".xlsx"):
        df = pd.read_excel(filepath)

    else:
        return "Unsupported file type. Please upload CSV or Excel."

    df.drop_duplicates(inplace=True)
    df.fillna("", inplace=True)

    output_path = os.path.join(OUTPUT_FOLDER, "cleaned_data.csv")
    df.to_csv(output_path, index=False)

    return redirect("/dashboard")
# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    filepath = os.path.join(OUTPUT_FOLDER, "cleaned_data.csv")

    if not os.path.exists(filepath):
        return redirect("/")

    df = pd.read_csv(filepath)

    columns = df.columns.tolist()
    preview = df.head(5).to_dict(orient="records")
    numeric_columns = df.select_dtypes(include="number").columns.tolist()

    chart_exists = os.path.exists(os.path.join(STATIC_FOLDER, "chart.png"))

    return render_template(
        "dashboard.html",
        columns=columns,
        preview=preview,
        numeric_columns=numeric_columns,
        chart=chart_exists
    )


# ---------------- GENERATE CHART ----------------
@app.route("/generate_chart", methods=["POST"])
def generate_chart():

    filepath = os.path.join(OUTPUT_FOLDER, "cleaned_data.csv")
    df = pd.read_csv(filepath)

    x_col = request.form["x_column"]
    y_col = request.form["y_column"]
    chart_type = request.form["chart_type"]

    # Convert Y column to numeric safely
    df[y_col] = pd.to_numeric(df[y_col], errors="coerce")

    plt.figure()

    if chart_type == "bar":
        plt.bar(df[x_col], df[y_col])
    else:
        plt.plot(df[x_col], df[y_col])

    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(f"{y_col} vs {x_col}")
    plt.xticks(rotation=45)
    plt.tight_layout()

    chart_path = os.path.join(STATIC_FOLDER, "chart.png")
    plt.savefig(chart_path)
    plt.close()

    return redirect("/dashboard")


# ---------------- DOWNLOAD ----------------
@app.route("/download")
def download():
    filepath = os.path.join(OUTPUT_FOLDER, "cleaned_data.csv")
    return send_file(filepath, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)