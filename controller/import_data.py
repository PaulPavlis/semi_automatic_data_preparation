from flask import Blueprint, render_template

import_data = Blueprint(
    "import_data",
    __name__,
    static_folder="static",
    template_folder="../templates/import_data/",
)


@import_data.route("/")
@import_data.route("/home")
def home():
    return render_template("index_import_data.html")
