# 🚀 Analytics Studio — Data Engineering Dashboard

## 📌 Project Overview

Analytics Studio is a full-stack Data Engineering and Analytics Dashboard project built using Flask, PostgreSQL, Docker, Pandas, Plotly, and Machine Learning.

The project allows users to:

* Register/Login securely
* Upload CSV or Excel datasets
* Run ETL pipelines
* Clean and process datasets
* Generate interactive charts
* Download cleaned CSV files
* Generate PDF analytics reports
* View AI insights and predictions
* Store data using PostgreSQL
* Run the entire application using Docker containers

---

# 🛠️ Tech Stack

## Backend

* Python
* Flask
* Flask-Login
* Flask-SQLAlchemy

## Database

* PostgreSQL
* SQLAlchemy ORM

## Data Engineering

* Pandas
* NumPy
* ETL Pipeline

## Data Visualization

* Plotly

## Machine Learning

* Scikit-learn
* Linear Regression

## Reports

* ReportLab PDF Generation

## DevOps

* Docker
* Docker Compose

---

# 📂 Project Structure

```bash
DATA-STREAM-PROJECT/
│
├── app/
│   ├── models/
│   │   ├── user_model.py
│   │   └── upload_model.py
│   │
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── dashboard_routes.py
│   │   └── api_routes.py
│   │
│   ├── services/
│   │   └── etl_service.py
│   │
│   └── utils/
│
├── static/
├── templates/
│   ├── dashboard.html
│   ├── login.html
│   ├── register.html
│   ├── upload.html
│   └── profile.html
│
├── uploads/
├── outputs/
├── tests/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── config.py
├── app.py
└── README.md
```

---

# ⚙️ Features

## 🔐 Authentication System

* User Registration
* User Login
* Password Hashing
* Session Management
* Protected Routes

---

## 📤 File Upload System

Supports:

* CSV files
* Excel files (.xlsx)

Uploaded datasets are processed automatically.

---

# 🔄 ETL Pipeline

The ETL pipeline performs:

## Extract

* Reads CSV and Excel datasets

## Transform

* Cleans column names
* Removes duplicate rows
* Handles missing values
* Converts numeric columns
* Removes symbols like `$` and commas

## Load

* Saves cleaned data to:

  * PostgreSQL
  * Output CSV files

---

# 📊 Dashboard Features

## KPI Metrics

* Total Rows
* Total Columns
* Missing Values
* Numeric Columns
* Categorical Columns

---

## 📈 Interactive Charts

Supports:

* Bar Charts
* Line Charts
* Scatter Plots
* Area Charts

Built using Plotly.

---

# 🤖 Machine Learning

Implemented:

* Linear Regression Prediction

The dashboard predicts future numeric values from uploaded datasets.

---

# 📄 PDF Report Generation

Users can:

* Download analytics reports
* Export cleaned data summaries
* View dataset previews

PDF reports are generated using ReportLab.

---

# 🐳 Docker Setup

The project is fully containerized using:

* Docker
* Docker Compose

Containers:

1. Flask Application Container
2. PostgreSQL Database Container

---

# 🧱 Architecture

```text
User Uploads Dataset
        ↓
Flask Backend
        ↓
ETL Pipeline
        ↓
Data Cleaning
        ↓
PostgreSQL Storage
        ↓
Analytics Dashboard
        ↓
Charts + ML + Reports
```

---

# ▶️ How To Run The Project

## 1️⃣ Clone Repository

```bash
git clone <your-github-url>
cd data-stream-project
```

---

# 2️⃣ Create Virtual Environment

```bash
python -m venv .venv
```

Activate:

## Windows

```bash
.venv\Scripts\activate
```

---

# 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 4️⃣ Run Using Docker

```bash
docker compose up --build
```

---

# 5️⃣ Open Application

```text
http://127.0.0.1:5000
```

---

# 🗄️ Database

Database used:

```text
PostgreSQL
```

Managed using:

```text
SQLAlchemy ORM
```

---

# 📦 Future Upgrades

Planned upgrades:

* REST APIs
* Apache Airflow Integration
* AWS Deployment
* Snowflake Integration
* dbt Transformation Layer
* Real-Time Streaming Data
* Kafka Integration
* CI/CD Pipelines
* Kubernetes Deployment
* Advanced ML Forecasting

---

# 🧠 Skills Demonstrated

## Backend Development

* Flask
* Authentication
* API Structure
* Routing
* Session Management

## Data Engineering

* ETL Pipelines
* Data Cleaning
* PostgreSQL
* Data Processing

## DevOps

* Docker
* Docker Compose
* Containerization

## Data Analytics

* Plotly Dashboards
* Reporting
* KPI Metrics
* Machine Learning

---

# 👨‍💻 Author

Dhanush S

Aspiring Data Engineer focused on:

* Python
* SQL
* Data Engineering
* Cloud Technologies
* Backend Development
* ETL Pipelines

---

# ⭐ Project Status

Current Version:

```text
Analytics Studio v2
```

Status:

```text
Actively Developing
```
