from flask import Flask, render_template
from controller.data_exploration import data_exploration
from controller.data_preparation import data_preparation
from controller.data_selection import data_selection
from controller.using_the_data import using_the_data
import os
from pathlib import Path
from controller.controller_helper import (
    get_active_dataframe,
    get_active_dataframe_prepared,
    get_active_user_file_config,
)
from numpy import nan

app = Flask(__name__)
app.secret_key = "semi_automatic_data_preparation"
app.register_blueprint(data_exploration, url_prefix="/data_exploration")
app.register_blueprint(data_preparation, url_prefix="/data_preparation")
app.register_blueprint(data_selection, url_prefix="/data_selection")
app.register_blueprint(using_the_data, url_prefix="/using_the_data")

UPLOAD_FOLDER = "stored_user_files"
ALLOWED_EXTENSIONS = {"csv", "json"}
ACTIVE_DATASET_FOLDER = os.path.join(UPLOAD_FOLDER, "active_dataset")
ACTIVE_DATASET_TRANSFORMED_FOLDER = os.path.join(
    UPLOAD_FOLDER, "active_dataset_prepared"
)
STORED_ML_MODELS_FOLDER = os.path.join(UPLOAD_FOLDER, "saved_models")
USER_FILE_CONFIGS = os.path.join(UPLOAD_FOLDER, "user_file_configs")
USER_FILE_CONFIGS_OPTIONS = [
    "has_header",
    "file_separator",
    "has_index",
    "column_types",
    "na_values_list",
]

# Create reqired folders:
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
Path(ACTIVE_DATASET_FOLDER).mkdir(parents=True, exist_ok=True)
Path(ACTIVE_DATASET_TRANSFORMED_FOLDER).mkdir(parents=True, exist_ok=True)
Path(USER_FILE_CONFIGS).mkdir(parents=True, exist_ok=True)
Path(STORED_ML_MODELS_FOLDER).mkdir(parents=True, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ALLOWED_EXTENSIONS"] = ALLOWED_EXTENSIONS
app.config["ACTIVE_DATASET_FOLDER"] = ACTIVE_DATASET_FOLDER
app.config["ACTIVE_DATASET_TRANSFORMED_FOLDER"] = ACTIVE_DATASET_TRANSFORMED_FOLDER
app.config["USER_FILE_CONFIGS"] = USER_FILE_CONFIGS
app.config["USER_FILE_CONFIGS_OPTIONS"] = USER_FILE_CONFIGS_OPTIONS
app.config["STORED_ML_MODELS_FOLDER"] = STORED_ML_MODELS_FOLDER


@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html", main_navbar_active="home")


@app.route("/return_active_ajax_data/<get_prepared>")
def return_active_ajax_data(get_prepared):
    df = None
    if get_prepared == "false":
        df = get_active_dataframe()
    elif get_prepared == "true":
        if get_active_user_file_config()["has_index"]["value"] == True:
            df = get_active_dataframe_prepared(reset_index=True)
        else:
            df = get_active_dataframe_prepared(reset_index=False)
            print(df)
            if "previous_header" in df:
                df = df[df["previous_header"] != "generated_index"]
            else:
                # dirty fix. This is only here, because the transpose logic above does not need the generated index in it
                df = df.reset_index()
                print(df)
    else:
        return "get prepared parameter is missing."

    # df.columns = df.columns.astype(str)

    # print(df.astype(object).replace(nan, "None").to_dict("records"))

    # This is needed because the columns might get mixed in the ajax call on js side
    column_order = ""
    for column in df:
        column_order = f"{column_order}|||{str(column)}"

    return {
        "data": df.astype(object).replace(nan, "None").to_dict("records"),
        "column_order": column_order,
    }


if __name__ == "__main__":
    app.run(debug=True)
