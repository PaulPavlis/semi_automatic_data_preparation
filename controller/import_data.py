from flask import Blueprint, render_template
from controller.controller_helper import (
    get_controller_general_template_with_args,
    get_controller_filename,
)

import_data = Blueprint(
    "import_data",
    __name__,
    static_folder="static",
    template_folder="../templates/import_data/",
)


def get_controller_specific_template_with_args(
    template_name_arg="index_import_data.html", sub_navbar_active_arg=""
):
    return get_controller_general_template_with_args(
        template_name_arg,
        [],
        sub_navbar_active_arg,
        get_controller_filename(__name__),
    )


@import_data.route("/")
@import_data.route("/home")
def home():
    # return get_controller_filename(__name__)
    return get_controller_specific_template_with_args("index_import_data.html")
