from flask import Flask
import os

from app.routes.dashboard_routes import dashboard_bp
from app.services.etl_service import run_etl

app = Flask(__name__)

app.register_blueprint(dashboard_bp)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/analytics_db"
)

app.config['SECRET_KEY'] = 'dhanush_secret_2026'


@app.route("/")
def home():
    return "WORKING 🚀"


@app.route("/run-etl")
def trigger_etl():
    try:
        run_etl()
        return "ETL DONE"

    except Exception as e:
        import traceback
        return f"<pre>{traceback.format_exc()}</pre>"