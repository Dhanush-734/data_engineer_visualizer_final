import os
import time
import pandas as pd
import numpy as np
from flask import Blueprint
import plotly.express as px
from flask import session
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    session
)

from flask_login import (
    login_required,
    current_user
)

from sqlalchemy import text

from sklearn.linear_model import LinearRegression

from app import db

from app.models.upload_model import UploadHistory

from app.services.etl_service import run_etl
dashboard_bp = Blueprint(
    "dashboard",
    __name__
)
from config import (
    UPLOAD_FOLDER,
    OUTPUT_FOLDER
)
@dashboard_bp.route("/upload", methods=["POST"])
@login_required
def upload():

    file = request.files.get("file")

    if not file or file.filename == "":
        return redirect(
            url_for("dashboard.upload_page")
        )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        f"user_{current_user.id}_{file.filename}"
    )

    file.save(file_path)

    # ---------------- RUN ETL ----------------

    output_path, quality_report = run_etl(
        file_path,
        user_id=current_user.id
    )

    # ---------------- SAVE HISTORY ----------------

    history = UploadHistory(
        filename=file.filename,
        rows_processed=quality_report["final_rows"],
        user_id=current_user.id
    )

    db.session.add(history)

    db.session.commit()

    # ---------------- SAVE QUALITY REPORT ----------------

    session["quality_report"] = quality_report

    return redirect(
        url_for("dashboard.dashboard")
    )

# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------

# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():

    cleaned_path = os.path.join(
        OUTPUT_FOLDER,
        f"cleaned_data_{current_user.id}.csv"
    )

    # ---------------------------------------------------
    # IF CSV DOES NOT EXIST
    # ---------------------------------------------------

    if not os.path.exists(cleaned_path):

        return redirect(
            url_for("dashboard.upload_page")
        )

    # ---------------------------------------------------
    # LOAD DATA
    # ---------------------------------------------------

    df = pd.read_csv(cleaned_path)

    # ---------------------------------------------------
    # DATE COLUMNS
    # ---------------------------------------------------

    date_columns = []

    for col in df.columns:

        try:

            pd.to_datetime(df[col])

            date_columns.append(col)

        except:

            pass

    # ---------------------------------------------------
    # KPI METRICS
    # ---------------------------------------------------

    total_rows = df.shape[0]

    total_columns = df.shape[1]

    numeric_column_count = len(
        df.select_dtypes(include="number").columns
    )

    categorical_column_count = len(
        df.select_dtypes(include="object").columns
    )

    missing_values = df.isnull().sum().sum()

    # ---------------------------------------------------
    # DATA
    # ---------------------------------------------------

    columns = df.columns.tolist()

    preview = df.head(5).to_dict(
        orient="records"
    )

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        include="object"
    ).columns.tolist()

    # ---------------------------------------------------
    # QUALITY REPORT
    # ---------------------------------------------------

    quality_report = session.get(
        "quality_report"
    )

    # ---------------------------------------------------
    # LEADERBOARD
    # ---------------------------------------------------

    leaderboard_x = None

    leaderboard_y = None

    leaderboard_data = []

    if categorical_columns and numeric_columns:

        leaderboard_x = categorical_columns[0]

        leaderboard_y = numeric_columns[0]

        leaderboard_data = (
            df.groupby(
                leaderboard_x,
                as_index=False
            )[leaderboard_y]
            .sum()
            .sort_values(
                by=leaderboard_y,
                ascending=False
            )
            .head(5)
            .to_dict(orient="records")
        )

    # ---------------------------------------------------
    # RECENT UPLOADS
    # ---------------------------------------------------

    recent_uploads = UploadHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(
        UploadHistory.uploaded_at.desc()
    ).limit(5).all()

    # ---------------------------------------------------
    # AI INSIGHTS
    # ---------------------------------------------------

    insights = []

    if numeric_columns:

        metric = numeric_columns[0]

        insights.append(
            f"Average {metric}: {round(df[metric].mean(), 2)}"
        )

        insights.append(
            f"Maximum {metric}: {df[metric].max()}"
        )

        insights.append(
            f"Minimum {metric}: {df[metric].min()}"
        )

    if categorical_columns and numeric_columns:

        top_category = (
            df.groupby(categorical_columns[0])[numeric_columns[0]]
            .sum()
            .idxmax()
        )

        insights.append(
            f"Top {categorical_columns[0]}: {top_category}"
        )

    insights.append(
        f"Dataset contains {total_rows} rows"
    )

    insights.append(
        f"Missing values remaining: {missing_values}"
    )

    # ---------------------------------------------------
    # ML PREDICTION
    # ---------------------------------------------------

    prediction_text = "No prediction available"

    try:

        if numeric_columns:

            target = numeric_columns[0]

            X = np.arange(len(df)).reshape(-1, 1)

            y = df[target].fillna(0)

            model = LinearRegression()

            model.fit(X, y)

            next_value = model.predict(
                [[len(df)]]
            )[0]

            prediction_text = (
                f"Predicted next {target}: "
                f"{round(float(next_value), 2)}"
            )

    except Exception as e:

        prediction_text = (
            f"Prediction Error: {str(e)}"
        )

    # ---------------------------------------------------
    # RENDER TEMPLATE
    # ---------------------------------------------------

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

        date_columns=date_columns,

        total_rows=total_rows,

        total_columns=total_columns,

        numeric_column_count=numeric_column_count,

        categorical_column_count=categorical_column_count,

        missing_values=missing_values,

        quality_report=quality_report,

        recent_uploads=recent_uploads,

        insights=insights,

        prediction_text=prediction_text,

        prediction_message=prediction_text,

        t=int(time.time())
    )


