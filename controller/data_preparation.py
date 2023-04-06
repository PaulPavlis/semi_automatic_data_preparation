from flask import Blueprint, request, flash, current_app
from controller.controller_helper import (
    get_controller_general_template_with_args,
    get_controller_filename,
    get_active_dataframe,
    get_active_dataframe_formatted,
    check_if_active_dataset_is_set,
    send_user_to_set_active_dataset,
    get_active_user_file_config,
    create_config_dict,
    create_or_modify_user_config_file,
    get_active_dataset_name,
    return_empty_plot,
    create_or_modify_active_prepared_file,
    get_active_dataframe_prepared,
    create_or_modify_active_file,
)
import numpy as np
import plotly
import plotly.express as px
import json
import pandas as pd

data_preparation = Blueprint(
    "data_preparation",
    __name__,
    static_folder="static",
    template_folder="../templates/data_preparation/",
)


# Just demonstration TODO: Fill me in correctly
method_preparation_list = [
    "adapt_file_configs",
    "capping",
    "transpose",
    "manual_repairing",
    "automatic_detection",
    "anomaly_detection",
    "normalisation",
]


def get_controller_specific_template_with_args(
    template_name_arg="index_data_preparation.html",
    sub_navbar_active_arg="",
    *additional_args,
):
    return get_controller_general_template_with_args(
        template_name_arg,
        method_preparation_list,
        sub_navbar_active_arg,
        get_controller_filename(__name__),
        *additional_args,
    )


@data_preparation.route("/")
@data_preparation.route("/home")
def home():
    # TODO: Add explanation to general pipeline and how to use
    return get_controller_specific_template_with_args("index_data_preparation.html")


@data_preparation.route("/manual_repairing", methods=["POST", "GET"])
def manual_repairing():
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
            "manual_repairing.html", manual_repairing.__name__, display_df_list_of_dicts
        )
    else:
        return "Use get or post to request this page"


@data_preparation.route("/automatic_detection", methods=["POST", "GET"])
def automatic_detection():
    return get_controller_specific_template_with_args(
        "index_data_preparation.html",
        automatic_detection.__name__,
    )


@data_preparation.route("/adapt_file_configs", methods=["POST", "GET"])
def adapt_file_configs():
    if not check_if_active_dataset_is_set():
        return send_user_to_set_active_dataset()

    # print(active_user_file_configs)

    if request.method == "GET" or request.method == "POST":
        if request.method == "POST":
            change_config_files(request.form)
            # print(request.form)

        # flash(
        #     f"Depending on the amount of data, displaying it in a smart table might take a few seconds.",
        #     "success",
        # )
        active_user_file_configs = get_active_user_file_config()

        return get_controller_specific_template_with_args(
            "adapt_file_configs.html",
            adapt_file_configs.__name__,
            current_app.config["USER_FILE_CONFIGS_OPTIONS"],
            active_user_file_configs,
        )
    else:
        return "Use get or post to request this page"


@data_preparation.route("/transpose", methods=["POST", "GET"])
def transpose():
    if not check_if_active_dataset_is_set():
        return send_user_to_set_active_dataset()

    # print(active_user_file_configs)

    if request.method == "GET" or request.method == "POST":
        if request.method == "POST":
            # change_config_files(request.form)
            print(request.form)

        # flash(
        #     f"Depending on the amount of data, displaying it in a smart table might take a few seconds.",
        #     "success",
        # )
        active_user_file_configs = get_active_user_file_config()

        return get_controller_specific_template_with_args(
            "transpose.html",
            transpose.__name__,
        )
    else:
        return "Use get or post to request this page"


@data_preparation.route("/capping", methods=["POST", "GET"])
def capping():
    if not check_if_active_dataset_is_set():
        return send_user_to_set_active_dataset()

    # print(active_user_file_configs)

    if request.method == "GET" or request.method == "POST":
        show_prepared_file = False
        if request.method == "POST":
            # change_config_files(request.form)
            print(request.form)
            if (
                not request.form["lower_limit"]
                or not request.form["upper_limit"]
                or request.form["column_prepare"] == "None"
            ):
                return get_controller_specific_template_with_args(
                    "capping.html",
                    capping.__name__,
                    get_active_dataframe_formatted(),
                    show_prepared_file,
                )

            lower_limit = float(request.form["lower_limit"])
            upper_limit = float(request.form["upper_limit"])
            column_prepare = request.form["column_prepare"]
            capping_type = request.form["capping_type"]

            if lower_limit >= upper_limit:
                flash(
                    f"Lower limit was higher or euqal to the upper limit. Nothing was done.",
                    "warning",
                )
                return get_controller_specific_template_with_args(
                    "capping.html",
                    capping.__name__,
                    get_active_dataframe_formatted(),
                    show_prepared_file,
                )

            prepared_df = get_active_dataframe()

            print(
                prepared_df[column_prepare]
                .describe(include="all")
                .reset_index()
                .rename(columns={"index": "Type"})
            )

            if capping_type == "replace":
                prepared_df[column_prepare] = prepared_df[column_prepare].mask(
                    prepared_df[column_prepare] < lower_limit, lower_limit
                )
                prepared_df[column_prepare] = prepared_df[column_prepare].mask(
                    prepared_df[column_prepare] > upper_limit, upper_limit
                )
            elif capping_type == "remove":
                prepared_df = prepared_df[prepared_df[column_prepare] > lower_limit]
                prepared_df = prepared_df[prepared_df[column_prepare] < upper_limit]
            else:
                flash(
                    f"Capping type option was not recognised. Nothing was done.",
                    "warning",
                )

            print(
                prepared_df[column_prepare]
                .describe(include="all")
                .reset_index()
                .rename(columns={"index": "Type"})
            )

            if "submit_preview" in request.form:
                create_or_modify_active_prepared_file(prepared_df)
                show_prepared_file = True
                flash(
                    f"Capping was successfull. The results can be seen in the right graph.",
                    "success",
                )
            elif "submit_permanent" in request.form:
                create_or_modify_active_file(prepared_df)
                show_prepared_file = False
                flash(
                    f"Capping was made permanent successfully.",
                    "success",
                )
            else:
                flash(
                    f"Not recognised submit type.",
                    "danger",
                )

        return get_controller_specific_template_with_args(
            "capping.html",
            capping.__name__,
            get_active_dataframe_formatted(),
            show_prepared_file,
        )
    else:
        return "Use get or post to request this page"


@data_preparation.route("/return_ajax_construct_before")
def return_ajax_construct_before():
    # print(f"inside regturn ajax data. Value: {request.args.get('data')}")
    return get_graph_json(get_active_dataframe(), request.args.get("column_prepare"))


@data_preparation.route("/return_ajax_construct_after")
def return_ajax_construct_after():
    # print(f"inside regturn ajax data. Value: {request.args.get('data')}")
    return get_graph_json(
        get_active_dataframe_prepared(), request.args.get("column_prepare")
    )


def change_config_files(new_config=None):
    if not new_config:
        flash("No changed configs received.", "warning")
        return None
    print(f"{new_config=}")

    return create_or_modify_user_config_file(
        get_active_dataset_name(),
        create_config_dict(
            "has_header" in new_config,
            new_config["file_separator"] if "file_separator" in new_config else "",
        ),
    )


def get_graph_json(df, column):
    if not column or column == "None":
        return return_empty_plot()

    # print(f"inside gm. Value: {column}")
    # print(f"inside gm. Value type: {type(column)}")
    fig = px.violin(df, x=column, points="all", title=f"Violin Plot of {column}")

    if not fig:
        return return_empty_plot()

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
