from flask import Blueprint, render_template
from controller.controller_helper import get_controller_general_template_with_args, get_controller_filename

data_exploration = Blueprint(
    "data_exploration",
    __name__,
    static_folder="static",
    template_folder="../templates/data_exploration/",
)

method_exploration_list = [
    "general_overview",
    "manual_exploration",
    "visual_exploration",
]


def get_controller_specific_template_with_args(
    template_name_arg="index_data_exploration.html", sub_navbar_active_arg=""
):
    return get_controller_general_template_with_args(
        template_name_arg, method_exploration_list, sub_navbar_active_arg, get_controller_filename(__name__),
    )


@data_exploration.route("/")
@data_exploration.route("/home")
def home():
    return get_controller_specific_template_with_args(
        "index_data_exploration.html"
    )


@data_exploration.route("/visual_exploration")
def visual_exploration():
    return get_controller_specific_template_with_args(
        "index_data_exploration.html",
        visual_exploration.__name__,
    )
