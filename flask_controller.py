from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)


@app.route("/")
@app.route("/home", methods=["POST", "GET"])
def home():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        form_email = request.form["email"]
        form_password = request.form["password"]
        return render_template("index.html", email=form_email, password=form_password)
    else:
        return "Use get or post to request this page"


@app.route("/import_data")
def import_data():
    return "<h1>Fill me in</h1>"


@app.route("/data_exploration_home")
def data_exploration_home():
    return "<h1>Fill me in</h1>"


@app.route("/data_preparation_home")
def data_preparation_home():
    return "<h1>Fill me in</h1>"


@app.route("/machine_learning")
def machine_learning():
    return "<h1>Fill me in</h1>"


if __name__ == "__main__":
    app.run(debug=True)
