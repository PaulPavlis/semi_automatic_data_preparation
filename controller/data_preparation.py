from flask import Blueprint, request, flash, current_app
from controller.controller_helper import (
    get_controller_general_template_with_args,
    get_controller_filename,
    get_active_dataframe,
    get_active_dataframe_formatted,
    check_if_active_dataset_is_set,
    send_user_to_set_active_dataset,
    get_active_user_file_config,
    create_config_dict,
    create_or_modify_user_config_file,
    get_active_dataset_name,
)
import numpy as np

data_preparation = Blueprint(
    "data_preparation",
    __name__,
    static_folder="static",
    template_folder="../templates/data_preparation/",
)


# Just demonstration TODO: Fill me in correctly
method_preparation_list = [
    "adapt_file_configs",
    "manual_repairing",
    "automatic_detection",
    "transpose",
    "anomaly_detection",
    "normalisation",
]


def get_controller_specific_template_with_args(
    template_name_arg="index_data_preparation.html",
    sub_navbar_active_arg="",
    *additional_args,
):
    return get_controller_general_template_with_args(
        template_name_arg,
        method_preparation_list,
        sub_navbar_active_arg,
        get_controller_filename(__name__),
        *additional_args,
    )


@data_preparation.route("/")
@data_preparation.route("/home")
def home():
    # TODO: Add explanation to general pipeline and how to use
    return get_controller_specific_template_with_args("index_data_preparation.html")


@data_preparation.route("/manual_repairing", methods=["POST", "GET"])
def manual_repairing():
    if not check_if_active_dataset_is_set():
        return send_user_to_set_active_dataset()

    display_df_list_of_dicts = get_active_dataframe_formatted()

    if request.method == "GET" or request.method == "POST":
        if request.method == "POST":
            n = 0

        flash(
            f"Depending on the amount of data, displaying it in a smart table might take a few seconds.",
            "info",
        )

        return get_controller_specific_template_with_args(
            "manual_repairing.html", manual_repairing.__name__, display_df_list_of_dicts
        )
    else:
        return "Use get or post to request this page"


@data_preparation.route("/automatic_detection", methods=["POST", "GET"])
def automatic_detection():
    return get_controller_specific_template_with_args(
        "index_data_preparation.html",
        automatic_detection.__name__,
    )


@data_preparation.route("/adapt_file_configs", methods=["POST", "GET"])
def adapt_file_configs():
    if not check_if_active_dataset_is_set():
        return send_user_to_set_active_dataset()

    # print(active_user_file_configs)

    if request.method == "GET" or request.method == "POST":
        if request.method == "POST":
            change_config_files(request.form)
            # print(request.form)

        # flash(
        #     f"Depending on the amount of data, displaying it in a smart table might take a few seconds.",
        #     "success",
        # )
        active_user_file_configs = get_active_user_file_config()

        return get_controller_specific_template_with_args(
            "adapt_file_configs.html",
            adapt_file_configs.__name__,
            current_app.config["USER_FILE_CONFIGS_OPTIONS"],
            active_user_file_configs,
        )
    else:
        return "Use get or post to request this page"


def change_config_files(new_config=None):
    if not new_config:
        flash("No changed configs received.", "warning")
        return None
    print(f"{new_config=}")

    create_or_modify_user_config_file(
        get_active_dataset_name(),
        create_config_dict(
            "has_header" in new_config,
            new_config["file_separator"] if "file_separator" in new_config else "",
        ),
    )

    # for config_option in current_app.config["USER_FILE_CONFIGS_OPTIONS"]:
    #     if config_option in new_config:
    #         print(config_option)
    #         print(f"{new_config[config_option]}")
    return 0
