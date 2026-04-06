import os, time
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# ── If etl.py is inside a 'script' subfolder, keep this import.
# ── Make sure script/__init__.py exists (can be empty).
from script.etl import run_etl

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'dhanush_studio_2026'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ── Models ──────────────────────────────────────────────────────────────────
class User(db.Model, UserMixin):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)   # hashed

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))   # SQLAlchemy 2.x compatible

# ── Folders ──────────────────────────────────────────────────────────────────
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
STATIC_FOLDER = "static"
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, STATIC_FOLDER]:
    os.makedirs(folder, exist_ok=True)

with app.app_context():
    db.create_all()

# ── Routes ───────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return redirect(url_for('login'))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for('upload_page'))
        error = "Invalid username or password."
    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form["username"].strip()
        if User.query.filter_by(username=username).first():
            error = "Username already taken."
        else:
            hashed = generate_password_hash(request.form["password"])
            db.session.add(User(username=username, password=hashed))
            db.session.commit()
            return redirect(url_for('login'))
    return render_template("register.html", error=error)


@app.route("/upload_page")
@login_required
def upload_page():
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
@login_required
def upload():
    file = request.files.get("file")
    if not file or file.filename == "":
        return redirect(url_for('upload_page'))

    save_path = os.path.join(UPLOAD_FOLDER, f"user_{current_user.id}_{file.filename}")
    file.save(save_path)
    run_etl(save_path, user_id=current_user.id)
    return redirect(url_for('dashboard'))


@app.route("/dashboard")
@login_required
def dashboard():
    cleaned_path = os.path.join(OUTPUT_FOLDER, f"cleaned_data_{current_user.id}.csv")
    if not os.path.exists(cleaned_path):
        return redirect(url_for('upload_page'))

    df = pd.read_csv(cleaned_path)
    cols     = df.columns.tolist()
    num_cols = df.select_dtypes(include="number").columns.tolist()

    # Revenue leaderboard — auto-detect a categorical + numeric column
    preview = []
    leaderboard_x = None
    leaderboard_y = None

    # Priority: look for columns whose names suggest ID/category and sales/revenue/amount
    id_keywords    = ['product', 'item', 'category', 'name', 'sku', 'id']
    sales_keywords = ['sales', 'revenue', 'amount', 'total', 'price', 'profit', 'income']

    cat_cols = df.select_dtypes(exclude="number").columns.tolist()
    for kw in id_keywords:
        match = next((c for c in cat_cols if kw in c.lower()), None)
        if match:
            leaderboard_x = match
            break
    if not leaderboard_x and cat_cols:
        leaderboard_x = cat_cols[0]   # fallback: first categorical column

    for kw in sales_keywords:
        match = next((c for c in num_cols if kw in c.lower()), None)
        if match:
            leaderboard_y = match
            break
    if not leaderboard_y and num_cols:
        leaderboard_y = num_cols[0]   # fallback: first numeric column

    if leaderboard_x and leaderboard_y:
        rev_df  = df.groupby(leaderboard_x)[leaderboard_y].sum().reset_index()
        preview = rev_df.sort_values(leaderboard_y, ascending=False).head(5).to_dict(orient="records")

    chart_fn   = f"chart_{current_user.id}.png"
    chart_path = os.path.join(STATIC_FOLDER, chart_fn)

    return render_template(
        "dashboard.html",
        columns=cols,
        preview=preview,
        numeric_columns=num_cols,
        chart=os.path.exists(chart_path),
        chart_filename=chart_fn,
        t=int(time.time()),
        leaderboard_x=leaderboard_x,
        leaderboard_y=leaderboard_y,
    )


@app.route("/generate_chart", methods=["POST"])
@login_required
def generate_chart():
    cleaned_path = os.path.join(OUTPUT_FOLDER, f"cleaned_data_{current_user.id}.csv")
    if not os.path.exists(cleaned_path):
        return redirect(url_for('upload_page'))

    df     = pd.read_csv(cleaned_path)
    x      = request.form["x_column"]
    y      = request.form["y_column"]
    c_type = request.form["chart_type"]

    if x not in df.columns or y not in df.columns:
        return redirect(url_for('dashboard'))

    data = df.groupby(x)[y].sum().sort_values(ascending=False).head(10)

    plt.figure(figsize=(10, 5))
    plt.style.use('seaborn-v0_8-whitegrid')

    if c_type == "bar":
        plt.bar(data.index.astype(str), data.values, color='#6366f1', edgecolor='white')
    else:
        plt.plot(data.index.astype(str), data.values, marker='o', color='#a855f7', linewidth=2)

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(STATIC_FOLDER, f"chart_{current_user.id}.png"), dpi=150)
    plt.close()

    return redirect(url_for('dashboard'))


@app.route("/download_csv")
@login_required
def download_csv():
    path = os.path.join(OUTPUT_FOLDER, f"cleaned_data_{current_user.id}.csv")
    if not os.path.exists(path):
        return redirect(url_for("upload_page"))
    return send_file(
        path,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"cleaned_data_{current_user.username}.csv"
    )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)