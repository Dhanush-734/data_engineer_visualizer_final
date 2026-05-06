
from flask import (
    Blueprint,
    jsonify,
    request
)

from flask_login import (
    login_required,
    current_user
)

import os
import pandas as pd

from config import OUTPUT_FOLDER

api_bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)

# ---------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------

@api_bp.route("/health")
def health():

    return jsonify({

        "status": "success",

        "message": "API is running"

    })


# ---------------------------------------------------
# DASHBOARD SUMMARY API
# ---------------------------------------------------

@api_bp.route("/dashboard")
@login_required
def dashboard_api():

    cleaned_path = os.path.join(
        OUTPUT_FOLDER,
        f"cleaned_data_{current_user.id}.csv"
    )

    if not os.path.exists(cleaned_path):

        return jsonify({

            "status": "error",

            "message": "No dataset found"

        }), 404

    df = pd.read_csv(cleaned_path)

    return jsonify({

        "status": "success",

        "username": current_user.username,

        "total_rows": int(df.shape[0]),

        "total_columns": int(df.shape[1]),

        "missing_values": int(
            df.isnull().sum().sum()
        ),

        "columns": df.columns.tolist()

    })


# ---------------------------------------------------
# DATA PREVIEW API
# ---------------------------------------------------

@api_bp.route("/preview")
@login_required
def preview_api():

    cleaned_path = os.path.join(
        OUTPUT_FOLDER,
        f"cleaned_data_{current_user.id}.csv"
    )

    if not os.path.exists(cleaned_path):

        return jsonify({

            "status": "error",

            "message": "No dataset found"

        }), 404

    df = pd.read_csv(cleaned_path)

    preview = df.head(10).to_dict(
        orient="records"
    )

    return jsonify({

        "status": "success",

        "preview": preview

    })


# ---------------------------------------------------
# QUALITY REPORT API
# ---------------------------------------------------

@api_bp.route("/quality-report")
@login_required
def quality_report_api():

    cleaned_path = os.path.join(
        OUTPUT_FOLDER,
        f"cleaned_data_{current_user.id}.csv"
    )

    if not os.path.exists(cleaned_path):

        return jsonify({

            "status": "error",

            "message": "No dataset found"

        }), 404

    df = pd.read_csv(cleaned_path)

    return jsonify({

        "status": "success",

        "report": {

            "rows": int(df.shape[0]),

            "columns": int(df.shape[1]),

            "missing_values": int(
                df.isnull().sum().sum()
            ),

            "duplicate_rows": int(
                df.duplicated().sum()
            )

        }

    })
from app.services.weather_service import fetch_weather
from flask import jsonify

@api_bp.route("/weather", methods=["GET"])
def weather_api():

    df = fetch_weather()

    data = df.to_dict(orient="records")

    return jsonify(data)


from flask import Blueprint, jsonify
from app.services.weather_service import fetch_weather

api_bp = Blueprint("api", __name__)

@api_bp.route("/api/weather")
def get_weather():
    df = fetch_weather()
    
    return jsonify(df.to_dict(orient="records"))




