from flask import Blueprint, request, current_app, flash, redirect, url_for
from controller.controller_helper import (
    get_controller_general_template_with_args,
    get_controller_filename,
    is_allowed_file,
    create_or_modify_user_config_file,
    get_user_file_config_name,
    create_config_dict,
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


@data_selection.route("/")
@data_selection.route("/home")
def home():
    return get_controller_specific_template_with_args("index_data_selection.html")


@data_selection.route("/import_new_dataset", methods=["POST", "GET"])
def import_new_dataset():
    if request.method == "GET" or request.method == "POST":
        if request.method == "POST":
            add_new_file(request)

        return get_controller_specific_template_with_args(
            "import_new_dataset.html", import_new_dataset.__name__
        )
    else:
        return "Use get or post to request this page"


@data_selection.route("/select_dataset_as_active", methods=["POST", "GET"])
def select_dataset_as_active():
    dataset_list = get_all_datasets()

    if not dataset_list:
        flash(
            f"No datasets imported yet. Redirecting you ...",
            "warning",
        )
        return redirect(url_for("data_selection.import_new_dataset"))

    if request.method == "GET" or request.method == "POST":
        if request.method == "POST":
            set_active_file(request.form["new_active_dataset"])

        dataset_list = get_all_datasets()
        return get_controller_specific_template_with_args(
            "select_dataset_as_active.html",
            select_dataset_as_active.__name__,
            dataset_list,
        )
    else:
        return "Use get or post to request this page"


@data_selection.route("/delete_dataset", methods=["POST", "GET"])
def delete_dataset():
    if request.method == "GET" or request.method == "POST":
        if request.method == "POST":
            delete_dataset_with_name(request.form["delete_dataset_name"])

        dataset_list = get_all_datasets()

        return get_controller_specific_template_with_args(
            "delete_dataset.html",
            delete_dataset.__name__,
            dataset_list,
        )
    else:
        return "Use get or post to request this page"


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


def set_active_file(new_active_dataset_name):
    active_dataset_list = get_active_dataset_list()

    for active_dataset in active_dataset_list:
        shutil.move(
            os.path.join(current_app.config["ACTIVE_DATASET_FOLDER"], active_dataset),
            os.path.join(current_app.config["UPLOAD_FOLDER"], active_dataset),
        )

    # Move new active dataset to active folder
    if new_active_dataset_name:
        shutil.copyfile(
            os.path.join(current_app.config["UPLOAD_FOLDER"], new_active_dataset_name),
            os.path.join(
                current_app.config["ACTIVE_DATASET_FOLDER"], new_active_dataset_name
            ),
        )

    flash(
        f"Successfully set {new_active_dataset_name} as the active dataset.",
        "success",
    )


def delete_dataset_with_name(delete_dataset_name):
    if delete_dataset_name:
        if delete_dataset_name == "active_file":
            delete_all_active_files()
            flash(
                f"Successfully removed the active dataset.",
                "success",
            )
        else:
            os.remove(
                os.path.join(
                    current_app.config["UPLOAD_FOLDER"],
                    delete_dataset_name,
                )
            )
            flash(
                f"Successfully removed the {delete_dataset_name} dataset.",
                "success",
            )

            if (
                "delete_file_config" in request.form
                and request.form["delete_file_config"]
            ):
                config_file_name = get_user_file_config_name(delete_dataset_name)
                os.remove(
                    os.path.join(
                        current_app.config["USER_FILE_CONFIGS"],
                        config_file_name,
                    )
                )
                flash(
                    f"Successfully removed the {config_file_name} config file.",
                    "success",
                )


def get_all_datasets():
    return [
        f
        for f in os.listdir(current_app.config["UPLOAD_FOLDER"])
        if os.path.isfile(os.path.join(current_app.config["UPLOAD_FOLDER"], f))
    ]


def add_new_file(request):
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
                    flash(
                        f"The file extension you are giving with the Filename is currently not supported.",
                        "danger",
                    )
                    return None
            else:
                file_name_final = file_name_uploaded

            print(
                f"{file_name_new=}, {file_name_uploaded=}, {file_uploaded=}, {file_name_final=}"
            )
            file_uploaded.save(
                os.path.join(current_app.config["UPLOAD_FOLDER"], file_name_final)
            )

            flash(
                f"Successfully imported the new dataset.",
                "success",
            )

            if "is_new_file_active" in request.form:
                set_active_file(file_name_final)

            user_file_configs = create_config_dict(
                "new_file_has_header" in request.form,
                request.form["new_file_separator"]
                if "new_file_separator" in request.form
                else None,
            )

            create_or_modify_user_config_file(file_name_final, user_file_configs)

        else:
            flash(
                f"This file extension is currently not supported.",
                "danger",
            )
            return None
    else:
        flash(
            f"You have not given a file to the site.",
            "warning",
        )
        return None
