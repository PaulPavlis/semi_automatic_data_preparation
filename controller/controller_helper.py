from flask import render_template, current_app, redirect, url_for, flash
import os
import pandas as pd
import yaml


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


def get_active_dataframe_formatted():
    return get_active_dataframe().to_dict("records")


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
        return pd.read_csv(file_path, encoding="latin1", header=None)
    elif file_extension == "json":
        return pd.read_json(file_path, encoding="latin1", header=None)
    else:
        flash("This file extension is currently not supported.", "danger")
        return None


def get_controller_filename(complete_name):
    return complete_name.split(".")[1]


def is_allowed_file(filename):
    return (
        "." in filename
        and get_file_extension(filename) in current_app.config["ALLOWED_EXTENSIONS"]
    )


def get_file_extension(filename):
    return filename.rsplit(".", 1)[1].lower()


def get_filename_without_extension(filename):
    return filename.rsplit(".", 1)[0].lower()


def check_if_active_dataset_is_set():
    return True if get_active_dataset_name() else False


def send_user_to_set_active_dataset():
    flash("You need to select an active dataset first. Redirecting you ...", "warning")
    return redirect(url_for("data_selection.select_dataset_as_active"))


def get_user_file_config_name(user_file_name):
    return f"{str(get_filename_without_extension(user_file_name))}.yaml"


def create_user_file_config(user_file_name, config_dict={}):
    if not isinstance(config_dict, dict):
        return None

    with open(
        os.path.join(
            current_app.config["USER_FILE_CONFIGS"],
            get_user_file_config_name(user_file_name),
        ),
        "w+",
    ) as fw:
        yaml.dump(config_dict, fw, default_flow_style=False, allow_unicode=True)
        flash("User file config adaptations were successful.", "success")


def get_user_file_config(user_file_name):
    with open(
        os.path.join(
            current_app.config["USER_FILE_CONFIGS"],
            get_user_file_config_name(user_file_name),
            "r",
        )
    ) as fr:
        try:
            return yaml.safe_load(fr)
        except yaml.YAMLError as exc:
            print(exc)


def modify_user_config_file(user_file_name, config_dict={}):
    if not isinstance(config_dict, dict):
        return None

    current_configs = get_user_file_config(get_user_file_config_name(user_file_name))

    print(f"{current_configs=}")
    print(f"{config_dict=}")
    current_configs.update(config_dict)

    print(f"Updated dict: {current_configs}")

    create_user_file_config(get_user_file_config_name(user_file_name), current_configs)
