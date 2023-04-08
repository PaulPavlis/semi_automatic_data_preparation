from flask import Blueprint, request, flash, current_app, redirect, url_for
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
    add_row_to_active_df,
    remove_row_from_active_df,
    remove_column_from_active_df,
    change_column_type,
    get_active_dataframe_column_type,
    get_active_dataframe_column_type_dict,
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
    "manual_repairing",
    "capping",
    "transpose",
    "filtering",
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

    if request.method == "GET" or request.method == "POST":
        if request.method == "POST":
            # print(request.form)

            if "submit_add_row" in request.form:
                print("submit_add_row")
                add_row_to_active_df(request.form)
            elif "submit_remove_row" in request.form:
                if (
                    "remove_row" in request.form
                    and request.form["remove_row"].isdigit()
                ):
                    remove_row_from_active_df(request.form["remove_row"])
                else:
                    flash("Please provide the row number to remove a row.", "info")
            elif "submit_remove_column" in request.form:
                if (
                    "remove_column" in request.form
                    and request.form["remove_column"] != "None"
                ):
                    remove_column_from_active_df(request.form["remove_column"])
                else:
                    flash("Please provide the column to remove it.", "info")
            elif "submit_change_column_type" in request.form:
                if (
                    "new_column_type" in request.form
                    and "change_column" in request.form
                    and request.form["change_column"] != "None"
                ):
                    change_column_type(
                        request.form["change_column"], request.form["new_column_type"]
                    )
                else:
                    flash("Please provide the column and a type to change it.", "info")
            else:
                return "No method like this."

        display_df_list_of_dicts = get_active_dataframe_formatted()
        print(display_df_list_of_dicts)
        return get_controller_specific_template_with_args(
            "manual_repairing.html", manual_repairing.__name__, display_df_list_of_dicts
        )
    else:
        return "Use get or post to request this page"


@data_preparation.route("/filtering", methods=["POST", "GET"])
def filtering():
    if not check_if_active_dataset_is_set():
        return send_user_to_set_active_dataset()

    show_prepared_file = False

    if request.method == "GET" or request.method == "POST":
        if request.method == "POST":
            print(request.form)

            show_prepared_file = True

            # if "submit_add_row" in request.form:
            #     print("submit_add_row")
            #     add_row_to_active_df(request.form)
            # elif "submit_remove_row" in request.form:
            #     if (
            #         "remove_row" in request.form
            #         and request.form["remove_row"].isdigit()
            #     ):
            #         remove_row_from_active_df(request.form["remove_row"])
            #     else:
            #         flash("Please provide the row number to remove a row.", "info")
            # elif "submit_remove_column" in request.form:
            #     if (
            #         "remove_column" in request.form
            #         and request.form["remove_column"] != "None"
            #     ):
            #         remove_column_from_active_df(request.form["remove_column"])
            #     else:
            #         flash("Please provide the column to remove it.", "info")
            # elif "submit_change_column_type" in request.form:
            #     if (
            #         "new_column_type" in request.form
            #         and "change_column" in request.form
            #         and request.form["change_column"] != "None"
            #     ):
            #         change_column_type(
            #             request.form["change_column"], request.form["new_column_type"]
            #         )
            #     else:
            #         flash("Please provide the column and a type to change it.", "info")
            # else:
            #     return "No method like this."

        display_df_list_of_dicts = get_active_dataframe_formatted()
        # print(display_df_list_of_dicts)
        return get_controller_specific_template_with_args(
            "filtering.html",
            filtering.__name__,
            display_df_list_of_dicts,
            show_prepared_file,
            get_active_dataframe_column_type_dict(),
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
        show_prepared_file = False
        prepared_df = get_active_dataframe()
        if request.method == "POST":
            # change_config_files(request.form)
            prepared_df = (
                prepared_df.transpose()
                .reset_index()
                .rename(columns={"index": "previous_header"})
            )
            print(prepared_df)
            for column_iterator in range(prepared_df.shape[1] - 1):
                prepared_df = prepared_df.rename(
                    columns={column_iterator: f"column_{column_iterator+1}"}
                )

            if "submit_preview" in request.form:
                create_or_modify_active_prepared_file(prepared_df)
                show_prepared_file = True
                flash(
                    f"Transposing (preview) was successfull. The results can be seen below.",
                    "success",
                )
            elif "submit_permanent" in request.form:
                create_or_modify_active_file(prepared_df)
                show_prepared_file = False
                flash(
                    f"Transposing was made permanent successfully.",
                    "success",
                )
                flash(
                    f"Transposing normally needs manual repairing, since the header row is now not labeled and maybe a row or column got added.",
                    "info",
                )

                # To load the site again. Otherwise it will not show the Display table
                return redirect(url_for("data_preparation.transpose"))
            elif "submit_reset" in request.form:
                prepared_df = get_active_dataframe()
                show_prepared_file = False
                flash(
                    f"Current dataframe is shown.",
                    "success",
                )
            else:
                flash(
                    f"Not recognised submit type.",
                    "danger",
                )

        return get_controller_specific_template_with_args(
            "transpose.html",
            transpose.__name__,
            prepared_df.to_dict("records"),
            show_prepared_file,
        )
    else:
        return "Use get or post to request this page"


@data_preparation.route("/capping", methods=["POST", "GET"])
def capping():
    if not check_if_active_dataset_is_set():
        return send_user_to_set_active_dataset()

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

            # print(
            #     prepared_df[column_prepare]
            #     .describe(include="all")
            #     .reset_index()
            #     .rename(columns={"index": "Type"})
            # )

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

            # print(
            #     prepared_df[column_prepare]
            #     .describe(include="all")
            #     .reset_index()
            #     .rename(columns={"index": "Type"})
            # )

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

        if show_prepared_file:
            show_prepared_file = str(request.form["column_prepare"])

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
    return get_graph_json(get_active_dataframe(), request.args.get("column_prepare"), request.args.get("graph_type"))


@data_preparation.route("/return_ajax_construct_after")
def return_ajax_construct_after():
    # print(f"inside regturn ajax data. Value: {request.args.get('data')}")
    return get_graph_json(
        get_active_dataframe_prepared(), request.args.get("column_prepare"), request.args.get("graph_type")
    )


@data_preparation.route("/return_ajax_dtype_value_of_column")
def return_ajax_dtype_value_of_column():
    # print(f"inside regturn ajax data. Value: {request.args.get('data')}")
    return get_active_dataframe_column_type(request.args.get("column_name"))


def change_config_files(new_config=None):
    if not new_config:
        flash("No changed configs received.", "warning")
        return None
    # print(f"{new_config=}")

    return create_or_modify_user_config_file(
        get_active_dataset_name(),
        create_config_dict(
            "has_header" in new_config,
            new_config["file_separator"] if "file_separator" in new_config else "",
            "has_index" in new_config,
        ),
    )


def get_graph_json(df, column, graph_type="violin"):
    if not column or column == "None":
        return return_empty_plot()

    # print(f"inside gm. Value: {column}")
    # print(f"inside gm. Value type: {type(column)}")
    if not graph_type or graph_type == "violin":
        fig = px.violin(df, x=column, points="all", title=f"Violin Plot of {column}")
    elif graph_type == "histogram":
        fig = px.histogram(df, x=column, title=f"Histogram of {column}")
    else:
        fig = None

    if not fig:
        return return_empty_plot("No graph type like this availabe.")

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
