from flask import Blueprint, render_template
from controller.controller_helper import (
    get_controller_general_template_with_args,
    get_controller_filename,
)

data_preparation = Blueprint(
    "data_preparation",
    __name__,
    static_folder="static",
    template_folder="../templates/data_preparation/",
)


# Just demonstration TODO: Fill me in correctly
method_preparation_list = [
    "automatic_detection",
    "manual_repairing",
    "transpose",
    "anomaly_detection",
    "normalisation",
]


def get_controller_specific_template_with_args(
    template_name_arg="index_data_preparation.html", sub_navbar_active_arg=""
):
    return get_controller_general_template_with_args(
        template_name_arg,
        method_preparation_list,
        sub_navbar_active_arg,
        get_controller_filename(__name__),
    )


@data_preparation.route("/")
@data_preparation.route("/home")
def home():
    # TODO: Add explanation to general pipeline and how to use
    return get_controller_specific_template_with_args("index_data_preparation.html")


@data_preparation.route("/automatic_detection")
def automatic_detection():
    return get_controller_specific_template_with_args(
        "index_data_preparation.html",
        automatic_detection.__name__,
    )
