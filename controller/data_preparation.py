from flask import Blueprint, render_template

data_preparation = Blueprint(
    "data_preparation",
    __name__,
    static_folder="static",
    template_folder="../templates/data_preparation/",
)


@data_preparation.route("/")
@data_preparation.route("/home")
def home():
    return render_template("index_data_preparation.html")
