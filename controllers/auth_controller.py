from flask import Blueprint, redirect, render_template, request, session, url_for

from models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Show the registration form, or create a new account from it.
    ---
    tags:
      - AuthController
    parameters:
      - name: first_name
        in: formData
        type: string
      - name: last_name
        in: formData
        type: string
      - name: email
        in: formData
        type: string
      - name: password
        in: formData
        type: string
      - name: role
        in: formData
        type: string
        enum: [alumni, student]
      - name: graduation_year
        in: formData
        type: integer
    responses:
      200:
        description: HTML registration form
      302:
        description: Redirect to login after a successful registration, or back with an error
    """
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")
        graduation_year = request.form.get("graduation_year")

        errors = User.validate_registration(
            first_name, last_name, email, graduation_year, role, password
        )
        if errors:
            return redirect(url_for("auth.register", error=", ".join(errors)))

        user = User.register(first_name, last_name, graduation_year, email, role, password)
        if user is None:
            return redirect(url_for("auth.register", error="An account with this email already exists"))

        return redirect(url_for("index"))

    return render_template("register.html", error=request.args.get("error"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Show the login form, or sign the user in from it.
    ---
    tags:
      - AuthController
    parameters:
      - name: email
        in: formData
        type: string
      - name: password
        in: formData
        type: string
    responses:
      200:
        description: HTML login form
      302:
        description: Redirect home after a successful login, or back with an error
    """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.get_by_email(email)
        if not User.verify_password(user, password):
            return redirect(url_for("auth.login", error="Invalid email or password"))

        session["user_id"] = user["id"]
        session["first_name"] = user["first_name"]
        session["role"] = user["role"]
        return redirect(url_for("index"))

    return render_template("login.html", error=request.args.get("error"))


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Sign the current user out.
    ---
    tags:
      - AuthController
    responses:
      302:
        description: Redirect home with the session cleared
    """
    session.clear()
    return redirect(url_for("index"))
