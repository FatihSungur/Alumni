from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify(status="ok")


users = []


@app.route("/api/users", methods=["GET", "POST"])
def users_collection():
    if request.method == "POST":
        user = {
            "first_name": request.form.get("first_name"),
            "last_name": request.form.get("last_name"),
            "graduation_year": request.form.get("graduation_year"),
            "email": request.form.get("email"),
        }
        users.append(user)
        return jsonify(user), 201

    return jsonify(users)


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
