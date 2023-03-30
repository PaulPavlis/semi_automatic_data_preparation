from flask import Blueprint, request
from controller.controller_helper import (
    get_controller_general_template_with_args,
    get_controller_filename,
    get_active_dataframe,
    check_if_active_dataset_is_set,
    send_user_to_set_active_dataset,
)

data_preparation = Blueprint(
    "data_preparation",
    __name__,
    static_folder="static",
    template_folder="../templates/data_preparation/",
)


# Just demonstration TODO: Fill me in correctly
method_preparation_list = [
    "manual_repairing",
    "automatic_detection",
    "transpose",
    "anomaly_detection",
    "normalisation",
]


def get_controller_specific_template_with_args(
    template_name_arg="index_data_preparation.html",
    sub_navbar_active_arg="",
    *additional_args
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


@data_preparation.route("/manual_repairing")
def manual_repairing():
    if not check_if_active_dataset_is_set():
        return send_user_to_set_active_dataset()

    active_dataframe = get_active_dataframe()

    display_df_list_of_dicts = active_dataframe.to_dict("records")

    if request.method == "GET" or request.method == "POST":
        if request.method == "POST":
            n = 0

        return get_controller_specific_template_with_args(
            "manual_repairing.html", manual_repairing.__name__, display_df_list_of_dicts
        )
    else:
        return "Use get or post to request this page"


@data_preparation.route("/automatic_detection")
def automatic_detection():
    return get_controller_specific_template_with_args(
        "index_data_preparation.html",
        automatic_detection.__name__,
    )
