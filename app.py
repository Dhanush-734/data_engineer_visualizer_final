import os
import time
import pandas as pd
import plotly.express as px

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_file
)

from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_required,
    login_user,
    logout_user,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from script.etl import run_etl


# ---------------------------------------------------
# APP CONFIG
# ---------------------------------------------------

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:devi7977%40dhanush@localhost/etl_dashboard'
app.config['SECRET_KEY'] = 'dhanush_secret_2026'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ---------------------------------------------------
# USER MODEL
# ---------------------------------------------------

class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(500),
        nullable=False
    )


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------------------------------------------------
# FOLDERS
# ---------------------------------------------------

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ---------------------------------------------------
# CREATE TABLES
# ---------------------------------------------------

with app.app_context():
    db.create_all()


# ---------------------------------------------------
# HOME
# ---------------------------------------------------

@app.route("/")
def home():
    return redirect(url_for("login"))


# ---------------------------------------------------
# REGISTER
# ---------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            return "Username already exists"

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            return redirect(url_for("upload_page"))

        return "Invalid username or password"

    return render_template("login.html")


# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))


# ---------------------------------------------------
# UPLOAD PAGE
# ---------------------------------------------------

@app.route("/upload_page")
@login_required
def upload_page():

    return render_template("upload.html")


# ---------------------------------------------------
# UPLOAD FILE
# ---------------------------------------------------

@app.route("/upload", methods=["POST"])
@login_required
def upload():

    file = request.files.get("file")

    if not file or file.filename == "":
        return redirect(url_for("upload_page"))

    file_path = os.path.join(
        UPLOAD_FOLDER,
        f"user_{current_user.id}_{file.filename}"
    )

    file.save(file_path)

    run_etl(file_path, user_id=current_user.id)

    return redirect(url_for("dashboard"))


# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------

# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():

    cleaned_path = os.path.join(
        OUTPUT_FOLDER,
        f"cleaned_data_{current_user.id}.csv"
    )

    if not os.path.exists(cleaned_path):
        return redirect(url_for("upload_page"))

    df = pd.read_csv(cleaned_path)

    columns = df.columns.tolist()

    preview = df.head(5).to_dict(orient="records")

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    # ---------------- LEADERBOARD AUTO DETECT ----------------

    leaderboard_x = None
    leaderboard_y = None
    leaderboard_data = []

    categorical_cols = df.select_dtypes(
        include="object"
    ).columns.tolist()

    numeric_cols = df.select_dtypes(
        include="number"
    ).columns.tolist()

    if categorical_cols and numeric_cols:

        leaderboard_x = categorical_cols[0]
        leaderboard_y = numeric_cols[0]

        leaderboard_data = (
            df.groupby(leaderboard_x, as_index=False)[leaderboard_y]
            .sum()
            .sort_values(by=leaderboard_y, ascending=False)
            .head(5)
            .to_dict(orient="records")
        )

    return render_template(
        "dashboard.html",
        columns=columns,
        preview=preview,
        numeric_columns=numeric_columns,
        graph_html=None,
        username=current_user.username,
        leaderboard_x=leaderboard_x,
        leaderboard_y=leaderboard_y,
        leaderboard_data=leaderboard_data,
        t=int(time.time())
    )

# ---------------------------------------------------
# GENERATE CHART
# ---------------------------------------------------

# ---------------------------------------------------
# GENERATE CHART
# ---------------------------------------------------

@app.route("/generate_chart", methods=["POST"])
@login_required
def generate_chart():

    cleaned_path = os.path.join(
        OUTPUT_FOLDER,
        f"cleaned_data_{current_user.id}.csv"
    )

    if not os.path.exists(cleaned_path):
        return redirect(url_for('upload_page'))

    df = pd.read_csv(cleaned_path)

    x = request.form["x_column"]
    y = request.form["y_column"]
    chart_type = request.form["chart_type"]

    if x not in df.columns or y not in df.columns:
        return redirect(url_for('dashboard'))

    # Prevent same column selection
    if x == y:
        return redirect(url_for('dashboard'))

    data = (
        df.groupby(x, as_index=False)[y]
        .sum()
        .sort_values(by=y, ascending=False)
        .head(10)
    )

    # ---------------- PLOTLY ----------------

    if chart_type == "bar":

        fig = px.bar(
            data,
            x=x,
            y=y,
            title=f"{y} vs {x}"
        )

    else:

        fig = px.line(
            data,
            x=x,
            y=y,
            title=f"{y} vs {x}"
        )

    graph_html = fig.to_html(full_html=False)

    # ---------------- LEADERBOARD ----------------

    leaderboard_data = (
        data.head(5)
        .to_dict(orient="records")
    )

    return render_template(
        "dashboard.html",
        columns=df.columns.tolist(),
        preview=df.head(5).to_dict(orient="records"),
        numeric_columns=df.select_dtypes(include="number").columns.tolist(),
        graph_html=graph_html,
        username=current_user.username,
        leaderboard_x=x,
        leaderboard_y=y,
        leaderboard_data=leaderboard_data,
        t=int(time.time())
    )
# ---------------------------------------------------
# DOWNLOAD CSV
# ---------------------------------------------------

@app.route("/download_csv")
@login_required
def download_csv():

    path = os.path.join(
        OUTPUT_FOLDER,
        f"cleaned_data_{current_user.id}.csv"
    )

    if not os.path.exists(path):
        return redirect(url_for("upload_page"))

    return send_file(
        path,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"cleaned_data_{current_user.username}.csv"
    )


# ---------------------------------------------------
# RUN APP
# ---------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)