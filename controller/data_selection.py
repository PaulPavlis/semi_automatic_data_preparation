from flask import Blueprint, request, current_app
from controller.controller_helper import (
    get_controller_general_template_with_args,
    get_controller_filename,
    is_allowed_file,
)
import pandas as pd
import os
from werkzeug.utils import secure_filename
import shutil

data_selection = Blueprint(
    "data_selection",
    __name__,
    static_folder="static",
    template_folder="../templates/data_selection/",
)

method_usage_list = [
    "import_new_dataset",
    "select_dataset_as_active",
    "delete_dataset",
]


def get_controller_specific_template_with_args(
    template_name_arg="index_data_selection.html",
    sub_navbar_active_arg="",
    *additional_args,
):
    return get_controller_general_template_with_args(
        template_name_arg,
        method_usage_list,
        sub_navbar_active_arg,
        get_controller_filename(__name__),
        *additional_args,
    )


def delete_all_active_files():
    active_dataset_list = get_active_dataset_list()

    for active_dataset in active_dataset_list:
        os.remove(
            os.path.join(current_app.config["ACTIVE_DATASET_FOLDER"], active_dataset)
        )


def get_active_dataset_list():
    return [
        f
        for f in os.listdir(current_app.config["ACTIVE_DATASET_FOLDER"])
        if os.path.isfile(os.path.join(current_app.config["ACTIVE_DATASET_FOLDER"], f))
    ]


def set_active_file(new_active_dataset):
    active_dataset_list = get_active_dataset_list()

    for active_dataset in active_dataset_list:
        shutil.move(
            os.path.join(current_app.config["ACTIVE_DATASET_FOLDER"], active_dataset),
            os.path.join(current_app.config["UPLOAD_FOLDER"], active_dataset),
        )

    # Move new active dataset to active folder
    if new_active_dataset:
        shutil.copyfile(
            os.path.join(current_app.config["UPLOAD_FOLDER"], new_active_dataset),
            os.path.join(
                current_app.config["ACTIVE_DATASET_FOLDER"], new_active_dataset
            ),
        )


def delete_dataset_with_name(delete_dataset_name):
    if delete_dataset_name:
        if delete_dataset_name == "active_file":
            delete_all_active_files()
        else:
            os.remove(
                os.path.join(
                    current_app.config["UPLOAD_FOLDER"],
                    delete_dataset_name,
                )
            )


@data_selection.route("/")
@data_selection.route("/home")
def home():
    return get_controller_specific_template_with_args("index_data_selection.html")


@data_selection.route("/import_new_dataset", methods=["POST", "GET"])
def import_new_dataset():
    if request.method == "GET":
        return get_controller_specific_template_with_args(
            "import_new_dataset.html", import_new_dataset.__name__
        )
    elif request.method == "POST":
        file_name_new = ""

        if "file_name_new" in request.form:
            file_name_new = request.form["file_name_new"]

        if "file_input" in request.files:
            file_uploaded = request.files["file_input"]
            print(f"{file_uploaded=}")

            file_name_uploaded = secure_filename(file_uploaded.filename)

            if is_allowed_file(file_name_uploaded):
                if file_name_new:
                    if is_allowed_file(secure_filename(file_name_new)):
                        file_name_final = secure_filename(file_name_new)
                    else:
                        raise ValueError(
                            "Custom Error: The file extension you are giving with the File name is not currently supported."
                        )
                else:
                    file_name_final = file_name_uploaded

                print(
                    f"{file_name_new=}, {file_name_uploaded=}, {file_uploaded=}, {file_name_final=}"
                )
                file_uploaded.save(
                    os.path.join(current_app.config["UPLOAD_FOLDER"], file_name_final)
                )

                if "is_new_file_active" in request.form:
                    print("Add me as active file")  # TODO: Do this

            else:
                raise ValueError(
                    "Custom Error: This file extension is not currently supported."
                )

        else:
            raise ValueError("Custom Error: You have not given a file to the site.")

        return get_controller_specific_template_with_args(
            "import_new_dataset.html", import_new_dataset.__name__
        )
    else:
        return "Use get or post to request this page"


@data_selection.route("/select_dataset_as_active", methods=["POST", "GET"])
def select_dataset_as_active():
    dataset_list = [
        f
        for f in os.listdir(current_app.config["UPLOAD_FOLDER"])
        if os.path.isfile(os.path.join(current_app.config["UPLOAD_FOLDER"], f))
    ]

    print(dataset_list)

    if request.method == "GET":
        return get_controller_specific_template_with_args(
            "select_dataset_as_active.html",
            select_dataset_as_active.__name__,
            dataset_list,
        )
    elif request.method == "POST":
        print(f"{request.form=}")

        set_active_file(request.form["new_active_dataset"])

        return get_controller_specific_template_with_args(
            "select_dataset_as_active.html",
            select_dataset_as_active.__name__,
            dataset_list,
        )

    else:
        return "Use get or post to request this page"


@data_selection.route("/delete_dataset", methods=["POST", "GET"])
def delete_dataset():
    dataset_list = [
        f
        for f in os.listdir(current_app.config["UPLOAD_FOLDER"])
        if os.path.isfile(os.path.join(current_app.config["UPLOAD_FOLDER"], f))
    ]

    print(dataset_list)

    if request.method == "GET":
        return get_controller_specific_template_with_args(
            "delete_dataset.html",
            delete_dataset.__name__,
            dataset_list,
        )
    elif request.method == "POST":
        print(f"{request.form=}")

        delete_dataset_with_name(request.form["delete_dataset_name"])

        return get_controller_specific_template_with_args(
            "delete_dataset.html",
            delete_dataset.__name__,
            dataset_list,
        )

    else:
        return "Use get or post to request this page"
