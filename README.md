# 🌦️ Weather Analytics Dashboard

A Real-Time Weather Analytics Data Engineering Project built using Flask, PostgreSQL, Docker, ETL Pipelines, and Plotly Dashboards.

---

# 🚀 Project Overview

This project collects real-time weather data from the OpenWeather API, processes it through an ETL pipeline, stores it in PostgreSQL, and visualizes it in an interactive analytics dashboard.

The system demonstrates a complete end-to-end Data Engineering workflow:

```text id="7e3t2x"
API → ETL Pipeline → PostgreSQL → Dashboard Visualization
```

---

# ⚙️ Tech Stack

## Backend

* Python
* Flask

## Database

* PostgreSQL

## Data Engineering

* ETL Pipeline
* API Integration
* Docker

## Data Visualization

* Plotly
* Pandas

## Deployment/Tools

* Docker Compose
* GitHub
* VS Code

---

# 📊 Features

✅ Real-time weather data collection
✅ ETL pipeline automation
✅ PostgreSQL data storage
✅ Interactive analytics dashboard
✅ KPI Cards
✅ Temperature analysis
✅ Humidity analysis
✅ Scatter plots & bar charts
✅ Historical weather logs
✅ Auto-refresh dashboard
✅ Multi-city analytics
✅ Karnataka + Indian city tracking
✅ Dockerized application

---

# 🏗️ Project Architecture

```text id="6b1j7f"
OpenWeather API
        ↓
ETL Pipeline
        ↓
PostgreSQL Database
        ↓
Flask Backend
        ↓
Plotly Dashboard
```

---

# 📂 Project Structure

```text id="4a2q9v"
project/
│
├── app/
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── templates/
│
├── airflow/dags/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── main.py
└── README.md
```

---

# 📈 Dashboard Includes

* KPI Cards
* Temperature Comparison Chart
* Humidity Analysis
* Scatter Plot Visualization
* Historical Weather Table
* Real-Time Auto Refresh

---

# 🔄 ETL Workflow

1. Extract weather data from OpenWeather API
2. Transform JSON data into structured format
3. Load processed data into PostgreSQL
4. Display analytics through dashboard

---

# ▶️ How To Run

## Clone Repository

```bash id="v8h7dj"
git clone https://github.com/yourusername/weather-analytics-dashboard.git
```

## Start Docker

```bash id="3mq2nz"
docker compose up --build
```

## Run ETL

Open browser:

```text id="7j2m1c"
http://127.0.0.1:5000/run-etl
```

## Open Dashboard

```text id="p6x1la"
http://127.0.0.1:5000/dashboard
```

---

# 📸 Screenshots

Add your dashboard screenshots here.

---

# 🎯 Future Improvements (V2)

* Apache Kafka Streaming
* Apache Airflow Scheduling
* Snowflake Data Warehouse
* dbt Transformations
* AWS Deployment
* CI/CD Pipeline
* Streamlit Dashboard
* Forecast Prediction
* Authentication System

---

# 📚 Learning Outcomes

Through this project I learned:

* ETL Pipeline Design
* API Integration
* PostgreSQL Database Management
* Docker Containerization
* Real-Time Dashboard Development
* Data Visualization
* Backend Development
* Debugging & System Integration

---

# 👨‍💻 Author

Dhanush S

Data Engineering & Analytics Enthusiast 🚀
