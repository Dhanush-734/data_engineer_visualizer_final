import requests
import pandas as pd
from datetime import datetime
from app import db
from app.models.weather_model import WeatherData
API_KEY = "befdb494a686cd597ee2499e45e9f5db"   # use your working key


def fetch_weather(city="Chennai"):

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}"
        f"&appid={API_KEY}"
        f"&units=metric"
    )

    response = requests.get(url)
    data = response.json()

    if "main" not in data:
        return pd.DataFrame()

    weather = {
        "city": city,
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "weather": data["weather"][0]["main"],
        "timestamp": datetime.now()
    }

    # ✅ THIS MUST BE INSIDE FUNCTION
    record = WeatherData(
        city=weather["city"],
        temperature=weather["temperature"],
        humidity=weather["humidity"],
        weather=weather["weather"],
        timestamp=weather["timestamp"]
    )

    db.session.add(record)
    db.session.commit()

    return pd.DataFrame([weather])






