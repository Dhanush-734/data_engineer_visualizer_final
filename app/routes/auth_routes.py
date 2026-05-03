from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)

from flask_login import (
    login_user,
    logout_user,
    login_required
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from app import db

from app.models.user_model import User


# ---------------------------------------------------
# BLUEPRINT
# ---------------------------------------------------

auth_bp = Blueprint(
    "auth",
    __name__
)


# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            return redirect(
                url_for("dashboard.dashboard")
            )

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")


# ---------------------------------------------------
# REGISTER
# ---------------------------------------------------

@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:

            return render_template(
                "register.html",
                error="Username already exists"
            )

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(
            url_for("auth.login")
        )

    return render_template("register.html")


# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------

@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("auth.login")
    )