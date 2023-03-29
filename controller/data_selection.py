from flask import Blueprint, render_template
from controller.controller_helper import (
    get_controller_general_template_with_args,
    get_controller_filename,
)

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
    template_name_arg="index_data_selection.html", sub_navbar_active_arg=""
):
    return get_controller_general_template_with_args(
        template_name_arg,
        method_usage_list,
        sub_navbar_active_arg,
        get_controller_filename(__name__),
    )


@data_selection.route("/")
@data_selection.route("/home")
def home():
    return get_controller_specific_template_with_args("index_data_selection.html")


@data_selection.route("/import_new_dataset")
def import_new_dataset():
    return get_controller_specific_template_with_args(
        "import_new_dataset.html",
        import_new_dataset.__name__,
    )
