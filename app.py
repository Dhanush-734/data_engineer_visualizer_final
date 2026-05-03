import os
import time
import pandas as pd
import numpy as np

from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    session
)

from flask_login import (
    LoginManager,
    login_required,
    login_user,
    logout_user,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from sqlalchemy import text

from sklearn.linear_model import LinearRegression



from app.models.user_model import User
from app.models.upload_model import UploadHistory

from app.services.etl_service import run_etl
from app.routes.auth_routes import auth_bp
from app.routes.dashboard_routes import dashboard_bp
from config import (
    UPLOAD_FOLDER,
    OUTPUT_FOLDER
)
# ---------------------------------------------------
# APP CONFIG
# ---------------------------------------------------

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/analytics_dbs"
)
app.config['SECRET_KEY'] = 'dhanush_secret_2026'

from app import db

db.init_app(app)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


# ---------------------------------------------------
# USER MODEL
# ---------------------------------------------------


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------------------------------------------------
# FOLDERS
# ---------------------------------------------------




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
    return redirect(url_for("auth.login"))





# ---------------------------------------------------

if __name__ == "__main__":
    app.run(
    host="0.0.0.0",
    port=5000,
    debug=True
)