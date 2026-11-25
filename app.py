import os

from flasgger import Swagger
from flask import Flask, jsonify, render_template

from controllers.admin_controller import admin_bp
from controllers.announcement_controller import announcement_bp
from controllers.api_announcement_controller import api_announcement_bp
from controllers.api_job_application_controller import api_job_application_bp
from controllers.api_job_posting_controller import api_job_posting_bp
from controllers.api_user_controller import api_user_bp
from controllers.auth_controller import auth_bp
from controllers.job_application_controller import job_application_bp
from controllers.job_posting_controller import job_posting_bp
from controllers.profile_controller import profile_bp
from controllers.user_controller import user_bp
from middleware.error_handlers import register_error_handlers
from middleware.logger import register_request_logger

app = Flask(__name__)

# Signs the login session cookie (see controllers/auth_controller.py) — without
# this, Flask refuses to use `session` at all.
app.secret_key = os.environ.get("SECRET_KEY")

# In debug mode, Flask/Werkzeug normally shows its own interactive debugger for
# unhandled exceptions instead of calling our error handlers below. Disabling
# this makes our 5xx guardian actually fire, even while debug=True.
app.config["PROPAGATE_EXCEPTIONS"] = False

app.config["SWAGGER"] = {
    "title": "Alumni API",
    "uiversion": 3,
}
Swagger(app, config={
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/swagger/",
})

app.register_blueprint(api_user_bp)
app.register_blueprint(user_bp)
app.register_blueprint(api_announcement_bp)
app.register_blueprint(announcement_bp)
app.register_blueprint(api_job_posting_bp)
app.register_blueprint(api_job_application_bp)
app.register_blueprint(job_posting_bp)
app.register_blueprint(job_application_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(profile_bp)

register_request_logger(app)
register_error_handlers(app)


@app.route("/")
def index():
    """
    Temporary main page.
    ---
    responses:
      200:
        description: HTML home page
    """
    return render_template("index.html")


@app.route("/api/health")
def health():
    """
    Health check.
    ---
    responses:
      200:
        description: Service status
    """
    return jsonify(status="ok")


@app.route("/about")
def about():
    """
    Temporary about page.
    ---
    responses:
      200:
        description: HTML about page
    """
    return render_template("about.html")


@app.route("/hello")
def hello():
    """
    Classic greeting.
    ---
    responses:
      200:
        description: Hello, World!
    """
    return "Hello, World!"


@app.route("/hello/<name>")
def hello_name(name):
    """
    Personalized greeting.
    ---
    parameters:
      - name: name
        in: path
        type: string
        required: true
    responses:
      200:
        description: Hello, <name>!
    """
    return f"Hello, {name.capitalize()}!"


@app.route("/sum/<int:number1>/<int:number2>")
def sum_numbers(number1, number2):
    """
    Adds two numbers.
    ---
    parameters:
      - name: number1
        in: path
        type: integer
        required: true
      - name: number2
        in: path
        type: integer
        required: true
    responses:
      200:
        description: The sum of number1 and number2
    """
    return str(number1 + number2)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
