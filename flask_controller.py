from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")


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
