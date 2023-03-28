from flask import Flask, redirect, url_for, render_template, request
from controller.data_exploration import data_exploration
from controller.data_preparation import data_preparation
from controller.import_data import import_data
from controller.using_the_data import using_the_data

app = Flask(__name__)
app.register_blueprint(data_exploration, url_prefix="/data_exploration")
app.register_blueprint(data_preparation, url_prefix="/data_preparation")
app.register_blueprint(import_data, url_prefix="/import_data")
app.register_blueprint(using_the_data, url_prefix="/using_the_data")


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


if __name__ == "__main__":
    app.run(debug=True)
