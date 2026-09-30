from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify(status="ok")


@app.route("/api/swagger")
def swagger():
    endpoints = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint == "static":
            continue
        methods = sorted(rule.methods - {"HEAD", "OPTIONS"})
        endpoints.append({"path": str(rule), "methods": methods})

    endpoints.sort(key=lambda endpoint: endpoint["path"])
    return render_template("swagger.html", endpoints=endpoints)


users = []
next_id = 1


@app.route("/api/users", methods=["GET", "POST"])
def users_collection():
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
    return render_template("about.html")


@app.route("/hello")
def hello():
    return "Hello, World!"


@app.route("/hello/<name>")
def hello_name(name):
    return f"Hello, {name.capitalize()}!"


@app.route("/sum/<int:number1>/<int:number2>")
def sum_numbers(number1, number2):
    return str(number1 + number2)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
