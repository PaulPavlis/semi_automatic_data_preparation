from flask import Flask, render_template
from controller.data_exploration import data_exploration
from controller.data_preparation import data_preparation
from controller.data_selection import data_selection
from controller.using_the_data import using_the_data
import os
from pathlib import Path
from controller.controller_helper import get_active_dataframe
from numpy import nan

app = Flask(__name__)
app.secret_key = "semi_automatic_data_preparation"
app.register_blueprint(data_exploration, url_prefix="/data_exploration")
app.register_blueprint(data_preparation, url_prefix="/data_preparation")
app.register_blueprint(data_selection, url_prefix="/data_selection")
app.register_blueprint(using_the_data, url_prefix="/using_the_data")

# Create reqired folders:
UPLOAD_FOLDER = "stored_user_files"
ALLOWED_EXTENSIONS = {"csv", "json"}
ACTIVE_DATASET_FOLDER = os.path.join(UPLOAD_FOLDER, "active_dataset")
USER_FILE_CONFIGS = os.path.join(UPLOAD_FOLDER, "user_file_configs")
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
Path(ACTIVE_DATASET_FOLDER).mkdir(parents=True, exist_ok=True)
Path(USER_FILE_CONFIGS).mkdir(parents=True, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ALLOWED_EXTENSIONS"] = ALLOWED_EXTENSIONS
app.config["ACTIVE_DATASET_FOLDER"] = ACTIVE_DATASET_FOLDER
app.config["USER_FILE_CONFIGS"] = USER_FILE_CONFIGS


@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html", main_navbar_active="home")


@app.route("/return_active_ajax_data")
def return_active_ajax_data():
    return {
        "data": get_active_dataframe()
        .astype(object)
        .replace(nan, "None")
        .to_dict("records")
    }


if __name__ == "__main__":
    app.run(debug=True)