# GENERATE CHART

@dashboard_bp.route("/generate_chart", methods=["POST"])
@login_required
def generate_chart():

    cleaned_path = os.path.join(
        OUTPUT_FOLDER,
        f"cleaned_data_{current_user.id}.csv"
    )

    # ---------------------------------------------------
    # CHECK FILE EXISTS
    # ---------------------------------------------------

    if not os.path.exists(cleaned_path):

        return redirect(
            url_for("dashboard.upload_page")
        )

    # ---------------------------------------------------
    # LOAD DATA
    # ---------------------------------------------------

    df = pd.read_csv(cleaned_path)

    # ---------------------------------------------------
    # GET FORM VALUES
    # ---------------------------------------------------

    x = request.form.get("x_column")

    y = request.form.get("y_column")

    chart_type = request.form.get(
        "chart_type",
        "bar"
    )

    # ---------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------

    if not x or not y:

        return redirect(
            url_for("dashboard.dashboard")
        )

    # ---------------------------------------------------
    # CHART DATA
    # ---------------------------------------------------

    if chart_type in ["bar", "line"]:

        chart_data = (
            df.groupby(x, as_index=False)[y]
            .sum()
            .sort_values(
                by=y,
                ascending=False
            )
            .head(10)
        )

    else:

        chart_data = (
            df[[x, y]]
            .dropna()
            .head(100)
        )

    # ---------------------------------------------------
    # CREATE CHART
    # ---------------------------------------------------

    if chart_type == "bar":

        fig = px.bar(
            chart_data,
            x=x,
            y=y,
            title=f"{y} vs {x}"
        )

    elif chart_type == "line":

        fig = px.line(
            chart_data,
            x=x,
            y=y,
            title=f"{y} Trend"
        )

    elif chart_type == "scatter":

        fig = px.scatter(
            chart_data,
            x=x,
            y=y,
            title=f"{y} vs {x}"
        )

    elif chart_type == "area":

        fig = px.area(
            chart_data,
            x=x,
            y=y,
            title=f"{y} Area Analysis"
        )

    else:

        fig = px.bar(
            chart_data,
            x=x,
            y=y
        )

    # ---------------------------------------------------
    # CHART STYLE
    # ---------------------------------------------------

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font_color="#111827"
    )

    graph_html = fig.to_html(
        full_html=False,
        config={"responsive": True}
    )

    # ---------------------------------------------------
    # KPI METRICS
    # ---------------------------------------------------

    total_rows = df.shape[0]

    total_columns = df.shape[1]

    numeric_column_count = len(
        df.select_dtypes(include="number").columns
    )

    categorical_column_count = len(
        df.select_dtypes(include="object").columns
    )

    missing_values = df.isnull().sum().sum()

    # ---------------------------------------------------
    # LEADERBOARD
    # ---------------------------------------------------

    leaderboard_data = (
        df[[x, y]]
        .dropna()
        .groupby(x, as_index=False)[y]
        .sum()
        .sort_values(
            by=y,
            ascending=False
        )
        .head(5)
        .to_dict(orient="records")
    )

    # ---------------------------------------------------
    # RECENT UPLOADS
    # ---------------------------------------------------

    recent_uploads = UploadHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(
        UploadHistory.uploaded_at.desc()
    ).limit(5).all()

    # ---------------------------------------------------
    # AI INSIGHTS
    # ---------------------------------------------------

    insights = []

    try:

        insights.append(
            f"Average {y}: "
            f"{round(df[y].mean(), 2)}"
        )

        insights.append(
            f"Maximum {y}: "
            f"{df[y].max()}"
        )

        insights.append(
            f"Minimum {y}: "
            f"{df[y].min()}"
        )

    except:

        pass

    insights.append(
        f"Dataset contains {total_rows} rows"
    )

    insights.append(
        f"Missing values remaining: {missing_values}"
    )

    # ---------------------------------------------------
    # ML PREDICTION
    # ---------------------------------------------------

    prediction_text = "No prediction available"

    try:

        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        if numeric_columns:

            target_col = numeric_columns[0]

            X = np.arange(len(df)).reshape(-1, 1)

            y_values = df[target_col].fillna(0)

            model = LinearRegression()

            model.fit(X, y_values)

            next_value = model.predict(
                [[len(df)]]
            )[0]

            prediction_text = (
                f"Predicted next {target_col}: "
                f"{round(float(next_value), 2)}"
            )

    except Exception as e:

        prediction_text = (
            f"Prediction Error: {str(e)}"
        )

    # ---------------------------------------------------
    # RENDER TEMPLATE
    # ---------------------------------------------------

    return render_template(
        "dashboard.html",

        columns=df.columns.tolist(),

        preview=df.head(5).to_dict(
            orient="records"
        ),

        numeric_columns=df.select_dtypes(
            include="number"
        ).columns.tolist(),

        graph_html=graph_html,

        username=current_user.username,

        leaderboard_x=x,

        leaderboard_y=y,

        leaderboard_data=leaderboard_data,

        total_rows=total_rows,

        total_columns=total_columns,

        numeric_column_count=numeric_column_count,

        categorical_column_count=categorical_column_count,

        missing_values=missing_values,

        insights=insights,

        quality_report=session.get(
            "quality_report"
        ),

        recent_uploads=recent_uploads,

        prediction_message=prediction_text,

        prediction_text=prediction_text,

        t=int(time.time())
    )


