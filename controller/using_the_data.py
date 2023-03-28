from flask import Blueprint, render_template

using_the_data = Blueprint(
    "using_the_data",
    __name__,
    static_folder="static",
    template_folder="../templates/using_the_data/",
)


@using_the_data.route("/")
@using_the_data.route("/home")
def home():
    return render_template("index_using_the_data.html")
