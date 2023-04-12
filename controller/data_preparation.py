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
    filter_active_dataframe_string_column,
    filter_active_dataframe_category_column,
    change_column_name,
    change_category_name,
    handle_missing_values,
    add_na_value_type,
    remove_complete_duplicates,
    one_hot_encode_column,
    get_active_dataframe_prepared_formatted,
    extract_dates_and_add,
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
    "transpose",
    "capping",
    "filtering",
    "missing_values",
    "encoding_extracting_duplicates",
    "automatic_detection",
    # "anomaly_detection",
    # "normalisation",
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
            elif "submit_change_column_name" in request.form:
                if (
                    "change_column_name" in request.form
                    and request.form["change_column_name"] != "None"
                    and "new_column_name" in request.form
                    and request.form["new_column_name"] != ""
                ):
                    change_column_name(
                        request.form["change_column_name"],
                        request.form["new_column_name"],
                    )
                else:
                    flash(
                        "Please provide the column and a new name to change it.", "info"
                    )
            elif "submit_change_category_name" in request.form:
                if (
                    "change_category_column_name" in request.form
                    and request.form["change_category_column_name"] != "None"
                    and "change_category_occurence_before" in request.form
                    and request.form["change_category_occurence_before"] != ""
                    and "change_category_occurence_after" in request.form
                    and request.form["change_category_occurence_after"] != ""
                ):
                    change_category_name(
                        request.form["change_category_column_name"],
                        request.form["change_category_occurence_before"],
                        request.form["change_category_occurence_after"],
                    )
                else:
                    flash(
                        "Please provide the column and a new name to change it.", "info"
                    )
            else:
                return "No method like this."

        display_df_list_of_dicts = get_active_dataframe_formatted()
        # print(display_df_list_of_dicts)
        return get_controller_specific_template_with_args(
            "manual_repairing.html",
            manual_repairing.__name__,
            display_df_list_of_dicts,
            get_active_dataframe_column_type_dict(),
        )
    else:
        return "Use get or post to request this page"


@data_preparation.route("/filtering", methods=["POST", "GET"])
def filtering():
    if not check_if_active_dataset_is_set():
        return send_user_to_set_active_dataset()

    show_prepared_file = False

    if request.method == "GET" or request.method == "POST":
        plot_to_show = "violin"
        if request.method == "POST":
            method = None
            is_preview = False

            for key, value in request.form.items():
                if "submit_filter" in key:
                    method = key
                    if "preview" in key:
                        is_preview = True
                    break

            # print(method)
            # print(is_preview)
            print(request.form)

            show_prepared_file = True

            if "submit_filter_string" in method:
                print("string")
                prepare_column = request.form["filter_column_string"]
                match_string = request.form["string_match"]
                has_to_be_complete_match = (
                    True if "has_to_be_complete_match" in request.form else False
                )
                delete_matches = (
                    True if "delete_matches_string" in request.form else False
                )

                # print(prepare_column)
                # print(match_string)
                # print(has_to_be_complete_match)
                # print(delete_matches)

                filter_active_dataframe_string_column(
                    prepare_column,
                    match_string,
                    has_to_be_complete_match,
                    delete_matches,
                    is_preview,
                )

                show_prepared_file = prepare_column
                plot_to_show = "histogram"
            # elif "submit_filter_date" in method:
            #     print("date")
            #     prepare_column = request.form["filter_column_date"]
            #     show_prepared_file = prepare_column
            # elif "submit_filter_int" in method:
            #     print("int")
            #     prepare_column = request.form["filter_column_int"]
            #     show_prepared_file = prepare_column
            # elif "submit_filter_float" in method:
            #     print("float")
            #     prepare_column = request.form["filter_column_float"]
            #     show_prepared_file = prepare_column
            elif "submit_filter_category" in method:
                print("category")
                prepare_column = request.form["filter_column_category"]
                category_match = request.form["category_match"]
                delete_matches = (
                    True if "delete_matches_category" in request.form else False
                )

                print(prepare_column)
                print(category_match)
                print(delete_matches)

                filter_active_dataframe_category_column(
                    prepare_column,
                    category_match,
                    delete_matches,
                    is_preview,
                )

                show_prepared_file = prepare_column
                plot_to_show = "histogram"
            else:
                return "No method like this."

        # if not show_prepared_file:
        #     show_prepared_file = "None"

        return get_controller_specific_template_with_args(
            "filtering.html",
            filtering.__name__,
            get_active_dataframe_formatted(),
            show_prepared_file,
            plot_to_show,
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
                    "violin",
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
            "violin",
            get_active_dataframe_column_type_dict(),
        )
    else:
        return "Use get or post to request this page"


