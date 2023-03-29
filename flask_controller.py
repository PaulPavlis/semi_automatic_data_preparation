from flask import Flask, render_template
from controller.data_exploration import data_exploration
from controller.data_preparation import data_preparation
from controller.data_selection import data_selection
from controller.using_the_data import using_the_data

app = Flask(__name__)
app.register_blueprint(data_exploration, url_prefix="/data_exploration")
app.register_blueprint(data_preparation, url_prefix="/data_preparation")
app.register_blueprint(data_selection, url_prefix="/data_selection")
app.register_blueprint(using_the_data, url_prefix="/using_the_data")

UPLOAD_FOLDER = "stored_user_files"
ALLOWED_EXTENSIONS = {"csv", "json"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ALLOWED_EXTENSIONS"] = ALLOWED_EXTENSIONS


@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html", main_navbar_active="home")


if __name__ == "__main__":
    app.run(debug=True)
