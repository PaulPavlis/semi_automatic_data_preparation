from flask import Blueprint, render_template

data_exploration = Blueprint(
    "data_exploration",
    __name__,
    static_folder="static",
    template_folder="../templates/data_exploration/",
)


@data_exploration.route("/")
@data_exploration.route("/home")
def home():
    return render_template("index_data_exploration.html")