@data_preparation.route("/missing_values", methods=["POST", "GET"])
def missing_values():
    if not check_if_active_dataset_is_set():
        return send_user_to_set_active_dataset()

    # print(active_user_file_configs)

    if request.method == "GET" or request.method == "POST":
        show_prepared = False
        if request.method == "POST":
            print(request.form)
            is_preview = False

            if "submit_add_na_value_type" in request.form:
                if (
                    "new_missing_value_string" in request.form
                    and request.form["new_missing_value_string"] != ""
                ):
                    add_na_value_type(request.form["new_missing_value_string"])
                else:
                    flash(
                        f"Please select a new missing values text.",
                        "info",
                    )
            else:
                if "submit_handle_missing_values_preview" in request.form:
                    is_preview = True

                if (
                    "missing_value_handling_option" in request.form
                    and request.form["missing_value_handling_option"] != "None"
                ):
                    handle_missing_values(
                        request.form["missing_value_handling_option"],
                        "handle_numbers" in request.form,
                        "handle_categories" in request.form,
                        is_preview,
                    )

                    if "submit_handle_missing_values" in request.form:
                        show_prepared = False
                    else:
                        show_prepared = True

                else:
                    flash(
                        f"Please select a missing values handling option.",
                        "info",
                    )

        # flash(
        #     f"Depending on the amount of data, displaying it in a smart table might take a few seconds.",
        #     "success",
        # )

        return get_controller_specific_template_with_args(
            "missing_values.html",
            missing_values.__name__,
            get_active_dataframe_formatted(),
            show_prepared,
            "missing_bar_chart",
            get_active_user_file_config()["na_values_list"],
        )
    else:
        return "Use get or post to request this page"


@data_preparation.route("/encoding_extracting_duplicates", methods=["POST", "GET"])
def encoding_extracting_duplicates():
    if not check_if_active_dataset_is_set():
        return send_user_to_set_active_dataset()

    # print(active_user_file_configs)

    if request.method == "GET" or request.method == "POST":
        is_preview = False
        if request.method == "POST":
            print(request.form)

            if (
                "submit_encode_column_preview" in request.form
                or "submit_encode_column" in request.form
            ):
                if (
                    "encode_column_name" in request.form
                    and request.form["encode_column_name"] != "None"
                ):
                    is_preview = "submit_encode_column_preview" in request.form
                    one_hot_encode_column(
                        request.form["encode_column_name"],
                        is_preview,
                        "remove_old_column_encode" in request.form,
                    )
                else:
                    flash(
                        f"Please select a column to encode.",
                        "info",
                    )
            elif (
                "submit_extract_dates_preview" in request.form
                or "submit_extract_dates" in request.form
            ):
                is_preview = "submit_extract_dates_preview" in request.form
                extract_dates_and_add(
                    is_preview, "remove_old_column_dates" in request.form
                )
            elif (
                "submit_remove_duplicates_preview" in request.form
                or "submit_remove_duplicates" in request.form
            ):
                is_preview = "submit_remove_duplicates_preview" in request.form
                remove_complete_duplicates(is_preview)
            else:
                flash(
                    f"No viable submit option given.",
                    "warning",
                )

            #     if (
            #         "missing_value_handling_option" in request.form
            #         and request.form["missing_value_handling_option"] != "None"
            #     ):
            #         handle_missing_values(
            #             request.form["missing_value_handling_option"],
            #             "handle_numbers" in request.form,
            #             "handle_categories" in request.form,
            #             is_preview,
            #         )

            #         if "submit_handle_missing_values" in request.form:
            #             show_prepared = False
            #         else:
            #             show_prepared = True

            #     else:
            #         flash(
            #             f"Please select a missing values handling option.",
            #             "info",
            #         )

        # flash(
        #     f"Depending on the amount of data, displaying it in a smart table might take a few seconds.",
        #     "success",
        # )

        return get_controller_specific_template_with_args(
            "encoding_extracting_duplicates.html",
            encoding_extracting_duplicates.__name__,
            get_active_dataframe_prepared_formatted()
            if is_preview
            else get_active_dataframe_formatted(),
            get_active_dataframe_column_type_dict(),
            is_preview,
        )
    else:
        return "Use get or post to request this page"


@data_preparation.route("/return_ajax_construct_before")
def return_ajax_construct_before():
    # print(f"inside regturn ajax data. Value: {request.args.get('data')}")
    return get_graph_json(
        get_active_dataframe(),
        request.args.get("column_prepare"),
        request.args.get("graph_type"),
    )


@data_preparation.route("/return_ajax_construct_after")
def return_ajax_construct_after():
    # print(f"inside regturn ajax data. Value: {request.args.get('data')}")
    return get_graph_json(
        get_active_dataframe_prepared(),
        request.args.get("column_prepare"),
        request.args.get("graph_type"),
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
    fig = None
    if not graph_type or graph_type == "violin":
        fig = px.violin(df, x=column, points="all", title=f"Violin Plot of {column}")
    elif graph_type == "histogram":
        fig = px.histogram(df, x=column, title=f"Histogram of {column}")
    elif graph_type == "missing_bar_chart":
        na_df = df.notnull().sum().to_frame("row_count")
        fig = px.bar(
            na_df,
            y="row_count",
            title=f"Count of rows without missing values. Total count: {df.shape[0]}",
        )
    else:
        fig = None

    if not fig:
        return return_empty_plot("No graph type like this availabe.")

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
