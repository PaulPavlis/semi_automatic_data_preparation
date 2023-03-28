from flask import Blueprint, render_template
from controller.controller_helper import (
    get_controller_general_template_with_args,
    get_controller_filename,
)

using_the_data = Blueprint(
    "using_the_data",
    __name__,
    static_folder="static",
    template_folder="../templates/using_the_data/",
)

method_usage_list = [
    "output_to_file",
    "automl_solution_1",
    "automl_solution_2",
]


def get_controller_specific_template_with_args(
    template_name_arg="index_using_the_data.html", sub_navbar_active_arg=""
):
    return get_controller_general_template_with_args(
        template_name_arg,
        method_usage_list,
        sub_navbar_active_arg,
        get_controller_filename(__name__),
    )


@using_the_data.route("/")
@using_the_data.route("/home")
def home():
    return get_controller_specific_template_with_args("index_using_the_data.html")


@using_the_data.route("/automl_solution_1")
def automl_solution_1():
    return get_controller_specific_template_with_args(
        "index_using_the_data.html",
        automl_solution_1.__name__,
    )
