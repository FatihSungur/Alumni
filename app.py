from flask import Flask, jsonify, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify(status="ok")


ALUMNI = [
    {
        "first_name": "Fatih",
        "last_name": "Sungur",
        "graduation_year": 2026,
        "email": "fatih.sungur@example.com",
    },
    {
        "first_name": "Emre",
        "last_name": "Yildiz",
        "graduation_year": 2025,
        "email": "emre.yildiz@example.com",
    },
    {
        "first_name": "Ayse",
        "last_name": "Kaya",
        "graduation_year": 2024,
        "email": "ayse.kaya@example.com",
    },
]


@app.route("/api/users")
def users():
    return jsonify(ALUMNI)


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
