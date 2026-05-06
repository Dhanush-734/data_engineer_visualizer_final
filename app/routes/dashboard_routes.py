from flask import Blueprint, render_template
import psycopg2
import pandas as pd
import plotly.express as px

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)

@dashboard_bp.route("/dashboard")
def dashboard():

    conn = psycopg2.connect(
        host="db",
        database="analytics_db",
        user="postgres",
        password="postgres"
    )

    query = "SELECT * FROM weather"

    df = pd.read_sql(query, conn)

    conn.close()

    # KPI VALUES

    avg_temp = round(df["temp"].mean(), 2)

    avg_humidity = round(df["humidity"].mean(), 2)

    total_cities = df["city"].nunique()

    last_updated = (
    df["created_at"]
    .max()
    .tz_localize("UTC")
    .tz_convert("Asia/Kolkata")
    .strftime("%d-%m-%Y %I:%M:%S %p")
)
    # CHART 1 → TEMPERATURE BAR

    fig1 = px.bar(
        df,
        x="city",
        y="temp",
        title="🌡 Temperature By City",
        color="temp"
    )

    temp_chart = fig1.to_html(full_html=False)

    # CHART 2 → HUMIDITY BAR

    fig2 = px.bar(
        df,
        x="city",
        y="humidity",
        title="💧 Humidity By City",
        color="humidity"
    )

    humidity_chart = fig2.to_html(full_html=False)

    # CHART 3 → LINE TREND

    fig3 = px.line(
        df,
        x="city",
        y="temp",
        markers=True,
        title="📈 Temperature Trend"
    )

    trend_chart = fig3.to_html(full_html=False)

    # CHART 4 → SCATTER

    fig4 = px.scatter(
        df,
        x="temp",
        y="humidity",
        color="city",
        size="humidity",
        title="🌍 Temp vs Humidity"
    )

    scatter_chart = fig4.to_html(full_html=False)

    weather_data = df.to_dict(orient="records")

    return render_template(
        "dashboard.html",

        avg_temp=avg_temp,
        avg_humidity=avg_humidity,
        total_cities=total_cities,
        last_updated=last_updated,

        temp_chart=temp_chart,
        humidity_chart=humidity_chart,
        trend_chart=trend_chart,
        scatter_chart=scatter_chart,

        weather_data=weather_data
    )