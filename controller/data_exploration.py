from flask import Blueprint, render_template, flash, request
from controller.controller_helper import get_controller_general_template_with_args, get_controller_filename, get_active_dataframe_formatted, check_if_active_dataset_is_set, send_user_to_set_active_dataset, get_active_dataframe


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
    template_name_arg="index_data_exploration.html", sub_navbar_active_arg="", *additional_args
):
    return get_controller_general_template_with_args(
        template_name_arg, method_exploration_list, sub_navbar_active_arg, get_controller_filename(__name__), *additional_args
    )


@data_exploration.route("/")
@data_exploration.route("/home")
def home():
    return get_controller_specific_template_with_args(
        "index_data_exploration.html"
    )


@data_exploration.route("/general_overview")
def general_overview():
    active_dataframe_description = get_active_dataframe().describe(include="all").reset_index().rename(columns={"index": "Type"})
    active_dataframe_description.fillna("-", inplace=True)
    

    # add the column type (categorical, numeric, ...) as a row to the df
    # for index in range(active_dataframe_description.shape[1]):
    #     print(active_dataframe_description.iloc[:, index])
    #     break
    
    active_dataframe_description = active_dataframe_description.to_dict("records")


    # print(get_active_dataframe().info())
    return get_controller_specific_template_with_args(
        "general_overview.html",
        general_overview.__name__,
        active_dataframe_description,
    )


@data_exploration.route("/visual_exploration")
def visual_exploration():
    return get_controller_specific_template_with_args(
        "index_data_exploration.html",
        visual_exploration.__name__,
    )

@data_exploration.route("/manual_exploration")
def manual_exploration():
    if not check_if_active_dataset_is_set():
        return send_user_to_set_active_dataset()

    display_df_list_of_dicts = get_active_dataframe_formatted()

    if request.method == "GET" or request.method == "POST":
        if request.method == "POST":
            n = 0

        flash(
            f"Depending on the amount of data, displaying it in a smart table might take a few seconds.",
            "info",
        )

        return get_controller_specific_template_with_args(
        "manual_exploration.html",
        manual_exploration.__name__, display_df_list_of_dicts
    )
    else:
        return "Use get or post to request this page"
    