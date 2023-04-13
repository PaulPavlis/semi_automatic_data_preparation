from flask import Blueprint, render_template, request, flash
from controller.controller_helper import (
    get_controller_general_template_with_args,
    get_controller_filename,
    get_all_datasets,
    get_active_dataframe_prepared,
    generate_h2o_model,
)

using_the_data = Blueprint(
    "using_the_data",
    __name__,
    static_folder="static",
    template_folder="../templates/using_the_data/",
)

method_usage_list = [
    "output_to_file",
    "h2o_automl",
    "automl_solution_2",
]


def get_controller_specific_template_with_args(
    template_name_arg="index_using_the_data.html",
    sub_navbar_active_arg="",
    *additional_args
):
    return get_controller_general_template_with_args(
        template_name_arg,
        method_usage_list,
        sub_navbar_active_arg,
        get_controller_filename(__name__),
        *additional_args
    )


@using_the_data.route("/")
@using_the_data.route("/home")
def home():
    return get_controller_specific_template_with_args("index_using_the_data.html")


@using_the_data.route("/h2o_automl", methods=["POST", "GET"])
def h2o_automl():
    if request.method == "GET" or request.method == "POST":
        if request.method == "POST":
            if (
                "submit_predict_using_h2o" in request.form
                and "column_to_predict" in request.form
                and request.form["column_to_predict"] != "None"
            ):
                # print(request.form["column_to_predict"])
                print(generate_h2o_model(request.form["column_to_predict"]))
            else:
                flash(
                    "Please choose a dataset and a column to predict to use this functionality",
                    "info",
                )

        return get_controller_specific_template_with_args(
            "h2o_automl.html", h2o_automl.__name__, get_active_dataframe_prepared()
        )
    else:
        return "Use get or post to request this page"
