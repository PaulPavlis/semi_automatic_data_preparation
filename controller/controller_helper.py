from flask import render_template, current_app, redirect, url_for, flash
import os
import pandas as pd


def get_controller_general_template_with_args(
    template_name="index.html",
    sub_navbar_list_arg=None,
    sub_navbar_active_arg="",
    main_navbar_active_arg="",
    *additional_args,
):
    return render_template(
        template_name,
        sub_navbar_list=sub_navbar_list_arg,
        sub_navbar_active=sub_navbar_active_arg,
        main_navbar_active=main_navbar_active_arg,
        active_dataset_info=f"Currently active dataset: {get_active_dataset_name()} || Infos: {get_dataset_basic_info_string(get_active_dataframe())}"
        if get_active_dataset_name()
        else "No active dataframe selected. Please choose one under data_selection --> select_dataset_as_active",
        additional_args=additional_args,
    )


def get_active_dataset_name():
    # Only get the first one (should also only ever be one)
    active_datasets = [
        f
        for f in os.listdir(current_app.config["ACTIVE_DATASET_FOLDER"])
        if os.path.isfile(os.path.join(current_app.config["ACTIVE_DATASET_FOLDER"], f))
    ]

    return active_datasets[0] if active_datasets else None


def get_active_dataframe():
    if not get_active_dataset_name():
        return None
    return read_generic_input_file(
        current_app.config["ACTIVE_DATASET_FOLDER"], get_active_dataset_name()
    )


def get_dataset_basic_info_string(dataframe):
    if dataframe.empty:
        return "No dataframe given."
    return (
        f"Number of rows: {dataframe.shape[0]}, Number of columns: {dataframe.shape[1]}"
    )


def read_generic_input_file(file_location, file_name):
    if not file_name:
        return None
    file_extension = get_file_extension(file_name)
    file_path = os.path.join(file_location, file_name)

    if file_extension == "csv":
        return pd.read_csv(file_path, encoding="latin1")
    elif file_extension == "json":
        return pd.read_json(file_path, encoding="latin1")
    else:
        raise ValueError(
            "Custom Error: This file extension is not currently supported."
        )


def get_controller_filename(complete_name):
    return complete_name.split(".")[1]


def is_allowed_file(filename):
    return (
        "." in filename
        and get_file_extension(filename) in current_app.config["ALLOWED_EXTENSIONS"]
    )


def get_file_extension(filename):
    return filename.rsplit(".", 1)[1].lower()


def check_if_active_dataset_is_set():
    return True if get_active_dataset_name() else False


def send_user_to_set_active_dataset():
    flash("You need to select an active dataset first. Redirecting you ...", "warning")
    return redirect(url_for("data_selection.select_dataset_as_active"))
