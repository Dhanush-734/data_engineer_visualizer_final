import requests
import psycopg2

API_KEY = "537d1e934a062c4e8001326d07df9566"


cities = [

    # Karnataka Cities

    "Bengaluru",
    "Mysuru",
    "Mangaluru",
    "Hubli",
    "Belagavi",
    "Shivamogga",
    "Udupi",
    "Davanagere",
    "Ballari",
    "Tumakuru",

    # Major Indian Metro Cities

    "Mumbai",
    "Delhi",
    "Chennai",
    "Hyderabad",
    "Kolkata"

]


def run_etl():

    conn = psycopg2.connect(
        host="db",
        database="analytics_db",
        user="postgres",
        password="postgres"
    )

    cur = conn.cursor()

    for city in cities:

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

        response = requests.get(url)
        data = response.json()

        print(data)

        if 'main' not in data:
            print(f"ERROR FOR CITY: {city}")
            continue

        temp = data['main']['temp']
        humidity = data['main']['humidity']

        cur.execute(
            """
            INSERT INTO weather (city, temp, humidity)
            VALUES (%s, %s, %s)
            """,
            (city, temp, humidity)
        )

    conn.commit()

    cur.close()
    conn.close()

    print("MULTI CITY ETL DONE")