# ---------------------------------------------------
# DOWNLOAD CSV
# ---------------------------------------------------

@dashboard_bp.route("/download_csv")
@login_required
def download_csv():

    path = os.path.join(
        OUTPUT_FOLDER,
        f"cleaned_data_{current_user.id}.csv"
    )

    if not os.path.exists(path):

        return redirect(
            url_for("dashboard.upload_page")
        )

    return send_file(
        path,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"cleaned_data_{current_user.username}.csv"
    )


# ---------------------------------------------------
# DOWNLOAD PDF REPORT
# ---------------------------------------------------

@dashboard_bp.route("/download_report")
@login_required
def download_report():

    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle
    )

    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import letter, landscape

    cleaned_path = os.path.join(
        OUTPUT_FOLDER,
        f"cleaned_data_{current_user.id}.csv"
    )

    # ---------------------------------------------------
    # CHECK FILE EXISTS
    # ---------------------------------------------------

    if not os.path.exists(cleaned_path):

        return redirect(
            url_for("dashboard.upload_page")
        )

    # ---------------------------------------------------
    # LOAD DATA
    # ---------------------------------------------------

    df = pd.read_csv(cleaned_path)

    # ---------------------------------------------------
    # PDF PATH
    # ---------------------------------------------------

    pdf_path = os.path.join(
        "static",
        f"report_{current_user.id}.pdf"
    )

    # ---------------------------------------------------
    # CREATE DOCUMENT
    # ---------------------------------------------------

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=landscape(letter)
    )

    styles = getSampleStyleSheet()

    elements = []

    # ---------------------------------------------------
    # TITLE
    # ---------------------------------------------------

    elements.append(
        Paragraph(
            "Analytics Studio Report",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 20))

    # ---------------------------------------------------
    # USER
    # ---------------------------------------------------

    elements.append(
        Paragraph(
            f"User: {current_user.username}",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 20))

    # ---------------------------------------------------
    # KPI INFO
    # ---------------------------------------------------

    elements.append(
        Paragraph(
            f"Total Rows: {df.shape[0]}",
            styles["BodyText"]
        )
    )

    elements.append(
        Paragraph(
            f"Total Columns: {df.shape[1]}",
            styles["BodyText"]
        )
    )

    elements.append(
        Paragraph(
            f"Missing Values: {df.isnull().sum().sum()}",
            styles["BodyText"]
        )
    )

    elements.append(Spacer(1, 20))

    # ---------------------------------------------------
    # TABLE DATA
    # ---------------------------------------------------

    table_data = [df.columns.tolist()]

    for row in df.head(15).values.tolist():

        table_data.append(row)

    # ---------------------------------------------------
    # COLUMN WIDTHS
    # ---------------------------------------------------

    col_widths = []

    for col in df.columns:

        if len(col) > 10:

            col_widths.append(90)

        else:

            col_widths.append(60)

    # ---------------------------------------------------
    # CREATE TABLE
    # ---------------------------------------------------

    table = Table(
        table_data,
        colWidths=col_widths,
        repeatRows=1
    )

    # ---------------------------------------------------
    # TABLE STYLE
    # ---------------------------------------------------

    table.setStyle(
        TableStyle([

            # HEADER
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

            # FONT
            ('FONTSIZE', (0, 0), (-1, -1), 8),

            # GRID
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

            # BODY
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),

            # PADDING
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),

            # ALIGNMENT
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        ])
    )

    # ---------------------------------------------------
    # ADD TABLE
    # ---------------------------------------------------

    elements.append(table)

    elements.append(Spacer(1, 30))

    # ---------------------------------------------------
    # FOOTER
    # ---------------------------------------------------

    elements.append(
        Paragraph(
            "Generated by Analytics Studio",
            styles["Italic"]
        )
    )

    # ---------------------------------------------------
    # BUILD PDF
    # ---------------------------------------------------

    doc.build(elements)

    # ---------------------------------------------------
    # SEND FILE
    # ---------------------------------------------------

    return send_file(
        pdf_path,
        as_attachment=True
    )


# ---------------------------------------------------
# PROFILE
# ---------------------------------------------------

@dashboard_bp.route("/profile")
@login_required
def profile():

    uploads = UploadHistory.query.filter_by(
        user_id=current_user.id
    ).count()

    return render_template(
        "profile.html",
        username=current_user.username,
        uploads=uploads
    )


# ---------------------------------------------------
# UPLOAD PAGE
# ---------------------------------------------------

@dashboard_bp.route("/upload_page")
@login_required
def upload_page():

    return render_template(
        "upload.html"
    )

