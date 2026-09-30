from flasgger import Swagger
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

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


users = []
next_id = 1


@app.route("/api/users", methods=["GET", "POST"])
def users_collection():
    """
    List all alumni records, or create a new one.
    ---
    parameters:
      - name: first_name
        in: formData
        type: string
      - name: last_name
        in: formData
        type: string
      - name: graduation_year
        in: formData
        type: string
      - name: email
        in: formData
        type: string
    responses:
      200:
        description: List of alumni records
      201:
        description: Created alumni record
    """
    global next_id

    if request.method == "POST":
        user = {
            "id": next_id,
            "first_name": request.form.get("first_name"),
            "last_name": request.form.get("last_name"),
            "graduation_year": request.form.get("graduation_year"),
            "email": request.form.get("email"),
        }
        next_id += 1
        users.append(user)
        return jsonify(user), 201

    return jsonify(users)


@app.route("/api/users/<int:user_id>", methods=["PUT", "PATCH", "DELETE"])
def user_item(user_id):
    """
    Replace, partially update, or delete an alumni record by id.
    ---
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
      - name: first_name
        in: formData
        type: string
      - name: last_name
        in: formData
        type: string
      - name: graduation_year
        in: formData
        type: string
      - name: email
        in: formData
        type: string
    responses:
      200:
        description: Updated or deleted alumni record
      404:
        description: User not found
    """
    user = next((u for u in users if u["id"] == user_id), None)
    if user is None:
        return jsonify(error="User not found"), 404

    if request.method == "PUT":
        user["first_name"] = request.form.get("first_name")
        user["last_name"] = request.form.get("last_name")
        user["graduation_year"] = request.form.get("graduation_year")
        user["email"] = request.form.get("email")
        return jsonify(user)

    if request.method == "PATCH":
        for field in ("first_name", "last_name", "graduation_year", "email"):
            if field in request.form:
                user[field] = request.form.get(field)
        return jsonify(user)

    users.remove(user)
    return jsonify(user)


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
